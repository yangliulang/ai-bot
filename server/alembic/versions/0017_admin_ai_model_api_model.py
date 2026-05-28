"""admin_ai_model.api_model — upstream wire-id vs catalog model_id.

Revision ID: 0017_admin_ai_model_api_model
Revises: 0016_read_account_balance_wealth_trading_prompt_seed
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0017_admin_ai_model_api_model"
down_revision: str | Sequence[str] | None = "0016_read_account_balance_wealth_trading_prompt_seed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "admin_ai_model",
        sa.Column("api_model", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("admin_ai_model", "api_model")
