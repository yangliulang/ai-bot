"""Admin observability execution detail tabs — queue / events / retries / recovery."""

from __future__ import annotations

import pytest

from chainup_agent.application.agent_execution_events import append_execution_timeline_event
from chainup_agent.infrastructure.persistence.base import get_session_factory


@pytest.mark.asyncio
async def test_execution_tabs_not_found(http_client) -> None:
    eid = "exec_tabs_missing_001"
    for suffix in ("queue", "events", "retries", "recovery"):
        r = await http_client.get(
            f"/api/v1/admin/observability/executions/{eid}/{suffix}",
        )
        assert r.status_code == 404
        assert r.json()["code"] == "AGENT_ADMIN_EXECUTION_NOT_FOUND"


@pytest.mark.asyncio
async def test_execution_queue_from_orchestration_steps(http_client) -> None:
    accept = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={
            "userId": "7001",
            "scenarioId": "read.market.ticker",
            "channel": "telegram",
        },
    )
    assert accept.status_code == 200
    eid = accept.json()["executionId"]
    factory = get_session_factory()
    async with factory() as session:
        from chainup_agent.application.orchestration_steps import append_orchestration_step

        await append_orchestration_step(
            session,
            execution_id=eid,
            user_id="7001",
            scenario_id="read.market.ticker",
            step_key="access.evaluate",
            outcome="success",
        )
        await session.commit()

    q = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/queue")
    assert q.status_code == 200
    items = q.json()["items"]
    assert items
    assert items[0]["state"] in ("PENDING", "RUNNING", "BLOCKED")
    assert "taskId" in items[0]
    assert items[0]["executionId"] == eid


@pytest.mark.asyncio
async def test_execution_runtime_events_and_retries(http_client) -> None:
    accept = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={"userId": "7002", "scenarioId": "chat.faq", "channel": "telegram"},
    )
    eid = accept.json()["executionId"]
    factory = get_session_factory()
    async with factory() as session:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id="7002",
            event_name="trading.exchange_private",
            step_kind="submit_order",
            outcome="unknown",
            payload={"appErrorCode": "AGENT_EXCHANGE_WRITE_UNKNOWN"},
        )
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id="7002",
            event_name="trading.reconcile",
            step_kind="reconcile",
            outcome="unknown",
            payload={"resolutionStatus": "UNKNOWN", "caseKind": "ORDER_UNKNOWN"},
        )
        await session.commit()

    ev = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/events")
    assert ev.status_code == 200
    types = {row["eventType"] for row in ev.json()["items"]}
    assert "trading.exchange_private" in types
    assert "trading.reconcile" in types
    assert "agent.orchestration.step" not in types

    ret = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/retries")
    assert ret.status_code == 200
    body = ret.json()
    assert body["retryCount"] >= 2
    assert body["items"][0]["attempt"] == 1
    assert "reason" in body["items"][0]


@pytest.mark.asyncio
async def test_execution_recovery_view(http_client) -> None:
    accept = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={"userId": "7003", "scenarioId": "chat.faq", "channel": "telegram"},
    )
    eid = accept.json()["executionId"]

    rec = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/recovery")
    assert rec.status_code == 200
    body = rec.json()
    assert body["executionId"] == eid
    assert body["recoveryTitle"]
    assert body["observabilitySearchPath"] == f"/observability?executionId={eid}"
    assert body["reconcileApiHint"]["path"] == "/api/v1/agent/trading/reconcile/status"
    assert body["manualRetrySupported"] is False
