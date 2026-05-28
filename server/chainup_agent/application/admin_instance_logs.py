"""Instance-scoped log slices — FR-AM-L01–L03 (execution + timeline 投影)."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.admin_agent_instances import get_agent_instance_joined_admin
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution
from chainup_agent.infrastructure.persistence.models.agent_execution_event import (
    AgentExecutionEvent,
)

_TOOL_EVENT_TYPES = frozenset({"trading.exchange_private", "trading.exchange_public"})
_FAIL_OUTCOMES = frozenset({"fail", "failure", "failed"})


def _timeline_path(execution_id: str) -> str:
    e = execution_id.strip()
    return f"/api/v1/admin/observability/executions/{e}/timeline"


def _execution_path(execution_id: str) -> str:
    e = execution_id.strip()
    return f"/api/v1/admin/observability/executions/{e}/timeline"


async def count_conversation_logs_for_instance(
    session: AsyncSession,
    *,
    user_id_str: str,
) -> int:
    stmt = select(func.count()).select_from(AgentExecution).where(
        AgentExecution.user_id == user_id_str.strip()
    )
    return int((await session.execute(stmt)).scalar_one())


async def list_conversation_logs_for_instance(
    session: AsyncSession,
    *,
    user_id_str: str,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    uid = user_id_str.strip()
    stmt = (
        select(AgentExecution)
        .where(AgentExecution.user_id == uid)
        .order_by(AgentExecution.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = (await session.execute(stmt)).scalars().all()
    out: list[dict[str, Any]] = []
    for r in rows:
        note = (r.note or "").strip()
        out.append(
            {
                "executionId": r.execution_id,
                "scenarioId": r.scenario_id,
                "channel": r.channel,
                "state": r.state,
                "createdAt": r.created_at,
                "notePreview": (note[:400] + "…") if len(note) > 400 else note or None,
                "observabilityExecutionPath": _execution_path(r.execution_id),
            }
        )
    return out


async def count_tool_logs_for_instance(
    session: AsyncSession,
    *,
    user_id_str: str,
) -> int:
    uid = user_id_str.strip()
    stmt = select(func.count()).select_from(AgentExecutionEvent).where(
        AgentExecutionEvent.user_id == uid,
        AgentExecutionEvent.event_type.in_(_TOOL_EVENT_TYPES),
    )
    return int((await session.execute(stmt)).scalar_one())


async def list_tool_logs_for_instance(
    session: AsyncSession,
    *,
    user_id_str: str,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    uid = user_id_str.strip()
    stmt = (
        select(AgentExecutionEvent)
        .where(
            AgentExecutionEvent.user_id == uid,
            AgentExecutionEvent.event_type.in_(_TOOL_EVENT_TYPES),
        )
        .order_by(AgentExecutionEvent.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = (await session.execute(stmt)).scalars().all()
    out: list[dict[str, Any]] = []
    for ev in rows:
        try:
            payload = json.loads(ev.payload_json or "{}")
            if not isinstance(payload, dict):
                payload = {}
        except json.JSONDecodeError:
            payload = {}
        summary = dict(payload)
        if ev.step_kind:
            summary.setdefault("stepKind", ev.step_kind)
        if ev.outcome:
            summary.setdefault("outcome", ev.outcome)
        out.append(
            {
                "eventId": ev.id,
                "executionId": ev.execution_id,
                "eventName": ev.event_type,
                "stepKind": ev.step_kind,
                "outcome": ev.outcome,
                "createdAt": ev.created_at,
                "summary": summary,
                "observabilityTimelinePath": _timeline_path(ev.execution_id),
            }
        )
    return out


async def _count_error_logs(session: AsyncSession, *, user_id_str: str) -> int:
    uid = user_id_str.strip()
    c1 = select(func.count()).select_from(AgentExecution).where(
        AgentExecution.user_id == uid,
        AgentExecution.state == "FAILED",
    )
    c2 = select(func.count()).select_from(AgentExecutionEvent).where(
        AgentExecutionEvent.user_id == uid,
        or_(
            AgentExecutionEvent.outcome.in_(_FAIL_OUTCOMES),
            AgentExecutionEvent.outcome == "unknown",
        ),
    )
    n1 = int((await session.execute(c1)).scalar_one())
    n2 = int((await session.execute(c2)).scalar_one())
    # 上限松合并：FAILED 执行与失败事件可能相关，列表侧不做去重计数（Phase1）
    return n1 + n2


async def list_error_logs_for_instance(
    session: AsyncSession,
    *,
    user_id_str: str,
    limit: int,
    offset: int,
) -> tuple[list[dict[str, Any]], int]:
    uid = user_id_str.strip()
    total = await _count_error_logs(session, user_id_str=uid)
    # Pull merged stream: executions FAILED + events failed, sort by ts desc — overscan for offset
    overfetch = min(offset + limit + 100, 500)
    ex_stmt = (
        select(AgentExecution)
        .where(
            AgentExecution.user_id == uid,
            AgentExecution.state == "FAILED",
        )
        .order_by(AgentExecution.updated_at.desc())
        .limit(overfetch)
    )
    ev_stmt = (
        select(AgentExecutionEvent)
        .where(
            AgentExecutionEvent.user_id == uid,
            or_(
                AgentExecutionEvent.outcome.in_(_FAIL_OUTCOMES),
                AgentExecutionEvent.outcome == "unknown",
            ),
        )
        .order_by(AgentExecutionEvent.created_at.desc())
        .limit(overfetch)
    )
    ex_rows = list((await session.execute(ex_stmt)).scalars().all())
    ev_rows = list((await session.execute(ev_stmt)).scalars().all())

    merged: list[tuple[datetime, dict[str, Any]]] = []
    for r in ex_rows:
        merged.append(
            (
                r.updated_at,
                {
                    "kind": "execution_failed",
                    "executionId": r.execution_id,
                    "createdAt": r.updated_at,
                    "scenarioId": r.scenario_id,
                    "channel": r.channel,
                    "stateOrOutcome": r.state,
                    "message": (r.note or "")[:2000] or None,
                    "observabilityTimelinePath": _timeline_path(r.execution_id),
                },
            )
        )
    for ev in ev_rows:
        merged.append(
            (
                ev.created_at,
                {
                    "kind": "timeline_step_failed",
                    "executionId": ev.execution_id,
                    "createdAt": ev.created_at,
                    "scenarioId": None,
                    "channel": None,
                    "stateOrOutcome": ev.outcome or "",
                    "message": (ev.step_kind or "")[:256] or None,
                    "observabilityTimelinePath": _timeline_path(ev.execution_id),
                },
            )
        )
    merged.sort(key=lambda x: x[0], reverse=True)
    slice_rows = [m[1] for m in merged[offset : offset + limit]]
    return slice_rows, total


async def require_instance_user_id_str(
    session: AsyncSession,
    *,
    instance_public_id: str,
) -> str:
    pair = await get_agent_instance_joined_admin(session, instance_public_id=instance_public_id)
    if pair is None:
        raise AppError(
            code="AGENT_ADMIN_INSTANCE_NOT_FOUND",
            message="实例不存在。",
            status_code=404,
            details={"instanceId": instance_public_id.strip()[:80]},
        )
    inst, _tb = pair
    return str(inst.telegram_user_id)
