"""LLM structured intent draft — Admin AI gateway; falls back to keyword in pipeline."""

from __future__ import annotations

import json
import logging
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.agent_runtime import IntentNluDraft, IntentScenarioCandidateDraft
from chainup_agent.application.agent_llm_chat import (
    _build_ark_responses_payload,
    _extract_openai_chat_content,
    _extract_text_from_ark_response,
    _volcengine_ark_responses_url,
    load_llm_gateway_context,
)
from chainup_agent.application.agent_llm_upstream import openai_chat_completions_url
from chainup_agent.application.agent_prompt_assembly import (
    assemble_intent_nlu_system_prompt,
)
from chainup_agent.application.agent_prompt_effective import load_intent_nlu_system_prompt
from chainup_agent.application.agent_scenario_catalog import scenario_readiness_map
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError

logger = logging.getLogger(__name__)

_MAX_PROMPT_CHARS = 8000
_MAX_INTENT_ASSEMBLED_SYSTEM_CHARS = 28000


class LlmIntentNluCandidate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(alias="scenarioId")
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class LlmIntentNluPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    primary_scenario_id: str = Field(alias="primaryScenarioId")
    scenario_id_candidates: list[LlmIntentNluCandidate] = Field(
        default_factory=list,
        alias="scenarioIdCandidates",
    )
    slots: dict[str, str] = Field(default_factory=dict)
    order_type_hint: Literal["market", "limit", "unknown"] = Field(
        default="unknown",
        alias="orderTypeHint",
    )


def _strip_json_fence(text: str) -> str:
    t = text.strip()
    if not t.startswith("```"):
        return t
    lines = t.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _coarse_intent_family(scenario_id: str | None) -> str:
    if scenario_id is None:
        return "unknown"
    if scenario_id == "chat.faq":
        return "chat"
    if scenario_id.startswith("read."):
        return "portfolio_read"
    if scenario_id.startswith("wealth."):
        return "wealth_read"
    if scenario_id.startswith("trade."):
        return "trade_write"
    if scenario_id.startswith("margin."):
        return "margin_trade"
    if scenario_id.startswith("automation."):
        return "automation"
    return "unknown"


def _parse_llm_intent_payload(text: str) -> LlmIntentNluPayload | None:
    try:
        blob = _strip_json_fence(text)
        raw = json.loads(blob)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(raw, dict):
        return None
    try:
        return LlmIntentNluPayload.model_validate(raw)
    except ValidationError:
        return None


def _llm_payload_to_draft(
    payload: LlmIntentNluPayload,
    *,
    registry: set[str],
) -> tuple[IntentNluDraft, list[tuple[str, float]]] | None:
    cands_in = list(payload.scenario_id_candidates)
    cands_in = [c for c in cands_in if c.scenario_id.strip() in registry]
    cands_in.sort(key=lambda x: x.confidence, reverse=True)
    ranked: list[tuple[str, float]] = [
        (c.scenario_id.strip(), float(c.confidence)) for c in cands_in[:8]
    ]

    primary = payload.primary_scenario_id.strip()
    if primary not in registry:
        primary = ranked[0][0] if ranked else ""

    if not primary or primary not in registry:
        return None

    if primary not in [x[0] for x in ranked]:
        ranked = [(primary, 0.9)] + [x for x in ranked if x[0] != primary]
    elif not ranked:
        ranked = [(primary, 0.9)]

    cand_models = [
        IntentScenarioCandidateDraft(scenario_id=sid, confidence=sc) for sid, sc in ranked[:5]
    ]
    slots = {k: str(v).strip() for k, v in payload.slots.items() if str(v).strip()}

    return (
        IntentNluDraft(
            source="llm_structured_v1",
            primary_intent_family=_coarse_intent_family(primary),
            scenario_id_candidates=cand_models,
            slots=slots,
            order_type_hint=payload.order_type_hint,
            clarify_hints=[],
        ),
        ranked,
    )


