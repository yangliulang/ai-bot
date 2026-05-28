"""Execution detail tabs — task queue, runtime events, retries, recovery (Admin observability)."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_execution_events import list_timeline_events_for_execution
from chainup_agent.application.agent_trading_reconcile import trading_reconcile_status_for_execution
from chainup_agent.application.orchestration_flow_catalog import flow_by_scenario_id
from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution
from chainup_agent.infrastructure.persistence.models.agent_execution_event import (
    AgentExecutionEvent,
)

TaskState = Literal["PENDING", "RUNNING", "BLOCKED"]

_RECOVERY_TITLE_ZH = "恢复与对账"
_RECOVERY_BODY_ZH = (
    "从日志检索与时间线核对终态；人工恢复操作将在接口就绪后开放。"
)
_RETRY_TRANSIENT_ZH = "瞬时故障 · 可重试"
_RETRY_RECONCILE_ZH = "对账 / 终态待核对"

_RUNTIME_EVENT_PREFIXES = (
    "agent.tool.",
    "trading.exchange_",
    "trading.reconcile",
    "llm.",
    "prompt.",
    "agent.execution.",
    "agent.prompt.",
    "billing.",
    "confirmation.",
    "confirm.",
)

_RUNTIME_EVENT_EXACT = frozenset(
    {
        "execution.accept",
        "execution.finalize",
        "routing.read.failed",
    }
)


def _parse_payload(ev: AgentExecutionEvent) -> dict[str, Any]:
    try:
        raw = json.loads(ev.payload_json or "{}")
    except json.JSONDecodeError:
        return {}
    return raw if isinstance(raw, dict) else {}


def _orch_step_key(ev: AgentExecutionEvent) -> str | None:
    if ev.event_type != "agent.orchestration.step":
        return None
    sk = (ev.step_kind or "").strip()
    if sk and sk != "orchestration":
        return sk
    payload = _parse_payload(ev)
    key = payload.get("stepKey")
    return str(key).strip() if key else None


def _runtime_event_summary(ev: AgentExecutionEvent) -> str:
    payload = _parse_payload(ev)
    parts: list[str] = []
    if ev.outcome:
        parts.append(ev.outcome.upper())
    if ev.step_kind and ev.step_kind not in ("orchestration",):
        parts.append(ev.step_kind)
    for key in (
        "methodPathSummary",
        "appErrorCode",
        "transitionTrigger",
        "planNextStep",
        "exchangeOutcome",
        "resolutionStatus",
        "userVisibleError",
    ):
        val = payload.get(key)
        if val is not None and str(val).strip():
            parts.append(str(val).strip())
    if not parts and payload.get("stepLabelZh"):
        parts.append(str(payload["stepLabelZh"]))
    return " · ".join(parts) if parts else ev.event_type


def _is_runtime_excerpt_event(ev: AgentExecutionEvent) -> bool:
    en = ev.event_type
    if en == "agent.orchestration.step":
        return False
    if en in _RUNTIME_EVENT_EXACT:
        return True
    return any(en.startswith(p) for p in _RUNTIME_EVENT_PREFIXES)


def _retry_reason_for_event(
    ev: AgentExecutionEvent,
    *,
    still_unknown: bool,
    is_last: bool,
) -> str:
    en = ev.event_type
    payload = _parse_payload(ev)
    if en == "trading.reconcile":
        rs = str(payload.get("resolutionStatus") or ev.outcome or "").upper()
        if rs in ("UNKNOWN", "INCONCLUSIVE", "PARTIAL_FAILURE") or still_unknown:
            return _RETRY_RECONCILE_ZH
        return payload.get("neutralHint") or payload.get("userMessage") or _RETRY_RECONCILE_ZH
    if "retry" in en:
        return payload.get("reason") or payload.get("message") or _RETRY_TRANSIENT_ZH
    if en == "trading.exchange_private" and (ev.outcome or "").strip() == "unknown":
        return _RETRY_RECONCILE_ZH
    if payload.get("exchangeOutcome") == "unknown" or payload.get("appErrorCode") in (
        "AGENT_EXCHANGE_WRITE_UNKNOWN",
        "AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED",
    ):
        return _RETRY_RECONCILE_ZH
    if still_unknown and is_last:
        return _RETRY_RECONCILE_ZH
    return _RETRY_TRANSIENT_ZH


def _is_retry_related_event(ev: AgentExecutionEvent) -> bool:
    en = ev.event_type
    if "retry" in en:
        return True
    if en == "trading.reconcile":
        return True
    if en == "trading.exchange_private":
        if (ev.outcome or "").strip() == "unknown":
            return True
        payload = _parse_payload(ev)
        return payload.get("exchangeOutcome") == "unknown" or bool(
            payload.get("appErrorCode")
            in (
                "AGENT_EXCHANGE_WRITE_UNKNOWN",
                "AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED",
            )
        )
    return False


async def list_execution_task_queue(
    session: AsyncSession,
    *,
    execution: AgentExecution,
    events: list[AgentExecutionEvent],
) -> list[dict[str, Any]]:
    """Pending orchestration / write-path steps for the queue tab."""
    eid = execution.execution_id
    sid = (execution.scenario_id or "").strip()
    flow = flow_by_scenario_id(sid) if sid else None

    step_outcomes: dict[str, tuple[str, datetime]] = {}
    for ev in events:
        if ev.event_type != "agent.orchestration.step":
            continue
        key = _orch_step_key(ev)
        if not key:
            continue
        step_outcomes[key] = ((ev.outcome or "").strip().lower(), ev.created_at)

    items: list[dict[str, Any]] = []
    if flow is not None:
        first_open_idx: int | None = None
        for i, step in enumerate(flow.execution_steps):
            oc, at = step_outcomes.get(step.step_key, ("", execution.created_at))
            if oc == "success":
                continue
            if first_open_idx is None:
                first_open_idx = i
            if oc in ("fail", "failed", "error"):
                state: TaskState = "BLOCKED"
            elif first_open_idx == i and execution.state == "ACCEPTED":
                state = "RUNNING"
            else:
                state = "PENDING"
            items.append(
                {
                    "taskId": f"task-{i + 1:03d}",
                    "executionId": eid,
                    "state": state,
                    "scheduledAt": at,
                    "stepKey": step.step_key,
                    "stepLabelZh": step.label_zh,
                }
            )
    elif execution.state == "ACCEPTED":
        items.append(
            {
                "taskId": "task-001",
                "executionId": eid,
                "state": "RUNNING",
                "scheduledAt": execution.created_at,
                "stepKey": None,
                "stepLabelZh": "执行中",
            }
        )

    write_steps_seen: set[str] = set()
    catalog_keys = (
        {s.step_key for s in flow.execution_steps} if flow is not None else set()
    )
    for ev in events:
        if ev.event_type != "agent.execution.step":
            continue
        sk = (ev.step_kind or "").strip()
        if not sk or sk in catalog_keys or sk in write_steps_seen:
            continue
        write_steps_seen.add(sk)
        oc = (ev.outcome or "").strip().lower()
        if oc == "success" and execution.state != "ACCEPTED":
            continue
        state = "BLOCKED" if oc in ("fail", "failed", "error") else (
            "RUNNING" if execution.state == "ACCEPTED" and oc != "success" else "PENDING"
        )
        if oc == "success":
            continue
        items.append(
            {
                "taskId": f"task-w-{len(items) + 1:03d}",
                "executionId": eid,
                "state": state,
                "scheduledAt": ev.created_at,
                "stepKey": sk,
                "stepLabelZh": sk,
            }
        )

    return items


async def list_execution_runtime_events(
    session: AsyncSession,
    *,
    execution: AgentExecution,
    events: list[AgentExecutionEvent],
) -> list[dict[str, Any]]:
    del session  # events preloaded
    eid = execution.execution_id
    rows: list[dict[str, Any]] = []
    for ev in events:
        if not _is_runtime_excerpt_event(ev):
            continue
        rows.append(
            {
                "executionId": eid,
                "at": ev.created_at,
                "eventType": ev.event_type,
                "summary": _runtime_event_summary(ev),
                "seq": ev.seq,
            }
        )
    return rows


async def list_execution_retries(
    session: AsyncSession,
    *,
    execution: AgentExecution,
    events: list[AgentExecutionEvent],
) -> dict[str, Any]:
    del session
    retry_events = [ev for ev in events if _is_retry_related_event(ev)]
    still_unknown = any(
        (ev.event_type == "trading.exchange_private" and (ev.outcome or "") == "unknown")
        or (
            ev.event_type == "trading.reconcile"
            and (_parse_payload(ev).get("resolutionStatus") or "")
            in ("UNKNOWN", "INCONCLUSIVE", "PARTIAL_FAILURE")
        )
        for ev in events
    )
    items: list[dict[str, Any]] = []
    for i, ev in enumerate(retry_events):
        items.append(
            {
                "attempt": i + 1,
                "at": ev.created_at,
                "reason": _retry_reason_for_event(
                    ev,
                    still_unknown=still_unknown,
                    is_last=(i == len(retry_events) - 1),
                ),
                "eventType": ev.event_type,
                "seq": ev.seq,
            }
        )
    return {"retryCount": len(items), "items": items}


async def get_execution_recovery_view(
    session: AsyncSession,
    *,
    execution: AgentExecution,
    events: list[AgentExecutionEvent],
) -> dict[str, Any]:
    eid = execution.execution_id
    uid = execution.user_id
    recon = await trading_reconcile_status_for_execution(
        session=session,
        user_id=uid,
        execution_id=eid,
    )
    last_at: datetime | None = None
    last_seq = recon.get("lastReconcileAtSeq")
    if last_seq is not None:
        for ev in events:
            if ev.seq == last_seq:
                last_at = ev.created_at
                break

    return {
        "executionId": eid,
        "scenarioId": execution.scenario_id,
        "executionState": execution.state,
        "caseKind": recon.get("caseKind") or "UNSPECIFIED",
        "resolutionStatus": recon.get("resolutionStatus") or "PENDING",
        "stillUnknown": bool(recon.get("stillUnknown")),
        "lastReconcileAt": last_at,
        "lastReconcileAtSeq": last_seq,
        "reconcileId": recon.get("reconcileId"),
        "userMessage": recon.get("userMessage"),
        "hints": list(recon.get("hints") or []),
        "recoveryTitle": _RECOVERY_TITLE_ZH,
        "recoveryBody": _RECOVERY_BODY_ZH,
        "observabilitySearchPath": f"/observability?executionId={eid}",
        "reconcileApiHint": {
            "method": "GET",
            "path": "/api/v1/agent/trading/reconcile/status",
            "query": {"executionId": eid, "userId": uid},
        },
        "manualRetrySupported": False,
    }


async def build_execution_tabs_for_id(
    session: AsyncSession,
    *,
    execution_public_id: str,
) -> tuple[AgentExecution | None, list[AgentExecutionEvent]]:
    eid = execution_public_id.strip()
    row = await session.get(AgentExecution, eid)
    if row is None:
        return None, []
    events = await list_timeline_events_for_execution(session, execution_public_id=eid)
    return row, events
