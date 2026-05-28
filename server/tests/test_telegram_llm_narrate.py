"""Tests for feature 2026-05-26--telegram-llm-narrate (gateway_defaults.telegramLlmNarrate)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from urllib.parse import quote

import pytest
from httpx import AsyncClient

from chainup_agent.application.telegram_llm_narrate_policy import (
    resolve_effective_telegram_llm_narrate,
)
from chainup_agent.core.config import Settings, reset_settings_cache

from tests.test_api import _init_binding_sqlite, _init_schema_sqlite, _mock_probe_ok


def test_resolve_effective_narrate_env_overrides_admin_false() -> None:
    settings = Settings(telegram_llm_narrate_read_market_ticker=True)
    assert (
        resolve_effective_telegram_llm_narrate(
            settings,
            {"telegramLlmNarrate": {"readMarketTicker": False}},
            "readMarketTicker",
        )
        is True
    )


def test_resolve_effective_narrate_admin_true_when_env_false() -> None:
    settings = Settings(telegram_llm_narrate_read_market_ticker=False)
    assert (
        resolve_effective_telegram_llm_narrate(
            settings,
            {"telegramLlmNarrate": {"readMarketTicker": True}},
            "readMarketTicker",
        )
        is True
    )
    assert (
        resolve_effective_telegram_llm_narrate(
            settings,
            {"telegramLlmNarrate": {"readMarketTicker": False}},
            "readMarketTicker",
        )
        is False
    )
    assert resolve_effective_telegram_llm_narrate(settings, None, "readMarketTicker") is False


@pytest.mark.asyncio
async def test_admin_defaults_telegram_llm_narrate_patch_get(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-01: PATCH/GET telegramLlmNarrate on gateway defaults."""
    await _init_schema_sqlite(monkeypatch, tmp_path)

    dr = await http_client.get("/api/v1/admin/ai/defaults")
    assert dr.status_code == 200
    narrate = dr.json().get("telegramLlmNarrate") or {}
    assert narrate.get("readMarketTicker") is False
    assert narrate.get("readMarketDepth") is False

    patch = await http_client.patch(
        "/api/v1/admin/ai/defaults",
        json={"telegramLlmNarrate": {"readMarketTicker": True}},
    )
    assert patch.status_code == 200
    assert patch.json()["telegramLlmNarrate"]["readMarketTicker"] is True
    assert patch.json()["telegramLlmNarrate"]["readMarketDepth"] is False

    again = await http_client.get("/api/v1/admin/ai/defaults")
    assert again.status_code == 200
    assert again.json()["telegramLlmNarrate"]["readMarketTicker"] is True


@pytest.mark.asyncio
async def test_admin_defaults_telegram_llm_narrate_partial_patch(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-08: partial PATCH does not reset other narrate keys."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    assert (
        await http_client.patch(
            "/api/v1/admin/ai/defaults",
            json={"telegramLlmNarrate": {"readMarketTicker": True}},
        )
    ).status_code == 200

    patch = await http_client.patch(
        "/api/v1/admin/ai/defaults",
        json={"telegramLlmNarrate": {"readMarketDepth": True}},
    )
    assert patch.status_code == 200
    body = patch.json()["telegramLlmNarrate"]
    assert body["readMarketTicker"] is True
    assert body["readMarketDepth"] is True
    assert body["readMarketTrades"] is False


