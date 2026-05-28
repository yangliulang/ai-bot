"""Admin console self-service registration (database auth mode)."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.auth import AdminLoginResponse, AdminRegisterRequest
from chainup_agent.application.admin_console_login import _issue_access_token
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence import admin_console_user_repository as user_repo
from chainup_agent.infrastructure.persistence.admin_user_password import hash_password


async def admin_console_register(
    session: AsyncSession,
    settings: Settings,
    body: AdminRegisterRequest,
) -> AdminLoginResponse:
    """
    Create an operator row and return the same bearer shape as login.

    - Requires ``admin_console_auth_mode=database``.
    - Allowed when ``admin_console_user`` is **empty** (bootstrap first admin), or when \
      ``CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION=true``.
    """
    if settings.admin_console_auth_mode != "database":
        raise AppError(
            code="ADMIN_CONSOLE_REGISTRATION_REQUIRES_DATABASE_AUTH",
            message=(
                "控制台自助注册仅适用于 CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE=database。"
                "请将环境改为 database 并完成数据库迁移后重试。"
            ),
            status_code=503,
        )

    dup = await user_repo.get_admin_console_user_by_username(session, body.username)
    if dup is not None:
        raise AppError(
            code="ADMIN_CONSOLE_USERNAME_ALREADY_EXISTS",
            message="用户名已被占用",
            status_code=409,
        )

    n_users = await user_repo.count_admin_console_users(session)
    if n_users > 0 and not settings.admin_console_open_registration:
        raise AppError(
            code="ADMIN_CONSOLE_REGISTRATION_DISABLED",
            message=(
                "当前已存在管理员账号：未开启开放注册。"
                "首张账号可在空库时通过注册创建；如需继续创建账号请设置 "
                "CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION=true，"
                "或使用 chainup-agent-seed-admin。"
            ),
            status_code=403,
        )

    try:
        ph = hash_password(body.password)
    except ValueError as e:
        raise AppError(
            code="VALIDATION_ERROR",
            message=str(e),
            status_code=422,
        ) from e

    try:
        await user_repo.add_admin_console_user(
            session, username=body.username, password_hash=ph
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise AppError(
            code="ADMIN_CONSOLE_USERNAME_ALREADY_EXISTS",
            message="用户名已被占用",
            status_code=409,
        ) from None

    token = _issue_access_token(settings, username=body.username)
    return AdminLoginResponse(access_token=token, username=body.username)
