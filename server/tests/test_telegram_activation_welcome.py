"""Telegram activation welcome (2026-05-26--telegram-welcome)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from chainup_agent.application.telegram_activation_welcome import (
    KEY_WELCOME_EN,
    KEY_WELCOME_LEGACY,
    KEY_WELCOME_ZH_CN,
    KEY_WELCOME_ZH_TW,
    render_activation_welcome,
    resolve_activation_welcome_text,
)


def test_resolve_activation_welcome_text_fallback_chain() -> None:
    params = {
        KEY_WELCOME_ZH_CN: "简体",
        KEY_WELCOME_EN: "English",
        KEY_WELCOME_ZH_TW: "繁體",
    }
    assert resolve_activation_welcome_text(params, tg_lang="zh-TW") == "繁體"
    assert resolve_activation_welcome_text(params, tg_lang="zh-CN") == "简体"
    assert (
        resolve_activation_welcome_text(
            {KEY_WELCOME_ZH_TW: "  ", KEY_WELCOME_EN: "EN only"},
            tg_lang="zh-TW",
        )
        == "EN only"
    )
    assert (
        resolve_activation_welcome_text(
            {KEY_WELCOME_LEGACY: "legacy"},
            tg_lang="fr",
        )
        == "legacy"
    )
    assert resolve_activation_welcome_text({}, tg_lang="en") is None


def test_render_activation_welcome_display_name() -> None:
    assert (
        render_activation_welcome(
            "Hi {displayName}",
            {"tg_first_name": "Ann", "tg_username": "ann_bot"},
        )
        == "Hi Ann"
    )
    assert (
        render_activation_welcome(
            "Hi {displayName}",
            {"tg_username": "ann_bot"},
        )
        == "Hi @ann_bot"
    )
    assert (
        render_activation_welcome(
            "Hi {displayName} {other}",
            {},
        )
        == "Hi 用户 {other}"
    )


async def _patch_telegram_bot_admin_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "123:abc")
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bot_admin.call_telegram_bot_api",
        AsyncMock(
            return_value={
                "ok": True,
                "result": {"id": 1, "first_name": "X", "username": "x_bot"},
            }
        ),
    )


async def _seed_welcome_template(http_client: AsyncClient) -> None:
    r = await http_client.patch(
        "/api/v1/admin/channels/telegram/bot",
        json={
            "runtimeParams": {
                "TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_CN": "欢迎 {displayName}",
                "TELEGRAM_DEFAULT_LOCALE": "zh-Hans",
            },
        },
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_confirm_sends_activation_welcome_first_time(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    await _patch_telegram_bot_admin_ok(monkeypatch)
    await _seed_welcome_template(http_client)

    send_mock = AsyncMock(return_value={"ok": True, "result": {"message_id": 1}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_activation_welcome.call_telegram_bot_api",
        send_mock,
    )

    r = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "88001", "tg_first_name": "Lee", "tg_lang": "zh-CN"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("activationWelcomeSent") is True
    assert body.get("bindingRowCreated") is True
    send_mock.assert_awaited_once()
    payload = send_mock.call_args.kwargs["json_payload"]
    assert payload["chat_id"] == 88001
    assert "Lee" in payload["text"]


@pytest.mark.asyncio
async def test_confirm_welcome_idempotent_second_confirm(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    await _patch_telegram_bot_admin_ok(monkeypatch)
    await _seed_welcome_template(http_client)

    send_mock = AsyncMock(return_value={"ok": True, "result": {"message_id": 1}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_activation_welcome.call_telegram_bot_api",
        send_mock,
    )

    base = {
        "openapi_base_url": "https://openapi.example.invalid",
        "api_key": "k" * 8,
        "secret_key": "s" * 8,
        "sub_account_id": "900001",
        "telegram": {"tg_id": "88002", "tg_first_name": "Ann"},
    }
    assert (await http_client.post("/api/v1/agent/api-binding/confirm", json=base)).status_code == 200
    assert send_mock.await_count == 1

    r2 = await http_client.post("/api/v1/agent/api-binding/confirm", json=base)
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2.get("activationWelcomeSent") is False
    assert body2.get("activationWelcomeSkipReason") == "already_sent"
    assert body2.get("bindingRowCreated") is False
    assert send_mock.await_count == 1


@pytest.mark.asyncio
async def test_confirm_welcome_no_template_skips_send(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "123:abc")
    from chainup_agent.core.config import reset_settings_cache

    reset_settings_cache()

    send_mock = AsyncMock(return_value={"ok": True})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_activation_welcome.call_telegram_bot_api",
        send_mock,
    )

    r = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "88003"},
        },
    )
    assert r.status_code == 200
    assert r.json().get("activationWelcomeSent") is False
    assert r.json().get("activationWelcomeSkipReason") == "no_template"
    send_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_admin_welcome_text_too_long(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await _patch_telegram_bot_admin_ok(monkeypatch)
    r = await http_client.patch(
        "/api/v1/admin/channels/telegram/bot",
        json={
            "runtimeParams": {
                "TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_CN": "x" * 5000,
            },
        },
    )
    assert r.status_code == 400
    assert r.json()["code"] == "ADMIN_TELEGRAM_WELCOME_TEXT_TOO_LONG"


@pytest.mark.asyncio
async def test_admin_welcome_trilingual_patch_get_echo(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-01 / TC-09: Admin 三语键 PATCH → GET 回显."""
    await _patch_telegram_bot_admin_ok(monkeypatch)
    params = {
        KEY_WELCOME_ZH_CN: "简体欢迎",
        KEY_WELCOME_ZH_TW: "繁體歡迎",
        KEY_WELCOME_EN: "Hello EN",
        KEY_WELCOME_LEGACY: "legacy-fallback",
    }
    r = await http_client.patch(
        "/api/v1/admin/channels/telegram/bot",
        json={"runtimeParams": params},
    )
    assert r.status_code == 200
    patched = r.json()["runtimeParams"]
    for key, val in params.items():
        assert patched[key] == val

    r2 = await http_client.get("/api/v1/admin/channels/telegram/bot")
    assert r2.status_code == 200
    got = r2.json()["runtimeParams"]
    assert got[KEY_WELCOME_ZH_CN] == "简体欢迎"
    assert got[KEY_WELCOME_ZH_TW] == "繁體歡迎"
    assert got[KEY_WELCOME_EN] == "Hello EN"
    assert got[KEY_WELCOME_LEGACY] == "legacy-fallback"


