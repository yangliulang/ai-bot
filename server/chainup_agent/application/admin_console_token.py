"""JWT access tokens for admin console (`admin/` SPA) when JWT secret is configured."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError

_TOKEN_TYP = "admin_console"


def mint_admin_console_access_token(settings: Settings, *, username: str) -> str:
    secret = settings.admin_console_jwt_secret.strip()
    if not secret:
        raise RuntimeError("admin_console_jwt_secret must be non-empty to mint tokens")

    now = datetime.now(UTC)
    exp = now + timedelta(seconds=max(60, settings.admin_console_access_token_ttl_seconds))
    payload = {
        "sub": username.strip(),
        "typ": _TOKEN_TYP,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_admin_console_access_token(settings: Settings, token: str) -> str:
    """
    Validate Bearer token; return authenticated console username.

    Raises ``AppError`` (401) when missing claims, wrong type, or bad signature.
    """
    secret = settings.admin_console_jwt_secret.strip()
    if not secret:
        raise RuntimeError("admin_console_jwt_secret must be set for verification")

    try:
        payload = jwt.decode(
            token.strip(),
            secret,
            algorithms=["HS256"],
            options={"require": ["exp", "iat", "sub"]},
        )
    except ExpiredSignatureError as exc:
        raise AppError(
            code="ADMIN_CONSOLE_ACCESS_TOKEN_EXPIRED",
            message="控制台会话已过期，请重新登录。",
            status_code=401,
        ) from exc
    except InvalidTokenError as exc:
        raise AppError(
            code="ADMIN_CONSOLE_ACCESS_TOKEN_INVALID",
            message="无效或损坏的控制台访问令牌。",
            status_code=401,
        ) from exc

    if payload.get("typ") != _TOKEN_TYP:
        raise AppError(
            code="ADMIN_CONSOLE_ACCESS_TOKEN_INVALID",
            message="令牌类型不匹配。",
            status_code=401,
        )
    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub.strip():
        raise AppError(
            code="ADMIN_CONSOLE_ACCESS_TOKEN_INVALID",
            message="令牌主体无效。",
            status_code=401,
        )
    return sub.strip()
