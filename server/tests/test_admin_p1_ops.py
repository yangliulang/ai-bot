"""P1 Admin — observability tool-calls/llm · instance I02/I04/I05."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.test_api import _init_binding_sqlite, _mock_probe_ok


@pytest.mark.asyncio
async def test_observability_tool_calls_and_llm(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from chainup_agent.application.agent_execution_events import append_execution_timeline_event
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    accept = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={"userId": "8181", "scenarioId": "chat.faq", "channel": "telegram"},
    )
    assert accept.status_code == 200
    eid = accept.json()["executionId"]

    factory = get_session_factory()
    async with factory() as session:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id="8181",
            event_name="trading.exchange_private",
            step_kind="submit_order",
            outcome="success",
            payload={"methodPathSummary": "POST /sapi/v2/order", "httpStatus": 200},
        )
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id="8181",
            event_name="llm.chat.faq",
            step_kind="chat_faq",
            outcome="success",
            payload={"gatewayModelId": "gpt-4.1-mini", "scenarioId": "chat.faq"},
        )
        await session.commit()

    tools = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/tool-calls")
    assert tools.status_code == 200
    titems = tools.json()["items"]
    assert len(titems) == 1
    assert titems[0]["invocationState"] == "SUCCESS"
    assert "POST /sapi/v2/order" in titems[0]["toolId"]

    llm = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/llm")
    assert llm.status_code == 200
    body = llm.json()
    assert body["modelId"] == "gpt-4.1-mini"
    assert len(body["calls"]) == 1
    assert body["calls"][0]["eventName"] == "llm.chat.faq"


@pytest.mark.asyncio
async def test_admin_instance_i02_i04_i05(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)

    create = await http_client.post(
        "/api/v1/admin/agents/instances",
        json={
            "telegramUserId": "88001",
            "exchangeSubAccountUserId": "sub_88001",
            "templateId": "tmpl_test",
        },
    )
    assert create.status_code == 201
    inst_id = create.json()["instanceId"]
    assert str(inst_id).startswith("inst_")

    dup = await http_client.post(
        "/api/v1/admin/agents/instances",
        json={"telegramUserId": "88001"},
    )
    assert dup.status_code == 422
    assert dup.json()["code"] == "AGENT_QUOTA_EXCEEDED"

    patch = await http_client.patch(
        f"/api/v1/admin/agents/instances/{inst_id}",
        json={"instanceOverrides": {"preferredLanguage": "zh-Hans"}},
    )
    assert patch.status_code == 200
    assert patch.json()["instanceOverrides"]["preferredLanguage"] == "zh-Hans"

    bad_patch = await http_client.patch(
        f"/api/v1/admin/agents/instances/{inst_id}",
        json={"instanceOverrides": {"secretApiKey": "x"}},
    )
    assert bad_patch.status_code == 422
    assert bad_patch.json()["code"] == "VALIDATION_ERROR"
    assert "secretApiKey" in bad_patch.json()["details"]["unknownKeys"]

    bind = await http_client.post(
        "/api/v1/admin/agents/instances/{0}/binding".format(inst_id),
        json={"subAccountId": "sub_88001_rebound"},
    )
    assert bind.status_code == 200
    assert bind.json()["exchangeSubAccountUserId"] == "sub_88001_rebound"

    bind_api = await http_client.post(
        "/api/v1/me/agent/bindings/trading-api",
        json={
            "openapiBaseUrl": "https://openapi.example.invalid",
            "apiKey": "k" * 8,
            "apiSecret": "s" * 8,
            "idempotencyKey": "idem-p1-88001",
            "subAccountId": "sub_88001_rebound",
            "telegram": {"tg_id": "88001"},
        },
    )
    assert bind_api.status_code == 200

    det = await http_client.get(f"/api/v1/admin/agents/instances/{inst_id}")
    assert det.status_code == 200
    assert det.json()["tradingApiBindingStatus"] == "BOUND"

    unbind = await http_client.delete(f"/api/v1/admin/agents/instances/{inst_id}/binding")
    assert unbind.status_code == 204

    det2 = await http_client.get(f"/api/v1/admin/agents/instances/{inst_id}")
    assert det2.json()["tradingApiBindingStatus"] == "NONE"
    assert det2.json()["instanceId"] == inst_id


@pytest.mark.asyncio
async def test_admin_instance_i02_global_off(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_AGENT_RUNTIME_GLOBAL_DISABLED", "true")
    reset_settings_cache()

    blocked = await http_client.post(
        "/api/v1/admin/agents/instances",
        json={"telegramUserId": "88009999"},
    )
    assert blocked.status_code == 422
    assert blocked.json()["code"] == "AGENT_GLOBAL_OFF"
