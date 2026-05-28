"""Admin execution detail tabs — queue / runtime events / retries / recovery."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

TaskQueueState = Literal["PENDING", "RUNNING", "BLOCKED"]


class ExecutionTaskQueueItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(alias="taskId")
    execution_id: str = Field(alias="executionId")
    state: TaskQueueState
    scheduled_at: datetime = Field(alias="scheduledAt")
    step_key: str | None = Field(default=None, alias="stepKey")
    step_label_zh: str | None = Field(default=None, alias="stepLabelZh")


class ExecutionTaskQueueResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ExecutionTaskQueueItem]


class ExecutionRuntimeEventItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    execution_id: str = Field(alias="executionId")
    at: datetime
    event_type: str = Field(alias="eventType")
    summary: str
    seq: int | None = None


class ExecutionRuntimeEventsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ExecutionRuntimeEventItem]


class ExecutionRetryItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    attempt: int
    at: datetime
    reason: str
    event_type: str | None = Field(default=None, alias="eventType")
    seq: int | None = None


class ExecutionRetriesResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    retry_count: int = Field(alias="retryCount")
    items: list[ExecutionRetryItem]


class ExecutionRecoveryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    execution_id: str = Field(alias="executionId")
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    execution_state: str = Field(alias="executionState")
    case_kind: str = Field(alias="caseKind")
    resolution_status: str = Field(alias="resolutionStatus")
    still_unknown: bool = Field(alias="stillUnknown")
    last_reconcile_at: datetime | None = Field(default=None, alias="lastReconcileAt")
    last_reconcile_at_seq: int | None = Field(default=None, alias="lastReconcileAtSeq")
    reconcile_id: str | None = Field(default=None, alias="reconcileId")
    user_message: str | None = Field(default=None, alias="userMessage")
    hints: list[str] = Field(default_factory=list)
    recovery_title: str = Field(alias="recoveryTitle")
    recovery_body: str = Field(alias="recoveryBody")
    observability_search_path: str = Field(alias="observabilitySearchPath")
    reconcile_api_hint: dict[str, Any] = Field(default_factory=dict, alias="reconcileApiHint")
    manual_retry_supported: bool = Field(default=False, alias="manualRetrySupported")
