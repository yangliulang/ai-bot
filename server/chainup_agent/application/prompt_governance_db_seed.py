"""Upsert governance ``pp-*`` rows (shared by Alembic 0030 and pytest)."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.data.prompt_governance_catalog import (
    LEGACY_PACK_IDS_SUPERSEDED,
    all_governance_pack_seeds,
)
from chainup_agent.data.prompt_governance_seed import pack_messages_and_schema


async def seed_governance_prompt_packs(session: AsyncSession) -> None:
    for seed in all_governance_pack_seeds():
        messages_json, etag, variable_schema_json = pack_messages_and_schema(seed)
        res = await session.execute(
            text(
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
        if res.rowcount == 0:
            await session.execute(
                text(
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

    for legacy_id in sorted(LEGACY_PACK_IDS_SUPERSEDED):
        await session.execute(
            text(
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
    await session.flush()
