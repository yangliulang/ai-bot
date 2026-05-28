"""DB access for admin Agent instance list/detail/delete."""

from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution
from chainup_agent.infrastructure.persistence.models.agent_instance import AgentInstance
from chainup_agent.infrastructure.persistence.models.agent_telegram_pending_confirm import (
    AgentTelegramPendingConfirm,
)
from chainup_agent.infrastructure.persistence.models.telegram_agent_trading_binding import (
    TelegramAgentTradingBinding,
)

_TERMINAL_EXECUTION_STATES = frozenset({"SUCCEEDED", "FAILED", "CANCELLED"})


def _apply_instance_filters(
    stmt,
    *,
    filter_instance_id: str | None,
    filter_telegram_user_id: int | None,
):
    if filter_instance_id:
        stmt = stmt.where(AgentInstance.instance_id == filter_instance_id.strip())
    if filter_telegram_user_id is not None:
        stmt = stmt.where(AgentInstance.telegram_user_id == filter_telegram_user_id)
    return stmt


async def count_agent_instances_admin(
    session: AsyncSession,
    *,
    filter_instance_id: str | None,
    filter_telegram_user_id: int | None,
) -> int:
    stmt = select(func.count()).select_from(AgentInstance)
    stmt = _apply_instance_filters(
        stmt,
        filter_instance_id=filter_instance_id,
        filter_telegram_user_id=filter_telegram_user_id,
    )
    row = await session.execute(stmt)
    return int(row.scalar_one())


async def list_agent_instances_joined_admin(
    session: AsyncSession,
    *,
    limit: int,
    offset: int,
    filter_instance_id: str | None,
    filter_telegram_user_id: int | None,
) -> list[tuple[AgentInstance, TelegramAgentTradingBinding | None]]:
    stmt = (
        select(AgentInstance, TelegramAgentTradingBinding)
        .outerjoin(
            TelegramAgentTradingBinding,
            TelegramAgentTradingBinding.telegram_user_id == AgentInstance.telegram_user_id,
        )
        .order_by(AgentInstance.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    stmt = _apply_instance_filters(
        stmt,
        filter_instance_id=filter_instance_id,
        filter_telegram_user_id=filter_telegram_user_id,
    )
    res = await session.execute(stmt)
    return [(r[0], r[1]) for r in res.all()]


async def get_agent_instance_joined_admin(
    session: AsyncSession,
    *,
    instance_public_id: str,
) -> tuple[AgentInstance, TelegramAgentTradingBinding | None] | None:
    stmt = (
        select(AgentInstance, TelegramAgentTradingBinding)
        .outerjoin(
            TelegramAgentTradingBinding,
            TelegramAgentTradingBinding.telegram_user_id == AgentInstance.telegram_user_id,
        )
        .where(AgentInstance.instance_id == instance_public_id.strip())
    )
    res = await session.execute(stmt)
    row = res.one_or_none()
    if row is None:
        return None
    return row[0], row[1]


async def _count_open_executions_for_telegram_user(
    session: AsyncSession,
    *,
    telegram_user_id: int,
) -> int:
    user_key = str(telegram_user_id)
    stmt = (
        select(func.count())
        .select_from(AgentExecution)
        .where(
            AgentExecution.user_id == user_key,
            AgentExecution.state.notin_(_TERMINAL_EXECUTION_STATES),
        )
    )
    row = await session.execute(stmt)
    return int(row.scalar_one())


async def _count_pending_confirms_for_telegram_user(
    session: AsyncSession,
    *,
    telegram_user_id: int,
) -> int:
    stmt = (
        select(func.count())
        .select_from(AgentTelegramPendingConfirm)
        .where(AgentTelegramPendingConfirm.telegram_user_id == telegram_user_id)
    )
    row = await session.execute(stmt)
    return int(row.scalar_one())


async def delete_agent_instance_admin(
    session: AsyncSession,
    *,
    instance_public_id: str,
) -> None:
    """
    Hard-delete ``agent_instance`` and clear Agent-side trading binding (I06).

    Also removes ``telegram_agent_trading_binding`` for the same ``telegram_user_id``
    so Deeplink / Telegram treat the user as unbound and can complete bind again.
    Does not touch the exchange sub-account itself (rules §2.3). Blocks when
    non-terminal executions or Telegram Type-A pending confirmations exist.
    """
    iid = instance_public_id.strip()
    pair = await get_agent_instance_joined_admin(session, instance_public_id=iid)
    if pair is None:
        raise AppError(
            code="AGENT_ADMIN_INSTANCE_NOT_FOUND",
            message="未找到该实例",
            status_code=404,
            details={"instanceId": iid[:80]},
        )
    inst, tb = pair
    open_exec = await _count_open_executions_for_telegram_user(
        session, telegram_user_id=inst.telegram_user_id
    )
    pending = await _count_pending_confirms_for_telegram_user(
        session, telegram_user_id=inst.telegram_user_id
    )
    if open_exec > 0 or pending > 0:
        reasons: list[str] = []
        if open_exec > 0:
            reasons.append("存在未终局的执行记录")
        if pending > 0:
            reasons.append("存在待确认的 Telegram 交易确认")
        raise AppError(
            code="AGENT_ADMIN_INSTANCE_DELETE_BLOCKED",
            message="；".join(reasons) + "，暂不可删除实例。",
            status_code=422,
            details={
                "instanceId": inst.instance_id,
                "telegramUserId": str(inst.telegram_user_id),
                "openExecutions": open_exec,
                "pendingConfirmations": pending,
            },
        )
    await session.delete(inst)
    if tb is not None:
        await session.delete(tb)
    await session.execute(
        delete(AgentTelegramPendingConfirm).where(
            AgentTelegramPendingConfirm.telegram_user_id == inst.telegram_user_id
        )
    )
    await session.flush()
