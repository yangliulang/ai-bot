"""Runtime-freeze §3 catalog/API alignment — 2026-05-28--pipeline-eval-orchestration-align."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from chainup_agent.application.orchestration_freeze_align import (
    FREEZE_WRITE_SCENARIO_IDS,
    assert_all_freeze_write_scenarios_aligned,
    assert_freeze_subsequence_present,
    assert_read_skill_before_confirm_write,
)
from chainup_agent.application.orchestration_flow_catalog import flow_by_scenario_id


@pytest.mark.parametrize("scenario_id", FREEZE_WRITE_SCENARIO_IDS)
def test_catalog_read_skill_before_confirm_write(scenario_id: str) -> None:
    flow = flow_by_scenario_id(scenario_id)
    assert flow is not None
    assert_read_skill_before_confirm_write(flow)
    assert_freeze_subsequence_present(flow)


def test_all_freeze_write_scenarios_aligned() -> None:
    assert_all_freeze_write_scenarios_aligned()


@pytest.mark.asyncio
@pytest.mark.parametrize("scenario_id", FREEZE_WRITE_SCENARIO_IDS)
async def test_scenarios_api_freeze_step_order(
    http_client: AsyncClient,
    scenario_id: str,
) -> None:
    r = await http_client.get(f"/api/v1/agent/scenarios/{scenario_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == scenario_id
    steps = body.get("executionSteps") or []
    assert steps
    read_order = next(s["order"] for s in steps if s["stepKey"] == "read.skill")
    gate_orders = [
        s["order"]
        for s in steps
        if s["stepKey"].startswith("confirm.") or s["stepKey"].startswith("exchange.")
    ]
    assert gate_orders
    assert read_order < min(gate_orders)


@pytest.mark.asyncio
async def test_orchestration_policy_includes_runtime_freeze_ref(
    http_client: AsyncClient,
) -> None:
    r = await http_client.get("/api/v1/admin/orchestration/policy")
    assert r.status_code == 200
    refs = r.json().get("engineeringSpecRefs") or []
    assert any("runtime-freeze" in ref and "§3" in ref for ref in refs)
