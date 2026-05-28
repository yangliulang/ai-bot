"""FastAPI dependencies (thin wrappers over infrastructure)."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.admin_console_token import verify_admin_console_access_token
from chainup_agent.core.config import get_settings
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.base import get_db_session, get_session_factory

_admin_console_http_bearer = HTTPBearer(auto_error=False)


async def require_admin_console_bearer(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_admin_console_http_bearer),
    ],
) -> None:
    """
    When ``CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET`` is set: require ``Authorization: Bearer``.

    When unset (legacy dev): no-op — login still returns an opaque token that is not verified
    server-side.
    """
    settings = get_settings()
    if not settings.admin_console_jwt_secret.strip():
        return
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppError(
            code="ADMIN_CONSOLE_AUTH_REQUIRED",
            message="需要控制台登录凭证：请在 Authorization 头携带 Bearer access_token。",
            status_code=401,
        )
    verify_admin_console_access_token(settings, credentials.credentials)


async def require_admin_console_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_admin_console_http_bearer),
    ],
) -> str:
    """
    Like ``require_admin_console_bearer`` but returns JWT ``sub`` (username).

    When JWT secret is unset: ``console.local`` (legacy dev).
    """
    settings = get_settings()
    if not settings.admin_console_jwt_secret.strip():
        return "console.local"
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppError(
            code="ADMIN_CONSOLE_AUTH_REQUIRED",
            message="需要控制台登录凭证：请在 Authorization 头携带 Bearer access_token。",
            status_code=401,
        )
    return verify_admin_console_access_token(settings, credentials.credentials)


async def get_admin_login_db_session() -> AsyncIterator[AsyncSession | None]:
    """Opens a DB session only for `admin_console_auth_mode=database`."""
    if get_settings().admin_console_auth_mode != "database":
        yield None
        return
    factory = get_session_factory()
    async with factory() as session:
        yield session


AdminLoginDbSession = Annotated[AsyncSession | None, Depends(get_admin_login_db_session)]

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
