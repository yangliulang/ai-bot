"""Eval runner for ``eval.memory.*`` STM P0 bundle (OP-MEM)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from chainup_agent.application.memory_session_store import _utc_iso

EVAL_VERSION = "0.1.0"

EVAL_MEMORY_STM_P0_SET_IDS: tuple[str, ...] = (
    "eval.memory.session_clear_stm",
    "eval.memory.stm_vs_ltm_intent",
    "eval.memory.stm_governance_regression",
    "eval.memory.idle_default_stale",
    "eval.memory.resume_classifier_gate",
    "eval.memory.resume_classifier_multi_episode",
    "eval.clarify.abandon_on_cancel",
    "eval.clarify.read_interrupts_write",
    "eval.clarify.no_internal_jargon",
    "eval.session.inbound_serial_no_double_parse",
    "eval.session.second_write_while_confirm",
    "eval.session.new_write_blocked_on_unknown",
    "eval.runtime.telegram_update_idempotent",
)

_STM_INTENT_MARKERS: tuple[str, ...] = (
    "重新开始",
    "新话题",
    "清空本会话",
)
_LTM_INTENT_MARKERS: tuple[str, ...] = (
    "清空记忆",
    "不再记住",
)


def build_session_cleared_event(
    user_id: str,
    session_id: str,
    cleared_at: datetime | str,
) -> dict[str, Any]:
    """FR-STM04 — observability payload for ``agent.memory.session_cleared``."""
    if isinstance(cleared_at, datetime):
        cleared_iso = _utc_iso(cleared_at)
    else:
        cleared_iso = str(cleared_at)
    return {
        "eventName": "agent.memory.session_cleared",
        "userId": user_id.strip(),
        "sessionId": session_id.strip(),
        "clearedAt": cleared_iso,
    }


def resolve_memory_user_intent(utterance: str) -> str:
    """Route STM clear vs LTM revoke — ``eval.memory.stm_vs_ltm_intent``."""
    text = utterance.strip()
    for marker in _LTM_INTENT_MARKERS:
        if marker in text:
            return "ltm_revoke"
    for marker in _STM_INTENT_MARKERS:
        if marker in text:
            return "stm_clear"
    raise ValueError(f"unrecognized memory intent utterance: {utterance!r}")


def assert_eval_memory_session_clear_stm(
    state_before: dict[str, Any],
    state_after: dict[str, Any],
    semantic_fixture: dict[str, Any],
) -> None:
    """``eval.memory.session_clear_stm`` — SC-STM01/02 GWT."""
    l0_before = state_before.get("l0Messages") or []
    if len(l0_before) < 3:
        raise AssertionError("Given requires at least 3 L0 turns in session")

    l0_after = state_after.get("l0Messages") or []
    if l0_after:
        raise AssertionError("Then requires empty L0 after STM clear")

    mem_after = state_after.get("memoryContext") or {}
    block = mem_after.get("semanticNarrativeBlock")
    if block is None:
        raise AssertionError("Then requires semanticNarrativeBlock still present (SC-STM02)")
    if block.get("summary") != semantic_fixture.get("summary"):
        raise AssertionError("Semantic fixture summary must survive STM clear")

    cleared_at = mem_after.get("sessionClearedAt")
    if not cleared_at:
        raise AssertionError("Then requires sessionClearedAt after clear")
