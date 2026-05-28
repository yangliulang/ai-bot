"""Admin access-control API + evaluate integration (FR-MC601–607)."""

from __future__ import annotations

from pathlib import Path

import pytest
from chainup_agent.core.config import reset_settings_cache
from chainup_agent.infrastructure.persistence import base as persistence_base
from chainup_agent.infrastructure.persistence.models import (
    AdminAccessMembershipPolicy,
    AdminAccessUserBan,
    Base,
)
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_access_whitelist_roundtrip(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "ac_whitelist.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()

    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    created = await http_client.post(
        "/api/v1/admin/access-control/whitelist",
        json={"listId": "rollout", "userUid": "4242", "note": "u"},
    )
    assert created.status_code == 201
    eid = created.json()["entryId"]
    assert created.json()["userUid"] == "4242"

    listed = await http_client.get(
        "/api/v1/admin/access-control/whitelist",
        params={"listId": "rollout"},
    )
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    dup = await http_client.post(
        "/api/v1/admin/access-control/whitelist",
        json={"listId": "rollout", "userUid": "4242"},
    )
    assert dup.status_code == 409
    assert dup.json()["code"] == "AGENT_ADMIN_ACCESS_WHITELIST_DUPLICATE"

    deleted = await http_client.delete(f"/api/v1/admin/access-control/whitelist/{eid}")
    assert deleted.status_code == 204

    missing = await http_client.delete("/api/v1/admin/access-control/whitelist/wle_nonexistent")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_access_evaluate_rollout_enforced_blocks_without_whitelist(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "ac_rollout.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()

    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = persistence_base.get_session_factory()
    async with factory() as session:
        session.add(
            AdminAccessMembershipPolicy(
                id=1,
                min_vip_tier=0,
                enforce_rollout_whitelist=True,
            ),
        )
        await session.commit()

    r = await http_client.post(
        "/api/v1/agent/access/evaluate",
        json={"userId": "100100100", "channel": "telegram"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["allowed"] is False
    assert body["code"] == "AGENT_ROLLOUT_BLOCKED"


@pytest.mark.asyncio
async def test_access_evaluate_rollout_whitelist_allows_user(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "ac_rollout2.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()

    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    ins = await http_client.post(
        "/api/v1/admin/access-control/whitelist",
        json={"listId": "rollout", "userUid": "200200200"},
    )
    assert ins.status_code == 201

    factory = persistence_base.get_session_factory()
    async with factory() as session:
        session.add(
            AdminAccessMembershipPolicy(
                id=1,
                min_vip_tier=0,
                enforce_rollout_whitelist=True,
            ),
        )
        await session.commit()

    r = await http_client.post(
        "/api/v1/agent/access/evaluate",
        json={"userId": "200200200", "channel": "telegram"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["allowed"] is False
    assert body["code"] == "AGENT_SUBACCOUNT_REQUIRED"


@pytest.mark.asyncio
async def test_access_evaluate_active_ban_blocks(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "ac_ban.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()

    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = persistence_base.get_session_factory()
    async with factory() as session:
        session.add(
            AdminAccessUserBan(
                ban_id="ban_t1",
                user_uid="300300300",
                reason_code="OPS_MANUAL",
                scope="AGENT_PRODUCT",
                linked_pause=False,
                created_by="test",
            ),
        )
        await session.commit()

    r = await http_client.post(
        "/api/v1/agent/access/evaluate",
        json={"userId": "300300300", "channel": "telegram"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["allowed"] is False
    assert body["code"] == "AGENT_USER_BLOCKED"


@pytest.mark.asyncio
async def test_access_evaluate_ban_compliance_maps_envelope(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "ac_ban2.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    reset_settings_cache()

    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = persistence_base.get_session_factory()
    async with factory() as session:
        session.add(
            AdminAccessUserBan(
                ban_id="ban_t2",
                user_uid="400400400",
                reason_code="COMPLIANCE_ABUSE",
                scope="AGENT_PRODUCT",
                linked_pause=False,
                created_by="test",
            ),
        )
        await session.commit()

    r = await http_client.post(
        "/api/v1/agent/access/evaluate",
        json={"userId": "400400400", "channel": "telegram"},
    )
    assert r.status_code == 200
    assert r.json()["code"] == "AGENT_COMPLIANCE_RESTRICTED"


@pytest.mark.asyncio
async def test_access_evaluate_ban_overrides_env_allowlist(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "ac_ban3.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "500500500")
    reset_settings_cache()

    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = persistence_base.get_session_factory()
    async with factory() as session:
        session.add(
            AdminAccessUserBan(
                ban_id="ban_t3",
                user_uid="500500500",
                reason_code="OPS_MANUAL",
                scope="AGENT_PRODUCT",
                linked_pause=False,
                created_by="test",
            ),
        )
        await session.commit()

    r = await http_client.post(
        "/api/v1/agent/access/evaluate",
        json={"userId": "500500500", "channel": "telegram"},
    )
    assert r.status_code == 200
    assert r.json()["allowed"] is False
    assert r.json()["code"] == "AGENT_USER_BLOCKED"
