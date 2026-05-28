"""Admin access control: whitelist, user bans, min VIP policy (FR-MC602/603/607).

Revision ID: 0010_admin_access_control
Revises: 0009_agent_instance_runtime
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010_admin_access_control"
down_revision: str | Sequence[str] | None = "0009_agent_instance_runtime"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admin_access_whitelist_entry",
        sa.Column("entry_id", sa.String(length=40), primary_key=True, nullable=False),
        sa.Column("list_id", sa.String(length=64), nullable=False),
        sa.Column("user_uid", sa.String(length=64), nullable=False),
        sa.Column("user_id_masked", sa.String(length=128), nullable=False),
        sa.Column("note", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=True),
    )
    op.create_index(
        "ix_admin_access_whitelist_user_uid",
        "admin_access_whitelist_entry",
        ["user_uid"],
    )
    op.create_index(
        "ix_admin_access_whitelist_list_user",
        "admin_access_whitelist_entry",
        ["list_id", "user_uid"],
        unique=True,
    )

    op.create_table(
        "admin_access_user_ban",
        sa.Column("ban_id", sa.String(length=48), primary_key=True, nullable=False),
        sa.Column("user_uid", sa.String(length=64), nullable=False),
        sa.Column("reason_code", sa.String(length=64), nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False, server_default="AGENT_PRODUCT"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("linked_pause", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=True),
    )
    op.create_index("ix_admin_access_user_ban_user_uid", "admin_access_user_ban", ["user_uid"])

    op.create_table(
        "admin_access_membership_policy",
        sa.Column("id", sa.SmallInteger(), primary_key=True, nullable=False),
        sa.Column("min_vip_tier", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column(
            "enforce_rollout_whitelist",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.bulk_insert(
        sa.table(
            "admin_access_membership_policy",
            sa.column("id", sa.SmallInteger()),
            sa.column("min_vip_tier", sa.SmallInteger()),
            sa.column("enforce_rollout_whitelist", sa.Boolean()),
        ),
        [{"id": 1, "min_vip_tier": 0, "enforce_rollout_whitelist": False}],
    )


def downgrade() -> None:
    op.drop_table("admin_access_membership_policy")
    op.drop_index("ix_admin_access_user_ban_user_uid", table_name="admin_access_user_ban")
    op.drop_table("admin_access_user_ban")
    op.drop_index("ix_admin_access_whitelist_list_user", table_name="admin_access_whitelist_entry")
    op.drop_index("ix_admin_access_whitelist_user_uid", table_name="admin_access_whitelist_entry")
    op.drop_table("admin_access_whitelist_entry")
