"""Admin-facing Telegram bot identity and connectivity checks (FR-TG-ADMIN-01, 05)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.telegram_admin import (
    TelegramBotIdentity,
    TelegramBotStatusResponse,
    TelegramSelfTestResult,
)
from chainup_agent.application import telegram_runtime_config as tg_runtime
from chainup_agent.application import telegram_webhook_admin as webhook_admin
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.telegram.bot_api import call_telegram_bot_api


def _token_fingerprint(token: str) -> str:
    t = token.strip()
    if len(t) <= 4:
        return "****"
    return f"…{t[-4:]}"


def _identity_from_get_me(result: dict) -> TelegramBotIdentity:
    first = (result.get("first_name") or "").strip()
    last = (result.get("last_name") or "").strip()
    name = " ".join(p for p in (first, last) if p).strip() or None
    username = result.get("username")
    return TelegramBotIdentity(
        id=str(result.get("id", "")),
        username=str(username) if username else None,
        name=name,
    )


def _env_urls(settings: Settings) -> tuple[str, str, str]:
    public = settings.public_base_url.rstrip("/")
    bind = settings.telegram_bind_page_url.strip()
    default_wh = ""
    if settings.telegram_bot_token.strip() and public:
        default_wh = webhook_admin.webhook_callback_public_url(
            settings,
            settings.telegram_bot_token.strip(),
        )
    return public, bind, default_wh


def _env_snapshot(settings: Settings) -> tuple[datetime, str, str, str]:
    now = datetime.now(timezone.utc)
    public, bind, default_wh = _env_urls(settings)
    return now, public, bind, default_wh


async def fetch_bot_status(
    settings: Settings,
    *,
    session: AsyncSession | None = None,
) -> TelegramBotStatusResponse:
    """Best-effort ``getMe``; never returns the Bot token."""
    raw = settings.telegram_bot_token.strip()
    runtime_params: dict[str, Any] | None = None
    config_version: int | None = None
    if session is not None:
        runtime_params, config_version = await tg_runtime.load_runtime_params(session)

    now, public, bind, default_wh = _env_snapshot(settings)
    if not raw:
        return TelegramBotStatusResponse(
            bot=None,
            last_fetched_at=now,
            last_error_summary=(
                "未配置 CHAINUP_AGENT_TELEGRAM_BOT_TOKEN（server/.env 或密钥托管）"
            ),
            secret_ref_fingerprint=None,
            token_configured=False,
            public_base_url=public,
            bind_page_url=bind,
            default_webhook_url=default_wh,
            runtime_params=runtime_params,
            config_version=config_version,
        )

    try:
        data = await call_telegram_bot_api(raw, "getMe", http_method="GET")
        inner = data.get("result") or {}
        if not isinstance(inner, dict):
            inner = {}
        bot = _identity_from_get_me(inner) if inner.get("id") is not None else None
        return TelegramBotStatusResponse(
            bot=bot,
            last_fetched_at=now,
            last_error_summary=None,
            secret_ref_fingerprint=_token_fingerprint(raw),
            token_configured=True,
            public_base_url=public,
            bind_page_url=bind,
            default_webhook_url=default_wh,
            runtime_params=runtime_params,
            config_version=config_version,
        )
    except AppError as exc:
        return TelegramBotStatusResponse(
            bot=None,
            last_fetched_at=now,
            last_error_summary=exc.message[:500],
            secret_ref_fingerprint=_token_fingerprint(raw),
            token_configured=True,
            public_base_url=public,
            bind_page_url=bind,
            default_webhook_url=default_wh,
            runtime_params=runtime_params,
            config_version=config_version,
        )


async def patch_bot_runtime(
    session: AsyncSession,
    settings: Settings,
    *,
    runtime_params: dict[str, Any] | None,
    telegram_bot_token_secret_ref: str | None,
    if_match: str | None,
) -> TelegramBotStatusResponse:
    if (telegram_bot_token_secret_ref or "").strip():
        raise AppError(
            code="ADMIN_TELEGRAM_SECRET_REF_NOT_IMPLEMENTED",
            message=(
                "TELEGRAM_BOT_TOKEN_SECRET_REF 轮换尚未在本环境实现；"
                "请继续使用 CHAINUP_AGENT_TELEGRAM_BOT_TOKEN（.env）并重启服务。"
            ),
            status_code=501,
        )
    if runtime_params is None:
        raise AppError(
            code="ADMIN_TELEGRAM_RUNTIME_PARAMS_REQUIRED",
            message="PATCH body 须包含 runtimeParams",
            status_code=400,
        )
    await tg_runtime.merge_runtime_params(session, runtime_params, if_match)
    return await fetch_bot_status(settings, session=session)


async def run_self_test(settings: Settings) -> TelegramSelfTestResult:
    errors: list[str] = []
    get_me_ok = False
    get_webhook_ok = False

    status = await fetch_bot_status(settings)
    if status.bot is not None and not status.last_error_summary:
        get_me_ok = True
    elif status.last_error_summary:
        errors.append(f"getMe: {status.last_error_summary}")

    try:
        info = await webhook_admin.fetch_webhook_info(settings)
        get_webhook_ok = True
        if info.last_error_message:
            errors.append(f"getWebhookInfo.last_error: {info.last_error_message[:300]}")
    except AppError as exc:
        errors.append(f"getWebhookInfo: {exc.message[:300]}")

    summary = "; ".join(errors) if errors else None
    if get_me_ok and get_webhook_ok and not errors:
        summary = None
    return TelegramSelfTestResult(
        get_me_ok=get_me_ok,
        get_webhook_info_ok=get_webhook_ok,
        error_summary=summary,
    )
