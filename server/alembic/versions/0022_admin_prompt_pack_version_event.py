"""Prompt pack version event log + backfill seed snapshots.

Revision ID: 0022_admin_prompt_pack_version_event
Revises: 0021_admin_safety_intercept_log
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0022_admin_prompt_pack_version_event"
down_revision: str | Sequence[str] | None = "0021_admin_safety_intercept_log"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admin_prompt_pack_version_event",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("prompt_pack_id", sa.String(length=128), nullable=False),
        sa.Column("prompt_pack_version", sa.String(length=64), nullable=False),
        sa.Column("lifecycle", sa.String(length=32), nullable=False),
        sa.Column("event", sa.String(length=32), nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=True),
        sa.Column("summary", sa.String(length=512), nullable=True),
        sa.Column("messages_json", sa.Text(), nullable=False),
        sa.Column("variable_schema_json", sa.Text(), nullable=True),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_admin_prompt_pack_version_event_pack_id",
        "admin_prompt_pack_version_event",
        ["prompt_pack_id"],
    )

    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            """
            SELECT prompt_pack_id, prompt_pack_version, lifecycle, messages_json, variable_schema_json
            FROM admin_prompt_pack
            WHERE lifecycle IN ('PUBLISHED', 'LOCKED')
            """
        ),
    ).fetchall()
    for row in rows:
        bind.execute(
            sa.text(
                """
                INSERT INTO admin_prompt_pack_version_event (
                    prompt_pack_id, prompt_pack_version, lifecycle, event,
                    actor, summary, messages_json, variable_schema_json
                ) VALUES (
                    :pid, :ver, :lc, 'PUBLISH',
                    'migration-0022', 'Backfill from existing row',
                    :messages, :schema
                )
                """
            ),
            {
                "pid": row[0],
                "ver": row[1],
                "lc": row[2],
                "messages": row[3],
                "schema": row[4],
            },
        )


def downgrade() -> None:
    op.drop_index(
        "ix_admin_prompt_pack_version_event_pack_id",
        table_name="admin_prompt_pack_version_event",
    )
    op.drop_table("admin_prompt_pack_version_event")
