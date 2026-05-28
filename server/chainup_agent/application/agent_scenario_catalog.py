"""Agent scenarioId registry — shared by GET /scenarios and intent policy.

Built from ``orchestration_flow_catalog`` (Phase 2 · FR-AO01 执行流程登记).
"""

from __future__ import annotations

from chainup_agent.api.schemas.agent_runtime import ExecutionFlowStepOut, ScenarioListItem
from chainup_agent.application.orchestration_flow_catalog import (
    ORCHESTRATION_FLOW_CATALOG,
    ORCHESTRATION_FLOW_VERSION,
    ScenarioOrchestrationFlow,
    flow_by_scenario_id,
)

ORCHESTRATION_REGISTRY_VERSION = ORCHESTRATION_FLOW_VERSION


def _flow_to_list_item(flow: ScenarioOrchestrationFlow) -> ScenarioListItem:
    return ScenarioListItem(
        scenario_id=flow.scenario_id,
        summary=flow.flow_summary,
        flow_summary=flow.flow_summary,
        readiness=flow.readiness,
        title=flow.title,
        category=flow.category,
        risk_level=flow.risk_level,
        closure_status=flow.closure_status,
        execution_steps=[
            ExecutionFlowStepOut(
                step_key=st.step_key,
                label_zh=st.label_zh,
                order=st.order,
            )
            for st in flow.execution_steps
        ],
    )


def scenario_to_detail_dict(flow: ScenarioOrchestrationFlow) -> dict:
    return {
        "scenarioId": flow.scenario_id,
        "title": flow.title,
        "category": flow.category,
        "riskLevel": flow.risk_level,
        "readiness": flow.readiness,
        "closureStatus": flow.closure_status,
        "flowSummary": flow.flow_summary,
        "summary": flow.flow_summary,
        "flowAnchor": flow.flow_anchor,
        "specRefs": list(flow.spec_refs),
        "promptBindingHint": flow.prompt_binding_hint,
        "executionSteps": [
            {"stepKey": st.step_key, "labelZh": st.label_zh, "order": st.order}
            for st in flow.execution_steps
        ],
        "orchestrationRegistryVersion": ORCHESTRATION_REGISTRY_VERSION,
    }


AGENT_SCENARIO_CATALOG: tuple[ScenarioListItem, ...] = tuple(
    _flow_to_list_item(f) for f in ORCHESTRATION_FLOW_CATALOG
)


def scenario_readiness_map() -> dict[str, str]:
    return {row.scenario_id: row.readiness for row in AGENT_SCENARIO_CATALOG}


def registered_scenario_ids() -> frozenset[str]:
    return frozenset(row.scenario_id for row in AGENT_SCENARIO_CATALOG)


__all__ = [
    "AGENT_SCENARIO_CATALOG",
    "ORCHESTRATION_REGISTRY_VERSION",
    "flow_by_scenario_id",
    "registered_scenario_ids",
    "scenario_readiness_map",
    "scenario_to_detail_dict",
]
