"""Admin console Bearer enforcement when CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET is set."""

from __future__ import annotations

import pytest
from chainup_agent.core.config import reset_settings_cache
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_routes_allow_anonymous_when_jwt_secret_unset(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Empty env must override `.env` file (otherwise delenv falls back to file-injected secret).
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET", "")
    reset_settings_cache()
    r = await http_client.get("/api/v1/admin/ai/providers")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_admin_routes_require_bearer_when_jwt_secret_configured(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET",
        "unit-test-jwt-secret-key-at-least-16-characters-long-ok",
    )
    monkeypatch.delenv("CHAINUP_AGENT_ADMIN_PANEL_USERNAME", raising=False)
    monkeypatch.delenv("CHAINUP_AGENT_ADMIN_PANEL_PASSWORD", raising=False)
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_PANEL_USERNAME", "adm")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_PANEL_PASSWORD", "pw-for-admin-login-test")
    reset_settings_cache()

    blocked = await http_client.get("/api/v1/admin/ai/providers")
    assert blocked.status_code == 401
    assert blocked.json()["code"] == "ADMIN_CONSOLE_AUTH_REQUIRED"

    lr = await http_client.post(
        "/api/auth/login",
        json={"username": "adm", "password": "pw-for-admin-login-test"},
    )
    assert lr.status_code == 200
    token = lr.json()["access_token"]
    assert token.count(".") == 2

    ok = await http_client.get(
        "/api/v1/admin/ai/providers",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ok.status_code == 200


@pytest.mark.asyncio
async def test_admin_routes_reject_garbage_bearer_when_jwt_secret_configured(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET",
        "unit-test-jwt-secret-key-at-least-16-characters-long-ok",
    )
    reset_settings_cache()

    r = await http_client.get(
        "/api/v1/admin/channels/telegram/webhook",
        headers={"Authorization": "Bearer not-a-jwt"},
    )
    assert r.status_code == 401
    assert r.json()["code"] == "ADMIN_CONSOLE_ACCESS_TOKEN_INVALID"
