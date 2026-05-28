"""Admin safety intercept log for prompt publish blocked etc.

Revision ID: 0021_admin_safety_intercept_log
Revises: 0020_admin_confirmation_rules
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0021_admin_safety_intercept_log"
down_revision: str | Sequence[str] | None = "0020_admin_confirmation_rules"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admin_safety_intercept_log",
        sa.Column("intercept_id", sa.String(length=48), primary_key=True, nullable=False),
        sa.Column("category", sa.String(length=16), nullable=False),
        sa.Column("scenario_label", sa.String(length=256), nullable=False),
        sa.Column("kind_label", sa.String(length=128), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("subject", sa.String(length=256), nullable=True),
        sa.Column("matched_rule_id", sa.String(length=64), nullable=True),
        sa.Column("execution_id", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_admin_safety_intercept_log_category",
        "admin_safety_intercept_log",
        ["category"],
    )
    op.create_index(
        "ix_admin_safety_intercept_log_created_at",
        "admin_safety_intercept_log",
        ["created_at"],
    )
    op.create_index(
        "ix_admin_safety_intercept_log_execution_id",
        "admin_safety_intercept_log",
        ["execution_id"],
    )


def downgrade() -> None:
    op.drop_table("admin_safety_intercept_log")
