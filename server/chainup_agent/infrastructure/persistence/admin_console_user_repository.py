from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.infrastructure.persistence.models import AdminConsoleUser


async def get_admin_console_user_by_username(
    session: AsyncSession, username: str
) -> AdminConsoleUser | None:
    stmt = select(AdminConsoleUser).where(AdminConsoleUser.username == username).limit(1)
    result = await session.execute(stmt)
    return result.scalars().first()


async def count_admin_console_users(session: AsyncSession) -> int:
    stmt = select(func.count()).select_from(AdminConsoleUser)
    result = await session.execute(stmt)
    return int(result.scalar_one())


async def add_admin_console_user(
    session: AsyncSession,
    *,
    username: str,
    password_hash: str,
) -> AdminConsoleUser:
    row = AdminConsoleUser(
        username=username,
        password_hash=password_hash,
        is_active=True,
    )
    session.add(row)
    await session.flush()
    return row
