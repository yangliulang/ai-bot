"""
Cross-scenario intent matrix (keyword NLU + policy, LLM off).

Guards regressions from Telegram multi-turn fixes (trade/read context).
"""

from __future__ import annotations

import pytest

from chainup_agent.application.agent_intent_pipeline import recognize_intent_full
from chainup_agent.application.memory_session_store import (
    remember_pending_clarify,
    reset_memory_session_store_for_tests,
)
from chainup_agent.core.config import Settings

_SETTINGS = Settings(intent_nlu_use_llm=False, intent_clarify_use_llm=False)


@pytest.fixture(autouse=True)
def _reset_stm() -> None:
    reset_memory_session_store_for_tests()


def _case(
    text: str,
    *,
    scenario: str | None,
    next_step: str,
    session_id: str | None = None,
    previous_scenario_id: str | None = None,
) -> tuple[str, dict]:
    return (
        text,
        {
            "scenario": scenario,
            "next_step": next_step,
            "session_id": session_id,
            "previous_scenario_id": previous_scenario_id,
        },
    )


# (text, expected scenarioId, expected plan.nextStep) — single-turn
SINGLE_TURN_CASES: list[tuple[str, dict]] = [
    _case("看下账户余额", scenario="read.account.balance", next_step="ROUTE_READ_SKILL"),
    _case("ETH 现在有行情吗", scenario="read.market.ticker", next_step="ROUTE_READ_SKILL"),
    _case("今天BTC-USDT的行情怎么样", scenario="read.market.ticker", next_step="ROUTE_READ_SKILL"),
    _case("帮我看看 BTC-USDT 盘口", scenario="read.market.depth", next_step="ROUTE_READ_SKILL"),
    _case("ETH-USDT 近期成交", scenario="read.market.trades", next_step="ROUTE_READ_SKILL"),
    _case("帮我看下理财持仓", scenario="wealth.holdings_read", next_step="ROUTE_READ_SKILL"),
    _case("市价买入 0.1 BTC-USDT", scenario="trade.spot.flash_convert", next_step="CONFIRM_TYPE_A"),
    _case(
        "BTC-USDT 限价买入 价格 65000 数量 0.01",
        scenario="trade.spot.limit_order",
        next_step="CONFIRM_TYPE_A",
    ),
    _case(
        "撤单 BTC-USDT 订单号 499890200602846976",
        scenario="trade.spot.cancel_order",
        next_step="EXECUTE_SPOT_CANCEL",
    ),
    _case("撤单 BTC-USDT", scenario="trade.spot.cancel_order", next_step="CLARIFY"),
    _case("BTC永续市价买入 0.01", scenario="trade.futures.market_order", next_step="CONFIRM_TYPE_A"),
    _case("ETH永续限价委托 62000", scenario="trade.futures.limit_order", next_step="CLARIFY"),
    _case("BTC-USDT 条件单 触发价 91000", scenario="automation.condition_order", next_step="CLARIFY"),
    _case(
        "全仓杠杆市价买入 BTC-USDT",
        scenario="margin.cross.market_order",
        next_step="RESOLVE_TRADE_NOTIONAL",
    ),
    _case("限价闪兑 0.1 BTC", scenario=None, next_step="CLARIFY"),
    _case("你好", scenario="chat.faq", next_step="ROUTE_CHAT_FAQ"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text,expected",
    SINGLE_TURN_CASES,
    ids=[c[0][:40] for c in SINGLE_TURN_CASES],
)
async def test_scenario_intent_matrix_single_turn(text: str, expected: dict) -> None:
    ir = await recognize_intent_full(
        settings=_SETTINGS,
        text=text,
        session_id=expected.get("session_id"),
        previous_scenario_id=expected.get("previous_scenario_id"),
    )
    assert ir.plan is not None
    assert ir.plan.next_step == expected["next_step"], (
        f"{text!r} -> {ir.plan.next_step} {ir.plan.resolved_scenario_id}"
    )
    if expected["scenario"] is None:
        assert ir.plan.resolved_scenario_id is None
        assert "FR_AO02" in " ".join(ir.plan.policy_codes or [])
    else:
        assert ir.plan.resolved_scenario_id == expected["scenario"]


@pytest.mark.asyncio
async def test_trade_multi_turn_buy_eth_flash_market() -> None:
    sid = "tg:matrix-trade"
    steps = [
        ("买入1个 eth", "CONFIRM_TYPE_A", "trade.spot.flash_convert"),
        ("闪兑", "CONFIRM_TYPE_A", "trade.spot.flash_convert"),
        ("当前市价", "CONFIRM_TYPE_A", "trade.spot.flash_convert"),
    ]
    for text, next_step, scenario in steps:
        ir = await recognize_intent_full(settings=_SETTINGS, text=text, session_id=sid)
        assert ir.plan is not None
        assert ir.plan.next_step == next_step, text
        assert ir.plan.resolved_scenario_id == scenario, text
        assert (ir.nlu.slots or {}).get("symbol") == "ETH-USDT", text


@pytest.mark.asyncio
async def test_read_multi_turn_ticker_then_depth() -> None:
    sid = "tg:matrix-read"
    ir1 = await recognize_intent_full(
        settings=_SETTINGS,
        text="BTC-USDT 行情",
        session_id=sid,
    )
    assert ir1.plan.next_step == "ROUTE_READ_SKILL"
    assert ir1.plan.resolved_scenario_id == "read.market.ticker"

    ir2 = await recognize_intent_full(
        settings=_SETTINGS,
        text="需要进行盘面分析",
        session_id=sid,
        previous_scenario_id="read.market.ticker",
    )
    assert ir2.plan.next_step == "ROUTE_READ_SKILL"
    assert ir2.plan.resolved_scenario_id == "read.market.depth"
    assert ir2.nlu.slots.get("symbol") == "BTC-USDT"


@pytest.mark.asyncio
async def test_read_followup_with_pending_symbol_only() -> None:
    sid = "tg:matrix-pending"
    remember_pending_clarify(
        sid,
        scenario_id="read.market.ticker",
        slots={"symbol": "BTC-USDT"},
    )
    ir = await recognize_intent_full(
        settings=_SETTINGS,
        text="需要进行盘面分析",
        session_id=sid,
    )
    assert ir.plan.resolved_scenario_id == "read.market.depth"
    assert ir.nlu.slots.get("symbol") == "BTC-USDT"
