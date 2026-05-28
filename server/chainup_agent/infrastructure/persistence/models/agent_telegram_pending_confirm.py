"""Telegram inline-button confirmation sessions (e.g. flash-convert type-A)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from chainup_agent.infrastructure.persistence.models.base import Base


class AgentTelegramPendingConfirm(Base):
    __tablename__ = "agent_telegram_pending_confirm"

    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    public_token: Mapped[str] = mapped_column(String(24), nullable=False, unique=True, index=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger(), nullable=False, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    kind: Mapped[str] = mapped_column(String(48), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
