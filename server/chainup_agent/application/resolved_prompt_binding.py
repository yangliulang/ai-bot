"""SC-PM-22 · cross-pack ``resolvedPromptBinding`` for effective read + observability."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_execution_events import (
    append_execution_timeline_event,
    list_timeline_events_for_execution,
)
from chainup_agent.data.prompt_governance_catalog import (
    PLATFORM_SAFETY_SCENARIO_ID,
    PLATFORM_SYSTEM_SCENARIO_ID,
    RUNTIME_CLARIFY_SCENARIO_ID,
    RUNTIME_OUTPUT_CONTRACT_SCENARIO_ID,
)
from chainup_agent.infrastructure.persistence.models.admin_prompt_pack import AdminPromptPack

# Governance ids (product-doc) → legacy DB primary keys (pre-0030 migrations).
_PACK_ID_CANDIDATES: dict[str, tuple[str, ...]] = {
    "system": ("pp-system-core", "pack_platform_system_v1"),
    "safety": ("pp-safety-global", "pack_platform_safety_v1"),
    "clarify": ("pp-runtime-clarify",),
    "output": ("pp-runtime-output-contract",),
}

PROMPT_BINDING_RESOLVED_EVENT = "agent.prompt.binding_resolved"
PROMPT_BINDING_LOADED_TRIGGER = "prompt.binding_resolved"


def _pack_slot(row: AdminPromptPack | None) -> tuple[str | None, str | None]:
    if row is None:
        return None, None
    return str(row.prompt_pack_id).strip(), str(row.prompt_pack_version).strip()


def _few_shot_digest(messages: list[dict[str, Any]]) -> str | None:
    pairs: list[dict[str, str]] = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        role = str(m.get("role") or "").strip().lower()
        if role not in ("user", "assistant"):
            continue
        content = m.get("content")
        if isinstance(content, str) and content.strip():
            pairs.append({"role": role, "content": content.strip()})
    if not pairs:
        return None
    raw = json.dumps(pairs, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return f"sha256:{hashlib.sha256(raw).hexdigest()[:16]}…"


async def _published_pack_by_id_candidates(
    session: AsyncSession,
    candidates: tuple[str, ...],
) -> AdminPromptPack | None:
    for pid in candidates:
        row = await session.get(AdminPromptPack, pid.strip())
        if row is None:
            continue
        life = str(row.lifecycle or "").strip().upper()
        if life in ("PUBLISHED", "LOCKED"):
            return row
    return None


async def build_resolved_prompt_binding(
    session: AsyncSession,
    *,
    scenario_id: str,
    session_id: str | None = None,
) -> dict[str, Any] | None:
    """Assemble OpenAPI ``ResolvedPromptBinding`` from platform + scenario published packs."""
    from chainup_agent.application.agent_prompt_effective import (
        get_published_pack_for_scenario,
        get_published_pack_for_scenario_and_type,
        pack_messages_or_empty,
    )
    from chainup_agent.application.prompt_governance_resolve import get_published_pack_by_id

    sid = scenario_id.strip()
    if not sid:
        return None

    row_sys = await get_published_pack_by_id(session, prompt_pack_id="pp-system-core")
    if row_sys is None:
        row_sys = await get_published_pack_for_scenario_and_type(
            session,
            scenario_id=PLATFORM_SYSTEM_SCENARIO_ID,
            prompt_pack_type="SYSTEM",
        )
    if row_sys is None:
        row_sys = await _published_pack_by_id_candidates(session, _PACK_ID_CANDIDATES["system"])

    row_safe = await get_published_pack_by_id(session, prompt_pack_id="pp-safety-global")
    if row_safe is None:
        row_safe = await get_published_pack_for_scenario_and_type(
            session,
            scenario_id=PLATFORM_SAFETY_SCENARIO_ID,
            prompt_pack_type="SAFETY",
        )
    if row_safe is None:
        row_safe = await _published_pack_by_id_candidates(session, _PACK_ID_CANDIDATES["safety"])

    row_clarify = await get_published_pack_by_id(session, prompt_pack_id="pp-runtime-clarify")
    if row_clarify is None:
        row_clarify = await _published_pack_by_id_candidates(session, _PACK_ID_CANDIDATES["clarify"])
    row_output = await get_published_pack_by_id(session, prompt_pack_id="pp-runtime-output-contract")
    if row_output is None:
        row_output = await _published_pack_by_id_candidates(session, _PACK_ID_CANDIDATES["output"])

    row_strategy = await get_published_pack_for_scenario(session, scenario_id=sid)

    sys_id, sys_ver = _pack_slot(row_sys)
    safe_id, safe_ver = _pack_slot(row_safe)
    clarify_id, clarify_ver = _pack_slot(row_clarify)
    output_id, output_ver = _pack_slot(row_output)

    trading_id: str | None = None
    trading_ver: str | None = None
    few_shot: str | None = None
    pdr: str | None = None
    spb: str | None = None

    if row_strategy is not None:
        trading_id, trading_ver = _pack_slot(row_strategy)
        few_shot = _few_shot_digest(pack_messages_or_empty(row_strategy))
        pdr = row_strategy.placeholder_denylist_revision
        spb = row_strategy.safety_phrase_blocklist_revision
    elif row_safe is not None:
        pdr = row_safe.placeholder_denylist_revision
        spb = row_safe.safety_phrase_blocklist_revision

    if not any((sys_id, safe_id, trading_id, clarify_id, output_id)):
        return None

    return {
        "scenarioId": sid,
        "sessionId": (session_id or "").strip() or None,
        "systemPromptPackId": sys_id,
        "systemPromptPackVersion": sys_ver,
        "safetyPromptPackId": safe_id,
        "safetyPromptPackVersion": safe_ver,
        "tradingPromptPackId": trading_id,
        "tradingPromptPackVersion": trading_ver,
        "runtimeClarifyPromptPackId": clarify_id,
        "runtimeClarifyPromptPackVersion": clarify_ver,
        "runtimeOutputContractPromptPackId": output_id,
        "runtimeOutputContractPromptPackVersion": output_ver,
        "fewShotDigest": few_shot,
        "placeholderDenylistRevision": pdr,
        "safetyPhraseBlocklistRevision": spb,
    }


async def primary_prompt_pack_version_for_binding(binding: dict[str, Any] | None) -> str | None:
    """Execution row ``prompt_pack_version`` — prefer scenario strategy pack."""
    if not binding:
        return None
    ver = binding.get("tradingPromptPackVersion")
    if ver is not None and str(ver).strip():
        return str(ver).strip()
    for key in ("systemPromptPackVersion", "safetyPromptPackVersion"):
        v = binding.get(key)
        if v is not None and str(v).strip():
            return str(v).strip()
    return None


async def append_prompt_binding_resolved_if_missing(
    session: AsyncSession,
    *,
    execution_id: str,
    user_id: str,
    scenario_id: str,
    session_id: str | None = None,
) -> bool:
    """Emit ``agent.prompt.binding_resolved`` once (after dispatched, before spec_read)."""
    sid = scenario_id.strip()
    eid = execution_id.strip()
    if not sid or not eid:
        return False
    existing = await list_timeline_events_for_execution(session, execution_public_id=eid)
    for row in existing:
        if row.event_type == PROMPT_BINDING_RESOLVED_EVENT:
            return False
    binding = await build_resolved_prompt_binding(session, scenario_id=sid, session_id=session_id)
    if not binding:
        return False
    await append_execution_timeline_event(
        session,
        execution_id=eid,
        user_id=user_id.strip(),
        event_name=PROMPT_BINDING_RESOLVED_EVENT,
        step_kind="prompt_binding",
        outcome="info",
        payload={
            "scenarioId": sid,
            "resolvedPromptBinding": binding,
            "transitionTrigger": PROMPT_BINDING_LOADED_TRIGGER,
        },
    )
    return True
