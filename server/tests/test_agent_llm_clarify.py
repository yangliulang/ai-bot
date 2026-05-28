"""CLARIFY LLM user block — session_id must not raise."""

from __future__ import annotations

from chainup_agent.application.agent_llm_clarify import _build_clarify_user_block


def test_build_clarify_user_block_accepts_session_id() -> None:
    block = _build_clarify_user_block(
        user_text="需要进行盘面分析",
        scenario_id="read.market.depth",
        rule_lines=["请带上交易对"],
        policy_codes=["SLOT_SYMBOL_REQUIRED"],
        slots={"symbol": "BTC-USDT"},
        session_id="tg:99",
    )
    assert "BTC-USDT" in block or "symbol" in block
    assert "盘面" in block
