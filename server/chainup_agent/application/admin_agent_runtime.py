"""Persisted instance Runtime FSM — R01–R05 + R06 batch (agent-management §3)."""

from __future__ import annotations

import logging
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.admin_agent_instances import get_agent_instance_joined_admin
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError

logger = logging.getLogger(__name__)

RuntimeAction = Literal["start", "pause", "resume", "stop"]

_VALID_RUNTIME = frozenset({"RUNNING", "PAUSED", "STOPPED", "ERROR"})


def _normalize_runtime_state(raw: str | None) -> str:
    s = (raw or "RUNNING").strip().upper()
    return s if s in _VALID_RUNTIME else "RUNNING"


def _target_state_after_action(cur: str, action: RuntimeAction) -> str | None:
    """Return new runtime_state or None if illegal; idempotent_ok means cur already terminal for action."""
    if action == "stop":
        return "STOPPED"
    if action == "pause":
        if cur == "RUNNING":
            return "PAUSED"
        if cur == "PAUSED":
            return "PAUSED"
        return None
    if action == "resume":
        if cur == "PAUSED":
            return "RUNNING"
        if cur == "RUNNING":
            return "RUNNING"
        return None
    if action == "start":
        if cur in ("STOPPED", "ERROR"):
            return "RUNNING"
        if cur == "RUNNING":
            return "RUNNING"
        return None
    return None


def _assert_global_allows_start_resume(settings: Settings, action: RuntimeAction) -> None:
    if action not in ("start", "resume"):
        return
    if settings.agent_runtime_global_disabled:
        raise AppError(
            code="AGENT_GLOBAL_OFF",
            message="GLOBAL_AGENT_SWITCH=OFF（G01）：禁止 Start / Resume。",
            status_code=422,
            details={"policy": "G01"},
        )
    if settings.agent_runtime_ops_suspended:
        raise AppError(
            code="AGENT_OPS_SUSPENDED",
            message="运维全局暂停：禁止 Start / Resume。",
            status_code=422,
            details={},
        )


async def apply_agent_instance_runtime_action(
    session: AsyncSession,
    *,
    settings: Settings,
    instance_public_id: str,
    action: RuntimeAction,
) -> str:
    """
    Mutates ``agent_instance.runtime_state``; returns **new** normalized runtime state.
    """
    _assert_global_allows_start_resume(settings, action)
    pair = await get_agent_instance_joined_admin(session, instance_public_id=instance_public_id)
    if pair is None:
        raise AppError(
            code="AGENT_ADMIN_INSTANCE_NOT_FOUND",
            message="实例不存在。",
            status_code=404,
            details={"instanceId": instance_public_id.strip()[:80]},
        )
    inst, _tb = pair
    cur = _normalize_runtime_state(inst.runtime_state)
    nxt = _target_state_after_action(cur, action)
    if nxt is None:
        raise AppError(
            code="RUNTIME_COMMAND_REJECTED",
            message=f"当前 runtimeState={cur} 不允许 action={action}。",
            status_code=422,
            details={"runtimeState": cur, "action": action},
        )
    if nxt != cur:
        inst.runtime_state = nxt
        await session.flush()
        logger.info(
            "agent_instance_runtime_transition instance=%s %s -> %s (%s)",
            inst.instance_id,
            cur,
            nxt,
            action,
        )
    return nxt
