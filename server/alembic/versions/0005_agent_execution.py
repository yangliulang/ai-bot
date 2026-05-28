"""agent_execution — persisted executionId for billing / audit (replaces in-memory scaffold).

Revision ID: 0005_exec
Revises: 0004_aisettings
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_exec"
down_revision: str | Sequence[str] | None = "0004_aisettings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_execution",
        sa.Column("execution_id", sa.String(length=80), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("scenario_id", sa.String(length=128), nullable=True),
        sa.Column("channel", sa.String(length=32), nullable=True),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("idempotency_key", sa.String(length=256), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
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
        sa.PrimaryKeyConstraint("execution_id"),
    )
    op.create_index(op.f("ix_agent_execution_user_id"), "agent_execution", ["user_id"], unique=False)
    op.create_index(op.f("ix_agent_execution_state"), "agent_execution", ["state"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_execution_state"), table_name="agent_execution")
    op.drop_index(op.f("ix_agent_execution_user_id"), table_name="agent_execution")
    op.drop_table("agent_execution")
