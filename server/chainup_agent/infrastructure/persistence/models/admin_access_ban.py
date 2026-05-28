"""User bans for Agent product scope (FR-MC603)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from chainup_agent.infrastructure.persistence.models.base import Base


class AdminAccessUserBan(Base):
    __tablename__ = "admin_access_user_ban"

    ban_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    user_uid: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    scope: Mapped[str] = mapped_column(String(32), nullable=False, default="AGENT_PRODUCT")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    linked_pause: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
