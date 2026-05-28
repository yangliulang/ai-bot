"""agent_execution_event — Admin timeline FR-MC801 (observability Phase1).

Revision ID: 0007_exec_event
Revises: 0006_pm_tg
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_exec_event"
down_revision: str | Sequence[str] | None = "0006_pm_tg"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_execution_event",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("execution_id", sa.String(length=80), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=96), nullable=False),
        sa.Column("step_kind", sa.String(length=64), nullable=True),
        sa.Column("outcome", sa.String(length=24), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(
            ["execution_id"],
            ["agent_execution.execution_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("execution_id", "seq", name="uq_agent_execution_event_exec_seq"),
    )
    op.create_index(op.f("ix_agent_execution_event_execution_id"), "agent_execution_event", ["execution_id"], unique=False)
    op.create_index(op.f("ix_agent_execution_event_user_id"), "agent_execution_event", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_execution_event_user_id"), table_name="agent_execution_event")
    op.drop_index(op.f("ix_agent_execution_event_execution_id"), table_name="agent_execution_event")
    op.drop_table("agent_execution_event")
