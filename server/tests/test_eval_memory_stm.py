"""Eval + Runtime API tests — 2026-05-28--memory-stm-session."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from chainup_agent.application.eval_memory_stm import (
    EVAL_MEMORY_STM_P0_SET_IDS,
    EVAL_VERSION,
    assert_eval_memory_session_clear_stm,
    build_session_cleared_event,
    resolve_memory_user_intent,
)
from chainup_agent.application.memory_session_store import (
    DEFAULT_SEMANTIC_FIXTURE,
    append_l0_message,
    clear_session_stm,
    get_l0_for_prompt,
    get_session_context_preview,
    invalidate_pending_type_a_on_stm_clear,
    register_pending_type_a,
    reset_memory_session_store_for_tests,
    set_semantic_fixture,
    snapshot_session_state,
)
from chainup_agent.api.schemas.agent_runtime import utc_now


@pytest.fixture(autouse=True)
def _reset_stm_store() -> None:
    reset_memory_session_store_for_tests()


def test_eval_memory_stm_p0_constants() -> None:
    assert EVAL_VERSION == "0.1.0"
    assert "eval.memory.session_clear_stm" in EVAL_MEMORY_STM_P0_SET_IDS
    assert "eval.memory.idle_default_stale" in EVAL_MEMORY_STM_P0_SET_IDS
    assert len(EVAL_MEMORY_STM_P0_SET_IDS) >= 12


def test_append_l0_and_get_for_prompt() -> None:
    sid = "test-stm-1"
    for i in range(3):
        append_l0_message(sid, role="user", content=f"turn-{i}")
    l0 = get_l0_for_prompt(sid)
    assert len(l0) == 3
    ctx = get_session_context_preview(sid, "u-demo")
    assert ctx["l0MessageCount"] == 3
    assert len(ctx["l0MessagesPreview"]) == 3


def test_clear_session_stm_clears_l0_preserves_semantic() -> None:
    sid = "test-stm-1"
    uid = "u-demo"
    set_semantic_fixture(uid, DEFAULT_SEMANTIC_FIXTURE)
    for i in range(3):
        append_l0_message(sid, role="user", content=f"eth-discussion-{i}")
    cleared_at, _ = clear_session_stm(sid, uid)
    assert cleared_at is not None
    assert get_l0_for_prompt(sid) == []
    ctx = get_session_context_preview(sid, uid, semantic_narrative_enabled=True)
    assert ctx["l0MessageCount"] == 0
    assert ctx["memoryContext"]["semanticNarrativeBlock"] is not None


def test_session_clear_stm_gwt() -> None:
    sid = "test-stm-gwt"
    uid = "u-gwt"
    fixture = DEFAULT_SEMANTIC_FIXTURE.to_dict()
    set_semantic_fixture(uid, DEFAULT_SEMANTIC_FIXTURE)
    for i in range(3):
        append_l0_message(sid, role="user", content=f"round-{i}")
    before = snapshot_session_state(sid, uid, semantic_narrative_enabled=True)
    clear_session_stm(sid, uid)
    after = snapshot_session_state(sid, uid, semantic_narrative_enabled=True)
    assert_eval_memory_session_clear_stm(before, after, fixture)


def test_pending_type_a_invalidated_on_clear() -> None:
    sid = "test-stm-pending"
    register_pending_type_a(sid, waiting=True)
    assert invalidate_pending_type_a_on_stm_clear(sid) is True
    ctx = get_session_context_preview(sid, "u1")
    assert ctx["pendingTypeAValid"] is False


def test_build_session_cleared_event() -> None:
    now = utc_now()
    event = build_session_cleared_event("u1", "tg:123", now)
    assert event["eventName"] == "agent.memory.session_cleared"
    assert event["userId"] == "u1"
    assert event["sessionId"] == "tg:123"
    assert event["clearedAt"]


def test_stm_vs_ltm_intent_routing() -> None:
    stm = resolve_memory_user_intent("我们重新开始吧")
    ltm = resolve_memory_user_intent("清空记忆")
    assert stm == "stm_clear"
    assert ltm == "ltm_revoke"
    assert stm != ltm


def test_clear_never_written_session_p1() -> None:
    cleared_at, pending = clear_session_stm("fresh-session", "u-new")
    assert cleared_at is not None
    assert pending is False


@pytest.mark.asyncio
async def test_runtime_post_clear_stm_and_get_context(http_client: AsyncClient) -> None:
    sid = "tg:123"
    uid = "u-demo"
    for i in range(3):
        append_l0_message(sid, role="user", content=f"msg-{i}")

    ctx_before = await http_client.get(
        f"/api/v1/runtime/memory/sessions/{sid}/context",
        params={"userId": uid},
    )
    assert ctx_before.status_code == 200
    assert ctx_before.json()["l0MessageCount"] == 3

    clear_resp = await http_client.post(
        f"/api/v1/runtime/memory/sessions/{sid}/clear-stm",
        json={"userId": uid},
    )
    assert clear_resp.status_code == 200
    body = clear_resp.json()
    assert body["sessionId"] == sid
    assert body["userId"] == uid
    assert body["clearedAt"]
    assert body["eventName"] == "agent.memory.session_cleared"

    ctx_after = await http_client.get(
        f"/api/v1/runtime/memory/sessions/{sid}/context",
        params={"userId": uid},
    )
    assert ctx_after.status_code == 200
    after = ctx_after.json()
    assert after["l0MessageCount"] == 0
    assert after["memoryContext"]["sessionClearedAt"]


@pytest.mark.asyncio
async def test_runtime_get_context_ltm_off_by_default(http_client: AsyncClient) -> None:
    r = await http_client.get(
        "/api/v1/runtime/memory/sessions/tg:456/context",
        params={"userId": "u1"},
    )
    assert r.status_code == 200
    body = r.json()
    mem = body["memoryContext"]
    assert mem["semanticNarrativeEnabled"] is False
    assert mem["semanticNarrativeBlock"] is None
