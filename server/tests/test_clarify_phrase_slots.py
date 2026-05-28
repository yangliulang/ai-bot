"""Short phrase → clarify slot merges (multi-turn trade/read)."""

from __future__ import annotations

import pytest

from chainup_agent.application.agent_intent_pipeline import (
    _prefer_pending_trade_clarify_context,
    _prefer_trade_on_complete_spot_slots,
    recognize_intent_keyword,
    build_nlu_draft_keyword_v1,
    enrich_draft_slots_from_text,
)
from chainup_agent.application.clarify_phrase_slots import merge_clarify_phrase_slots
from chainup_agent.application.memory_session_store import (
    remember_pending_clarify,
    reset_memory_session_store_for_tests,
)


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_memory_session_store_for_tests()


def test_merge_flash_typo_and_phrase() -> None:
    s = merge_clarify_phrase_slots("闪队", {})
    assert s.get("tradeMode") == "flash_convert"
    s2 = merge_clarify_phrase_slots("当前市价", {})
    assert s2.get("tradeMode") == "flash_convert"


def test_prefer_trade_skips_futures_context() -> None:
    text = "BTC永续市价买入 0.01"
    best, _conf, ranked = recognize_intent_keyword(text)
    draft = enrich_draft_slots_from_text(
        text, build_nlu_draft_keyword_v1(text, best_sid=best, ranked=ranked)
    )
    best2, _ = _prefer_trade_on_complete_spot_slots(
        text, best, ranked, dict(draft.slots)
    )
    assert best2 == "trade.futures.market_order"


def test_prefer_trade_on_buy_eth_slots() -> None:
    text = "买入1个 eth"
    best, conf, ranked = recognize_intent_keyword(text)
    draft = enrich_draft_slots_from_text(
        text, build_nlu_draft_keyword_v1(text, best_sid=best, ranked=ranked)
    )
    best2, ranked2 = _prefer_trade_on_complete_spot_slots(
        text, best, ranked, dict(draft.slots)
    )
    assert best2 == "trade.spot.flash_convert"
    assert draft.slots.get("symbol") == "ETH-USDT"


def test_pending_trade_flash_phrase_beats_ticker() -> None:
    pend = {
        "symbol": "ETH-USDT",
        "side": "BUY",
        "quantity": "1",
    }
    best, _conf, ranked = recognize_intent_keyword("当前市价")
    best2, _ = _prefer_pending_trade_clarify_context(
        "当前市价",
        best,
        ranked,
        pending_scenario_id="trade.spot.flash_convert",
        pending_slots=merge_clarify_phrase_slots("当前市价", pend),
    )
    assert best2 == "trade.spot.flash_convert"
