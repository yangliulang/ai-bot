"""Multi-turn clarify slot merge + unified trade write policy."""

from __future__ import annotations

import pytest

from chainup_agent.application.agent_intent_pipeline import (
    apply_intent_policy,
    build_nlu_draft_keyword_v1,
    enrich_draft_slots_from_text,
    recognize_intent_full,
)
from chainup_agent.application.memory_session_store import (
    get_pending_clarify_slots,
    merge_clarify_slot_dict,
    remember_pending_clarify,
    reset_memory_session_store_for_tests,
)
from chainup_agent.application.trade_slot_clarify import (
    enrich_trade_slots_from_text,
    evaluate_trade_write_clarify,
)
from chainup_agent.core.config import Settings


def test_merge_clarify_slots() -> None:
    base = {"symbol": "BCH-USDT", "side": "BUY"}
    inc = {"quoteNotionalFrozen": "yes", "price": ""}
    merged = merge_clarify_slot_dict(base, inc)
    assert merged["symbol"] == "BCH-USDT"
    assert merged["quoteNotionalFrozen"] == "yes"


def test_margin_market_all_buy_needs_resolve() -> None:
    text = "全仓杠杆 全部买入 ETH"
    slots = enrich_trade_slots_from_text(
        text,
        {"symbol": "ETH-USDT", "side": "BUY", "notionalMode": "all_quote"},
    )
    dec = evaluate_trade_write_clarify(
        "margin.cross.market_order",
        text,
        slots,
    )
    assert dec.next_step in ("CLARIFY", "RESOLVE_TRADE_NOTIONAL")


def test_futures_limit_clarify_nominal() -> None:
    text = "BTC-USDT 限价 65000 用 100U 开多"
    slots = {"symbol": "BTC-USDT", "side": "BUY", "price": "65000"}
    dec = evaluate_trade_write_clarify("trade.futures.limit_order", text, slots)
    assert dec.next_step == "CLARIFY"
    assert "FUTURES_NOMINAL_AMBIGUOUS" in dec.policy_codes


@pytest.mark.asyncio
async def test_recognize_merges_pending_slots(http_client) -> None:
    reset_memory_session_store_for_tests()
    remember_pending_clarify(
        "tg:99",
        scenario_id="trade.spot.flash_convert",
        slots={"symbol": "BCH-USDT", "side": "BUY", "quoteNotionalFrozen": "yes"},
    )
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={
            "text": "全部买入",
            "sessionId": "tg:99",
            "previousScenarioId": "trade.spot.flash_convert",
        },
    )
    assert r.status_code == 200
    body = r.json()
    pend_sid, pend = get_pending_clarify_slots("tg:99")
    assert pend.get("symbol") == "BCH-USDT"
    assert body.get("plan", {}).get("nextStep") in (
        "RESOLVE_TRADE_NOTIONAL",
        "RESOLVE_FLASH_NOTIONAL",
        "CLARIFY",
    )
