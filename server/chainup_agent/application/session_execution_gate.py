"""Per-user execution gates — unknown_pending, pending Type-A (session-concurrency §5)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution
from chainup_agent.infrastructure.persistence.models.agent_telegram_pending_confirm import (
    AgentTelegramPendingConfirm,
)


async def telegram_user_has_unknown_write_execution(
    session: AsyncSession,
    telegram_user_id: int,
) -> bool:
    """``execution.state == UNKNOWN`` — D-1 block new write (§5.3)."""
    user_key = str(telegram_user_id)
    stmt = (
        select(func.count())
        .select_from(AgentExecution)
        .where(
            AgentExecution.user_id == user_key,
            AgentExecution.state == "UNKNOWN",
        )
    )
    row = await session.execute(stmt)
    return int(row.scalar_one()) > 0


async def telegram_user_has_pending_type_a_confirm(
    session: AsyncSession,
    telegram_user_id: int,
) -> bool:
    """DB-backed Type-A pending rows for chat user."""
    stmt = (
        select(func.count())
        .select_from(AgentTelegramPendingConfirm)
        .where(AgentTelegramPendingConfirm.telegram_user_id == telegram_user_id)
    )
    row = await session.execute(stmt)
    return int(row.scalar_one()) > 0
