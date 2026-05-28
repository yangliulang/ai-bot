"""Persisted access-control whitelist rows (FR-MC602)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from chainup_agent.infrastructure.persistence.models.base import Base


class AdminAccessWhitelistEntry(Base):
    __tablename__ = "admin_access_whitelist_entry"

    entry_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    list_id: Mapped[str] = mapped_column(String(64), nullable=False)
    user_uid: Mapped[str] = mapped_column(String(64), nullable=False)
    user_id_masked: Mapped[str] = mapped_column(String(128), nullable=False)
    note: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_by: Mapped[str | None] = mapped_column(String(128), nullable=True)

    __table_args__ = (
        Index("ix_admin_access_whitelist_user_uid", "user_uid"),
        Index("ix_admin_access_whitelist_list_user", "list_id", "user_uid", unique=True),
    )
