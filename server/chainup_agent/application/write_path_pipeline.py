"""Write-path pipeline timeline — read_skill before Type A + causal event order (P-04/P-05)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_execution_events import (
    append_execution_timeline_event,
    list_timeline_events_for_execution,
)
from chainup_agent.application.resolved_prompt_binding import append_prompt_binding_resolved_if_missing
from chainup_agent.application.orchestration_steps import append_orchestration_step
from chainup_agent.application.runtime_skill_operation_spec import (
    EffectiveSkillOperationSpec,
    _SCENARIO_SKILL_ID,
    scenario_to_skill_id,
)
from chainup_agent.application.skill_operation_spec_store import get_effective_from_db
from chainup_agent.core.errors import AppError

_WRITE_SCENARIOS = frozenset(_SCENARIO_SKILL_ID.keys())


def is_write_path_scenario(scenario_id: str | None) -> bool:
    return bool(scenario_id and scenario_id.strip() in _WRITE_SCENARIOS)


def write_path_has_skill_spec(scenario_id: str | None) -> bool:
    return scenario_to_skill_id(scenario_id or "") is not None


async def append_execution_dispatched(
    session: AsyncSession,
    *,
    execution_id: str,
    user_id: str,
    scenario_id: str | None,
    source: str | None = None,
    channel: str | None = None,
) -> None:
    payload: dict[str, Any] = {
        "transitionTrigger": "execution.dispatched",
    }
    if scenario_id:
        payload["scenarioId"] = scenario_id
    if source:
        payload["source"] = source
    if channel:
        payload["channel"] = channel
    await append_execution_timeline_event(
        session,
        execution_id=execution_id,
        user_id=user_id,
        event_name="execution.dispatched",
        step_kind="dispatch",
        outcome="success",
        payload=payload,
    )


async def ensure_write_path_skill_spec_read(
    session: AsyncSession,
    *,
    execution_id: str,
    user_id: str,
    scenario_id: str,
    channel: str,
) -> EffectiveSkillOperationSpec:
    """Load PUBLISHED spec, emit ``read.skill`` orchestration step + ``agent.skill.spec_read``."""
    sid = scenario_id.strip()
    await append_prompt_binding_resolved_if_missing(
        session,
        execution_id=execution_id,
        user_id=user_id,
        scenario_id=sid,
    )
    skill_id = scenario_to_skill_id(sid)
    if not skill_id:
        raise AppError(
            "PROMPT_SKILL_REF_INVALID",
            f"写路径场景未登记 skillId：{sid}",
            status_code=403,
        )
    spec = await get_effective_from_db(session, skill_id=skill_id, scenario_id=sid)

    await append_orchestration_step(
        session,
        execution_id=execution_id,
        user_id=user_id,
        scenario_id=sid,
        step_key="read.skill",
        outcome="success",
        extra={"skillId": spec.skill_id, "skillSpecVersion": spec.skill_spec_version},
    )
    await append_execution_timeline_event(
        session,
        execution_id=execution_id,
        user_id=user_id,
        event_name="agent.skill.spec_read",
        step_kind="skill_spec",
        outcome="success",
        payload={
            "phase": "success",
            "skillId": spec.skill_id,
            "skillSpecVersion": spec.skill_spec_version,
            "specDigest": spec.spec_digest,
            "scenarioId": sid,
            "channel": channel,
            "transitionTrigger": "agent.skill.spec_read",
        },
    )
    return spec


async def append_confirmation_required(
    session: AsyncSession,
    *,
    execution_id: str,
    user_id: str,
    scenario_id: str,
    channel: str,
    confirm_kind: str = "type_a_inline",
    extra: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "scenarioId": scenario_id,
        "channel": channel,
        "confirmKind": confirm_kind,
        "transitionTrigger": "confirmation.required",
    }
    if extra:
        payload.update(extra)
    await append_execution_timeline_event(
        session,
        execution_id=execution_id,
        user_id=user_id,
        event_name="confirmation.required",
        step_kind="confirm_gate",
        outcome="success",
        payload=payload,
    )


async def ensure_write_path_skill_spec_read_if_missing(
    session: AsyncSession,
    *,
    execution_id: str,
    user_id: str,
    scenario_id: str,
    channel: str,
) -> EffectiveSkillOperationSpec | None:
    rows = await list_timeline_events_for_execution(session, execution_public_id=execution_id)
    if any(r.event_type == "agent.skill.spec_read" for r in rows):
        return None
    return await ensure_write_path_skill_spec_read(
        session,
        execution_id=execution_id,
        user_id=user_id,
        scenario_id=scenario_id,
        channel=channel,
    )


async def append_user_confirmed(
    session: AsyncSession,
    *,
    execution_id: str,
    user_id: str,
    scenario_id: str,
    channel: str,
    extra: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "scenarioId": scenario_id,
        "channel": channel,
        "transitionTrigger": "user.confirmed",
    }
    if extra:
        payload.update(extra)
    await append_execution_timeline_event(
        session,
        execution_id=execution_id,
        user_id=user_id,
        event_name="user.confirmed",
        step_kind="confirm",
        outcome="success",
        payload=payload,
    )


def assert_write_path_pipeline_order(events: list[dict[str, Any]]) -> None:
    """Port of Admin ``writePathPipelineOrder.ts``; delegates to eval runner."""
    from chainup_agent.application.eval_pipeline_write_order import (
        assert_eval_pipeline_write_order_positive,
    )

    assert_eval_pipeline_write_order_positive(events)