@pytest.mark.asyncio
async def test_telegram_ticker_narrate_via_admin_defaults(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-02: Admin readMarketTicker enables LLM narrate."""
    from cryptography.fernet import Fernet

    async def fake_ticker_json(*, openapi_base_url: str, symbol_candidates: list[str]) -> dict:
        _ = openapi_base_url
        sym = symbol_candidates[0] if symbol_candidates else ""
        return {"symbol": sym, "lastPrice": "12345.67", "volume": "999"}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_ticker_json_with_fallbacks",
        fake_ticker_json,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY", "true")
    reset_settings_cache()
    assert (await http_client.get("/api/v1/admin/ai/providers")).status_code == 200
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88001"},
            },
        )
    ).status_code == 200

    assert (
        await http_client.patch(
            "/api/v1/admin/ai/defaults",
            json={"telegramLlmNarrate": {"readMarketTicker": True}},
        )
    ).status_code == 200

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER", "false")
    reset_settings_cache()

    llm_mock = AsyncMock(
        return_value=("Admin 配置启用的 LLM 行情简述。", None, {"gatewayModelId": "gpt-mini"}),
    )
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        llm_mock,
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 12}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 11,
                "from": {"id": 88001, "is_bot": False, "username": "alice"},
                "chat": {"id": 424880, "type": "private"},
                "text": "看看 BTC 行情",
            },
        },
    )
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    assert "Admin 配置启用的 LLM 行情简述。" in body["text"]
    llm_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_telegram_ticker_narrate_llm_fallback_deterministic(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-03: narrate enabled but LLM fails → deterministic ticker lines."""
    from cryptography.fernet import Fernet

    async def fake_ticker_json(*, openapi_base_url: str, symbol_candidates: list[str]) -> dict:
        _ = openapi_base_url
        sym = symbol_candidates[0] if symbol_candidates else ""
        return {"symbol": sym, "lastPrice": "99.01", "volume": "1"}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_ticker_json_with_fallbacks",
        fake_ticker_json,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY", "true")
    reset_settings_cache()
    assert (await http_client.get("/api/v1/admin/ai/providers")).status_code == 200
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88002"},
            },
        )
    ).status_code == 200
    await http_client.patch(
        "/api/v1/admin/ai/defaults",
        json={"telegramLlmNarrate": {"readMarketTicker": True}},
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL", "https://example.com/bind")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()

    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        AsyncMock(return_value=(None, "err", {"gatewayModelId": "gpt-4"})),
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 31}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 81,
                "from": {"id": 88002, "is_bot": False},
                "chat": {"id": 424881, "type": "private"},
                "text": "ETH 价格",
            },
        },
    )
    assert r.status_code == 200
    text = mocked.await_args.kwargs["json_payload"]["text"]
    assert "99.01" in text
    assert "数据来源：现货公共 ticker（只读）" not in text


