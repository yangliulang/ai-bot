"""telegram_agent_trading_binding

Revision ID: 0002_tatb
Revises: 0001_acu
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_tatb"
down_revision: str | Sequence[str] | None = "0001_acu"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "telegram_agent_trading_binding",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("tg_username", sa.String(length=128), nullable=True),
        sa.Column("tg_first_name", sa.String(length=256), nullable=True),
        sa.Column("tg_last_name", sa.String(length=256), nullable=True),
        sa.Column("tg_lang", sa.String(length=32), nullable=True),
        sa.Column("openapi_base_url", sa.Text(), nullable=False),
        sa.Column("trading_credentials_sealed", sa.LargeBinary(), nullable=False),
        sa.Column("idempotency_key_last", sa.String(length=128), nullable=True),
        sa.Column("deeplink_token_last", sa.String(length=512), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_telegram_agent_trading_binding_telegram_user_id"),
        "telegram_agent_trading_binding",
        ["telegram_user_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_telegram_agent_trading_binding_telegram_user_id"),
        table_name="telegram_agent_trading_binding",
    )
    op.drop_table("telegram_agent_trading_binding")
