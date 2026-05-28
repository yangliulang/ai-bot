"""Skill operation spec — PUBLISHED snapshots for read_skill_operation_spec (FR-T11)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from chainup_agent.infrastructure.persistence.models.base import Base


class SkillOperationSpecVersion(Base):
    __tablename__ = "skill_operation_spec_version"

    skill_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    skill_spec_version: Mapped[str] = mapped_column(String(64), primary_key=True)
    lifecycle: Mapped[str] = mapped_column(String(16), nullable=False, default="PUBLISHED")
    body_markdown: Mapped[str] = mapped_column(Text(), nullable=False)
    spec_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    source_git_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    contract_complete: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)


class SkillOperationSpecPointer(Base):
    __tablename__ = "skill_operation_spec_pointer"

    skill_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    skill_spec_version: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
