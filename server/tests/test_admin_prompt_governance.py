"""Prompt governance: create draft, publish, LOCKED patch guard, PM-C04 size (Phase1)."""

from __future__ import annotations

from pathlib import Path

import pytest
from chainup_agent.core.config import reset_settings_cache
from chainup_agent.infrastructure.persistence import base as persistence_base
from chainup_agent.infrastructure.persistence.models import AdminPromptPack, Base
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_draft_and_publish_trading_pack(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_gov.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()
    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    c = await http_client.post(
        "/api/v1/admin/prompt-packs",
        json={
            "promptPackType": "TRADING",
            "scenarioId": "read.market.ticker",
            "promptPackId": "pack_test_gov_ticker",
        },
    )
    assert c.status_code == 201
    assert c.json()["lifecycle"] == "DRAFT"

    pub = await http_client.post("/api/v1/admin/prompt-packs/pack_test_gov_ticker/publish")
    assert pub.status_code == 200
    body = pub.json()
    assert body["lifecycle"] == "PUBLISHED"
    assert body["promptPackVersion"] == "2"

    eff = await http_client.get(
        "/api/v1/internal/prompts/effective",
        params={"scenarioId": "read.market.ticker"},
    )
    assert eff.status_code == 200
    assert eff.json()["promptPackVersion"] == "2"


@pytest.mark.asyncio
async def test_create_draft_requires_scenario_for_trading(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_create_req.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()
    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    bad = await http_client.post(
        "/api/v1/admin/prompt-packs",
        json={"promptPackType": "TRADING"},
    )
    assert bad.status_code == 422
    assert bad.json()["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_create_draft_from_template_source(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_create_tpl.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()
    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    seed = await http_client.post(
        "/api/v1/admin/prompt-packs",
        json={
            "promptPackType": "TRADING",
            "scenarioId": "read.market.ticker",
            "promptPackId": "pack_tpl_seed",
        },
    )
    assert seed.status_code == 201
    await http_client.patch(
        "/api/v1/admin/prompt-packs/pack_tpl_seed",
        json={
            "messages": [{"role": "system", "content": "template body {{effective_locale}}"}],
            "variableSchema": {"effective_locale": {"type": "string"}},
        },
    )

    cloned = await http_client.post(
        "/api/v1/admin/prompt-packs",
        json={
            "promptPackType": "TRADING",
            "scenarioId": "read.market.depth",
            "sourcePromptPackId": "pack_tpl_seed",
        },
    )
    assert cloned.status_code == 201
    body = cloned.json()
    assert body["lifecycle"] == "DRAFT"
    assert body["scenarioId"] == "read.market.depth"
    assert body["promptPackId"] != "pack_tpl_seed"
    assert "template body" in (body.get("bodyMarkdown") or "")
    assert body["title"] == "盘口深度（草稿）"


@pytest.mark.asyncio
async def test_prompt_pack_summary_includes_display_title(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_title.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()
    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = persistence_base.get_session_factory()
    async with factory() as session:
        session.add(
            AdminPromptPack(
                prompt_pack_id="pack_platform_system_v1",
                prompt_pack_type="SYSTEM",
                scenario_id="agent.runtime.platform_system",
                lifecycle="PUBLISHED",
                prompt_pack_version="1",
                etag='W/"x"',
                messages_json='[{"role":"system","content":"x"}]',
            ),
        )
        await session.commit()

    created = await http_client.post(
        "/api/v1/admin/prompt-packs",
        json={"promptPackType": "TRADING", "scenarioId": "chat.faq"},
    )
    assert created.status_code == 201
    assert created.json()["title"] == "纯对话问答（草稿）"

    listing = await http_client.get("/api/v1/admin/prompt-packs")
    assert listing.status_code == 200
    by_id = {r["promptPackId"]: r for r in listing.json()["items"]}
    assert by_id["pack_platform_system_v1"]["title"] == "平台 SYSTEM 内核"
    draft_id = created.json()["promptPackId"]
    assert "草稿" in by_id[draft_id]["title"]


@pytest.mark.asyncio
async def test_create_draft_rejects_unknown_scenario(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_create_bad_sid.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()
    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    bad = await http_client.post(
        "/api/v1/admin/prompt-packs",
        json={
            "promptPackType": "ANALYSIS",
            "scenarioId": "not.in.registry",
        },
    )
    assert bad.status_code == 422
    assert bad.json()["code"] == "PROMPT_SCENARIO_INVALID"


@pytest.mark.asyncio
async def test_publish_rejects_unknown_scenario(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_gov2.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()
    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = persistence_base.get_session_factory()
    async with factory() as session:
        session.add(
            AdminPromptPack(
                prompt_pack_id="pack_bad_sid",
                prompt_pack_type="ANALYSIS",
                scenario_id="not.in.registry",
                lifecycle="DRAFT",
                prompt_pack_version="1",
                etag='W/"x"',
                messages_json='[{"role":"system","content":"x"}]',
            ),
        )
        await session.commit()

    pub = await http_client.post("/api/v1/admin/prompt-packs/pack_bad_sid/publish")
    assert pub.status_code == 422
    assert pub.json()["code"] == "PROMPT_SCENARIO_INVALID"


@pytest.mark.asyncio
async def test_patch_rejects_locked_pack(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_gov3.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()
    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = persistence_base.get_session_factory()
    async with factory() as session:
        session.add(
            AdminPromptPack(
                prompt_pack_id="pack_locked_test",
                prompt_pack_type="SYSTEM",
                scenario_id="x",
                lifecycle="LOCKED",
                prompt_pack_version="1",
                etag='W/"x"',
                messages_json="[]",
            ),
        )
        await session.commit()

    p = await http_client.patch(
        "/api/v1/admin/prompt-packs/pack_locked_test",
        json={"messages": [{"role": "system", "content": "nope"}]},
    )
    assert p.status_code == 409
    assert p.json()["code"] == "PROMPT_PACK_LOCKED"


@pytest.mark.asyncio
async def test_patch_variable_schema_rejects_unknown_placeholder(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_gov_schema.sqlite3"
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
            "promptPackId": "pack_schema_test",
        },
    )
    bad = await http_client.patch(
        "/api/v1/admin/prompt-packs/pack_schema_test",
        json={
            "messages": [{"role": "system", "content": "{{only_schema}}"}],
            "variableSchema": {"other": {}},
        },
    )
    assert bad.status_code == 422
    assert bad.json()["code"] == "PROMPT_VALIDATION_FAILED"

    ok = await http_client.patch(
        "/api/v1/admin/prompt-packs/pack_schema_test",
        json={
            "messages": [{"role": "system", "content": "{{only_schema}}"}],
            "variableSchema": {"only_schema": {"type": "string"}},
        },
    )
    assert ok.status_code == 200


@pytest.mark.asyncio
async def test_patch_rejects_placeholder_secret_slug(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "pm_gov4.sqlite3"
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
            "promptPackId": "pack_bad_ph",
        },
    )
    p = await http_client.patch(
        "/api/v1/admin/prompt-packs/pack_bad_ph",
        json={
            "messages": [
                {"role": "system", "content": "do not {{ SECRET_KEY }} here"},
            ],
        },
    )
    assert p.status_code == 422
    assert p.json()["code"] == "PROMPT_VALIDATION_FAILED"
