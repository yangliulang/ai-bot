"""Seed 16 governance ``pp-*`` prompt packs (product-doc promptBodyTemplates).

Revision ID: 0030_governance_prompt_pack_seed
Revises: 0029_skill_operation_spec_publish
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0030_governance_prompt_pack_seed"
down_revision: str | Sequence[str] | None = "0029_skill_operation_spec_publish"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    from chainup_agent.data.prompt_governance_catalog import all_governance_pack_seeds
    from chainup_agent.data.prompt_governance_seed import pack_messages_and_schema

    bind = op.get_bind()

    for seed in all_governance_pack_seeds():
        messages_json, etag, variable_schema_json = pack_messages_and_schema(seed)
        res = bind.execute(
            sa.text(
                """
                UPDATE admin_prompt_pack
                SET prompt_pack_type = :ptype,
                    scenario_id = :sid,
                    lifecycle = 'PUBLISHED',
                    prompt_pack_version = '1',
                    etag = :etag,
                    messages_json = :messages,
                    variable_schema_json = :vschema,
                    placeholder_denylist_revision = 'pdr-2026-05-07',
                    safety_phrase_blocklist_revision = 'spb-2026-05-05',
                    updated_at = CURRENT_TIMESTAMP
                WHERE prompt_pack_id = :pid
                """
            ),
            {
                "pid": seed.prompt_pack_id,
                "ptype": seed.prompt_pack_type,
                "sid": seed.scenario_id,
                "etag": etag,
                "messages": messages_json,
                "vschema": variable_schema_json,
            },
        )
        if getattr(res, "rowcount", None) == 0:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO admin_prompt_pack (
                        prompt_pack_id, prompt_pack_type, scenario_id, lifecycle,
                        prompt_pack_version, etag, messages_json,
                        placeholder_denylist_revision, safety_phrase_blocklist_revision,
                        variable_schema_json, row_version
                    ) VALUES (
                        :pid, :ptype, :sid, 'PUBLISHED',
                        '1', :etag, :messages,
                        'pdr-2026-05-07', 'spb-2026-05-05',
                        :vschema, 1
                    )
                    """
                ),
                {
                    "pid": seed.prompt_pack_id,
                    "ptype": seed.prompt_pack_type,
                    "sid": seed.scenario_id,
                    "etag": etag,
                    "messages": messages_json,
                    "vschema": variable_schema_json,
                },
            )

    from chainup_agent.data.prompt_governance_catalog import LEGACY_PACK_IDS_SUPERSEDED

    for legacy_id in sorted(LEGACY_PACK_IDS_SUPERSEDED):
        bind.execute(
            sa.text(
                """
                UPDATE admin_prompt_pack
                SET lifecycle = 'DEPRECATED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE prompt_pack_id = :pid
                  AND lifecycle = 'PUBLISHED'
                """
            ),
            {"pid": legacy_id},
        )


def downgrade() -> None:
    from chainup_agent.data.prompt_governance_catalog import all_governance_pack_seeds

    bind = op.get_bind()
    for seed in all_governance_pack_seeds():
        bind.execute(
            sa.text("DELETE FROM admin_prompt_pack WHERE prompt_pack_id = :pid"),
            {"pid": seed.prompt_pack_id},
        )
