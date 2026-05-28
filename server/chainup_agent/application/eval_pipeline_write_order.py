"""Eval runner for ``eval.runtime.pipeline_write_order`` (OP-AO3 · W2)."""

from __future__ import annotations

from typing import Any

EVAL_SET_ID = "eval.runtime.pipeline_write_order"
EVAL_VERSION = "0.1.0"

_WRITE_EVENT_NAMES = frozenset(
    {
        "trading.exchange_private",
        "tool.round_complete",
        "tool.final_failed",
    }
)
_WRITE_TRANSITIONS = frozenset(_WRITE_EVENT_NAMES)


def _event_index(events: list[dict[str, Any]], name: str) -> int:
    for i, e in enumerate(events):
        en = e.get("eventName") or e.get("event_name")
        summary = e.get("summary") or {}
        tr = summary.get("transitionTrigger") or e.get("transitionTrigger")
        if en == name or tr == name:
            return i
    return -1


def _first_write_index(events: list[dict[str, Any]]) -> int:
    for i, e in enumerate(events):
        en = e.get("eventName") or e.get("event_name")
        summary = e.get("summary") or {}
        tr = summary.get("transitionTrigger") or e.get("transitionTrigger")
        if en in _WRITE_EVENT_NAMES or tr in _WRITE_TRANSITIONS:
            return i
    return -1


def assert_eval_pipeline_write_order_positive(events: list[dict[str, Any]]) -> None:
    """``evals/pipeline-write-order.md`` §2 positive GWT (five-segment causal order)."""
    dispatched = _event_index(events, "execution.dispatched")
    spec = _event_index(events, "agent.skill.spec_read")
    confirm = _event_index(events, "confirmation.required")
    user_ok = _event_index(events, "user.confirmed")
    write = _first_write_index(events)

    if dispatched < 0:
        raise AssertionError("missing execution.dispatched")
    if spec < 0:
        raise AssertionError("missing agent.skill.spec_read")
    if confirm < 0:
        raise AssertionError("missing confirmation.required")
    if user_ok < 0:
        raise AssertionError("missing user.confirmed")
    if write < 0:
        raise AssertionError("missing write-path tool event")
    if spec <= dispatched:
        raise AssertionError("agent.skill.spec_read must be after execution.dispatched")
    if confirm <= spec:
        raise AssertionError("confirmation.required must be after agent.skill.spec_read")
    if user_ok <= confirm:
        raise AssertionError("user.confirmed must be after confirmation.required")
    if write <= user_ok:
        raise AssertionError("write tool event must be after user.confirmed")


def assert_eval_pipeline_write_order_negative_pn1(events: list[dict[str, Any]]) -> None:
    """§3 P-N1: exchange write before user confirmed (SC-TA01 direction)."""
    user_ok = _event_index(events, "user.confirmed")
    write = _first_write_index(events)
    if write < 0:
        raise AssertionError("P-N1 fixture must include a write-path event")
    if user_ok < 0:
        return
    if write < user_ok:
        raise AssertionError(
            "P-N1 violated: trading write must not occur before user.confirmed"
        )


def assert_eval_pipeline_write_order_negative_pn2(events: list[dict[str, Any]]) -> None:
    """§3 P-N2: spec_read not strictly before confirmation.required (SC-OBS11)."""
    spec = _event_index(events, "agent.skill.spec_read")
    confirm = _event_index(events, "confirmation.required")
    if spec < 0 or confirm < 0:
        raise AssertionError("P-N2 fixture must include spec_read and confirmation.required")
    if spec >= confirm:
        raise AssertionError(
            "P-N2 violated: agent.skill.spec_read must be before confirmation.required"
        )
