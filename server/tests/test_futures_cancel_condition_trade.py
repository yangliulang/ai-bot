"""P0 — futures cancel, condition orders read/cancel HTTP + intent."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _bind_user_79(http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    from cryptography.fernet import Fernet

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    c = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900079",
            "telegram": {"tg_id": "79"},
        },
    )
    assert c.status_code == 200


@pytest.mark.asyncio
async def test_futures_cancel_http_success(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    async def fake_cancel(**kwargs: object) -> dict:
        _ = kwargs
        return {
            "scenarioId": "trade.futures.cancel_order",
            "orderId": "259396989397942275",
            "orderIdString": "259396989397942275",
            "contractName": "E-BTC-USDT",
            "symbol": "BTC_USDT",
            "status": "CANCELLED",
            "exchangeOrderPreview": {"orderId": "259396989397942275"},
        }

    monkeypatch.setattr(
        "chainup_agent.application.agent_futures_trade.post_signed_futures_cancel_json",
        fake_cancel,
    )
    await _bind_user_79(http_client, monkeypatch, tmp_path)
    r = await http_client.post(
        "/api/v1/agent/trade/futures/cancel",
        json={
            "userId": "79",
            "symbol": "BTC-USDT",
            "orderId": "259396989397942275",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.futures.cancel_order"
    assert body["orderIdString"] == "259396989397942275"


@pytest.mark.asyncio
async def test_condition_orders_read_http(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    async def fake_open(**kwargs: object) -> list:
        _ = kwargs
        return [
            {
                "orderId": "1",
                "contractName": "E-BTC-USDT",
                "triggerPrice": "90000",
                "triggerType": "3UP",
                "status": "INIT",
            },
            {"orderId": "2", "contractName": "E-BTC-USDT", "side": "BUY", "type": "LIMIT"},
        ]

    monkeypatch.setattr(
        "chainup_agent.application.agent_futures_trade.fetch_signed_futures_open_orders_json",
        fake_open,
    )
    await _bind_user_79(http_client, monkeypatch, tmp_path)
    r = await http_client.get(
        "/api/v1/agent/trade/futures/condition-orders",
        params={"userId": "79", "symbol": "BTC-USDT"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "automation.condition_orders_read"
    assert len(body["orders"]) == 1
    assert body["totalOpenOrders"] == 2


@pytest.mark.asyncio
async def test_condition_cancel_http_success(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    async def fake_cancel(**kwargs: object) -> dict:
        _ = kwargs
        return {"orderId": "111", "orderIdString": "111"}

    monkeypatch.setattr(
        "chainup_agent.application.agent_futures_trade.post_signed_futures_cancel_json",
        fake_cancel,
    )
    await _bind_user_79(http_client, monkeypatch, tmp_path)
    r = await http_client.post(
        "/api/v1/agent/trade/futures/cancel-condition",
        json={
            "userId": "79",
            "symbol": "BTC-USDT",
            "orderId": "111",
        },
    )
    assert r.status_code == 200
    assert r.json()["scenarioId"] == "automation.condition_order_cancel"


@pytest.mark.asyncio
async def test_scenarios_futures_cancel_and_condition_read_ready(
    http_client: AsyncClient,
) -> None:
    r = await http_client.get("/api/v1/agent/scenarios")
    assert r.status_code == 200
    by_id = {s["scenarioId"]: s for s in r.json()["scenarios"]}
    assert by_id["trade.futures.cancel_order"]["readiness"] == "ready"
    assert by_id["automation.condition_orders_read"]["readiness"] == "ready"
    assert by_id["automation.condition_order_cancel"]["readiness"] == "ready"
    assert by_id["trade.spot.oco"]["readiness"] == "stub"


@pytest.mark.asyncio
async def test_runtime_intent_futures_cancel_execute(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "永续 BTC-USDT 撤单 订单号 259396989397942275"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.futures.cancel_order"
    assert body.get("plan", {}).get("nextStep") == "EXECUTE_FUTURES_CANCEL"


@pytest.mark.asyncio
async def test_runtime_intent_condition_orders_read(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "查询我的条件单 BTC-USDT"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "automation.condition_orders_read"
    assert body.get("plan", {}).get("nextStep") == "ROUTE_READ_SKILL"


@pytest.mark.asyncio
async def test_runtime_intent_condition_cancel_confirm(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "永续 撤销条件单 BTC-USDT 订单号 259396989397942275"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "automation.condition_order_cancel"
    assert body.get("plan", {}).get("nextStep") == "CONFIRM_TYPE_A"


@pytest.mark.asyncio
async def test_is_condition_order_row_filter() -> None:
    from chainup_agent.application.agent_futures_condition_trade import _is_condition_order_row

    assert _is_condition_order_row({"triggerType": "3UP", "orderId": "1"})
    assert not _is_condition_order_row({"side": "BUY", "type": "LIMIT", "orderId": "2"})


@pytest.mark.asyncio
async def test_coobit_fapi_cancel_body() -> None:
    from chainup_agent.domain.canonical_trading import coobit_fapi_v1_cancel_body

    body = coobit_fapi_v1_cancel_body(
        contract_name="E-BTC-USDT",
        order_id="259396989397942275",
    )
    assert body == {
        "contractName": "E-BTC-USDT",
        "orderId": "259396989397942275",
    }
