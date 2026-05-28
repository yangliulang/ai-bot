"""Agent runtime instance (one row per Telegram user, PM instance-management carrier)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from chainup_agent.infrastructure.persistence.models.base import Base


class AgentInstance(Base):
    """User-visible Agent instance; created/updated on trading API confirm binding."""

    __tablename__ = "agent_instance"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    instance_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger(), nullable=False, unique=True, index=True
    )
    exchange_sub_account_user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    template_id: Mapped[str] = mapped_column(String(64), nullable=False)
    template_version: Mapped[str] = mapped_column(String(32), nullable=False)
    #: 机电态：RUNNING / PAUSED / STOPPED / ERROR（与控制台 RuntimeStateVm 对齐；不含 STARTING 时序态）
    runtime_state: Mapped[str] = mapped_column(
        String(16), nullable=False, default="RUNNING", server_default="RUNNING"
    )
    instance_overrides_json: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
        default="{}",
        server_default="{}",
    )
    activation_welcome_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
