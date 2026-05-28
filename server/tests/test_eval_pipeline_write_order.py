"""Eval runner tests — 2026-05-28--pipeline-eval-orchestration-align."""

from __future__ import annotations

import pytest

from chainup_agent.application.eval_pipeline_write_order import (
    EVAL_SET_ID,
    EVAL_VERSION,
    assert_eval_pipeline_write_order_negative_pn1,
    assert_eval_pipeline_write_order_negative_pn2,
    assert_eval_pipeline_write_order_positive,
)


def _positive_timeline() -> list[dict]:
    return [
        {"eventName": "execution.dispatched", "summary": {"transitionTrigger": "execution.dispatched"}},
        {"eventName": "agent.skill.spec_read", "summary": {"phase": "success"}},
        {"eventName": "confirmation.required", "summary": {"transitionTrigger": "confirmation.required"}},
        {"eventName": "user.confirmed", "summary": {"transitionTrigger": "user.confirmed"}},
        {"eventName": "trading.exchange_private", "summary": {"exchangeOutcome": "success"}},
    ]


def test_eval_constants() -> None:
    assert EVAL_SET_ID == "eval.runtime.pipeline_write_order"
    assert EVAL_VERSION == "0.1.0"


def test_eval_positive_synthetic_timeline() -> None:
    assert_eval_pipeline_write_order_positive(_positive_timeline())


def test_eval_pn1_rejects_write_before_confirm() -> None:
    bad = [
        {"eventName": "execution.dispatched"},
        {"eventName": "agent.skill.spec_read"},
        {"eventName": "confirmation.required"},
        {"eventName": "trading.exchange_private"},
        {"eventName": "user.confirmed"},
    ]
    with pytest.raises(AssertionError, match="P-N1 violated"):
        assert_eval_pipeline_write_order_negative_pn1(bad)


def test_eval_pn1_passes_on_positive_timeline() -> None:
    assert_eval_pipeline_write_order_negative_pn1(_positive_timeline())


def test_eval_pn2_rejects_spec_read_after_confirm() -> None:
    bad = [
        {"eventName": "execution.dispatched"},
        {"eventName": "confirmation.required"},
        {"eventName": "agent.skill.spec_read"},
        {"eventName": "user.confirmed"},
        {"eventName": "trading.exchange_private"},
    ]
    with pytest.raises(AssertionError, match="P-N2 violated"):
        assert_eval_pipeline_write_order_negative_pn2(bad)


def test_eval_pn2_passes_on_positive_timeline() -> None:
    assert_eval_pipeline_write_order_negative_pn2(_positive_timeline())


def test_write_path_pipeline_delegates_to_eval_positive() -> None:
    from chainup_agent.application.write_path_pipeline import assert_write_path_pipeline_order

    assert_write_path_pipeline_order(_positive_timeline())
