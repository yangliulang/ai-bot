"""Resolve published ``AdminPromptPack`` rows via governance ``pp-*`` catalog."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.data.prompt_governance_catalog import governance_pack_id_for_scenario
from chainup_agent.infrastructure.persistence.models.admin_prompt_pack import AdminPromptPack

import logging

logger = logging.getLogger(__name__)


async def get_published_pack_by_id(
    session: AsyncSession,
    *,
    prompt_pack_id: str,
) -> AdminPromptPack | None:
    pid = prompt_pack_id.strip()
    if not pid:
        return None
    row = await session.get(AdminPromptPack, pid)
    if row is None:
        return None
    if str(row.lifecycle or "").strip().upper() != "PUBLISHED":
        return None
    return row


async def get_published_governance_pack_for_scenario(
    session: AsyncSession,
    *,
    scenario_id: str,
) -> AdminPromptPack | None:
    """Prefer ``governance-map`` ``pp-*`` row when seeded and PUBLISHED."""
    pack_id = governance_pack_id_for_scenario(scenario_id)
    if not pack_id:
        return None
    return await get_published_pack_by_id(session, prompt_pack_id=pack_id)


async def get_published_pack_for_scenario_legacy(
    session: AsyncSession,
    *,
    scenario_id: str,
) -> AdminPromptPack | None:
    """Lookup by ``scenario_id`` column (pre-governance migrations)."""
    sid = scenario_id.strip()
    stmt = (
        select(AdminPromptPack)
        .where(
            AdminPromptPack.scenario_id == sid,
            AdminPromptPack.lifecycle == "PUBLISHED",
        )
        .limit(1)
    )
    try:
        return (await session.execute(stmt)).scalar_one_or_none()
    except (OperationalError, ProgrammingError) as exc:
        logger.info(
            "prompt_pack_query_skipped reason=%s scenario=%s",
            type(exc).__name__,
            sid[:80],
        )
        return None
