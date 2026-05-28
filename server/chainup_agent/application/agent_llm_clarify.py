"""Optional LLM polish for rule-based CLARIFY lines (``agent.runtime.runtime_clarify``)."""

from __future__ import annotations

import logging

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_llm_chat import (
    _build_ark_responses_payload,
    _extract_openai_chat_content,
    _extract_text_from_ark_response,
    _volcengine_ark_responses_url,
    load_llm_gateway_context,
    openai_chat_completions_url,
)
from chainup_agent.application.agent_prompt_effective import (
    effective_prompt_snapshot_for_scenario,
    get_published_pack_for_scenario,
    pack_messages_or_empty,
)
from chainup_agent.core.config import Settings
from chainup_agent.data.prompt_governance_bodies import PROMPT_BODY_BY_PACK_ID
from chainup_agent.data.prompt_governance_catalog import RUNTIME_CLARIFY_SCENARIO_ID

logger = logging.getLogger(__name__)

_MAX_USER_CHARS = 6000
_CLARIFY_SCENARIO_ID = RUNTIME_CLARIFY_SCENARIO_ID


def resolve_effective_intent_clarify_use_llm(
    settings: Settings,
    merged_defaults: dict | None = None,
) -> bool:
    if settings.intent_clarify_use_llm:
        return True
    if merged_defaults and merged_defaults.get("intentClarifyUseLlm") is True:
        return True
    return False


def _system_from_clarify_pack(row) -> str:
    for m in pack_messages_or_empty(row):
        if str(m.get("role", "")).lower() == "system":
            c = m.get("content")
            if isinstance(c, str) and c.strip():
                return c.strip()
    return PROMPT_BODY_BY_PACK_ID.get("pp-runtime-clarify", "你是交易 Agent，负责澄清缺失参数。")


def _build_clarify_user_block(
    *,
    user_text: str,
    scenario_id: str | None,
    rule_lines: list[str],
    policy_codes: list[str],
    slots: dict[str, str],
    session_id: str | None = None,
) -> str:
    stm_summary = ""
    if session_id:
        from chainup_agent.application.clarify_session import get_clarify_session_raw

        snap = get_clarify_session_raw(session_id)
        if snap and not snap.abandoned:
            stm_summary = snap.memory_summary().get("resolvedSlotsHumanSummary", "")

    lines = [
        "【任务】根据下方规则澄清要点，用 1～3 句中文向用户追问；禁止猜测价格/数量/交易对。",
        f"【场景】{scenario_id or 'unknown'}",
        f"【policyCodes】{', '.join(policy_codes) if policy_codes else '-'}",
    ]
    if stm_summary:
        lines.append(f"【会话已确认摘要】{stm_summary}")
    lines.append("【当前已识别槽位（可能不完整）】")
    if slots:
        for k, v in sorted(slots.items()):
            lines.append(f"- {k}: {v}")
    else:
        lines.append("- （无）")
    lines.append("【规则层必须覆盖的澄清点（不可遗漏）】")
    for r in rule_lines:
        lines.append(f"- {r}")
    lines.append("【用户本轮原话】")
    lines.append(user_text.strip()[:_MAX_USER_CHARS])
    lines.append(
        "【输出要求】只输出给用户看的追问正文，不要 JSON、不要 markdown 代码块、不要解释系统规则。"
    )
    return "\n".join(lines)


async def try_llm_clarify_reply(
    session: AsyncSession,
    settings: Settings,
    *,
    user_text: str,
    scenario_id: str | None,
    rule_lines: list[str],
    policy_codes: list[str] | None = None,
    slots: dict[str, str] | None = None,
    effective_locale: str | None = None,
    execution_id: str | None = None,
    session_id: str | None = None,
) -> tuple[str | None, dict[str, str] | None]:
    """
    Returns (assistant_text, observability_dict) or (None, None) on skip/failure.
    """
    _ = (effective_locale, execution_id)
    raw = user_text.strip()
    if not raw or not rule_lines:
        return None, None

    ctx, err = await load_llm_gateway_context(session, settings)
    if ctx is None:
        logger.info("clarify_llm_skip reason=gateway:%s", (err or "")[:120])
        return None, None

    pack_row = await get_published_pack_for_scenario(session, scenario_id=_CLARIFY_SCENARIO_ID)
    system = _system_from_clarify_pack(pack_row) if pack_row else _system_from_clarify_pack(None)

    timeout_sec = min(
        float(settings.intent_clarify_llm_timeout_sec),
        float(ctx.merged_defaults.get("timeoutSec") or 120),
    )
    user_block = _build_clarify_user_block(
        user_text=raw,
        scenario_id=scenario_id,
        rule_lines=rule_lines,
        policy_codes=list(policy_codes or []),
        slots=dict(slots or {}),
        session_id=session_id,
    )

    if ctx.use_ark:
        combined = f"{system}\n\n{user_block}"
        payload = _build_ark_responses_payload(ctx.upstream_model_id, combined, stream=False)
    else:
        payload = {
            "model": ctx.upstream_model_id,
            "messages": [
                {"role": "system", "content": system[:28000]},
                {"role": "user", "content": user_block},
            ],
            "max_tokens": 600,
            "temperature": 0.2,
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
        logger.info("clarify_llm_skip reason=transport:%s", type(exc).__name__)
        return None, None

    try:
        data = r.json() if r.content else {}
    except ValueError:
        return None, None
    if not isinstance(data, dict) or r.status_code >= 400:
        logger.info("clarify_llm_skip reason=http status=%s", r.status_code)
        return None, None

    text_out = (
        _extract_text_from_ark_response(data)
        if ctx.use_ark
        else _extract_openai_chat_content(data)
    )
    text_out = (text_out or "").strip()
    if not text_out:
        return None, None

    ver, binding = await effective_prompt_snapshot_for_scenario(
        session, scenario_id=_CLARIFY_SCENARIO_ID
    )
    obs = {
        "scenarioId": _CLARIFY_SCENARIO_ID,
        "targetScenarioId": scenario_id,
        "promptPackVersion": ver,
        "resolvedPromptBinding": binding,
        "ruleLineCount": len(rule_lines),
        "gatewayModelId": ctx.model_id,
    }
    return text_out[:2000], obs
