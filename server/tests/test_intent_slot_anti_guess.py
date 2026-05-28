"""P2 — LLM NLU slots must be grounded in utterance extractors."""

from __future__ import annotations

from chainup_agent.application.agent_intent_pipeline import (
    IntentNluDraft,
    prune_llm_slots_without_text_evidence,
)


def test_prune_drops_invented_quantity() -> None:
    draft = IntentNluDraft(
        source="llm_structured_v1",
        primary_intent_family="trade",
        scenario_id_candidates=[],
        slots={"symbol": "BTCUSDT", "side": "BUY", "quantity": "99"},
        order_type_hint="market",
        clarify_hints=[],
    )
    out = prune_llm_slots_without_text_evidence("买一点 btc", draft)
    assert "quantity" not in out.slots
    assert out.slots.get("symbol")
