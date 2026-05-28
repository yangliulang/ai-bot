"""Telegram ↔ in-memory STM (L0 recall / turn writeback / §2.8 clear)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_execution_events import append_execution_timeline_event
from chainup_agent.application.eval_memory_stm import (
    build_session_cleared_event,
    resolve_memory_user_intent,
)
from chainup_agent.application.memory_governance import merge_memory_into_runtime_context
from chainup_agent.application.memory_session_store import (
    append_l0_message,
    bind_session_user,
    build_memory_context_preview,
    clear_session_stm,
    clear_pending_clarify,
    get_l0_for_prompt,
    get_session_context_preview,
    register_pending_type_a,
    set_last_resolved_scenario,
    get_last_resolved_scenario,
)
from chainup_agent.application.clarify_session import abandon_clarify_session
from chainup_agent.core.config import get_settings


def telegram_session_id(chat_id: int) -> str:
    return f"tg:{chat_id}"


def merge_stm_runtime_context(
    *,
    session_id: str,
    user_id: str,
    base: dict[str, Any] | None = None,
    semantic_narrative_enabled: bool = False,
) -> dict[str, Any]:
    """PRS block-5 style memory slice for LLM ``runtime_context``."""
    settings = get_settings()
    ctx = merge_memory_into_runtime_context(
        session_id=session_id,
        user_id=user_id,
        base=base,
        settings=settings,
        semantic_narrative_enabled=semantic_narrative_enabled,
    )
    l0 = get_l0_for_prompt(session_id)
    if l0:
        ctx["stmL0Messages"] = l0[-8:]
    preview = get_session_context_preview(
        session_id, user_id, semantic_narrative_enabled=semantic_narrative_enabled
    )
    ctx["memoryContext"] = preview.get("memoryContext")
    return ctx


def record_telegram_stm_turn(
    *,
    session_id: str,
    user_id: str,
    user_text: str,
    assistant_text: str,
) -> None:
    bind_session_user(session_id, user_id)
    ut = user_text.strip()
    if ut:
        append_l0_message(session_id, role="user", content=ut[:4000])
    at = assistant_text.strip()
    if at:
        append_l0_message(session_id, role="assistant", content=at[:4000])


def try_memory_command_intent(text: str) -> str | None:
    try:
        return resolve_memory_user_intent(text)
    except ValueError:
        return None


_STM_CLEAR_REPLY = "好的，我们重新开始。你可以直接说想查什么。"
_LTM_REVOKE_REPLY = (
    "「清空记忆」会撤销跨会话偏好（长期记忆），与「重新开始」不同。\n"
    "长期记忆撤销功能尚在筹备；若仅需清空本会话，请说「重新开始」或「新话题」。"
)


async def handle_telegram_memory_command(
    session: AsyncSession,
    *,
    intent: str,
    user_id: str,
    session_id: str,
    execution_id: str,
) -> str:
    if intent == "stm_clear":
        abandon_clarify_session(session_id, reason="stm_clear")
        clear_pending_clarify(session_id)
        cleared_at, pending_invalidated = clear_session_stm(session_id, user_id)
        event = build_session_cleared_event(user_id, session_id, cleared_at)
        await append_execution_timeline_event(
            session,
            execution_id=execution_id,
            user_id=user_id,
            event_name="agent.memory.session_cleared",
            step_kind="memory",
            outcome="success",
            payload={
                **event,
                "pendingTypeAInvalidated": pending_invalidated,
                "transitionTrigger": "memory.session_cleared",
            },
        )
        return _STM_CLEAR_REPLY
    if intent == "ltm_revoke":
        await append_execution_timeline_event(
            session,
            execution_id=execution_id,
            user_id=user_id,
            event_name="agent.memory.ltm_revoke_requested",
            step_kind="memory",
            outcome="pending",
            payload={
                "userId": user_id,
                "sessionId": session_id,
                "transitionTrigger": "memory.ltm_revoke_not_implemented",
            },
        )
        return _LTM_REVOKE_REPLY
    return "暂不支持该记忆操作。"


def remember_resolved_scenario(session_id: str, scenario_id: str | None) -> None:
    if scenario_id and scenario_id.strip():
        set_last_resolved_scenario(session_id, scenario_id.strip())


def previous_scenario_for_session(session_id: str) -> str | None:
    return get_last_resolved_scenario(session_id)


def mark_type_a_pending(session_id: str) -> None:
    register_pending_type_a(session_id, waiting=True)
