"""Admin observability FR-MC803 / FR-MC804 response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolCallDetailItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tool_id: str = Field(alias="toolId")
    tool_call_seq: int = Field(alias="toolCallSeq")
    invocation_state: str = Field(alias="invocationState")
    phase: str | None = None
    duration_ms: int | None = Field(default=None, alias="durationMs")
    agent_sub_account_id: str | None = Field(default=None, alias="agentSubAccountId")
    event_name: str | None = Field(default=None, alias="eventName")
    step_kind: str | None = Field(default=None, alias="stepKind")
    ts: datetime | None = None
    summary: dict[str, Any] = Field(default_factory=dict)


class ToolCallsPageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ToolCallDetailItem]


class LlmCallItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    event_name: str = Field(alias="eventName")
    tool_call_seq: int = Field(alias="toolCallSeq")
    ts: datetime
    model_id: str | None = Field(default=None, alias="modelId")
    gateway_model_id: str | None = Field(default=None, alias="gatewayModelId")
    gateway_upstream_model: str | None = Field(default=None, alias="gatewayUpstreamModel")
    gateway_provider_id: str | None = Field(default=None, alias="gatewayProviderId")
    outcome: str | None = None
    step_kind: str | None = Field(default=None, alias="stepKind")
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    prompt_pack_version: str | None = Field(default=None, alias="promptPackVersion")
    input_tokens: int | None = Field(default=None, alias="inputTokens")
    output_tokens: int | None = Field(default=None, alias="outputTokens")
    total_tokens: int | None = Field(default=None, alias="totalTokens")


class LlmUsageSummaryResponse(BaseModel):
    """FR-MC804 — no message bodies; optional per-call rows in ``calls``."""

    model_config = ConfigDict(populate_by_name=True)

    model_id: str | None = Field(default=None, alias="modelId")
    input_tokens: int | None = Field(default=None, alias="inputTokens")
    output_tokens: int | None = Field(default=None, alias="outputTokens")
    total_tokens: int | None = Field(default=None, alias="totalTokens")
    calls: list[LlmCallItem] = Field(default_factory=list)
