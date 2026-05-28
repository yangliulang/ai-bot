"""Schemas aligned with product ``telegram-channels-schemas.yaml``."""

from __future__ import annotations

from datetime import datetime, timezone

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TelegramWebhookSetRequest(BaseModel):
    """Body for POST …/admin/channels/telegram/webhook · optional overrides."""

    model_config = ConfigDict(populate_by_name=True)

    url: str | None = Field(
        default=None,
        description="Webhook URL override; omit to derive from PUBLIC_BASE_URL + token path",
    )
    secret_token: str | None = Field(default=None, alias="secretToken")
    drop_pending_updates: bool | None = Field(default=None, alias="dropPendingUpdates")


class TelegramBotPatchRequest(BaseModel):
    """PATCH …/admin/channels/telegram/bot (FR-TG-ADMIN-02/03)."""

    model_config = ConfigDict(populate_by_name=True)

    telegram_bot_token_secret_ref: str | None = Field(
        default=None,
        alias="telegramBotTokenSecretRef",
        description="FR-TG-ADMIN-03 — not persisted in Phase1 patch (vault only).",
    )
    runtime_params: dict[str, Any] | None = Field(
        default=None,
        alias="runtimeParams",
        description="TELEGRAM_* non-secret keys (keys.md §4.2); merged into stored document.",
    )


class TelegramBotIdentity(BaseModel):
    """``getMe`` subset (FR-TG-ADMIN-01)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    username: str | None = None
    name: str | None = None


class TelegramBotStatusResponse(BaseModel):
    """GET ``…/admin/channels/telegram/bot``."""

    model_config = ConfigDict(populate_by_name=True)

    bot: TelegramBotIdentity | None = None
    channel_telegram_enabled: bool = Field(
        default=True,
        serialization_alias="channelTelegramEnabled",
    )
    last_fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        serialization_alias="lastFetchedAt",
    )
    last_error_summary: str | None = Field(
        default=None,
        serialization_alias="lastErrorSummary",
    )
    secret_ref_fingerprint: str | None = Field(
        default=None,
        serialization_alias="secretRefFingerprint",
        description="Masked token tail or env hint; never the full Bot token.",
    )
    token_configured: bool = Field(
        default=False,
        serialization_alias="tokenConfigured",
    )
    public_base_url: str = Field(
        default="",
        serialization_alias="publicBaseUrl",
        description="CHAINUP_AGENT_PUBLIC_BASE_URL (normalized, no trailing slash).",
    )
    bind_page_url: str = Field(
        default="",
        serialization_alias="bindPageUrl",
        description="CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL for Bot bind CTA.",
    )
    default_webhook_url: str = Field(
        default="",
        serialization_alias="defaultWebhookUrl",
        description=(
            "URL used when POST …/webhook with empty body (PUBLIC_BASE_URL + encoded token path)."
        ),
    )
    runtime_params: dict[str, Any] | None = Field(
        default=None,
        serialization_alias="runtimeParams",
    )
    config_version: int | None = Field(
        default=None,
        serialization_alias="configVersion",
        description="Optimistic lock version for PATCH If-Match.",
    )


class TelegramSelfTestResult(BaseModel):
    """POST ``…/admin/channels/telegram/self-test`` (FR-TG-ADMIN-05)."""

    model_config = ConfigDict(populate_by_name=True)

    get_me_ok: bool = Field(serialization_alias="getMeOk")
    get_webhook_info_ok: bool = Field(serialization_alias="getWebhookInfoOk")
    error_summary: str | None = Field(default=None, serialization_alias="errorSummary")


class TelegramWebhookInfo(BaseModel):
    """``getWebhookInfo`` summary (no webhook secret leakage)."""

    model_config = ConfigDict(populate_by_name=True)

    url: str
    has_custom_certificate: bool = Field(serialization_alias="hasCustomCertificate")
    pending_update_count: int = Field(serialization_alias="pendingUpdateCount")
    last_error_date: int | None = Field(default=None, serialization_alias="lastErrorDate")
    last_error_message: str | None = Field(default=None, serialization_alias="lastErrorMessage")
    max_connections: int | None = Field(default=None, serialization_alias="maxConnections")
