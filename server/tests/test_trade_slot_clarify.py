"""S11 trade slot clarify — rule-based messages and completeness."""

from __future__ import annotations

import pytest

from chainup_agent.application.agent_intent_pipeline import (
    apply_intent_policy,
    build_nlu_draft_keyword_v1,
    enrich_draft_slots_from_text,
)
from chainup_agent.application.trade_slot_clarify import (
    build_flash_clarify_lines,
    enrich_trade_slots_from_text,
    flash_needs_notional_resolve,
    flash_slots_complete,
    needs_quote_pair_clarify,
)
from chainup_agent.core.config import Settings


def test_all_buy_bch_needs_pair_clarify() -> None:
    text = "全部买入 BCH"
    slots = enrich_trade_slots_from_text(
        text,
        {"symbol": "BCH-USDT", "side": "BUY", "notionalMode": "all_quote"},
    )
    assert needs_quote_pair_clarify(text, slots)
    lines = build_flash_clarify_lines(text, slots)
    assert any("BCH-USDT" in ln and "USDT" in ln for ln in lines)


def test_affirm_frozen_skips_pair_clarify() -> None:
    text = "是"
    slots = enrich_trade_slots_from_text(text, {})
    assert slots.get("quoteNotionalFrozen") == "yes"
    assert not needs_quote_pair_clarify(text, {"symbol": "BCH-USDT", "side": "BUY"})


def test_flash_all_quote_needs_resolve() -> None:
    slots = {"symbol": "BCH-USDT", "side": "BUY", "notionalMode": "all_quote"}
    assert flash_needs_notional_resolve(slots)
    assert not flash_slots_complete(slots)


def test_flash_quote_qty_complete() -> None:
    slots = {"symbol": "BTC-USDT", "side": "BUY", "quoteQty": "100"}
    assert flash_slots_complete(slots)


@pytest.mark.asyncio
async def test_intent_all_buy_bch_clarify_or_resolve() -> None:
    settings = Settings()
    draft = enrich_draft_slots_from_text(
        "全部买入 BCH",
        build_nlu_draft_keyword_v1(
            "全部买入 BCH",
            best_sid="trade.spot.flash_convert",
            ranked=[("trade.spot.flash_convert", 0.9)],
        ),
    )
    plan, _, _, _ = apply_intent_policy(
        settings=settings,
        text="全部买入 BCH",
        draft=draft,
        ranked=[("trade.spot.flash_convert", 0.9)],
        best_sid="trade.spot.flash_convert",
    )
    assert plan.next_step == "CLARIFY"
    assert "QUOTE_PAIR_NOT_FROZEN" in (plan.policy_codes or [])
    assert any("USDT" in c for c in plan.clarify)


@pytest.mark.asyncio
async def test_intent_explicit_pair_with_usdt_amount() -> None:
    settings = Settings()
    text = "BCH-USDT 用 50 USDT 买入"
    draft = enrich_draft_slots_from_text(
        text,
        build_nlu_draft_keyword_v1(
            text,
            best_sid="trade.spot.flash_convert",
            ranked=[("trade.spot.flash_convert", 0.9)],
        ),
    )
    plan, _, _, _ = apply_intent_policy(
        settings=settings,
        text=text,
        draft=draft,
        ranked=[("trade.spot.flash_convert", 0.9)],
        best_sid="trade.spot.flash_convert",
    )
    assert plan.next_step == "CONFIRM_TYPE_A"
    assert draft.slots.get("quoteQty") == "50" or draft.slots.get("quantity")
