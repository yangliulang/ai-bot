"""Telegram STM — memory commands + L0 writeback helpers."""

from __future__ import annotations

import pytest

from chainup_agent.application.memory_session_store import (
    append_l0_message,
    get_l0_for_prompt,
    reset_memory_session_store_for_tests,
)
from chainup_agent.application.telegram_stm import (
    merge_stm_runtime_context,
    record_telegram_stm_turn,
    try_memory_command_intent,
)


@pytest.fixture(autouse=True)
def _reset_stm() -> None:
    reset_memory_session_store_for_tests()


def test_memory_command_detection() -> None:
    assert try_memory_command_intent("我们重新开始吧") == "stm_clear"
    assert try_memory_command_intent("清空记忆") == "ltm_revoke"
    assert try_memory_command_intent("买 btc") is None


def test_stm_merge_and_record_turn() -> None:
    sid = "tg:42"
    append_l0_message(sid, role="user", content="上一轮")
    ctx = merge_stm_runtime_context(session_id=sid, user_id="u1")
    assert ctx.get("stmL0Messages")
    assert ctx["memoryContext"]["semanticNarrativeEnabled"] is False
    record_telegram_stm_turn(
        session_id=sid,
        user_id="u1",
        user_text="新问题",
        assistant_text="新回答",
    )
    l0 = get_l0_for_prompt(sid)
    assert len(l0) >= 2
