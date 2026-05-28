"""Admin read-only listing for persisted Telegram ↔ trading API bindings (no secret material)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


def mask_optional_tail(raw: str | None, *, edge: int = 4) -> str | None:
    if raw is None:
        return None
    t = raw.strip()
    if not t:
        return None
    if len(t) <= edge * 2:
        return "••••"
    return f"{t[:edge]}…{t[-edge:]}"


class AdminTradingBindingListItem(BaseModel):
    """One row from ``telegram_agent_trading_binding`` — wire JSON camelCase."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    telegram_user_id: int = Field(serialization_alias="telegramUserId")
    tg_username: str | None = Field(default=None, serialization_alias="tgUsername")
    tg_first_name: str | None = Field(default=None, serialization_alias="tgFirstName")
    tg_last_name: str | None = Field(default=None, serialization_alias="tgLastName")
    tg_lang: str | None = Field(default=None, serialization_alias="tgLang")
    openapi_base_url: str = Field(serialization_alias="openapiBaseUrl")
    idempotency_key_last_masked: str | None = Field(
        default=None,
        serialization_alias="idempotencyKeyLastMasked",
    )
    deeplink_token_last_masked: str | None = Field(
        default=None,
        serialization_alias="deeplinkTokenLastMasked",
    )
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class AdminTradingBindingListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[AdminTradingBindingListItem]
    total: int
