"""Ranked score clamp — IntentCandidate.score must stay in [0, 1]."""

from __future__ import annotations

from chainup_agent.application.agent_intent_pipeline import (
    _clamp_ranked_scores,
    _prefer_read_balance_on_explicit_phrase,
)


def test_clamp_ranked_scores_caps_above_one() -> None:
    ranked = [("read.account.balance", 1.08), ("chat.faq", 0.35)]
    out = _clamp_ranked_scores(ranked)
    assert out[0][1] == 1.0


def test_read_balance_boost_never_exceeds_one() -> None:
    ranked = [("chat.faq", 0.88), ("read.account.balance", 0.5)]
    _, out = _prefer_read_balance_on_explicit_phrase("看下账户余额", "chat.faq", ranked)
    out = _clamp_ranked_scores(out)
    assert all(0.0 <= sc <= 1.0 for _, sc in out)
