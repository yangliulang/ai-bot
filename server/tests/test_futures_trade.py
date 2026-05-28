"""Phase 2.3 — futures order HTTP tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_futures_order_http_market_success(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    async def fake_futures_order(**kwargs: object) -> dict:
        _ = kwargs
        return {
            "orderIdString": "9001",
            "clientOrderId": "cu_agent_test",
            "status": "NEW",
            "symbol": "BTC_USDT",
            "side": "BUY",
            "type": "MARKET",
        }

    monkeypatch.setattr(
        "chainup_agent.application.agent_futures_trade.post_signed_futures_order_json",
        fake_futures_order,
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
            "telegram": {"tg_id": "77"},
        },
    )
    assert c.status_code == 200

    r = await http_client.post(
        "/api/v1/agent/trade/futures/order",
        json={
            "userId": "77",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "orderType": "MARKET",
            "volume": "1",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.futures.market_order"
    assert body["orderIdString"] == "9001"
    assert body["exchangeOrderPreview"]["symbol"] == "BTC_USDT"


@pytest.mark.asyncio
async def test_futures_order_feature_off(http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_FEATURE_AGENT_FUTURES", "false")
    reset_settings_cache()
    r = await http_client.post(
        "/api/v1/agent/trade/futures/order",
        json={
            "userId": "1",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "orderType": "MARKET",
            "volume": "1",
        },
    )
    assert r.status_code == 403
    assert r.json()["code"] == "FEATURE_AGENT_FUTURES_OFF"


@pytest.mark.asyncio
async def test_scenarios_futures_readiness_ready(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/agent/scenarios")
    assert r.status_code == 200
    by_id = {s["scenarioId"]: s for s in r.json()["scenarios"]}
    assert by_id["trade.futures.market_order"]["readiness"] == "ready"
    assert by_id["trade.futures.limit_order"]["readiness"] == "ready"
    assert by_id["margin.cross.market_order"]["readiness"] == "ready"
    assert by_id["margin.cross.limit_order"]["readiness"] == "ready"
    assert by_id["automation.condition_order"]["readiness"] == "ready"


@pytest.mark.asyncio
async def test_telegram_webhook_callback_futures_market_confirm(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock
    from urllib.parse import quote

    from chainup_agent.application.telegram_flash_pending import create_futures_market_pending
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
                "telegram": {"tg_id": "1004"},
            },
        )
    ).status_code == 200

    token = ""
    factory = get_session_factory()
    async with factory() as session:
        token = await create_futures_market_pending(
            session,
            telegram_user_id=1004,
            chat_id=444444,
            symbol="BTC-USDT",
            side="BUY",
            quantity="0.01",
            open_close="OPEN",
        )
        await session.commit()

    bot_tok = "configured:eeeeeeeeeeeeeeeeeeeeeeeeeeee"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    reset_settings_cache()

    mocked = AsyncMock(return_value={"ok": True, "result": {}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_callback_handler.call_telegram_bot_api",
        mocked,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_futures_trade.post_signed_futures_order_json",
        AsyncMock(
            return_value={
                "orderIdString": "8001",
                "clientOrderId": "cu_agent_futures_cb",
                "status": "NEW",
                "symbol": "BTC_USDT",
                "side": "BUY",
                "type": "MARKET",
            }
        ),
    )

    enc = quote(bot_tok, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 44,
            "callback_query": {
                "id": "cq-fm1",
                "from": {"id": 1004, "is_bot": False},
                "message": {"message_id": 5, "chat": {"id": 444444, "type": "private"}},
                "data": f"ump{token}",
            },
        },
    )
    assert r.status_code == 200
    methods = [c.args[1] for c in mocked.await_args_list if len(c.args) >= 2]
    assert "answerCallbackQuery" in methods
    assert "sendMessage" in methods

    from sqlalchemy import select

    from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution

    factory = get_session_factory()
    async with factory() as session:
        res = await session.execute(
            select(AgentExecution.execution_id)
            .where(AgentExecution.user_id == "1004")
            .order_by(AgentExecution.created_at.desc())
            .limit(1)
        )
        eid_row = res.scalar_one()
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid_row}/timeline")
    assert tl.status_code == 200
    titems = tl.json()["items"]
    step_events = [x for x in titems if x["eventName"] == "agent.execution.step"]
    assert len(step_events) == 2
    assert [x["summary"].get("stepKind") for x in step_events] == [
        "confirm_accept",
        "submit_order",
    ]
    assert titems[-1]["eventName"] == "trading.exchange_private"
    ob = titems[-1]["summary"].get("orderRequest") or {}
    assert ob.get("type") == "MARKET"
