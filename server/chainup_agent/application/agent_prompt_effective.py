"""Load published prompt packs for runtime (FR-PM08 — effective read slice)."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.infrastructure.persistence.models.admin_prompt_pack import AdminPromptPack

from chainup_agent.application.effective_locale import normalize_effective_locale
from chainup_agent.application.prompt_runtime_substitution import substitute_runtime_placeholders
from chainup_agent.application.resolved_prompt_binding import (
    build_resolved_prompt_binding,
    primary_prompt_pack_version_for_binding,
)

logger = logging.getLogger(__name__)

# Frozen scenario key for structured intent NLU system prompt (seeded migration 0006).
INTENT_NLU_SCENARIO_ID = "agent.runtime.intent_nlu"

_INTENT_NLU_FALLBACK_SYSTEM = """\
你是交易所 Telegram 机器人的「意图解析」模块。仅输出 **一个 JSON 对象**
（不要 Markdown、不要代码围栏、不要解释文字）。
JSON 字段（camelCase）：
- primaryScenarioId: string，必须从下列 id 中选一个作为主意图：
  read.market.ticker, read.market.depth, read.market.trades, read.account.balance,
  wealth.holdings_read,
  trade.spot.flash_convert, trade.spot.limit_order, trade.spot.open_orders, trade.spot.cancel_order,
  trade.futures.market_order, trade.futures.limit_order,
  margin.cross.market_order,
  automation.condition_order,
  chat.faq
- scenarioIdCandidates: 数组，元素为 { "scenarioId": string, "confidence": number 0到1 }，
  最多 5 条，按置信度降序
- slots: 对象，可含 symbol（如 BTC-USDT）、side（BUY 或 SELL）、quantity（十进制字符串）
- orderTypeHint: "market" | "limit" | "unknown"

