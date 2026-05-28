"""Phase 2.5 — futures condition order HTTP + intent tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_condition_order_http_success(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    async def fake_condition_order(**kwargs: object) -> dict:
        _ = kwargs
        return {"orderId": 256609229205684228}

    monkeypatch.setattr(
        "chainup_agent.application.agent_futures_condition_trade.post_signed_futures_condition_order_json",
        fake_condition_order,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    c = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "88"},
        },
    )
    assert c.status_code == 200

    r = await http_client.post(
        "/api/v1/agent/trade/futures/condition-order",
        json={
            "userId": "88",
            "symbol": "BTC-USDT",
            "side": "SELL",
            "orderType": "MARKET",
            "volume": "1",
            "triggerPrice": "91000",
            "triggerType": "3UP",
            "openClose": "CLOSE",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "automation.condition_order"
    assert body["orderId"] == "256609229205684228"
    assert body["contractName"] == "E-BTC-USDT"
    assert body["triggerPrice"] == "91000"
    assert body["triggerType"] == "3UP"


@pytest.mark.asyncio
async def test_condition_order_feature_off(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_FEATURE_AGENT_FUTURES", "false")
    reset_settings_cache()
    r = await http_client.post(
        "/api/v1/agent/trade/futures/condition-order",
        json={
            "userId": "1",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "orderType": "MARKET",
            "volume": "1",
            "triggerPrice": "91000",
            "triggerType": "4DOWN",
        },
    )
    assert r.status_code == 403
    assert r.json()["code"] == "FEATURE_AGENT_FUTURES_OFF"


@pytest.mark.asyncio
async def test_scenarios_condition_order_readiness_ready(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/agent/scenarios")
    assert r.status_code == 200
    by_id = {s["scenarioId"]: s for s in r.json()["scenarios"]}
    assert by_id["automation.condition_order"]["readiness"] == "ready"


@pytest.mark.asyncio
async def test_runtime_intent_condition_order_clarify(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "BTC-USDT 条件单 触发价 91000"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "automation.condition_order"
    assert body.get("plan", {}).get("nextStep") == "CLARIFY"


@pytest.mark.asyncio
async def test_runtime_intent_condition_order_confirm_type_a(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={
            "text": "BTC-USDT 条件单 卖出 1张 触发价 91000 上涨触发 平仓",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "automation.condition_order"
    assert body.get("plan", {}).get("nextStep") == "CONFIRM_TYPE_A"


@pytest.mark.asyncio
async def test_telegram_webhook_callback_condition_confirm(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock
    from urllib.parse import quote

    from chainup_agent.application.telegram_flash_pending import create_condition_pending
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
                "telegram": {"tg_id": "881"},
            },
        )
    ).status_code == 200

    async def fake_condition(**kwargs: object) -> dict:
        _ = kwargs
        return {
            "orderIdString": "cond-1",
            "contractName": "E-BTC-USDT",
            "triggerPrice": "91000",
            "triggerType": "3UP",
        }

    monkeypatch.setattr(
        "chainup_agent.application.agent_futures_condition_trade.post_signed_futures_condition_order_json",
        fake_condition,
    )
    send_mock = AsyncMock(return_value={"ok": True})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_callback_handler.call_telegram_bot_api",
        send_mock,
    )

    factory = get_session_factory()
    async with factory() as session:
        token = await create_condition_pending(
            session,
            telegram_user_id=881,
            chat_id=881,
            symbol="BTC-USDT",
            side="SELL",
            quantity="1",
            trigger_price="91000",
            trigger_type="3UP",
            order_type="MARKET",
            open_close="CLOSE",
        )
        await session.commit()

    reset_settings_cache()
    bot_tok = "configured:cccccccccccccccccccccccccccc"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    reset_settings_cache()

    enc = quote(bot_tok, safe="")
    wh = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 881001,
            "callback_query": {
                "id": "cb881",
                "from": {"id": 881, "is_bot": False, "first_name": "T"},
                "message": {"message_id": 1, "chat": {"id": 881, "type": "private"}},
                "data": f"cop{token}",
            },
        },
    )
    assert wh.status_code == 200
    methods = [c.args[1] for c in send_mock.await_args_list if len(c.args) >= 2]
    assert "answerCallbackQuery" in methods
    assert "sendMessage" in methods