@pytest.mark.asyncio
async def test_me_binding_sends_activation_welcome(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-04: Me 绑定路径与 confirm 同语义."""
    from cryptography.fernet import Fernet

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    await _patch_telegram_bot_admin_ok(monkeypatch)
    await _seed_welcome_template(http_client)

    send_mock = AsyncMock(return_value={"ok": True, "result": {"message_id": 2}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_activation_welcome.call_telegram_bot_api",
        send_mock,
    )

    r = await http_client.post(
        "/api/v1/me/agent/bindings/trading-api",
        json={
            "openapiBaseUrl": "https://openapi.example.invalid",
            "apiKey": "k" * 8,
            "apiSecret": "s" * 8,
            "subAccountId": "900001",
            "idempotencyKey": "welcome-me-1",
            "telegram": {"tg_id": "88010", "tg_first_name": "MeUser", "tg_lang": "zh-CN"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("activationWelcomeSent") is True
    assert body.get("bindingRowCreated") is True
    send_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_confirm_welcome_send_failed_still_200(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-07: sendMessage 失败时 confirm 仍 200，绑定成功."""
    from cryptography.fernet import Fernet

    from chainup_agent.core.errors import AppError
    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    await _patch_telegram_bot_admin_ok(monkeypatch)
    await _seed_welcome_template(http_client)

    send_mock = AsyncMock(side_effect=AppError("TELEGRAM_API_ERROR", "mock fail", status_code=502))
    monkeypatch.setattr(
        "chainup_agent.application.telegram_activation_welcome.call_telegram_bot_api",
        send_mock,
    )

    r = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "88011", "tg_first_name": "FailUser"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("activationWelcomeSent") is False
    assert body.get("activationWelcomeSkipReason") == "send_failed"
    assert body.get("bindingRowCreated") is True
    assert body.get("telegramUserId") == 88011
