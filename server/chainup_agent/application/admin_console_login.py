import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.auth import AdminLoginRequest, AdminLoginResponse
from chainup_agent.application.admin_console_token import mint_admin_console_access_token
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence import admin_console_user_repository as user_repo
from chainup_agent.infrastructure.persistence.admin_user_password import verify_password


def _issue_access_token(settings: Settings, *, username: str) -> str:
    if settings.admin_console_jwt_secret.strip():
        return mint_admin_console_access_token(settings, username=username)
    return secrets.token_urlsafe(32)


def _login_env(settings: Settings, body: AdminLoginRequest) -> AdminLoginResponse:
    if not settings.admin_panel_username or not settings.admin_panel_password:
        raise AppError(
            code="ADMIN_CONSOLE_AUTH_DISABLED",
            message=(
                "Admin console login is disabled "
                "(set CHAINUP_AGENT_ADMIN_PANEL_USERNAME and CHAINUP_AGENT_ADMIN_PANEL_PASSWORD)"
            ),
            status_code=503,
        )
    if (
        body.username != settings.admin_panel_username
        or body.password != settings.admin_panel_password
    ):
        raise AppError(
            code="ADMIN_CONSOLE_AUTH_INVALID_CREDENTIALS",
            message="无效账户名或密码",
            status_code=401,
        )
    token = _issue_access_token(settings, username=body.username)
    return AdminLoginResponse(access_token=token, username=body.username)


async def _login_database(
    session: AsyncSession,
    settings: Settings,
    body: AdminLoginRequest,
) -> AdminLoginResponse:
    row = await user_repo.get_admin_console_user_by_username(session, body.username)
    if row is None or not row.is_active or not verify_password(body.password, row.password_hash):
        raise AppError(
            code="ADMIN_CONSOLE_AUTH_INVALID_CREDENTIALS",
            message="无效账户名或密码",
            status_code=401,
        )
    token = _issue_access_token(settings, username=row.username)
    return AdminLoginResponse(access_token=token, username=row.username)


async def admin_console_login(
    session: AsyncSession | None,
    settings: Settings,
    body: AdminLoginRequest,
) -> AdminLoginResponse:
    if settings.admin_console_auth_mode == "database":
        if session is None:
            raise RuntimeError("database auth mode requires an AsyncSession")
        return await _login_database(session, settings, body)
    return _login_env(settings, body)
