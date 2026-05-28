"""Admin AI Settings persistence — providers, models, JSON documents (gateway/health)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chainup_agent.infrastructure.persistence.models.base import Base


class AdminAiProvider(Base):
    __tablename__ = "admin_ai_provider"

    provider_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    base_url: Mapped[str] = mapped_column(String(512), nullable=False)
    secret_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    row_version: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.CURRENT_TIMESTAMP(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.CURRENT_TIMESTAMP(),
        onupdate=func.CURRENT_TIMESTAMP(),
        nullable=False,
    )

    models: Mapped[list["AdminAiModel"]] = relationship(
        back_populates="provider",
        cascade="all, delete-orphan",
    )


class AdminAiModel(Base):
    __tablename__ = "admin_ai_model"

    model_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    provider_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("admin_ai_provider.provider_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # OpenAI-compat / Ark `model` field sent upstream; omit to use catalog `model_id`.
    api_model: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="enabled")
    context_window_tokens: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    row_version: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="1")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.CURRENT_TIMESTAMP(),
        onupdate=func.CURRENT_TIMESTAMP(),
        nullable=False,
    )

    provider: Mapped["AdminAiProvider"] = relationship(back_populates="models")


class AdminAiDocument(Base):
    __tablename__ = "admin_ai_document"

    doc_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    payload_json: Mapped[str] = mapped_column(String(length=65_536), nullable=False)
    row_version: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="1")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.CURRENT_TIMESTAMP(),
        onupdate=func.CURRENT_TIMESTAMP(),
        nullable=False,
    )
