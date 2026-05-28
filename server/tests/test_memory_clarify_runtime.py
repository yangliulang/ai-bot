"""MR-MEM-01 — clarify session, stale/resume, governance, concurrency."""

from __future__ import annotations

import asyncio
from datetime import timedelta

import pytest

from chainup_agent.api.schemas.agent_runtime import utc_now
from chainup_agent.application.clarify_session import (
    apply_clarify_callback,
    get_clarify_session,
    evaluate_idle_or_ttl_stale,
    reset_clarify_session_store_for_tests,
    upsert_clarify_session,
)
from chainup_agent.application.clarify_user_visible import (
    classify_clarify_inbound,
    strip_internal_jargon_from_outbound,
)
from chainup_agent.application.clarify_inbound import preprocess_clarify_inbound
from chainup_agent.application.memory_governance import run_memory_governance_gate
from chainup_agent.application.memory_stale_resume import (
    classify_resume,
    reset_warm_episode_store_for_tests,
    upsert_warm_execution_episode,
)
from chainup_agent.application.memory_session_store import reset_memory_session_store_for_tests
from chainup_agent.application.read_clarify_session import (
    apply_read_clarify_callback,
    reset_read_clarify_session_store_for_tests,
)
from chainup_agent.application.session_concurrency import (
    remember_telegram_update_id,
    reset_session_concurrency_for_tests,
    run_serial_per_session,
)
from chainup_agent.core.config import Settings


@pytest.fixture(autouse=True)
def _reset_stores() -> None:
    reset_memory_session_store_for_tests()
    reset_clarify_session_store_for_tests()
    reset_read_clarify_session_store_for_tests()
    reset_warm_episode_store_for_tests()
    reset_session_concurrency_for_tests()


def test_clarify_callback_merges_slots() -> None:
    settings = Settings()
    upsert_clarify_session(
        session_id="tg:1",
        execution_id="exec-1",
        slots={"side": "BUY", "baseAsset": "BNB"},
        pending_kind="spot_trade_mode",
        settings=settings,
    )
    snap, phrase, err = apply_clarify_callback("tg:1", "cl:fc", settings=settings)
    assert err is None
    assert phrase == "闪兑"
    assert snap is not None
    assert snap.clarify_turn == 2
    assert snap.resolved_slots_so_far.get("tradeMode") == "flash_convert"
    assert snap.resolved_slots_so_far.get("side") == "BUY"


def test_abandon_on_cancel() -> None:
    settings = Settings()
    upsert_clarify_session(
        session_id="tg:2",
        execution_id="e2",
        slots={"side": "BUY"},
        pending_kind="spot_trade_mode",
        settings=settings,
    )
    pre = preprocess_clarify_inbound(
        session_id="tg:2",
        user_text="都不要了",
        settings=settings,
    )
    assert pre.proceed_to_intent is False
    assert pre.early_reply
    assert classify_clarify_inbound("都不要了") == "abandon"


def test_read_interrupt_abandons_write_clarify() -> None:
    settings = Settings()
    upsert_clarify_session(
        session_id="tg:3",
        execution_id="e3",
        slots={"side": "BUY"},
        pending_kind="qty",
        settings=settings,
    )
    pre = preprocess_clarify_inbound(
        session_id="tg:3",
        user_text="只查价",
        settings=settings,
    )
    assert pre.proceed_to_intent is True
    assert "行情" in (pre.early_reply or "")


def test_greeting_no_write_clarify_when_stale() -> None:
    settings = Settings(stm_idle_resume_prompt_sec=60)
    snap = upsert_clarify_session(
        session_id="tg:4",
        execution_id="e4",
        slots={"side": "BUY", "baseAsset": "BNB"},
        pending_kind="spot_trade_mode",
        settings=settings,
    )
    snap.last_user_message_at = utc_now() - timedelta(seconds=120)
    assert evaluate_idle_or_ttl_stale("tg:4", settings)
    pre = preprocess_clarify_inbound(
        session_id="tg:4",
        user_text="你好",
        settings=settings,
    )
    assert pre.early_reply


