"""Phase 2.x — spot logical amend (cancel→order) HTTP + intent tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_spot_amend_http_success(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    prior_oid = "256609229205684228"

    async def fake_open_orders(**kwargs: object) -> list[dict]:
        _ = kwargs
        return [
            {
                "orderId": prior_oid,
                "orderIdString": prior_oid,
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "LIMIT",
                "price": "64000",
                "origQty": "0.01",
                "timeInForce": "GTC",
            }
        ]

    async def fake_cancel(**kwargs: object) -> dict:
        _ = kwargs
        return {"orderId": prior_oid, "status": "CANCELED"}

    async def fake_order(**kwargs: object) -> dict:
        _ = kwargs
        return {"orderId": "256609229205684229", "status": "NEW", "type": "LIMIT"}

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_signed_spot_open_orders_json",
        fake_open_orders,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_cancel_json",
        fake_cancel,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        fake_order,
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
            "telegram": {"tg_id": "91"},
        },
    )
    assert c.status_code == 200

    r = await http_client.post(
        "/api/v1/agent/trade/spot/amend-limit-order",
        json={
            "userId": "91",
            "symbol": "BTC-USDT",
            "orderId": prior_oid,
            "price": "65000",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.spot.amend_limit_order"
    assert body["amendCorrelationId"]
    assert body["cancelledOrderId"] == prior_oid
    assert body["orderId"]


@pytest.mark.asyncio
async def test_spot_amend_cancel_ok_replace_fail(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    from chainup_agent.core.errors import AppError
    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    prior_oid = "256609229205684228"

    async def fake_open_orders(**kwargs: object) -> list[dict]:
        _ = kwargs
        return [
            {
                "orderId": prior_oid,
                "orderIdString": prior_oid,
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "LIMIT",
                "price": "64000",
                "origQty": "0.01",
            }
        ]

    async def fake_cancel(**kwargs: object) -> dict:
        _ = kwargs
        return {"orderId": prior_oid, "status": "CANCELED"}

    async def fake_order(**kwargs: object) -> dict:
        _ = kwargs
        raise AppError(code="EXCHANGE_REJECTED", message="mock replace fail", status_code=400)

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_signed_spot_open_orders_json",
        fake_open_orders,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_cancel_json",
        fake_cancel,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        fake_order,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "92"},
        },
    )

    r = await http_client.post(
        "/api/v1/agent/trade/spot/amend-limit-order",
        json={
            "userId": "92",
            "symbol": "BTC-USDT",
            "orderId": prior_oid,
            "price": "65000",
        },
    )
    assert r.status_code == 502
    body = r.json()
    assert body["code"] == "AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED"
    details = body.get("details") or {}
    assert details.get("reconcileSuggested") is True
    assert details.get("reconcileCaseKind") == "CANCEL_SUCCEEDED_REPLACE_FAILED"
    assert details.get("reconcilePath") == "/api/v1/agent/trading/reconcile"


@pytest.mark.asyncio
async def test_scenarios_amend_ready_oco_stub(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/agent/scenarios")
    assert r.status_code == 200
    by_id = {s["scenarioId"]: s for s in r.json()["scenarios"]}
    assert by_id["trade.spot.amend_limit_order"]["readiness"] == "ready"
    assert by_id["trade.spot.oco"]["readiness"] == "stub"
    assert by_id["trade.spot.bracket"]["readiness"] == "stub"


@pytest.mark.asyncio
async def test_runtime_intent_amend_clarify(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "BTC-USDT 改单"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.spot.amend_limit_order"
    assert body.get("plan", {}).get("nextStep") == "CLARIFY"


@pytest.mark.asyncio
async def test_runtime_intent_amend_confirm_type_a(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={
            "text": "BTC-USDT 改单 订单号 256609229205684228 新价 65000",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.spot.amend_limit_order"
    assert body.get("plan", {}).get("nextStep") == "CONFIRM_TYPE_A"


@pytest.mark.asyncio
async def test_runtime_intent_oco_stub(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "BTC-USDT OCO 买入 65000 止损 60000"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] in ("trade.spot.oco", "trade.spot.bracket")
    assert body.get("plan", {}).get("nextStep") == "STUB_NOT_EXECUTABLE"
