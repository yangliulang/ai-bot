"""agent_instance.instance_overrides_json (I05).

Revision ID: 0027_agent_instance_overrides
Revises: 0026_spot_amend_trading_prompt_seed
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0027_agent_instance_overrides"
down_revision: str | Sequence[str] | None = "0026_spot_amend_trading_prompt_seed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "agent_instance",
        sa.Column(
            "instance_overrides_json",
            sa.Text(),
            nullable=False,
            server_default="{}",
        ),
    )


def downgrade() -> None:
    op.drop_column("agent_instance", "instance_overrides_json")