def test_resume_classifier_gate() -> None:
    settings = Settings(resume_classifier_min_confidence=0.75)
    upsert_warm_execution_episode(
        session_id="tg:5",
        execution_id="e5",
        resolved_slots={"side": "BUY", "baseAsset": "BNB", "tradeMode": "flash_convert"},
        human_summary="买入 BNB · 闪兑",
        stale_at=utc_now(),
        settings=settings,
    )
    r = classify_resume(
        session_id="tg:5",
        inbound_text="还是买 BNB，100U 闪兑",
        settings=settings,
    )
    assert r.decision == "resume_prior_write"
    assert r.confidence >= 0.75
    assert r.merged_slots and r.merged_slots.get("quoteQty") == "100"


def test_no_internal_jargon() -> None:
    raw = "请先补全 routingHints 与 orchestrationNextSteps"
    cleaned = strip_internal_jargon_from_outbound(raw)
    assert "routingHints" not in cleaned


def test_memory_governance_filters_denylist() -> None:
    from chainup_agent.application.memory_session_store import append_l0_message

    append_l0_message("tg:6", role="assistant", content='{"routingHints": ["x"]}')
    gate = run_memory_governance_gate(session_id="tg:6", settings=Settings())
    assert gate["memoryGovernanceGate"]["passed"] is True
    assert "routing_hints_raw" in gate["memoryGovernanceGate"]["filteredDenylistHits"]


def test_telegram_update_idempotent() -> None:
    assert remember_telegram_update_id("bot123", 42) is True
    assert remember_telegram_update_id("bot123", 42) is False


@pytest.mark.asyncio
async def test_inbound_serial_no_double_parse() -> None:
    settings = Settings()
    counter = {"n": 0}

    async def work() -> int:
        counter["n"] += 1
        await asyncio.sleep(0.05)
        return counter["n"]

    async def run() -> int:
        return await run_serial_per_session(
            "tg:7", settings=settings, coro_factory=work
        )

    a, b = await asyncio.gather(run(), run())
    assert a == 1
    assert b == 2


def test_read_clarify_scope_keyboard_markup() -> None:
    from chainup_agent.application.telegram_clarify_outbound import (
        build_read_clarify_reply_markup,
        read_clarify_outbound_body,
    )

    body = read_clarify_outbound_body("scope_portfolio_vs_market")
    assert "持仓" in body
    markup = build_read_clarify_reply_markup(
        pending_kind="scope_portfolio_vs_market",
        effective_locale="zh-Hans",
    )
    assert markup is not None
    row = markup["inline_keyboard"][0]
    callbacks = [b["callback_data"] for b in row]
    assert "rc:scope:market" in callbacks
    assert "rc:scope:portfolio" in callbacks


def test_read_clarify_callback_scope() -> None:
    settings = Settings()
    from chainup_agent.application.read_clarify_session import upsert_read_clarify_session

    upsert_read_clarify_session(
        session_id="tg:8",
        slots={},
        pending_kind="scope_portfolio_vs_market",
        settings=settings,
    )
    snap, phrase, err = apply_read_clarify_callback("tg:8", "rc:scope:portfolio")
    assert err is None
    assert phrase == "看我的持仓"
    assert snap and snap.resolved_read_slots_so_far.get("scope") == "portfolio"


def test_infer_spot_trade_mode_keyboard() -> None:
    from chainup_agent.application.telegram_clarify_outbound import (
        build_clarify_reply_markup,
        infer_clarify_keyboard_kind,
    )

    settings = Settings()
    slots = {"side": "BUY", "baseAsset": "BNB"}
    kind = infer_clarify_keyboard_kind(
        scenario_id="trade.spot.flash_convert",
        slots=slots,
        policy_codes=[],
        session_id="tg:10",
        settings=settings,
    )
    assert kind == "spot_trade_mode"
    markup = build_clarify_reply_markup(
        scenario_id="trade.spot.flash_convert",
        slots=slots,
        policy_codes=[],
        effective_locale="zh-Hans",
        session_id="tg:10",
        settings=settings,
    )
    assert markup is not None
    row = markup["inline_keyboard"][0]
    callbacks = {b["callback_data"] for b in row}
    assert callbacks == {"cl:fc", "cl:lo"}
    assert "确认下单" not in {b["text"] for b in row}


def test_cl_new_abandons() -> None:
    settings = Settings()
    upsert_clarify_session(
        session_id="tg:9",
        execution_id="e9",
        slots={"side": "BUY"},
        pending_kind="x",
        settings=settings,
    )
    _, _, err = apply_clarify_callback("tg:9", "cl:new", settings=settings)
    assert err and "聊点别的" in err
    assert get_clarify_session("tg:9") is None
