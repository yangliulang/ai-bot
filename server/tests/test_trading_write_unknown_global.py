"""P0 — global 504/UNKNOWN on Coobit signed writes (2026-05-26--trading-write-unknown-global)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import httpx
import pytest
from httpx import AsyncClient

from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.exchange.coobit_openapi import (
    _FUTURES_CANCEL_V1_PATH,
    _FUTURES_CONDITION_ORDER_V1_PATH,
    _FUTURES_ORDER_V1_PATH,
    _MARGIN_ORDER_V2_PATH,
    _coobit_spot_order_rejected_app_error,
    app_error_indicates_exchange_unknown,
    check_exchange_write_http_unknown,
    post_signed_futures_cancel_json,
    post_signed_futures_condition_order_json,
    post_signed_futures_order_json,
    post_signed_margin_order_json,
    post_signed_spot_cancel_json,
    post_signed_spot_order_json,
    raise_exchange_write_unknown,
)

_UNKNOWN_EXC = AppError(
    code="AGENT_EXCHANGE_WRITE_UNKNOWN",
    message="交易所写请求结果未知，请稍后对账重试",
    status_code=502,
    details={"exchangeOutcome": "unknown", "path": "/sapi/v2/order"},
)


class _FakeHttpResponse:
    def __init__(self, status_code: int, payload: dict | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload


class _FakeAsyncClient:
    def __init__(self, response: _FakeHttpResponse) -> None:
        self._response = response

    async def __aenter__(self) -> _FakeAsyncClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def post(self, *args: object, **kwargs: object) -> _FakeHttpResponse:
        return self._response


def test_check_exchange_write_http_unknown_504() -> None:
    with pytest.raises(AppError) as ei:
        check_exchange_write_http_unknown(504, "/sapi/v2/order")
    assert ei.value.code == "AGENT_EXCHANGE_WRITE_UNKNOWN"
    assert ei.value.status_code == 502
    assert ei.value.details["exchangeOutcome"] == "unknown"


def test_raise_exchange_write_unknown_timeout() -> None:
    with pytest.raises(AppError) as ei:
        raise_exchange_write_unknown(path="/sapi/v2/order", reason="timeout")
    assert ei.value.code == "AGENT_EXCHANGE_WRITE_UNKNOWN"
    assert ei.value.details["reason"] == "timeout"
    assert app_error_indicates_exchange_unknown(ei.value)


@pytest.mark.asyncio
async def test_post_signed_spot_order_504_tc01(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "chainup_agent.infrastructure.exchange.coobit_openapi.httpx.AsyncClient",
        lambda *a, **k: _FakeAsyncClient(_FakeHttpResponse(504, {})),
    )
    with pytest.raises(AppError) as ei:
        await post_signed_spot_order_json(
            openapi_base_url="https://openapi.example.invalid",
            api_key="k" * 8,
            secret_key="s" * 8,
            order_body={
                "symbol": "BTC/USDT",
                "side": "BUY",
                "type": "LIMIT",
                "volume": 0.01,
                "price": 1.0,
            },
        )
    assert ei.value.code == "AGENT_EXCHANGE_WRITE_UNKNOWN"
    assert ei.value.details.get("http_status") == 504


@pytest.mark.asyncio
async def test_post_signed_spot_cancel_timeout_tc10(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _timeout_post(*args: object, **kwargs: object) -> None:
        raise httpx.TimeoutException("timeout")

    class _TimeoutClient:
        async def __aenter__(self) -> _TimeoutClient:
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        post = _timeout_post

    monkeypatch.setattr(
        "chainup_agent.infrastructure.exchange.coobit_openapi.httpx.AsyncClient",
        lambda *a, **k: _TimeoutClient(),
    )
    with pytest.raises(AppError) as ei:
        await post_signed_spot_cancel_json(
            openapi_base_url="https://openapi.example.invalid",
            api_key="k" * 8,
            secret_key="s" * 8,
            cancel_body={"symbol": "BTC/USDT", "orderId": "1"},
        )
    assert ei.value.code == "AGENT_EXCHANGE_WRITE_UNKNOWN"
    assert ei.value.details.get("reason") == "timeout"


async def _confirm_binding(http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch, tmp_path, tg_id: str) -> None:
    from cryptography.fernet import Fernet

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

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
                "telegram": {"tg_id": tg_id},
            },
        )
    ).status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("post_fn", "path"),
    [
        (post_signed_futures_order_json, _FUTURES_ORDER_V1_PATH),
        (post_signed_futures_cancel_json, _FUTURES_CANCEL_V1_PATH),
        (post_signed_margin_order_json, _MARGIN_ORDER_V2_PATH),
        (post_signed_futures_condition_order_json, _FUTURES_CONDITION_ORDER_V1_PATH),
    ],
)
async def test_post_signed_writes_504_param_tc01_ac4_ac6(
    monkeypatch: pytest.MonkeyPatch,
    post_fn: object,
    path: str,
) -> None:
    monkeypatch.setattr(
        "chainup_agent.infrastructure.exchange.coobit_openapi.httpx.AsyncClient",
        lambda *a, **k: _FakeAsyncClient(_FakeHttpResponse(504, {})),
    )
    base_kw = {
        "openapi_base_url": "https://openapi.example.invalid",
        "api_key": "k" * 8,
        "secret_key": "s" * 8,
    }
    with pytest.raises(AppError) as ei:
        if post_fn is post_signed_futures_order_json:
            await post_fn(
                **base_kw,
                order_body={
                    "contractName": "E-BTC-USDT",
                    "side": "BUY",
                    "type": "MARKET",
                    "volume": "1",
                },
            )
        elif post_fn is post_signed_futures_cancel_json:
            await post_fn(**base_kw, cancel_body={"contractName": "E-BTC-USDT", "orderId": "1"})
        elif post_fn is post_signed_margin_order_json:
            await post_fn(
                **base_kw,
                order_body={
                    "symbol": "BTC/USDT",
                    "side": "BUY",
                    "type": "MARKET",
                    "volume": "0.01",
                },
            )
        else:
            await post_fn(
                **base_kw,
                order_body={
                    "contractName": "E-BTC-USDT",
                    "side": "BUY",
                    "type": "MARKET",
                    "volume": "1",
                    "triggerPrice": "1",
                    "triggerType": "1",
                },
            )
    assert ei.value.code == "AGENT_EXCHANGE_WRITE_UNKNOWN"
    assert ei.value.details.get("path") == path


@pytest.mark.asyncio
async def test_spot_cancel_http_unknown_tc03(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _confirm_binding(http_client, monkeypatch, tmp_path, "92022")
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_cancel_json",
        AsyncMock(side_effect=_UNKNOWN_EXC),
    )
    r = await http_client.post(
        "/api/v1/agent/trade/spot/cancel",
        json={"userId": "92022", "symbol": "BTC-USDT", "orderId": "123"},
    )
    assert r.status_code == 502
    assert r.json()["code"] == "AGENT_EXCHANGE_WRITE_UNKNOWN"


@pytest.mark.asyncio
async def test_futures_order_http_unknown_tc04(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _confirm_binding(http_client, monkeypatch, tmp_path, "92023")
    monkeypatch.setattr(
        "chainup_agent.application.agent_futures_trade.post_signed_futures_order_json",
        AsyncMock(side_effect=_UNKNOWN_EXC),
    )
    r = await http_client.post(
        "/api/v1/agent/trade/futures/order",
        json={
            "userId": "92023",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "orderType": "MARKET",
            "volume": "1",
        },
    )
    assert r.status_code == 502
    assert r.json()["code"] == "AGENT_EXCHANGE_WRITE_UNKNOWN"


@pytest.mark.asyncio
async def test_futures_cancel_http_unknown_tc04(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _confirm_binding(http_client, monkeypatch, tmp_path, "92025")
    monkeypatch.setattr(
        "chainup_agent.application.agent_futures_trade.post_signed_futures_cancel_json",
        AsyncMock(side_effect=_UNKNOWN_EXC),
    )
    r = await http_client.post(
        "/api/v1/agent/trade/futures/cancel",
        json={"userId": "92025", "symbol": "BTC-USDT", "orderId": "123"},
    )
    assert r.status_code == 502
    assert r.json()["code"] == "AGENT_EXCHANGE_WRITE_UNKNOWN"


@pytest.mark.asyncio
async def test_futures_condition_order_http_unknown_tc06(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _confirm_binding(http_client, monkeypatch, tmp_path, "92026")
    monkeypatch.setattr(
        "chainup_agent.application.agent_futures_condition_trade.post_signed_futures_condition_order_json",
        AsyncMock(side_effect=_UNKNOWN_EXC),
    )
    r = await http_client.post(
        "/api/v1/agent/trade/futures/condition-order",
        json={
            "userId": "92026",
            "symbol": "BTC-USDT",
            "side": "SELL",
            "orderType": "MARKET",
            "volume": "1",
            "triggerPrice": "91000",
            "triggerType": "3UP",
            "openClose": "CLOSE",
        },
    )
    assert r.status_code == 502
    assert r.json()["code"] == "AGENT_EXCHANGE_WRITE_UNKNOWN"


@pytest.mark.asyncio
async def test_margin_order_http_unknown_tc05(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _confirm_binding(http_client, monkeypatch, tmp_path, "92024")
    monkeypatch.setattr(
        "chainup_agent.application.agent_margin_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "64000"}),
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_margin_trade.post_signed_margin_order_json",
        AsyncMock(side_effect=_UNKNOWN_EXC),
    )
    r = await http_client.post(
        "/api/v1/agent/trade/margin/order",
        json={
            "userId": "92024",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "orderType": "MARKET",
            "volume": "0.01",
        },
    )
    assert r.status_code == 502
    assert r.json()["code"] == "AGENT_EXCHANGE_WRITE_UNKNOWN"


@pytest.mark.asyncio
async def test_spot_limit_order_http_unknown_timeline_and_finalize(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    await _confirm_binding(http_client, monkeypatch, tmp_path, "92020")

    unknown = AppError(
        code="AGENT_EXCHANGE_WRITE_UNKNOWN",
        message="交易所返回 504，订单终态未知，请稍后对账重试",
        status_code=502,
        details={
            "http_status": 504,
            "path": "/sapi/v2/order",
            "exchangeOutcome": "unknown",
        },
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        AsyncMock(side_effect=unknown),
    )

    r = await http_client.post(
        "/api/v1/agent/trade/spot/limit-order",
        json={
            "userId": "92020",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "volume": "0.01",
            "price": "48000",
            "timeInForce": "GTC",
        },
    )
    assert r.status_code == 502
    body = r.json()
    assert body["code"] == "AGENT_EXCHANGE_WRITE_UNKNOWN"
    factory = get_session_factory()
    async with factory() as session:
        from sqlalchemy import select

        from chainup_agent.infrastructure.persistence.models.agent_execution import (
            AgentExecution,
        )
        from chainup_agent.infrastructure.persistence.models.agent_execution_event import (
            AgentExecutionEvent,
        )

        row = (
            await session.execute(
                select(AgentExecution)
                .where(AgentExecution.user_id == "92020")
                .order_by(AgentExecution.created_at.desc())
                .limit(1)
            )
        ).scalar_one()
        eid = row.execution_id
        assert row.state == "UNKNOWN"
        events = (
            await session.execute(
                select(AgentExecutionEvent).where(
                    AgentExecutionEvent.execution_id == eid,
                    AgentExecutionEvent.event_type == "trading.exchange_private",
                )
            )
        ).scalars().all()
        assert events
        payload = json.loads(events[-1].payload_json or "{}")
        assert payload.get("exchangeOutcome") == "unknown"

    st = await http_client.get(
        "/api/v1/agent/trading/reconcile/status",
        params={"userId": "92020", "executionId": eid},
    )
    assert st.status_code == 200
    assert st.json()["resolutionStatus"] == "UNKNOWN"


@pytest.mark.asyncio
async def test_spot_rejected_not_mapped_to_unknown(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _confirm_binding(http_client, monkeypatch, tmp_path, "92021")

    rej = _coobit_spot_order_rejected_app_error(
        {"code": -2010, "msg": "insufficient balance"},
        http_status=400,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        AsyncMock(side_effect=rej),
    )

    r = await http_client.post(
        "/api/v1/agent/trade/spot/limit-order",
        json={
            "userId": "92021",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "volume": "0.01",
            "price": "48000",
            "timeInForce": "GTC",
        },
    )
    assert r.status_code == 400
    assert r.json()["code"] == "AGENT_SPOT_ORDER_REJECTED"

    from chainup_agent.infrastructure.persistence.base import get_session_factory
    from sqlalchemy import select

    from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution

    factory = get_session_factory()
    async with factory() as session:
        row = (
            await session.execute(
                select(AgentExecution)
                .where(AgentExecution.user_id == "92021")
                .order_by(AgentExecution.created_at.desc())
                .limit(1)
            )
        ).scalar_one()
        assert row.state == "FAILED"
