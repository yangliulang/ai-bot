"""Agent instance persisted runtime_state (R01–R05).

Revision ID: 0009_agent_instance_runtime
Revises: 0008_intent_nlu_read_market_expand
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_agent_instance_runtime"
down_revision: str | Sequence[str] | None = "0008_intent_nlu_read_market_expand"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "agent_instance",
        sa.Column(
            "runtime_state",
            sa.String(length=16),
            nullable=False,
            server_default="RUNNING",
        ),
    )


def downgrade() -> None:
    op.drop_column("agent_instance", "runtime_state")
