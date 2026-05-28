"""Trade-path multi-turn slot carryover (last_trade_slots survives CONFIRM clear)."""

from __future__ import annotations

import pytest

from chainup_agent.application.agent_intent_pipeline import recognize_intent_full
from chainup_agent.application.memory_session_store import (
    get_trade_write_context,
    reset_memory_session_store_for_tests,
)
from chainup_agent.core.config import Settings


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_memory_session_store_for_tests()


@pytest.mark.asyncio
async def test_trade_flash_phrase_after_confirm_inherits_slots() -> None:
    settings = Settings(intent_nlu_use_llm=False, intent_clarify_use_llm=False)
    sid = "tg:trade-carry"
    for text in ("买入1个 eth", "闪兑", "当前市价"):
        await recognize_intent_full(settings=settings, text=text, session_id=sid)

    ctx_sid, ctx_slots = get_trade_write_context(sid)
    assert ctx_sid == "trade.spot.flash_convert"
    assert ctx_slots.get("symbol") == "ETH-USDT"
    assert ctx_slots.get("side") == "BUY"
    assert ctx_slots.get("quantity") == "1"

    ir = await recognize_intent_full(settings=settings, text="当前市价", session_id=sid)
    assert ir.plan is not None
    assert ir.plan.next_step == "CONFIRM_TYPE_A"
    assert ir.plan.resolved_scenario_id == "trade.spot.flash_convert"
    assert ir.nlu is not None
    assert ir.nlu.slots.get("symbol") == "ETH-USDT"
    assert ir.nlu.slots.get("tradeMode") == "flash_convert"
