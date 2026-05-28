"""Instance-scoped observability log slices (FR-AM-L01–L03 · 基于 execution + timeline)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class InstanceConversationLogItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    execution_id: str = Field(alias="executionId")
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    channel: str | None = None
    state: str
    created_at: datetime = Field(alias="createdAt")
    note_preview: str | None = Field(default=None, alias="notePreview")
    observability_execution_path: str = Field(
        alias="observabilityExecutionPath",
        description="Admin Observability 执行详情相对路径（深链）",
    )


class InstanceToolLogItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    event_id: str = Field(alias="eventId")
    execution_id: str = Field(alias="executionId")
    event_name: str = Field(alias="eventName")
    step_kind: str | None = Field(default=None, alias="stepKind")
    outcome: str | None = None
    created_at: datetime = Field(alias="createdAt")
    summary: dict[str, Any] = Field(default_factory=dict)
    observability_timeline_path: str = Field(
        alias="observabilityTimelinePath",
        description="该执行的 Timeline 相对路径",
    )


class InstanceErrorLogItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    kind: Literal["execution_failed", "timeline_step_failed"]
    execution_id: str = Field(alias="executionId")
    created_at: datetime = Field(alias="createdAt")
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    channel: str | None = None
    state_or_outcome: str = Field(alias="stateOrOutcome")
    message: str | None = None
    observability_timeline_path: str = Field(alias="observabilityTimelinePath")


class InstanceConversationLogsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tab: Literal["conversations"] = "conversations"
    items: list[InstanceConversationLogItem]
    total: int
    observability_base_path: str = Field(
        default="/api/v1/admin/observability/executions",
        alias="observabilityBasePath",
    )


class InstanceToolLogsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tab: Literal["tools"] = "tools"
    items: list[InstanceToolLogItem]
    total: int
    observability_base_path: str = Field(
        default="/api/v1/admin/observability/executions",
        alias="observabilityBasePath",
    )


class InstanceErrorLogsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tab: Literal["errors"] = "errors"
    items: list[InstanceErrorLogItem]
    total: int
    observability_base_path: str = Field(
        default="/api/v1/admin/observability/executions",
        alias="observabilityBasePath",
    )
