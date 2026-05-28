"""Singleton row for AGENT_MIN_VIP_TIER operator edit (FR-MC607). Runtime VIP compare TBD exchange."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, SmallInteger, func
from sqlalchemy.orm import Mapped, mapped_column

from chainup_agent.infrastructure.persistence.models.base import Base


class AdminAccessMembershipPolicy(Base):
    __tablename__ = "admin_access_membership_policy"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, default=1)
    min_vip_tier: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    enforce_rollout_whitelist: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
