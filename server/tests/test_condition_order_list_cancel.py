"""Tests for feature 2026-05-26--condition-order-list-cancel (condition orders read/cancel HTTP)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from chainup_agent.core.errors import AppError
from tests.test_futures_cancel_condition_trade import _bind_user_79


@pytest.mark.asyncio
async def test_condition_list_cancel_tc04_unbound_user_403(
    http_client: AsyncClient,
) -> None:
    """TC-04 / AC-4: unbound userId → 403 AGENT_SUBACCOUNT_REQUIRED."""
    uid = "99999901"
    r_get = await http_client.get(
        "/api/v1/agent/trade/futures/condition-orders",
        params={"userId": uid},
    )
    assert r_get.status_code == 403
    assert r_get.json()["code"] == "AGENT_SUBACCOUNT_REQUIRED"

    r_post = await http_client.post(
        "/api/v1/agent/trade/futures/cancel-condition",
        json={"userId": uid, "symbol": "BTC-USDT", "orderId": "111"},
    )
    assert r_post.status_code == 403
    assert r_post.json()["code"] == "AGENT_SUBACCOUNT_REQUIRED"


@pytest.mark.asyncio
async def test_condition_list_cancel_tc05_feature_futures_off_403(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-05 / AC-5: FEATURE_AGENT_FUTURES=false → 403 FEATURE_AGENT_FUTURES_OFF."""
    from chainup_agent.core.config import reset_settings_cache

    await _bind_user_79(http_client, monkeypatch, tmp_path)
    monkeypatch.setenv("CHAINUP_AGENT_FEATURE_AGENT_FUTURES", "false")
    reset_settings_cache()
    try:
        r_get = await http_client.get(
            "/api/v1/agent/trade/futures/condition-orders",
            params={"userId": "79"},
        )
        assert r_get.status_code == 403
        assert r_get.json()["code"] == "FEATURE_AGENT_FUTURES_OFF"

        r_post = await http_client.post(
            "/api/v1/agent/trade/futures/cancel-condition",
            json={"userId": "79", "symbol": "BTC-USDT", "orderId": "111"},
        )
        assert r_post.status_code == 403
        assert r_post.json()["code"] == "FEATURE_AGENT_FUTURES_OFF"
    finally:
        monkeypatch.delenv("CHAINUP_AGENT_FEATURE_AGENT_FUTURES", raising=False)
        reset_settings_cache()


@pytest.mark.asyncio
async def test_condition_list_cancel_tc06_open_orders_failed_502(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-06 / AC-6: openOrders failure → 502 AGENT_FUTURES_OPEN_ORDERS_FAILED."""

    async def fail_open(**kwargs: object) -> list:
        _ = kwargs
        raise AppError(
            code="AGENT_FUTURES_OPEN_ORDERS_FAILED",
            message="查询合约当前委托未成功",
            status_code=502,
        )

    monkeypatch.setattr(
        "chainup_agent.application.agent_futures_trade.fetch_signed_futures_open_orders_json",
        fail_open,
    )
    await _bind_user_79(http_client, monkeypatch, tmp_path)
    r = await http_client.get(
        "/api/v1/agent/trade/futures/condition-orders",
        params={"userId": "79"},
    )
    assert r.status_code == 502
    assert r.json()["code"] == "AGENT_FUTURES_OPEN_ORDERS_FAILED"


@pytest.mark.asyncio
async def test_condition_list_cancel_tc07_cancel_rejected_400(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-07 / AC-7: exchange cancel reject → 400 AGENT_FUTURES_CANCEL_REJECTED."""

    async def reject_cancel(**kwargs: object) -> dict:
        _ = kwargs
        raise AppError(
            code="AGENT_FUTURES_CANCEL_REJECTED",
            message="合约撤单被交易所拒绝",
            status_code=400,
            details={"exchange_code": "10001"},
        )

    monkeypatch.setattr(
        "chainup_agent.application.agent_futures_trade.post_signed_futures_cancel_json",
        reject_cancel,
    )
    await _bind_user_79(http_client, monkeypatch, tmp_path)
    r = await http_client.post(
        "/api/v1/agent/trade/futures/cancel-condition",
        json={"userId": "79", "symbol": "BTC-USDT", "orderId": "111"},
    )
    assert r.status_code == 400
    assert r.json()["code"] == "AGENT_FUTURES_CANCEL_REJECTED"
