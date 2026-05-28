"""Read-path multi-turn symbol carryover (Telegram STM / pending_clarify_slots)."""

from __future__ import annotations

import pytest

from chainup_agent.application.agent_intent_pipeline import recognize_intent_full
from chainup_agent.application.memory_session_store import (
    remember_pending_clarify,
    reset_memory_session_store_for_tests,
)
from chainup_agent.core.config import Settings


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_memory_session_store_for_tests()


@pytest.mark.asyncio
async def test_read_followup_inherits_symbol_from_pending() -> None:
    settings = Settings()
    sid = "tg:read-carry"
    remember_pending_clarify(
        sid,
        scenario_id="read.market.ticker",
        slots={"symbol": "BTC-USDT"},
    )
    ir = await recognize_intent_full(
        settings=settings,
        text="需要进行盘面分析",
        session_id=sid,
        previous_scenario_id="read.market.ticker",
    )
    assert ir.plan is not None
    assert ir.plan.next_step == "ROUTE_READ_SKILL"
    assert ir.plan.resolved_scenario_id == "read.market.depth"
    assert ir.nlu is not None
    assert ir.nlu.slots.get("symbol") == "BTC-USDT"


@pytest.mark.asyncio
async def test_depth_followup_keeps_read_symbol_over_trade_context() -> None:
    """「深度数据呢」须继承只读 pending，不被 last_trade_slots 覆盖。"""
    from chainup_agent.application.memory_session_store import remember_trade_write_context

    settings = Settings()
    sid = "tg:read-over-trade"
    remember_trade_write_context(
        sid,
        scenario_id="trade.spot.flash_convert",
        slots={
            "symbol": "ETH-USDT",
            "side": "BUY",
            "quantity": "1",
            "tradeMode": "flash_convert",
        },
    )
    remember_pending_clarify(
        sid,
        scenario_id="read.market.depth",
        slots={"symbol": "BTC-USDT"},
    )
    ir = await recognize_intent_full(
        settings=settings,
        text="深度数据呢",
        session_id=sid,
    )
    assert ir.plan.resolved_scenario_id == "read.market.depth"
    assert ir.nlu.slots.get("symbol") == "BTC-USDT"
