"""Emit ``agent.orchestration.step`` timeline rows (FR-AO05 slice)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_execution_events import append_execution_timeline_event
from chainup_agent.application.orchestration_flow_catalog import flow_by_scenario_id

ORCHESTRATION_VERSION_INTENT = "intent-router.policy.v2"
ORCHESTRATION_VERSION_RUNTIME = "orchestration.runtime.v1"

_READ_STEP_BY_SCENARIO: dict[str, str] = {
    "read.market.ticker": "read.market",
    "read.market.depth": "read.depth",
    "read.market.trades": "read.trades",
    "read.account.balance": "read.balance",
    "wealth.holdings_read": "read.wealth",
    "trade.spot.open_orders": "read.orders",
}


async def append_routing_orchestration_steps(
    session: AsyncSession,
    *,
    execution_id: str,
    user_id: str,
    scenario_id: str,
    outcome: str = "success",
) -> None:
    """Emit catalog steps for a routing/execute turn (read paths + summarize)."""
    sid = scenario_id.strip()
    if not sid:
        return

    await append_orchestration_step(
        session,
        execution_id=execution_id,
        user_id=user_id,
        scenario_id=sid,
        step_key="access.evaluate",
        outcome=outcome,
    )
    read_key = _READ_STEP_BY_SCENARIO.get(sid)
    if read_key:
        await append_orchestration_step(
            session,
            execution_id=execution_id,
            user_id=user_id,
            scenario_id=sid,
            step_key=read_key,
            outcome=outcome,
        )
    if outcome == "success":
        await append_orchestration_step(
            session,
            execution_id=execution_id,
            user_id=user_id,
            scenario_id=sid,
            step_key="summarize.return",
            outcome=outcome,
        )


async def append_orchestration_step(
    session: AsyncSession,
    *,
    execution_id: str,
    user_id: str,
    scenario_id: str,
    step_key: str,
    outcome: str = "success",
    orchestration_version: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Record one orchestration step against the frozen flow catalog."""
    sid = scenario_id.strip()
    flow = flow_by_scenario_id(sid)
    label = step_key
    if flow is not None:
        for st in flow.execution_steps:
            if st.step_key == step_key:
                label = st.label_zh
                break

    payload: dict[str, Any] = {
        "scenarioId": sid,
        "orchestrationVersion": orchestration_version or ORCHESTRATION_VERSION_RUNTIME,
        "stepKey": step_key,
        "stepLabelZh": label,
        "transitionTrigger": f"orchestration.step.{step_key}",
    }
    if flow is not None:
        payload["flowSummary"] = flow.flow_summary
    if extra:
        payload.update(extra)

    await append_execution_timeline_event(
        session,
        execution_id=execution_id,
        user_id=user_id,
        event_name="agent.orchestration.step",
        step_kind="orchestration",
        outcome=outcome,
        payload=payload,
    )


async def append_intent_orchestration_step(
    session: AsyncSession,
    *,
    execution_id: str | None,
    user_id: str,
    scenario_id: str | None,
) -> None:
    if not execution_id or not scenario_id:
        return
    await append_orchestration_step(
        session,
        execution_id=execution_id,
        user_id=user_id,
        scenario_id=scenario_id,
        step_key="intent.route",
        orchestration_version=ORCHESTRATION_VERSION_INTENT,
    )