规则：不得编造未列出的 scenarioId；不确定时降低 confidence 或选 chat.faq。"""


def _sha_etag(messages: list[dict[str, Any]]) -> str:
    raw = json.dumps(messages, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return f'W/"{hashlib.sha256(raw).hexdigest()[:32]}"'


PROMPT_BODY_MAX_BYTES = 256 * 1024


def messages_json_byte_length(messages: list[dict[str, Any]]) -> int:
    """PM-C04 — serialized `messages_json` UTF-8 byte length."""
    return len(json.dumps(messages, ensure_ascii=False).encode("utf-8"))


async def get_published_pack_for_scenario(
    session: AsyncSession,
    *,
    scenario_id: str,
) -> AdminPromptPack | None:
    from chainup_agent.application.prompt_governance_resolve import (
        get_published_governance_pack_for_scenario,
        get_published_pack_for_scenario_legacy,
    )

    gov = await get_published_governance_pack_for_scenario(session, scenario_id=scenario_id)
    if gov is not None:
        return gov
    return await get_published_pack_for_scenario_legacy(session, scenario_id=scenario_id)


async def get_published_pack_for_scenario_and_type(
    session: AsyncSession,
    *,
    scenario_id: str,
    prompt_pack_type: str,
) -> AdminPromptPack | None:
    """Prefer newest ``updated_at`` when multiple published rows match (ops nuance)."""
    sid = scenario_id.strip()
    ptype = prompt_pack_type.strip().upper()
    lifecycles = ("PUBLISHED", "LOCKED") if ptype == "SYSTEM" else ("PUBLISHED",)
    stmt = (
        select(AdminPromptPack)
        .where(
            AdminPromptPack.scenario_id == sid,
            AdminPromptPack.prompt_pack_type == ptype,
            AdminPromptPack.lifecycle.in_(lifecycles),
        )
        .order_by(AdminPromptPack.updated_at.desc())
        .limit(1)
    )
    try:
        return (await session.execute(stmt)).scalar_one_or_none()
    except (OperationalError, ProgrammingError) as exc:
        logger.info(
            "prompt_pack_query_skipped reason=%s scenario=%s type=%s",
            type(exc).__name__,
            sid[:80],
            ptype,
        )
        return None


def pack_messages_or_empty(row: AdminPromptPack) -> list[dict[str, Any]]:
    try:
        raw = json.loads(row.messages_json)
    except (json.JSONDecodeError, TypeError):
        return []
    return raw if isinstance(raw, list) else []


async def load_intent_nlu_system_prompt(
    session: AsyncSession,
    *,
    effective_locale: str | None = None,
    previous_scenario_id: str | None = None,
    execution_id: str | None = None,
    session_id: str | None = None,
) -> tuple[str, str]:
    row = await get_published_pack_for_scenario(session, scenario_id=INTENT_NLU_SCENARIO_ID)

    eff = normalize_effective_locale(effective_locale)
    pack_ver = str(row.prompt_pack_version).strip() if row is not None else "0"
    schema_blob: str | None = row.variable_schema_json if row is not None else None

    def _finalize(raw_prompt: str) -> str:
        builtin_upper = {
            "EFFECTIVE_LOCALE": eff,
            "SCENARIO_ID": (previous_scenario_id or "").strip(),
            "EXECUTION_ID": (execution_id or "").strip(),
            "PROMPT_PACK_VERSION": pack_ver,
            "USER_VISIBLE_MESSAGE": "",
            # Intent NLU system text only; Telegram bind/deeplink UX is orthogonal.
            "REQUIRES_MAIN_SITE": "false",
            "SESSION_ID": (session_id or "").strip(),
            "AGENT_CONTEXT": "",
        }
        resolved, stripped = substitute_runtime_placeholders(
            raw_prompt,
            variable_schema_json=schema_blob,
            builtin_values_upper=builtin_upper,
            observability_context="intent_nlu.system_prompt",
        )
        if stripped:
            logger.warning(
                "intent_nlu_prompt_runtime_stripped stripped=%s pack=%s",
                stripped[:48],
                row.prompt_pack_id if row else "-",
            )
        return resolved

    if row is None:
        logger.info(
            "intent_nlu_prompt_fallback reason=no_published_row scenario=%s", INTENT_NLU_SCENARIO_ID
        )
        return _finalize(_INTENT_NLU_FALLBACK_SYSTEM.strip()), pack_ver
    msgs = pack_messages_or_empty(row)
    parts: list[str] = []
    for m in msgs:
        if not isinstance(m, dict):
            continue
        if str(m.get("role") or "").strip().lower() != "system":
            continue
        c = m.get("content")
        if isinstance(c, str) and c.strip():
            parts.append(c.strip())
    if not parts:
        logger.info(
            "intent_nlu_prompt_fallback reason=no_system_message_in_row pack=%s", row.prompt_pack_id
        )
        return _finalize(_INTENT_NLU_FALLBACK_SYSTEM.strip()), pack_ver
    return _finalize("\n\n".join(parts)), pack_ver


async def effective_prompt_snapshot_for_scenario(
    session: AsyncSession,
    *,
    scenario_id: str | None,
    session_id: str | None = None,
) -> tuple[str | None, dict[str, Any] | None]:
    """Published-pack version + binding for observability / execution row (FR-PM read path).

    When no resolvable cross-pack binding exists, returns ``(None, None)`` — callers store
    nullable columns.
    """
    if not scenario_id or not str(scenario_id).strip():
        return None, None
    bind = await build_resolved_prompt_binding(
        session,
        scenario_id=str(scenario_id).strip(),
        session_id=session_id,
    )
    if bind is None:
        return None, None
    ver = await primary_prompt_pack_version_for_binding(bind)
    return ver, bind


def _variable_schema_from_row(row: AdminPromptPack) -> dict[str, Any] | None:
    raw = row.variable_schema_json
    if raw is None or not str(raw).strip():
        return None
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


async def build_effective_prompt_view(
    session: AsyncSession,
    *,
    scenario_id: str,
    session_id: str | None = None,
) -> dict[str, Any] | None:
    row = await get_published_pack_for_scenario(session, scenario_id=scenario_id)
    binding = await build_resolved_prompt_binding(
        session,
        scenario_id=scenario_id,
        session_id=session_id,
    )
    if row is None and binding is None:
        return None
    messages = pack_messages_or_empty(row) if row is not None else []
    pack_ver = (
        await primary_prompt_pack_version_for_binding(binding)
        if binding
        else (str(row.prompt_pack_version).strip() if row is not None else None)
    )
    etag = row.etag if row is not None else None
    var_schema = _variable_schema_from_row(row) if row is not None else None
    if binding is None and row is not None:
        binding = {
            "scenarioId": scenario_id,
            "sessionId": None,
            "systemPromptPackId": row.prompt_pack_id if row.prompt_pack_type == "SYSTEM" else None,
            "systemPromptPackVersion": row.prompt_pack_version
            if row.prompt_pack_type == "SYSTEM"
            else None,
            "safetyPromptPackId": None,
            "safetyPromptPackVersion": None,
            "tradingPromptPackId": row.prompt_pack_id if row.prompt_pack_type == "TRADING" else None,
            "tradingPromptPackVersion": row.prompt_pack_version
            if row.prompt_pack_type == "TRADING"
            else None,
            "fewShotDigest": None,
            "placeholderDenylistRevision": row.placeholder_denylist_revision,
            "safetyPhraseBlocklistRevision": row.safety_phrase_blocklist_revision,
        }
    return {
        "scenarioId": scenario_id,
        "promptPackVersion": pack_ver or (row.prompt_pack_version if row else None),
        "etag": etag,
        "messages": messages,
        "variableSchema": var_schema,
        "resolvedPromptBinding": binding,
    }


async def patch_prompt_pack_messages(
    session: AsyncSession,
    *,
    prompt_pack_id: str,
    messages: list[dict[str, Any]],
    bump_version: bool = True,
) -> AdminPromptPack | None:
    """admin: overwrite messages + etag; optional version bump.

    Publish uses bump_version=False.
    """
    row = await session.get(AdminPromptPack, prompt_pack_id.strip())
    if row is None:
        return None
    row.messages_json = json.dumps(messages, ensure_ascii=False)
    row.etag = _sha_etag(messages)
    if bump_version:
        try:
            v = int(str(row.prompt_pack_version)) + 1
            row.prompt_pack_version = str(v)
        except ValueError:
            row.prompt_pack_version = f"{row.prompt_pack_version}.patched"
    row.row_version = int(row.row_version) + 1
    await session.flush()
    return row
