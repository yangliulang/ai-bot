"""Purge auto-generated ``pack_draft_*`` prompt pack rows (editor fork noise)."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

PACK_DRAFT_ID_PREFIX = "pack_draft_"


async def purge_pack_draft_prompt_packs(session: AsyncSession) -> int:
    """Delete ``pack_draft_%`` packs and their version events. Returns deleted pack count."""
    pat = f"{PACK_DRAFT_ID_PREFIX}%"
    await session.execute(
        text(
            """
            DELETE FROM admin_prompt_pack_version_event
            WHERE prompt_pack_id LIKE :pat
            """
        ),
        {"pat": pat},
    )
    res = await session.execute(
        text(
            """
            DELETE FROM admin_prompt_pack
            WHERE prompt_pack_id LIKE :pat
            """
        ),
        {"pat": pat},
    )
    await session.flush()
    return int(res.rowcount or 0)
