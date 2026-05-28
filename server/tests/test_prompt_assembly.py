"""prompt assembly helpers (runtime-injection §1 ordering hints)."""

from __future__ import annotations

import pytest
from chainup_agent.application.agent_prompt_assembly import (
    _partition_scenario_body_and_few_shots,
    _scenario_strategy_marker_slug,
    assemble_trading_llm_payload,
)
from chainup_agent.core.config import reset_settings_cache
from chainup_agent.infrastructure.persistence.base import get_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from tests.test_api import _init_schema_sqlite


def test_scenario_strategy_marker_slug_chat_faq() -> None:
    assert _scenario_strategy_marker_slug("chat.faq") == "CHAT_FAQ"


def test_scenario_strategy_marker_slug_read_market_ticker() -> None:
    assert _scenario_strategy_marker_slug("read.market.ticker") == "READ_MARKET_TICKER"


def test_scenario_strategy_marker_slug_read_market_depth() -> None:
    assert _scenario_strategy_marker_slug("read.market.depth") == "READ_MARKET_DEPTH"


def test_scenario_strategy_marker_slug_read_market_trades() -> None:
    assert _scenario_strategy_marker_slug("read.market.trades") == "READ_MARKET_TRADES"


def test_scenario_strategy_marker_slug_read_account_balance() -> None:
    assert _scenario_strategy_marker_slug("read.account.balance") == "READ_ACCOUNT_BALANCE"


def test_scenario_strategy_marker_slug_wealth_holdings_read() -> None:
    assert _scenario_strategy_marker_slug("wealth.holdings_read") == "WEALTH_HOLDINGS_READ"


def test_scenario_strategy_marker_slug_spot_flash_convert() -> None:
    assert _scenario_strategy_marker_slug("trade.spot.flash_convert") == "TRADE_SPOT_FLASH_CONVERT"


def test_scenario_strategy_marker_slug_spot_limit_order() -> None:
    assert _scenario_strategy_marker_slug("trade.spot.limit_order") == "TRADE_SPOT_LIMIT_ORDER"


@pytest.mark.asyncio
async def test_assemble_trading_rejects_unknown_scenario(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    reset_settings_cache()
    factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    async with factory() as session:
        with pytest.raises(ValueError, match="TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS"):
            await assemble_trading_llm_payload(
                session,
                scenario_id="trade.margin.market_order",
                user_text="hi",
                effective_locale=None,
                execution_id=None,
                session_id=None,
                runtime_context=None,
            )


def test_partition_scenario_then_few_shot_pairs() -> None:
    msgs = [
        {"role": "system", "content": "intro"},
        {"role": "system", "content": "detail"},
        {"role": "user", "content": "demo-q"},
        {"role": "assistant", "content": "demo-a"},
    ]
    body, pairs = _partition_scenario_body_and_few_shots(msgs)
    assert "intro" in body and "detail" in body
    assert pairs == [("demo-q", "demo-a")]
