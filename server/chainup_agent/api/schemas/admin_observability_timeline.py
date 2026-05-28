"""Admin observability timeline — FR-MC801 fragment (``ObservabilityTimelineResponse`` 同窗)."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from chainup_agent.infrastructure.persistence.models.agent_execution_event import (
    AgentExecutionEvent,
)


class ObservabilityTimelineItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ts: datetime
    event_name: str = Field(alias="eventName")
    execution_id: str | None = Field(default=None, alias="executionId")
    user_id: str | None = Field(default=None, alias="userId")
    summary: dict[str, Any] = Field(default_factory=dict)


class ObservabilityTimelineResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ObservabilityTimelineItem]


def _enrich_timeline_summary(event_name: str, summary: dict[str, Any]) -> dict[str, Any]:
    """Hoist governance fields for Admin / product-doc timeline mappers (SC-PM-22 / SC-OBS04)."""
    bind = summary.get("resolvedPromptBinding")
    if isinstance(bind, dict):
        summary.setdefault("promptBindingResolved", bind)
    if event_name == "agent.skill.spec_read":
        skill_read: dict[str, Any] = {}
        for key in ("skillId", "skillSpecVersion", "specDigest", "scenarioId", "phase"):
            if key in summary and summary[key] is not None:
                skill_read[key] = summary[key]
        if skill_read:
            summary.setdefault("skillSpecRead", skill_read)
    return summary


def observability_timeline_item_from_row(row: AgentExecutionEvent) -> ObservabilityTimelineItem:
    raw = row.payload_json or "{}"
    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            payload = {}
    except json.JSONDecodeError:
        payload = {}
    summary = _enrich_timeline_summary(row.event_type, dict(payload))
    if row.step_kind:
        summary.setdefault("stepKind", row.step_kind)
    if row.outcome:
        summary.setdefault("outcome", row.outcome)
    return ObservabilityTimelineItem(
        ts=row.created_at,
        eventName=row.event_type,
        executionId=row.execution_id,
        userId=row.user_id,
        summary=summary,
    )
