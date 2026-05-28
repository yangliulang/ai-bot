"""Operational Telegram channel API — aligns with ``admin/telegram-channels.yaml`` webhook paths."""

from __future__ import annotations

from chainup_agent.api.deps import DbSession, require_admin_console_bearer
from chainup_agent.api.schemas.telegram_admin import (
    TelegramBotPatchRequest,
    TelegramBotStatusResponse,
    TelegramSelfTestResult,
    TelegramWebhookInfo,
    TelegramWebhookSetRequest,
)
from chainup_agent.application import telegram_bot_admin as telegram_bot
from chainup_agent.application import telegram_webhook_admin as telegram_wh
from chainup_agent.core.config import get_settings
from fastapi import APIRouter, Body, Depends, Header

router = APIRouter(
    prefix="/api/v1/admin/channels/telegram",
    tags=["Admin — Telegram"],
    dependencies=[Depends(require_admin_console_bearer)],
)


@router.get(
    "/bot",
    response_model=TelegramBotStatusResponse,
    response_model_by_alias=True,
)
async def get_admin_telegram_bot(db: DbSession) -> TelegramBotStatusResponse:
    """Bot identity via ``getMe`` (no token in response). FR-TG-ADMIN-01."""
    return await telegram_bot.fetch_bot_status(get_settings(), session=db)


@router.patch(
    "/bot",
    response_model=TelegramBotStatusResponse,
    response_model_by_alias=True,
)
async def patch_admin_telegram_bot(
    body: TelegramBotPatchRequest,
    db: DbSession,
    if_match: str | None = Header(default=None, alias="If-Match"),
) -> TelegramBotStatusResponse:
    """Merge ``runtimeParams`` (FR-TG-ADMIN-02); optional ``If-Match`` = ``configVersion``."""
    result = await telegram_bot.patch_bot_runtime(
        db,
        get_settings(),
        runtime_params=body.runtime_params,
        telegram_bot_token_secret_ref=body.telegram_bot_token_secret_ref,
        if_match=if_match,
    )
    await db.commit()
    return result


@router.post(
    "/self-test",
    response_model=TelegramSelfTestResult,
    response_model_by_alias=True,
)
async def post_admin_telegram_self_test() -> TelegramSelfTestResult:
    """Connectivity check: ``getMe`` + ``getWebhookInfo``. FR-TG-ADMIN-05."""
    return await telegram_bot.run_self_test(get_settings())


@router.post(
    "/webhook",
    response_model=TelegramWebhookInfo,
    response_model_by_alias=True,
)
async def post_admin_telegram_webhook(
    body: TelegramWebhookSetRequest | None = Body(default=None),  # noqa: B008
) -> TelegramWebhookInfo:
    """Register Telegram webhook (derive URL from ``CHAINUP_AGENT_PUBLIC_BASE_URL`` by default)."""
    return await telegram_wh.apply_set_webhook(get_settings(), body)


@router.get(
    "/webhook",
    response_model=TelegramWebhookInfo,
    response_model_by_alias=True,
)
async def get_admin_telegram_webhook() -> TelegramWebhookInfo:
    """Return ``getWebhookInfo`` summary."""
    return await telegram_wh.fetch_webhook_info(get_settings())


@router.delete(
    "/webhook",
    response_model=TelegramWebhookInfo,
    response_model_by_alias=True,
)
async def delete_admin_telegram_webhook() -> TelegramWebhookInfo:
    """Delete webhook then return refreshed info (Telegram clears ``url``)."""
    return await telegram_wh.apply_delete_webhook(get_settings())
