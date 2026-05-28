"""agent_instance — Phase1 Telegram-scoped instance row on binding confirm.

Revision ID: 0003_ai
Revises: 0002_tatb
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_ai"
down_revision: str | Sequence[str] | None = "0002_tatb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_instance",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("instance_id", sa.String(length=64), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("exchange_sub_account_user_id", sa.String(length=128), nullable=False),
        sa.Column("template_id", sa.String(length=64), nullable=False),
        sa.Column("template_version", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_instance_instance_id"), "agent_instance", ["instance_id"], unique=True)
    op.create_index(
        op.f("ix_agent_instance_telegram_user_id"),
        "agent_instance",
        ["telegram_user_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_instance_telegram_user_id"), table_name="agent_instance")
    op.drop_index(op.f("ix_agent_instance_instance_id"), table_name="agent_instance")
    op.drop_table("agent_instance")
