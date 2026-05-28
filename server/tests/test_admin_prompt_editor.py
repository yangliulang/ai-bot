"""Prompt editor governance: fork, versions, rollback, If-Match (Phase1)."""

from __future__ import annotations

from pathlib import Path

import pytest
from chainup_agent.core.config import reset_settings_cache
from chainup_agent.infrastructure.persistence import base as persistence_base
from chainup_agent.infrastructure.persistence.models import AdminPromptPack, Base
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_fork_locked_system_creates_editable_draft(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_fork.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()
    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = persistence_base.get_session_factory()
    async with factory() as session:
        session.add(
            AdminPromptPack(
                prompt_pack_id="pack_locked_sys",
                prompt_pack_type="SYSTEM",
                scenario_id="agent.runtime.platform_system",
                lifecycle="LOCKED",
                prompt_pack_version="2",
                etag='W/"locked"',
                messages_json='[{"role":"system","content":"locked body v2"}]',
            ),
        )
        await session.commit()

    fork = await http_client.post(
        "/api/v1/admin/prompt-packs/pack_locked_sys/fork",
        json={"promptPackId": "pack_locked_sys_v3_draft"},
    )
    assert fork.status_code == 201
    body = fork.json()
    assert body["lifecycle"] == "DRAFT"
    assert body["promptPackId"] == "pack_locked_sys_v3_draft"
    assert body["bodyMarkdown"] == "locked body v2"

    patch = await http_client.patch(
        "/api/v1/admin/prompt-packs/pack_locked_sys_v3_draft",
        json={"messages": [{"role": "system", "content": "edited draft"}]},
    )
    assert patch.status_code == 200
    assert patch.json()["messages"][0]["content"] == "edited draft"


@pytest.mark.asyncio
async def test_publish_records_version_history(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_versions.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()
    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await http_client.post(
        "/api/v1/admin/prompt-packs",
        json={
            "promptPackType": "TRADING",
            "scenarioId": "read.market.ticker",
            "promptPackId": "pack_ver_hist",
        },
    )
    pub = await http_client.post("/api/v1/admin/prompt-packs/pack_ver_hist/publish")
    assert pub.status_code == 200

    versions = await http_client.get("/api/v1/admin/prompt-packs/pack_ver_hist/versions")
    assert versions.status_code == 200
    items = versions.json()["items"]
    assert len(items) >= 1
    assert items[0]["event"] == "PUBLISH"
    assert items[0]["promptPackVersion"] == "2"


@pytest.mark.asyncio
async def test_rollback_restores_snapshot(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_rollback.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()
    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await http_client.post(
        "/api/v1/admin/prompt-packs",
        json={
            "promptPackType": "TRADING",
            "scenarioId": "read.market.ticker",
            "promptPackId": "pack_rb",
        },
    )
    await http_client.patch(
        "/api/v1/admin/prompt-packs/pack_rb",
        json={"messages": [{"role": "system", "content": "version one body"}]},
    )
    pub1 = await http_client.post("/api/v1/admin/prompt-packs/pack_rb/publish")
    assert pub1.status_code == 200
    v1 = pub1.json()["promptPackVersion"]

    await http_client.patch(
        "/api/v1/admin/prompt-packs/pack_rb",
        json={"messages": [{"role": "system", "content": "version two body"}]},
    )

    rb = await http_client.post(
        "/api/v1/admin/prompt-packs/pack_rb/rollback",
        json={"promptPackVersion": v1},
    )
    assert rb.status_code == 200
    detail = await http_client.get("/api/v1/admin/prompt-packs/pack_rb")
    assert detail.json()["bodyMarkdown"] == "version one body"


@pytest.mark.asyncio
async def test_patch_if_match_conflict(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_ifmatch.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()
    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await http_client.post(
        "/api/v1/admin/prompt-packs",
        json={
            "promptPackType": "TRADING",
            "scenarioId": "read.market.ticker",
            "promptPackId": "pack_ifmatch",
        },
    )
    get0 = await http_client.get("/api/v1/admin/prompt-packs/pack_ifmatch")
    rv = str(get0.json()["rowVersion"])

    conflict = await http_client.patch(
        "/api/v1/admin/prompt-packs/pack_ifmatch",
        json={"messages": [{"role": "system", "content": "x"}]},
        headers={"If-Match": '"999"'},
    )
    assert conflict.status_code == 409
    assert conflict.json()["code"] == "AGENT_PROMPT_PACK_VERSION_CONFLICT"

    ok = await http_client.patch(
        "/api/v1/admin/prompt-packs/pack_ifmatch",
        json={"messages": [{"role": "system", "content": "x"}]},
        headers={"If-Match": f'"{rv}"'},
    )
    assert ok.status_code == 200
