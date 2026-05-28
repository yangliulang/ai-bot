"""Admin prompt packs — persistence for runtime effective prompts (FR-PM08 slice)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from chainup_agent.infrastructure.persistence.models.base import Base


class AdminPromptPack(Base):
    __tablename__ = "admin_prompt_pack"

    prompt_pack_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    prompt_pack_type: Mapped[str] = mapped_column(String(32), nullable=False)
    scenario_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    lifecycle: Mapped[str] = mapped_column(String(32), nullable=False)
    prompt_pack_version: Mapped[str] = mapped_column(String(64), nullable=False)
    etag: Mapped[str] = mapped_column(String(128), nullable=False)
    messages_json: Mapped[str] = mapped_column(Text(), nullable=False)
    variable_schema_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    placeholder_denylist_revision: Mapped[str | None] = mapped_column(String(64), nullable=True)
    safety_phrase_blocklist_revision: Mapped[str | None] = mapped_column(String(64), nullable=True)
    row_version: Mapped[int] = mapped_column(BigInteger(), nullable=False, server_default="1")
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
