"""Admin safety intercept audit rows (prompt publish blocked, etc.)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from chainup_agent.infrastructure.persistence.models.base import Base


class AdminSafetyInterceptLog(Base):
    __tablename__ = "admin_safety_intercept_log"

    intercept_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    category: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    scenario_label: Mapped[str] = mapped_column(String(256), nullable=False)
    kind_label: Mapped[str] = mapped_column(String(128), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str | None] = mapped_column(String(256), nullable=True)
    matched_rule_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    execution_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
