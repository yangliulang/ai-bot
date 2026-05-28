"""Admin-facing Telegram webhook operations (FR-TG-ADMIN-04)."""

from __future__ import annotations

from urllib.parse import quote, urlparse

from chainup_agent.api.schemas.telegram_admin import (
    TelegramWebhookInfo,
    TelegramWebhookSetRequest,
)
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.telegram.bot_api import call_telegram_bot_api


def _require_bot_token(settings: Settings) -> str:
    raw = settings.telegram_bot_token.strip()
    if not raw:
        raise AppError(
            code="TELEGRAM_WEBHOOK_NOT_CONFIGURED",
            message=(
                "Telegram bot token is not set (CHAINUP_AGENT_TELEGRAM_BOT_TOKEN in server/.env)"
            ),
            status_code=503,
        )
    return raw


def _require_https_webhook_url(url: str) -> None:
    """Telegram ``setWebhook`` rejects non-https URLs."""
    parsed = urlparse(url)
    scheme = (parsed.scheme or "").lower()
    if scheme != "https":
        raise AppError(
            code="ADMIN_TELEGRAM_WEBHOOK_HTTPS_REQUIRED",
            message=(
                "Telegram requires an HTTPS webhook URL. "
                "Set CHAINUP_AGENT_PUBLIC_BASE_URL to a public https origin "
                "(e.g. ngrok / cloudflared tunnel), or pass an https `url` in the request body."
            ),
            status_code=400,
            details={"url_scheme": scheme or "missing"},
        )


def webhook_callback_public_url(settings: Settings, bot_token: str) -> str:
    """
    Public URL aligned with ``POST /webhook/telegram/{bot_token}``.

    Token in the path is percent-encoded so characters like ``:`` survive URL handling.
    """
    base = settings.public_base_url.rstrip("/")
    suffix = quote(bot_token, safe="")
    return f"{base}/webhook/telegram/{suffix}"


def _result_to_webhook_info(result_field: dict) -> TelegramWebhookInfo:
    """Map Telegram ``getWebhookInfo`` result object to API schema."""
    return TelegramWebhookInfo(
        url=(result_field.get("url") or "") or "",
        has_custom_certificate=bool(result_field.get("has_custom_certificate")),
        pending_update_count=int(result_field.get("pending_update_count") or 0),
        last_error_date=(
            None
            if result_field.get("last_error_date") is None
            else int(result_field.get("last_error_date"))
        ),
        last_error_message=(
            None
            if result_field.get("last_error_message") in (None, "")
            else str(result_field.get("last_error_message"))
        ),
        max_connections=(
            None
            if result_field.get("max_connections") is None
            else int(result_field.get("max_connections"))
        ),
    )


async def fetch_webhook_info(settings: Settings) -> TelegramWebhookInfo:
    token = _require_bot_token(settings)
    data = await call_telegram_bot_api(token, "getWebhookInfo", http_method="GET")
    inner = data.get("result") or {}
    if not isinstance(inner, dict):
        inner = {}
    return _result_to_webhook_info(inner)


async def apply_set_webhook(
    settings: Settings,
    body: TelegramWebhookSetRequest | None,
) -> TelegramWebhookInfo:
    opts = body or TelegramWebhookSetRequest()
    token = _require_bot_token(settings)
    url = (opts.url or "").strip() or webhook_callback_public_url(settings, token)
    _require_https_webhook_url(url)
    payload: dict = {"url": url}
    if opts.drop_pending_updates is not None:
        payload["drop_pending_updates"] = opts.drop_pending_updates
    if opts.secret_token:
        payload["secret_token"] = opts.secret_token
    await call_telegram_bot_api(token, "setWebhook", json_payload=payload)
    return await fetch_webhook_info(settings)


async def apply_delete_webhook(settings: Settings) -> TelegramWebhookInfo:
    token = _require_bot_token(settings)
    await call_telegram_bot_api(token, "deleteWebhook", json_payload={})
    return await fetch_webhook_info(settings)
