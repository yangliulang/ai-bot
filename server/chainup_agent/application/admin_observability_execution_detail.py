"""FR-MC803 / FR-MC804 — execution-scoped tool-calls & LLM observability."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.infrastructure.persistence.models.agent_execution_event import (
    AgentExecutionEvent,
)

_TOOL_EVENT_TYPES = frozenset(
    {
        "trading.exchange_private",
        "trading.exchange_public",
        "agent.tool.call",
    }
)
_LLM_EVENT_PREFIX = "llm."


def _parse_payload(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _outcome_to_invocation_state(outcome: str | None) -> str:
    o = (outcome or "").strip().lower()
    if o in ("success", "ok", "succeeded"):
        return "SUCCESS"
    if o in ("fail", "failure", "failed", "error"):
        return "FAILED"
    if o == "unknown":
        return "RETRYING"
    return "EXECUTING"


def _tool_id_from_event(ev: AgentExecutionEvent, payload: dict[str, Any]) -> str:
    mp = (payload.get("methodPathSummary") or payload.get("method_path_summary") or "").strip()
    if mp:
        return mp[:128]
    sk = (ev.step_kind or "").strip()
    if sk:
        return sk[:128]
    return (ev.event_type or "tool")[:128]


async def list_tool_calls_for_execution(
    session: AsyncSession,
    *,
    execution_public_id: str,
) -> list[dict[str, Any]]:
    eid = execution_public_id.strip()
    stmt = (
        select(AgentExecutionEvent)
        .where(
            AgentExecutionEvent.execution_id == eid,
            AgentExecutionEvent.event_type.in_(_TOOL_EVENT_TYPES),
        )
        .order_by(AgentExecutionEvent.seq.asc())
    )
    rows = list((await session.execute(stmt)).scalars().all())
    items: list[dict[str, Any]] = []
    for ev in rows:
        payload = _parse_payload(ev.payload_json)
        phase = "success" if (ev.outcome or "").lower() in ("success", "ok") else "fail"
        if (ev.outcome or "").lower() == "unknown":
            phase = "fail"
        items.append(
            {
                "toolId": _tool_id_from_event(ev, payload),
                "toolCallSeq": ev.seq,
                "invocationState": _outcome_to_invocation_state(ev.outcome),
                "phase": phase,
                "durationMs": payload.get("durationMs"),
                "agentSubAccountId": payload.get("agentSubAccountId")
                or payload.get("exchangeSubAccountUserId"),
                "eventName": ev.event_type,
                "stepKind": ev.step_kind,
                "ts": ev.created_at,
                "summary": {
                    **payload,
                    **({"stepKind": ev.step_kind} if ev.step_kind else {}),
                    **({"outcome": ev.outcome} if ev.outcome else {}),
                },
            }
        )
    return items


async def list_llm_usage_for_execution(
    session: AsyncSession,
    *,
    execution_public_id: str,
) -> dict[str, Any]:
    eid = execution_public_id.strip()
    stmt = (
        select(AgentExecutionEvent)
        .where(
            AgentExecutionEvent.execution_id == eid,
            AgentExecutionEvent.event_type.like("llm.%"),
        )
        .order_by(AgentExecutionEvent.seq.asc())
    )
    rows = list((await session.execute(stmt)).scalars().all())
    calls: list[dict[str, Any]] = []
    primary_model: str | None = None
    for ev in rows:
        payload = _parse_payload(ev.payload_json)
        model = (
            (payload.get("gatewayModelId") or payload.get("gateway_model_id") or "")
            .strip()
            or None
        )
        if model and primary_model is None:
            primary_model = model
        calls.append(
            {
                "eventName": ev.event_type,
                "toolCallSeq": ev.seq,
                "ts": ev.created_at,
                "modelId": model,
                "gatewayModelId": model,
                "gatewayUpstreamModel": payload.get("gatewayUpstreamModel")
                or payload.get("gateway_upstream_model"),
                "gatewayProviderId": payload.get("gatewayProviderId")
                or payload.get("gateway_provider_id"),
                "outcome": ev.outcome,
                "stepKind": ev.step_kind,
                "scenarioId": payload.get("scenarioId"),
                "promptPackVersion": payload.get("promptPackVersion"),
                "inputTokens": payload.get("inputTokens"),
                "outputTokens": payload.get("outputTokens"),
                "totalTokens": payload.get("totalTokens"),
            }
        )
    return {
        "modelId": primary_model,
        "inputTokens": None,
        "outputTokens": None,
        "totalTokens": None,
        "calls": calls,
    }
