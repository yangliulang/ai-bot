"""Create or update Agent instance rows (Telegram-scoped Phase1)."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.core.config import Settings
from chainup_agent.infrastructure.persistence.models.agent_instance import AgentInstance


def _new_public_instance_id() -> str:
    return f"inst_{secrets.token_hex(12)}"


async def upsert_agent_instance_for_telegram_binding(
    session: AsyncSession,
    *,
    settings: Settings,
    telegram_user_id: int,
    exchange_sub_account_user_id: str,
) -> tuple[AgentInstance, bool]:
    """
    One instance per ``telegram_user_id`` for Phase1.

    Returns ``(row, created)`` where ``created`` is True on first insert.
    """
    sub = exchange_sub_account_user_id.strip()
    tid = settings.default_agent_template_id.strip() or "tmpl_agent_default"
    tv = settings.default_agent_template_version.strip() or "1"
    now = datetime.now(UTC)

    stmt = select(AgentInstance).where(AgentInstance.telegram_user_id == telegram_user_id)
    res = await session.execute(stmt)
    row = res.scalar_one_or_none()
    if row is None:
        inst = AgentInstance(
            instance_id=_new_public_instance_id(),
            telegram_user_id=telegram_user_id,
            exchange_sub_account_user_id=sub[:128],
            template_id=tid[:64],
            template_version=tv[:32],
            instance_overrides_json="{}",
            created_at=now,
            updated_at=now,
        )
        session.add(inst)
        await session.flush()
        return inst, True

    row.exchange_sub_account_user_id = sub[:128]
    row.template_id = tid[:64]
    row.template_version = tv[:32]
    row.updated_at = now
    await session.flush()
    return row, False