@pytest.mark.asyncio
async def test_telegram_ticker_narrate_disabled_skips_llm(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-04: narrate off → no LLM call."""
    from cryptography.fernet import Fernet

    async def fake_ticker_json(*, openapi_base_url: str, symbol_candidates: list[str]) -> dict:
        _ = openapi_base_url
        sym = symbol_candidates[0] if symbol_candidates else ""
        return {"symbol": sym, "lastPrice": "1.23", "volume": "1"}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_ticker_json_with_fallbacks",
        fake_ticker_json,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY", "true")
    reset_settings_cache()
    assert (await http_client.get("/api/v1/admin/ai/providers")).status_code == 200
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88003"},
            },
        )
    ).status_code == 200

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL", "https://example.com/bind")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER", "false")
    reset_settings_cache()

    llm_mock = AsyncMock(return_value=("nope", None, {}))
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        llm_mock,
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 1}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 1,
                "from": {"id": 88003, "is_bot": False},
                "chat": {"id": 424882, "type": "private"},
                "text": "BTC 行情",
            },
        },
    )
    assert r.status_code == 200
    llm_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_telegram_ticker_narrate_env_overrides_admin_false(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-05: env true forces narrate even when admin readMarketTicker=false."""
    from cryptography.fernet import Fernet

    async def fake_ticker_json(*, openapi_base_url: str, symbol_candidates: list[str]) -> dict:
        _ = openapi_base_url
        sym = symbol_candidates[0] if symbol_candidates else ""
        return {"symbol": sym, "lastPrice": "50", "volume": "1"}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_ticker_json_with_fallbacks",
        fake_ticker_json,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY", "true")
    reset_settings_cache()
    assert (await http_client.get("/api/v1/admin/ai/providers")).status_code == 200
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88004"},
            },
        )
    ).status_code == 200
    await http_client.patch(
        "/api/v1/admin/ai/defaults",
        json={"telegramLlmNarrate": {"readMarketTicker": False}},
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL", "https://example.com/bind")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER", "true")
    reset_settings_cache()

    llm_mock = AsyncMock(return_value=("env 强制 narrate。", None, {}))
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        llm_mock,
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 2}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 2,
                "from": {"id": 88004, "is_bot": False},
                "chat": {"id": 424883, "type": "private"},
                "text": "BTC 行情",
            },
        },
    )
    assert r.status_code == 200
    assert "env 强制 narrate。" in mocked.await_args.kwargs["json_payload"]["text"]
    llm_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_telegram_depth_narrate_via_admin_defaults(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-06 (depth): Admin readMarketDepth enables narrate."""
    from cryptography.fernet import Fernet

    async def fake_depth(*, openapi_base_url: str, symbol_candidates: list[str], limit: int):
        _ = openapi_base_url, limit
        return {"asks": [["1", "1"]], "bids": [["0.9", "2"]]}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_depth_json_with_fallbacks",
        fake_depth,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY", "true")
    reset_settings_cache()
    assert (await http_client.get("/api/v1/admin/ai/providers")).status_code == 200
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88005"},
            },
        )
    ).status_code == 200
    await http_client.patch(
        "/api/v1/admin/ai/defaults",
        json={"telegramLlmNarrate": {"readMarketDepth": True}},
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL", "https://example.com/bind")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()

    llm_mock = AsyncMock(return_value=("深度 LLM 简述。", None, {}))
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        llm_mock,
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 3}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 3,
                "from": {"id": 88005, "is_bot": False},
                "chat": {"id": 424884, "type": "private"},
                "text": "BTC-USDT 盘口",
            },
        },
    )
    assert r.status_code == 200
    assert "深度 LLM 简述。" in mocked.await_args.kwargs["json_payload"]["text"]
    assert llm_mock.await_args.kwargs["scenario_id"] == "read.market.depth"


@pytest.mark.asyncio
async def test_telegram_ticker_narrate_timeline_effective_flag(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-07: timeline payload includes effectiveTelegramLlmNarrateEnabled."""
    from cryptography.fernet import Fernet

    async def fake_ticker_json(*, openapi_base_url: str, symbol_candidates: list[str]) -> dict:
        _ = openapi_base_url
        sym = symbol_candidates[0] if symbol_candidates else ""
        return {"symbol": sym, "lastPrice": "1", "volume": "1"}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_ticker_json_with_fallbacks",
        fake_ticker_json,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY", "true")
    reset_settings_cache()
    assert (await http_client.get("/api/v1/admin/ai/providers")).status_code == 200
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88006"},
            },
        )
    ).status_code == 200
    await http_client.patch(
        "/api/v1/admin/ai/defaults",
        json={"telegramLlmNarrate": {"readMarketTicker": True}},
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL", "https://example.com/bind")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()

    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        AsyncMock(return_value=(None, "err", {"gatewayModelId": "gpt-4"})),
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 31}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 81,
                "from": {"id": 88006, "is_bot": False},
                "chat": {"id": 424885, "type": "private"},
                "text": "ETH 价格",
            },
        },
    )

    lst = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"userId": "88006", "limit": 5},
    )
    assert lst.status_code == 200
    eid = lst.json()["items"][0]["executionId"]
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    llm_events = [x for x in tl.json()["items"] if x["eventName"] == "llm.read.market.ticker"]
    assert llm_events
    summary = llm_events[0].get("summary") or {}
    assert summary.get("effectiveTelegramLlmNarrateEnabled") is True
