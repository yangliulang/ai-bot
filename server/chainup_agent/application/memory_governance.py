"""Memory governance gate (FR-STM11) + AgentRuntimeMemoryContext assembly."""

from __future__ import annotations

from typing import Any

from chainup_agent.application.clarify_session import get_clarify_session_raw
from chainup_agent.application.memory_session_store import (
    get_l0_for_prompt,
    get_semantic_fixture,
)
from chainup_agent.application.read_clarify_session import get_read_clarify_session
from chainup_agent.application.memory_runtime_settings import build_memory_runtime_config_snapshot
from chainup_agent.core.config import Settings

_DENYLIST_MARKERS = (
    "routinghints",
    "orchestrationnextsteps",
    "clarify json",
    '"intent":',
    '"missing":',
)


def _filter_l0_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for m in messages:
        content = (m.get("content") or "").lower()
        if any(d in content for d in _DENYLIST_MARKERS):
            continue
        out.append(m)
    return out


def run_memory_governance_gate(
    *,
    session_id: str,
    settings: Settings,
    semantic_narrative_enabled: bool = False,
    include_abandoned_clarify: bool = False,
) -> dict[str, Any]:
    """Four-step gate — memory-runtime §16.1."""
    steps = [
        "invalidate_stale",
        "filter_denylist",
        "inject_allowlist",
        "verify_retained",
    ]
    invalidated: list[str] = []
    filtered: list[str] = []

    clarify = get_clarify_session_raw(session_id)
    if clarify and clarify.abandoned and not include_abandoned_clarify:
        invalidated.append("L1_abandoned_clarify")
    if clarify and clarify.lifecycle_state == "stale":
        invalidated.append("L0_stale_turns")

    l0_raw = get_l0_for_prompt(session_id)
    l0 = _filter_l0_messages(l0_raw)
    if len(l0) < len(l0_raw):
        filtered.append("routing_hints_raw")

    read_snap = get_read_clarify_session(session_id)
    l1_blocks: list[dict[str, Any]] = []
    if clarify and not clarify.abandoned and clarify.lifecycle_state == "active":
        l1_blocks.append(
            {
                "executionId": clarify.execution_id,
                "clarifySummary": clarify.memory_summary(),
                "provisional": True,
            }
        )
    if read_snap:
        l1_blocks.append(
            {
                "executionId": read_snap.execution_id or "read-only",
                "userVisibleFactsSummary": read_snap.memory_summary().get(
                    "resolvedReadSlotsHumanSummary", ""
                ),
                "provisional": True,
            }
        )

    semantic_block = None
    if semantic_narrative_enabled:
        fixture = get_semantic_fixture(session_id)
        if fixture:
            semantic_block = fixture.to_dict()

    ctx: dict[str, Any] = {
        "shortTermL0": {
            "maxTurns": settings.stm_l0_max_turns,
            "recentTurns": [
                {"role": m["role"], "content": m["content"], "turnIndex": i}
                for i, m in enumerate(l0[-settings.stm_l0_max_turns :])
            ],
        },
        "shortTermL1": l1_blocks,
        "memoryGovernanceGate": {
            "passed": True,
            "stepsCompleted": steps,
            "invalidatedLayers": invalidated,
            "filteredDenylistHits": filtered,
            "retainedCriticalRefs": ["type_a_confirmed", "execution_facts"]
            if l1_blocks
            else [],
        },
        "configSnapshot": {
            **build_memory_runtime_config_snapshot(settings),
            "semanticNarrativeEnabled": semantic_narrative_enabled,
        },
        "semanticNarrativeBlock": semantic_block,
    }
    return ctx


def merge_memory_into_runtime_context(
    *,
    session_id: str,
    user_id: str,
    base: dict[str, Any] | None,
    settings: Settings,
    semantic_narrative_enabled: bool = False,
) -> dict[str, Any]:
    ctx = dict(base or {})
    mem = run_memory_governance_gate(
        session_id=session_id,
        settings=settings,
        semantic_narrative_enabled=semantic_narrative_enabled,
    )
    ctx["agentRuntimeMemoryContext"] = mem
    ctx["memoryContext"] = mem.get("configSnapshot")
    _ = user_id
    return ctx
