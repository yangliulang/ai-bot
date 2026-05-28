"""Remove auto-generated ``pack_draft_*`` / ``*_fork_*`` editor noise (post ``pp-*`` governance seed).

Revision ID: 0031_purge_pack_draft_prompt_packs
Revises: 0030_governance_prompt_pack_seed
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0031_purge_pack_draft_prompt_packs"
down_revision: str | Sequence[str] | None = "0030_governance_prompt_pack_seed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Auto IDs from ``admin_prompt_packs`` fork/draft helpers — not governance ``pp-*``.
_DRAFT_ID_PREFIX = "pack_draft_"


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            DELETE FROM admin_prompt_pack_version_event
            WHERE prompt_pack_id LIKE :pat
            """
        ),
        {"pat": f"{_DRAFT_ID_PREFIX}%"},
    )
    bind.execute(
        sa.text(
            """
            DELETE FROM admin_prompt_pack
            WHERE prompt_pack_id LIKE :pat
            """
        ),
        {"pat": f"{_DRAFT_ID_PREFIX}%"},
    )


def downgrade() -> None:
    """Purged rows are not restored."""
