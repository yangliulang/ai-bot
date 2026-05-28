"""Tests for feature 2026-05-26--futures-cancel (POST …/trade/futures/cancel HTTP)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from chainup_agent.core.errors import AppError
from tests.test_futures_cancel_condition_trade import _bind_user_79

_CANCEL_PATH = "/api/v1/agent/trade/futures/cancel"
_CANCEL_BODY = {
    "userId": "79",
    "symbol": "BTC-USDT",
    "orderId": "259396989397942275",
}


@pytest.mark.asyncio
async def test_futures_cancel_tc02_unbound_user_403(http_client: AsyncClient) -> None:
    """TC-02 / AC-2: unbound userId → 403 AGENT_SUBACCOUNT_REQUIRED."""
    r = await http_client.post(
        _CANCEL_PATH,
        json={"userId": "99999902", "symbol": "BTC-USDT", "orderId": "111"},
    )
    assert r.status_code == 403
    assert r.json()["code"] == "AGENT_SUBACCOUNT_REQUIRED"


@pytest.mark.asyncio
async def test_futures_cancel_tc03_feature_futures_off_403(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-03 / AC-3: FEATURE_AGENT_FUTURES=false → 403 FEATURE_AGENT_FUTURES_OFF."""
    from chainup_agent.core.config import reset_settings_cache

    await _bind_user_79(http_client, monkeypatch, tmp_path)
    monkeypatch.setenv("CHAINUP_AGENT_FEATURE_AGENT_FUTURES", "false")
    reset_settings_cache()
    try:
        r = await http_client.post(_CANCEL_PATH, json=_CANCEL_BODY)
        assert r.status_code == 403
        assert r.json()["code"] == "FEATURE_AGENT_FUTURES_OFF"
    finally:
        monkeypatch.delenv("CHAINUP_AGENT_FEATURE_AGENT_FUTURES", raising=False)
        reset_settings_cache()


@pytest.mark.asyncio
async def test_futures_cancel_tc04_cancel_rejected_400(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-04 / AC-4: exchange cancel reject → 400 AGENT_FUTURES_CANCEL_REJECTED."""

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
    r = await http_client.post(_CANCEL_PATH, json=_CANCEL_BODY)
    assert r.status_code == 400
    assert r.json()["code"] == "AGENT_FUTURES_CANCEL_REJECTED"


@pytest.mark.asyncio
async def test_futures_cancel_tc05_validation_empty_symbol_422(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-05 / AC-5: empty symbol → 422 VALIDATION_ERROR."""
    await _bind_user_79(http_client, monkeypatch, tmp_path)
    r = await http_client.post(
        _CANCEL_PATH,
        json={"userId": "79", "symbol": "", "orderId": "259396989397942275"},
    )
    assert r.status_code == 422
    assert r.json()["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_futures_cancel_tc05_validation_empty_order_id_422(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-05 / AC-5: empty orderId → 422 VALIDATION_ERROR."""
    await _bind_user_79(http_client, monkeypatch, tmp_path)
    r = await http_client.post(
        _CANCEL_PATH,
        json={"userId": "79", "symbol": "BTC-USDT", "orderId": ""},
    )
    assert r.status_code == 422
    assert r.json()["code"] == "VALIDATION_ERROR"
