"""Persisted Telegram user ↔ validated trading API binding (secrets sealed at rest)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, LargeBinary, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from chainup_agent.infrastructure.persistence.models.base import Base


class TelegramAgentTradingBinding(Base):
    """One row per Telegram user id (deeplink anchor) after confirm."""

    __tablename__ = "telegram_agent_trading_binding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger(), nullable=False, unique=True)
    tg_username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tg_first_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    tg_last_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    tg_lang: Mapped[str | None] = mapped_column(String(32), nullable=True)
    openapi_base_url: Mapped[str] = mapped_column(Text(), nullable=False)
    trading_credentials_sealed: Mapped[bytes] = mapped_column(LargeBinary(), nullable=False)
    idempotency_key_last: Mapped[str | None] = mapped_column(String(128), nullable=True)
    deeplink_token_last: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
