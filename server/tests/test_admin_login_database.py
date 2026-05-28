from pathlib import Path

import pytest
from chainup_agent.core.config import reset_settings_cache
from chainup_agent.infrastructure.persistence import base as persistence_base
from chainup_agent.infrastructure.persistence.admin_user_password import hash_password
from chainup_agent.infrastructure.persistence.models import AdminConsoleUser, Base
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_login_database_mode_success(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "login.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE", "database")
    monkeypatch.delenv("CHAINUP_AGENT_ADMIN_PANEL_USERNAME", raising=False)
    monkeypatch.delenv("CHAINUP_AGENT_ADMIN_PANEL_PASSWORD", raising=False)
    reset_settings_cache()

    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = persistence_base.get_session_factory()
    async with factory() as session:
        session.add(
            AdminConsoleUser(
                username="dbuser",
                password_hash=hash_password("secret"),
                is_active=True,
            ),
        )
        await session.commit()

    r = await http_client.post(
        "/api/auth/login",
        json={"username": "dbuser", "password": "secret"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == "dbuser"
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 10


@pytest.mark.asyncio
async def test_admin_login_database_mode_wrong_password(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "login2.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE", "database")
    reset_settings_cache()

    engine = persistence_base.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = persistence_base.get_session_factory()
    async with factory() as session:
        session.add(
            AdminConsoleUser(
                username="ops",
                password_hash=hash_password("secret"),
                is_active=True,
            ),
        )
        await session.commit()

    r = await http_client.post(
        "/api/auth/login",
        json={"username": "ops", "password": "wrong"},
    )
    assert r.status_code == 401
    assert r.json()["code"] == "ADMIN_CONSOLE_AUTH_INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_admin_login_env_mode_skips_db_session(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """env 模式不打开 DB 会话，未建表亦可登录。"""
    db_path = tmp_path / "unused.sqlite3"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE", "env")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_PANEL_USERNAME", "u")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_PANEL_PASSWORD", "p")
    reset_settings_cache()

    r = await http_client.post("/api/auth/login", json={"username": "u", "password": "p"})
    assert r.status_code == 200
