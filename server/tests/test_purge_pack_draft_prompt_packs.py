"""Purge ``pack_draft_*`` editor noise."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from chainup_agent.application.prompt_pack_draft_cleanup import purge_pack_draft_prompt_packs
from chainup_agent.infrastructure.persistence.base import get_session_factory
from chainup_agent.infrastructure.persistence.models.admin_prompt_pack import AdminPromptPack
from tests.test_api import _init_schema_sqlite


@pytest.mark.asyncio
async def test_purge_pack_draft_removes_fork_chain(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    factory = get_session_factory()
    async with factory() as session:
        session.add(
            AdminPromptPack(
                prompt_pack_id="pack_draft_testdeadbeef",
                prompt_pack_type="SYSTEM",
                scenario_id="agent.runtime.platform_system",
                lifecycle="DRAFT",
                prompt_pack_version="1",
                etag='W/"x"',
                messages_json='[{"role":"system","content":"x"}]',
            )
        )
        session.add(
            AdminPromptPack(
                prompt_pack_id="pack_draft_testdeadbeef_fork_abcd1234",
                prompt_pack_type="SYSTEM",
                scenario_id=None,
                lifecycle="LOCKED",
                prompt_pack_version="1",
                etag='W/"y"',
                messages_json='[{"role":"system","content":"y"}]',
            )
        )
        session.add(
            AdminPromptPack(
                prompt_pack_id="pp-system-core",
                prompt_pack_type="SYSTEM",
                scenario_id="agent.runtime.platform_system",
                lifecycle="PUBLISHED",
                prompt_pack_version="1",
                etag='W/"z"',
                messages_json='[{"role":"system","content":"z"}]',
            )
        )
        await session.commit()

    async with factory() as session:
        n = await purge_pack_draft_prompt_packs(session)
        await session.commit()
    assert n == 2

    async with factory() as session:
        left = (
            await session.execute(
                select(AdminPromptPack.prompt_pack_id).where(
                    AdminPromptPack.prompt_pack_id.like("pack_draft_%")
                )
            )
        ).all()
        assert left == []
        assert (
            await session.execute(
                select(AdminPromptPack.prompt_pack_id).where(
                    AdminPromptPack.prompt_pack_id == "pp-system-core"
                )
            )
        ).scalar_one_or_none() == "pp-system-core"
