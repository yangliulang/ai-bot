"""Prompt pack version audit trail — publish / rollback snapshots (FR-PM02 · PM-C02)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from chainup_agent.infrastructure.persistence.models.base import Base


class AdminPromptPackVersionEvent(Base):
    __tablename__ = "admin_prompt_pack_version_event"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    prompt_pack_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    prompt_pack_version: Mapped[str] = mapped_column(String(64), nullable=False)
    lifecycle: Mapped[str] = mapped_column(String(32), nullable=False)
    event: Mapped[str] = mapped_column(String(32), nullable=False)
    actor: Mapped[str | None] = mapped_column(String(128), nullable=True)
    summary: Mapped[str | None] = mapped_column(String(512), nullable=True)
    messages_json: Mapped[str] = mapped_column(Text(), nullable=False)
    variable_schema_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
