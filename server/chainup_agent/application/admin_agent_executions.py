"""Admin queries and ops delete over persisted ``agent_execution``."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution
from chainup_agent.infrastructure.persistence.models.agent_execution_event import (
    AgentExecutionEvent,
)


def _apply_execution_filters(
    stmt,
    *,
    execution_id: str | None,
    user_id: str | None,
    channel: str | None,
    scenario_id: str | None,
    state: str | None,
    keyword: str | None,
    created_after: datetime | None,
    created_before: datetime | None,
):
    if execution_id:
        stmt = stmt.where(AgentExecution.execution_id == execution_id.strip())
    if user_id:
        stmt = stmt.where(AgentExecution.user_id == user_id.strip())
    if channel:
        stmt = stmt.where(AgentExecution.channel == channel.strip())
    if scenario_id:
        stmt = stmt.where(AgentExecution.scenario_id == scenario_id.strip())
    if state:
        stmt = stmt.where(AgentExecution.state == state.strip())
    if keyword:
        kw = keyword.strip()
        if kw:
            pat = f"%{kw}%"
            stmt = stmt.where(
                or_(
                    AgentExecution.execution_id.like(pat),
                    AgentExecution.user_id.like(pat),
                    AgentExecution.scenario_id.like(pat),
                )
            )
    if created_after is not None:
        stmt = stmt.where(AgentExecution.created_at >= created_after)
    if created_before is not None:
        stmt = stmt.where(AgentExecution.created_at <= created_before)
    return stmt


async def count_agent_executions_admin(
    session: AsyncSession,
    *,
    execution_id: str | None,
    user_id: str | None,
    channel: str | None,
    scenario_id: str | None,
    state: str | None,
    keyword: str | None,
    created_after: datetime | None,
    created_before: datetime | None,
) -> int:
    stmt = select(func.count()).select_from(AgentExecution)
    stmt = _apply_execution_filters(
        stmt,
        execution_id=execution_id,
        user_id=user_id,
        channel=channel,
        scenario_id=scenario_id,
        state=state,
        keyword=keyword,
        created_after=created_after,
        created_before=created_before,
    )
    row = await session.execute(stmt)
    return int(row.scalar_one())


async def list_agent_executions_admin(
    session: AsyncSession,
    *,
    limit: int,
    offset: int,
    execution_id: str | None,
    user_id: str | None,
    channel: str | None,
    scenario_id: str | None,
    state: str | None,
    keyword: str | None,
    created_after: datetime | None,
    created_before: datetime | None,
) -> list[AgentExecution]:
    stmt = (
        select(AgentExecution)
        .order_by(AgentExecution.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    stmt = _apply_execution_filters(
        stmt,
        execution_id=execution_id,
        user_id=user_id,
        channel=channel,
        scenario_id=scenario_id,
        state=state,
        keyword=keyword,
        created_after=created_after,
        created_before=created_before,
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def get_agent_execution_admin(
    session: AsyncSession,
    *,
    execution_public_id: str,
) -> AgentExecution | None:
    eid = execution_public_id.strip()
    if not eid:
        return None
    return await session.get(AgentExecution, eid)


async def delete_agent_execution_admin(
    session: AsyncSession,
    *,
    execution_public_id: str,
) -> bool:
    """Hard-delete one row. Returns ``True`` if a row was deleted."""
    row = await get_agent_execution_admin(session, execution_public_id=execution_public_id)
    if row is None:
        return False
    await session.execute(
        delete(AgentExecutionEvent).where(AgentExecutionEvent.execution_id == row.execution_id)
    )
    await session.delete(row)
    await session.flush()
    return True
