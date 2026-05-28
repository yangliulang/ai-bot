"""Catalog alignment with ``runtime-freeze`` §3 write-path minimum DAG (OP-AO3)."""

from __future__ import annotations

from chainup_agent.application.orchestration_flow_catalog import (
    ScenarioOrchestrationFlow,
    flow_by_scenario_id,
)

FREEZE_WRITE_SCENARIO_IDS: tuple[str, ...] = (
    "trade.spot.limit_order",
    "trade.spot.flash_convert",
    "trade.spot.amend_limit_order",
)

_FREEZE_SUBSEQUENCE: tuple[str, ...] = (
    "read.skill",
    "validate.slots",
    "confirm.type_a",
    "exchange.write",
)


def _confirm_or_write_step_key(step_key: str) -> bool:
    return step_key.startswith("confirm.") or step_key.startswith("exchange.")


def assert_read_skill_before_confirm_write(flow: ScenarioOrchestrationFlow) -> None:
    """AC-1: ``read.skill`` order strictly before first confirm/write step."""
    read_order: int | None = None
    first_gate_order: int | None = None
    for step in flow.execution_steps:
        if step.step_key == "read.skill":
            read_order = step.order
        elif _confirm_or_write_step_key(step.step_key) and first_gate_order is None:
            first_gate_order = step.order
    if read_order is None:
        raise AssertionError(f"{flow.scenario_id}: missing read.skill in executionSteps")
    if first_gate_order is None:
        raise AssertionError(f"{flow.scenario_id}: missing confirm/write step in executionSteps")
    if read_order >= first_gate_order:
        raise AssertionError(
            f"{flow.scenario_id}: read.skill order {read_order} must be < "
            f"first confirm/write order {first_gate_order}"
        )


def assert_freeze_subsequence_present(flow: ScenarioOrchestrationFlow) -> None:
    """AC-6: catalog contains read.skill → validate → confirm → write subsequence."""
    keys = [s.step_key for s in flow.execution_steps]
    pos = 0
    for required in _FREEZE_SUBSEQUENCE:
        try:
            idx = keys.index(required, pos)
        except ValueError as exc:
            raise AssertionError(
                f"{flow.scenario_id}: missing freeze §3 step {required!r} after position {pos}"
            ) from exc
        pos = idx + 1


def assert_all_freeze_write_scenarios_aligned() -> None:
    for sid in FREEZE_WRITE_SCENARIO_IDS:
        flow = flow_by_scenario_id(sid)
        if flow is None:
            raise AssertionError(f"missing catalog entry for {sid}")
        assert_read_skill_before_confirm_write(flow)
        assert_freeze_subsequence_present(flow)


def execution_steps_for_api(flow: ScenarioOrchestrationFlow) -> list[dict[str, int | str]]:
    return [
        {"stepKey": s.step_key, "labelZh": s.label_zh, "order": s.order}
        for s in flow.execution_steps
    ]
