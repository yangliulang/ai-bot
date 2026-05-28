"""agent_instance.activation_welcome_sent_at (telegram welcome idempotency).

Revision ID: 0028_agent_instance_activation_welcome
Revises: 0027_agent_instance_overrides
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0028_agent_instance_activation_welcome"
down_revision: str | Sequence[str] | None = "0027_agent_instance_overrides"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "agent_instance",
        sa.Column("activation_welcome_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("agent_instance", "activation_welcome_sent_at")
