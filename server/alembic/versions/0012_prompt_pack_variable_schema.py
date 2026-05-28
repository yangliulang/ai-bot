"""admin_prompt_pack — variable_schema_json (§8 AC-09f).

Revision ID: 0012_prompt_pack_variable_schema
Revises: 0011_exec_prompt_meta
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0012_prompt_pack_variable_schema"
down_revision: str | Sequence[str] | None = "0011_exec_prompt_meta"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "admin_prompt_pack",
        sa.Column("variable_schema_json", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("admin_prompt_pack", "variable_schema_json")