async def try_llm_intent_nlu_draft(
    session: AsyncSession,
    settings: Settings,
    user_text: str,
    *,
    effective_locale: str | None = None,
    previous_scenario_id: str | None = None,
    execution_id: str | None = None,
    session_id: str | None = None,
) -> tuple[IntentNluDraft, list[tuple[str, float]]] | None:
    """
    Call gateway LLM once; parse JSON into ``IntentNluDraft`` + keyword-style ``ranked``.

    Returns ``None`` on any failure (caller falls back to keyword NLU).
    """
    raw = user_text.strip()
    if not raw:
        return None

    ctx, err = await load_llm_gateway_context(session, settings)
    if ctx is None:
        logger.info("intent_nlu_llm_skip reason=gateway:%s", (err or "")[:120])
        return None

    timeout_sec = min(
        float(settings.intent_nlu_llm_timeout_sec),
        float(ctx.merged_defaults.get("timeoutSec") or 120),
    )
    try:
        core, core_ver = await load_intent_nlu_system_prompt(
            session,
            effective_locale=effective_locale,
            previous_scenario_id=previous_scenario_id,
            execution_id=execution_id,
            session_id=session_id,
        )
        system, _asm_meta = await assemble_intent_nlu_system_prompt(
            session,
            intent_core_text=core,
            effective_locale=effective_locale,
            previous_scenario_id=previous_scenario_id,
            execution_id=execution_id,
            session_id=session_id,
            intent_pack_version=core_ver,
        )
        system = system[:_MAX_INTENT_ASSEMBLED_SYSTEM_CHARS]
    except AppError as exc:
        if exc.code == "PROMPT_INJECTION_FORBIDDEN":
            logger.error(
                "intent_nlu_llm_skip reason=PROMPT_INJECTION_FORBIDDEN details=%s",
                exc.details,
            )
            return None
        raise
    user_block = f"用户原话：\n{raw[:_MAX_PROMPT_CHARS]}"

    if ctx.use_ark:
        combined = f"{system}\n\n{user_block}"
        payload: dict[str, Any] = _build_ark_responses_payload(
            ctx.upstream_model_id, combined, stream=False
        )
    else:
        payload = {
            "model": ctx.upstream_model_id,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_block},
            ],
            "max_tokens": 900,
            "temperature": 0.1,
        }

    headers = {
        "Authorization": f"Bearer {ctx.token}",
        "Content-Type": "application/json",
    }
    url = (
        _volcengine_ark_responses_url(ctx.base_url)
        if ctx.use_ark
        else openai_chat_completions_url(ctx.base_url)
    )

    try:
        async with httpx.AsyncClient(timeout=timeout_sec, follow_redirects=True) as client:
            r = await client.post(url, json=payload, headers=headers)
    except (httpx.TimeoutException, httpx.HTTPError) as exc:
        logger.warning("intent_nlu_llm_transport err=%s", type(exc).__name__)
        return None

    try:
        data = r.json() if r.content else {}
    except ValueError:
        return None
    if not isinstance(data, dict) or r.status_code >= 400:
        logger.info("intent_nlu_llm_bad_http status=%s", r.status_code)
        return None

    if ctx.use_ark:
        content = _extract_text_from_ark_response(data)
    else:
        content = _extract_openai_chat_content(data)

    if not content:
        logger.info("intent_nlu_llm_empty_body")
        return None

    parsed = _parse_llm_intent_payload(content)
    if parsed is None:
        logger.info("intent_nlu_llm_json_parse_failed preview=%s", content[:160])
        return None

    registry = set(scenario_readiness_map().keys())
    out = _llm_payload_to_draft(parsed, registry=registry)
    if out is None:
        logger.info("intent_nlu_llm_registry_reject primary=%s", parsed.primary_scenario_id)
        return None

    logger.info(
        "intent_nlu_llm_ok model=%s primary=%s",
        ctx.model_id,
        out[0].scenario_id_candidates[0].scenario_id if out[0].scenario_id_candidates else "-",
    )
    return out
