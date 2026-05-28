"""Phase 2.4 — cross margin order HTTP + Telegram dual confirm tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_margin_order_http_market_success(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    from unittest.mock import AsyncMock

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    async def fake_margin_order(**kwargs: object) -> dict:
        _ = kwargs
        return {
            "orderIdString": "7001",
            "clientOrderId": "cu_agent_margin_test",
            "status": "NEW",
            "symbol": "BTC/USDT",
            "side": "BUY",
            "type": "MARKET",
        }

    monkeypatch.setattr(
        "chainup_agent.application.agent_margin_trade.post_signed_margin_order_json",
        AsyncMock(side_effect=fake_margin_order),
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_margin_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "64000"}),
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88"},
            },
        )
    ).status_code == 200

    r = await http_client.post(
        "/api/v1/agent/trade/margin/order",
        json={
            "userId": "88",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "orderType": "MARKET",
            "volume": "0.01",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "margin.cross.market_order"
    assert body["orderIdString"] == "7001"


@pytest.mark.asyncio
async def test_margin_order_feature_off(http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_FEATURE_AGENT_MARGIN", "false")
    reset_settings_cache()
    r = await http_client.post(
        "/api/v1/agent/trade/margin/order",
        json={
            "userId": "1",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "orderType": "MARKET",
            "volume": "1",
        },
    )
    assert r.status_code == 403
    assert r.json()["code"] == "FEATURE_AGENT_MARGIN_OFF"


@pytest.mark.asyncio
async def test_scenarios_margin_readiness_ready(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/agent/scenarios")
    assert r.status_code == 200
    by_id = {s["scenarioId"]: s for s in r.json()["scenarios"]}
    assert by_id["margin.cross.market_order"]["readiness"] == "ready"
    assert by_id["margin.cross.limit_order"]["readiness"] == "ready"


@pytest.mark.asyncio
async def test_telegram_margin_market_dual_confirm_phase2_submit(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock
    from urllib.parse import quote

    from chainup_agent.application.telegram_flash_pending import create_margin_market_pending_phase2
    from chainup_agent.core.config import reset_settings_cache
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "1005"},
            },
        )
    ).status_code == 200

    payload = {
        "symbol": "BTC-USDT",
        "side": "BUY",
        "quantity": "0.01",
        "scenarioId": "margin.cross.market_order",
    }
    token = ""
    factory = get_session_factory()
    async with factory() as session:
        token = await create_margin_market_pending_phase2(
            session,
            telegram_user_id=1005,
            chat_id=555555,
            payload=payload,
        )
        await session.commit()

    bot_tok = "configured:ffffffffffffffffffffffffffff"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    reset_settings_cache()

    mocked = AsyncMock(return_value={"ok": True, "result": {}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_callback_handler.call_telegram_bot_api",
        mocked,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_margin_trade.post_signed_margin_order_json",
        AsyncMock(
            return_value={
                "orderIdString": "7002",
                "clientOrderId": "cu_agent_margin_cb",
                "status": "NEW",
                "symbol": "BTC/USDT",
                "side": "BUY",
                "type": "MARKET",
            }
        ),
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_margin_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "64000"}),
    )

    enc = quote(bot_tok, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 45,
            "callback_query": {
                "id": "cq-mg1",
                "from": {"id": 1005, "is_bot": False},
                "message": {"message_id": 6, "chat": {"id": 555555, "type": "private"}},
                "data": f"xm2p{token}",
            },
        },
    )
    assert r.status_code == 200
    methods = [c.args[1] for c in mocked.await_args_list if len(c.args) >= 2]
    assert "answerCallbackQuery" in methods
    assert "sendMessage" in methods
