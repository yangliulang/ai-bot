"""Phase 2 orchestration flow catalog, scenarios API, policy, budget."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from chainup_agent.application.agent_execution_events import append_execution_timeline_event
from chainup_agent.application.orchestration_flow_catalog import (
    ORCHESTRATION_FLOW_CATALOG,
    ORCHESTRATION_FLOW_VERSION,
    flow_by_scenario_id,
)
from chainup_agent.core.errors import AppError


def test_flow_catalog_has_execution_steps() -> None:
    assert len(ORCHESTRATION_FLOW_CATALOG) >= 12
    ticker = flow_by_scenario_id("read.market.ticker")
    assert ticker is not None
    assert ticker.flow_summary == "分析 → 读行情 → 返回结果"
    keys = [s.step_key for s in ticker.execution_steps]
    assert keys == ["intent.route", "access.evaluate", "read.market", "summarize.return"]


def test_flow_catalog_version() -> None:
    assert ORCHESTRATION_FLOW_VERSION == "2026.05-orc-v1"


@pytest.mark.asyncio
async def test_runtime_scenarios_list_phase2_fields(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/agent/scenarios")
    assert r.status_code == 200
    body = r.json()
    assert body.get("orchestrationRegistryVersion") == "2026.05-orc-v1"
    ticker = next(s for s in body["scenarios"] if s["scenarioId"] == "read.market.ticker")
    assert ticker.get("flowSummary") == "分析 → 读行情 → 返回结果"
    assert ticker.get("closureStatus") == "FROZEN"
    steps = ticker.get("executionSteps") or []
    assert len(steps) >= 3
    assert steps[0]["stepKey"] == "intent.route"


@pytest.mark.asyncio
async def test_runtime_scenario_detail(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/agent/scenarios/read.market.ticker")
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "read.market.ticker"
    assert body["flowSummary"] == "分析 → 读行情 → 返回结果"
    assert body.get("orchestrationRegistryVersion") == "2026.05-orc-v1"
    assert body.get("specRefs")


@pytest.mark.asyncio
async def test_runtime_scenario_detail_not_found(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/agent/scenarios/not.a.real.scenario")
    assert r.status_code == 404
    assert r.json()["code"] == "AGENT_SCENARIO_NOT_FOUND"


@pytest.mark.asyncio
async def test_admin_orchestration_policy(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/admin/orchestration/policy")
    assert r.status_code == 200
    body = r.json()
    assert body.get("orchestrationRegistryVersion") == "2026.05-orc-v1"
    assert body.get("budgetExceededStableCode") == "ORCHESTRATION_BUDGET_EXCEEDED"
    assert isinstance(body.get("maxToolCalls"), int)
    assert isinstance(body.get("maxOrchestrationSteps"), int)
    assert body.get("engineeringSpecRefs")


@pytest.mark.asyncio
async def test_orchestration_budget_exceeded() -> None:
    from chainup_agent.application.orchestration_budget import assert_execution_budget_allows_append
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    factory = get_session_factory()
    async with factory() as db_session:
        eid = "exec_budget_test_001"
        uid = "u_budget"
        for _ in range(32):
            await append_execution_timeline_event(
                db_session,
                execution_id=eid,
                user_id=uid,
                event_name="agent.orchestration.step",
                step_kind="orchestration",
                payload={"scenarioId": "read.market.ticker", "stepKey": "intent.route"},
            )
        with pytest.raises(AppError) as exc:
            await assert_execution_budget_allows_append(
                db_session,
                execution_id=eid,
                step_kind="orchestration",
                event_name="agent.orchestration.step",
            )
        assert exc.value.code == "ORCHESTRATION_BUDGET_EXCEEDED"
