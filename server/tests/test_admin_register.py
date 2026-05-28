"""Tests for POST /api/auth/register."""

import pytest
from chainup_agent.core.config import reset_settings_cache
from chainup_agent.infrastructure.persistence.base import dispose_engine
from chainup_agent.infrastructure.persistence.models import Base
from chainup_agent.main import app
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client_db_mode(monkeypatch: pytest.MonkeyPatch, tmp_path) -> AsyncClient:
    """Fresh sqlite file + database auth (no JWT for admin routes unless overridden)."""
    db_file = (tmp_path / "register_test.sqlite3").resolve()
    url = f"sqlite+aiosqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", url)
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE", "database")
    monkeypatch.delenv("CHAINUP_AGENT_ADMIN_PANEL_USERNAME", raising=False)
    monkeypatch.delenv("CHAINUP_AGENT_ADMIN_PANEL_PASSWORD", raising=False)
    monkeypatch.delenv("CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION", raising=False)
    reset_settings_cache()

    # create schema for this isolated path (outside conftest sync create_all target)
    from sqlalchemy import create_engine

    sync_engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()

    await dispose_engine()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    await dispose_engine()


@pytest.mark.asyncio
async def test_admin_register_requires_database_auth(
    monkeypatch: pytest.MonkeyPatch, tmp_path,
) -> None:
    db_file = (tmp_path / "r2.sqlite3").resolve()
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_file.as_posix()}")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE", "env")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_PANEL_USERNAME", "ops")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_PANEL_PASSWORD", "pw")
    reset_settings_cache()

    from sqlalchemy import create_engine

    sync_engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()

    await dispose_engine()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/auth/register",
            json={"username": "new", "password": "87654321"},
        )
        assert r.status_code == 503
        assert r.json()["code"] == "ADMIN_CONSOLE_REGISTRATION_REQUIRES_DATABASE_AUTH"
    await dispose_engine()


@pytest.mark.asyncio
async def test_admin_register_bootstrap_then_login(client_db_mode: AsyncClient) -> None:
    r = await client_db_mode.post(
        "/api/auth/register",
        json={"username": "alice", "password": "alicepw1"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == "alice"
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 10

    r2 = await client_db_mode.post(
        "/api/auth/login",
        json={"username": "alice", "password": "alicepw1"},
    )
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_admin_register_duplicate_username(client_db_mode: AsyncClient) -> None:
    r = await client_db_mode.post(
        "/api/auth/register",
        json={"username": "bob", "password": "longpass99"},
    )
    assert r.status_code == 200

    r2 = await client_db_mode.post(
        "/api/auth/register",
        json={"username": "bob", "password": "otherpass77"},
    )
    assert r2.status_code == 409
    assert r2.json()["code"] == "ADMIN_CONSOLE_USERNAME_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_admin_register_second_account_requires_open_registration(
    client_db_mode: AsyncClient,
) -> None:
    r = await client_db_mode.post(
        "/api/auth/register",
        json={"username": "first", "password": "password8x"},
    )
    assert r.status_code == 200

    r2 = await client_db_mode.post(
        "/api/auth/register",
        json={"username": "second", "password": "password9y"},
    )
    assert r2.status_code == 403
    assert r2.json()["code"] == "ADMIN_CONSOLE_REGISTRATION_DISABLED"


@pytest.mark.asyncio
async def test_admin_register_open_registration_allows_second(
    monkeypatch: pytest.MonkeyPatch, tmp_path,
) -> None:
    db_file = (tmp_path / "r_open.sqlite3").resolve()
    url = f"sqlite+aiosqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", url)
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE", "database")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION", "true")
    monkeypatch.delenv("CHAINUP_AGENT_ADMIN_PANEL_USERNAME", raising=False)
    monkeypatch.delenv("CHAINUP_AGENT_ADMIN_PANEL_PASSWORD", raising=False)
    reset_settings_cache()

    from sqlalchemy import create_engine

    sync_engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()

    await dispose_engine()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (
            await client.post(
                "/api/auth/register",
                json={"username": "u1", "password": "xxxxxxxx"},
            )
        ).status_code == 200

        r2 = await client.post(
            "/api/auth/register",
            json={"username": "u2", "password": "yyyyyyyy"},
        )
        assert r2.status_code == 200
        assert r2.json()["username"] == "u2"
    await dispose_engine()


@pytest.mark.asyncio
async def test_admin_register_password_too_short(client_db_mode: AsyncClient) -> None:
    r = await client_db_mode.post(
        "/api/auth/register",
        json={"username": "short", "password": "short7"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_admin_register_issues_jwt_when_secret_set(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    db_file = (tmp_path / "jwtreg.sqlite3").resolve()
    url = f"sqlite+aiosqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", url)
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE", "database")
    monkeypatch.setenv(
        "CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET",
        "jwt-secret-for-register-test-0123456789",
    )
    monkeypatch.delenv("CHAINUP_AGENT_ADMIN_PANEL_USERNAME", raising=False)
    monkeypatch.delenv("CHAINUP_AGENT_ADMIN_PANEL_PASSWORD", raising=False)
    reset_settings_cache()

    from sqlalchemy import create_engine

    sync_engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()

    await dispose_engine()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/auth/register",
            json={"username": "jwtusr", "password": "jwtusrpw00"},
        )
        assert r.status_code == 200
        token = r.json()["access_token"]
        assert token.count(".") == 2
    await dispose_engine()
