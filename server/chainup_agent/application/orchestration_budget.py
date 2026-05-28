"""FR-AO06 — per-execution orchestration / tool-call budget enforcement."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.admin_ai_settings import ensure_gateway_defaults
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.models.agent_execution_event import AgentExecutionEvent

_BUDGET_CODE = "ORCHESTRATION_BUDGET_EXCEEDED"
_TOOL_STEP_KINDS = frozenset({"exchange_read", "exchange_write", "tool_call"})
_ORCH_STEP_KINDS = frozenset({"orchestration", "routing_note"})


async def load_orchestration_execution_budget(session: AsyncSession) -> dict[str, Any]:
    doc = await ensure_gateway_defaults(session)
    import json

    try:
        raw = json.loads(doc.payload_json)
    except (json.JSONDecodeError, TypeError):
        raw = {}
    bud = raw.get("orchestrationExecutionBudget")
    return bud if isinstance(bud, dict) else {}


async def _count_tool_like_events(session: AsyncSession, *, execution_id: str) -> int:
    eid = execution_id.strip()
    stmt = (
        select(func.count())
        .select_from(AgentExecutionEvent)
        .where(
            AgentExecutionEvent.execution_id == eid,
            or_(
                AgentExecutionEvent.step_kind.in_(tuple(_TOOL_STEP_KINDS)),
                AgentExecutionEvent.event_type.in_(
                    ("trading.exchange_public", "trading.exchange_private"),
                ),
            ),
        )
    )
    return int((await session.execute(stmt)).scalar_one())


async def _count_orchestration_step_events(session: AsyncSession, *, execution_id: str) -> int:
    eid = execution_id.strip()
    stmt = (
        select(func.count())
        .select_from(AgentExecutionEvent)
        .where(
            AgentExecutionEvent.execution_id == eid,
            or_(
                AgentExecutionEvent.step_kind.in_(tuple(_ORCH_STEP_KINDS)),
                AgentExecutionEvent.event_type == "agent.orchestration.step",
            ),
        )
    )
    return int((await session.execute(stmt)).scalar_one())


async def assert_execution_budget_allows_append(
    session: AsyncSession,
    *,
    execution_id: str,
    step_kind: str | None,
    event_name: str,
) -> None:
    """Raise ``ORCHESTRATION_BUDGET_EXCEEDED`` when configured caps would be exceeded."""
    eid = execution_id.strip()
    if not eid:
        return

    budget = await load_orchestration_execution_budget(session)
    max_tools = int(budget.get("maxToolCallsPerExecution") or 32)
    max_steps = int(budget.get("maxOrchestrationStepsPerExecution") or 32)

    sk = (step_kind or "").strip()
    en = event_name.strip()

    if sk in _TOOL_STEP_KINDS or en in ("trading.exchange_public", "trading.exchange_private"):
        current = await _count_tool_like_events(session, execution_id=eid)
        if current >= max_tools:
            raise AppError(
                code=_BUDGET_CODE,
                message="本 execution 工具调用次数已达编排预算上限。",
                status_code=422,
                details={
                    "executionId": eid,
                    "limit": max_tools,
                    "kind": "maxToolCallsPerExecution",
                },
            )

    if sk in _ORCH_STEP_KINDS or en == "agent.orchestration.step":
        current = await _count_orchestration_step_events(session, execution_id=eid)
        if current >= max_steps:
            raise AppError(
                code=_BUDGET_CODE,
                message="本 execution 编排步骤数已达预算上限。",
                status_code=422,
                details={
                    "executionId": eid,
                    "limit": max_steps,
                    "kind": "maxOrchestrationStepsPerExecution",
                },
            )
