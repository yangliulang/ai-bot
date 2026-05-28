"""agent_execution — prompt pack version + resolved binding JSON (observability AC-09j/k).

Revision ID: 0011_exec_prompt_meta
Revises: 0010_admin_access_control
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011_exec_prompt_meta"
down_revision: str | Sequence[str] | None = "0010_admin_access_control"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "agent_execution",
        sa.Column("prompt_pack_version", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "agent_execution",
        sa.Column("resolved_prompt_binding", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("agent_execution", "resolved_prompt_binding")
    op.drop_column("agent_execution", "prompt_pack_version")
