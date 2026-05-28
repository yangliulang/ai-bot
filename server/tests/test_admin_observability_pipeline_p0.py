"""Pipeline P0 — admin observability tool-calls / llm (feature 2026-05-26--admin-observability)."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from chainup_agent.main import app


@pytest.mark.asyncio
async def test_observability_execution_not_found_tc02(
    http_client,
) -> None:
    eid = "exec_nonexistent_000"
    tools = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/tool-calls")
    assert tools.status_code == 404
    assert tools.json()["code"] == "AGENT_ADMIN_EXECUTION_NOT_FOUND"

    llm = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/llm")
    assert llm.status_code == 404
    assert llm.json()["code"] == "AGENT_ADMIN_EXECUTION_NOT_FOUND"


@pytest.mark.asyncio
async def test_observability_llm_empty_calls_tc05(http_client) -> None:
    accept = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={"userId": "9191", "scenarioId": "chat.faq", "channel": "telegram"},
    )
    assert accept.status_code == 200
    eid = accept.json()["executionId"]

    llm = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/llm")
    assert llm.status_code == 200
    assert llm.json().get("calls", []) == []


@pytest.mark.asyncio
async def test_observability_tool_calls_schema_tc04(
    http_client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from chainup_agent.application.agent_execution_events import append_execution_timeline_event
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    accept = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={"userId": "8282", "scenarioId": "chat.faq", "channel": "telegram"},
    )
    eid = accept.json()["executionId"]
    factory = get_session_factory()
    async with factory() as session:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id="8282",
            event_name="trading.exchange_private",
            step_kind="submit_order",
            outcome="success",
            payload={"methodPathSummary": "POST /sapi/v2/order", "httpStatus": 200},
        )
        await session.commit()

    tools = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/tool-calls")
    assert tools.status_code == 200
    item = tools.json()["items"][0]
    assert "invocationState" in item
    assert isinstance(item.get("summary"), dict)


@pytest.mark.asyncio
async def test_observability_admin_auth_required_tc07(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET", "test-jwt-secret-16b")
    reset_settings_cache()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get(
            "/api/v1/admin/observability/executions/exec_x/tool-calls",
        )
    assert r.status_code == 401
    assert r.json()["code"] == "ADMIN_CONSOLE_AUTH_REQUIRED"
