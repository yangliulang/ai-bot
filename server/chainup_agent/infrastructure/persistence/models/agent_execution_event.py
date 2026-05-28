"""Append-only timeline rows for Admin observability FR-MC801 (coarse Phase1)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from chainup_agent.infrastructure.persistence.models.base import Base


class AgentExecutionEvent(Base):
    """
    Structured events keyed by ``execution_id`` for operator 协查 / timeline.

    Event names align with product ``observability/overview.md`` §2 / §2.1
    (e.g. ``agent.execution.step``, ``trading.exchange_private``).
    """

    __tablename__ = "agent_execution_event"
    __table_args__ = (UniqueConstraint("execution_id", "seq", name="uq_agent_execution_event_exec_seq"),)

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    execution_id: Mapped[str] = mapped_column(
        String(80),
        ForeignKey("agent_execution.execution_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(96), nullable=False)
    step_kind: Mapped[str | None] = mapped_column(String(64), nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(24), nullable=True)
    payload_json: Mapped[str] = mapped_column(Text(), nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
