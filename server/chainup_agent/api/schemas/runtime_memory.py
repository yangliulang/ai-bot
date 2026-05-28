"""Runtime memory HTTP schemas (STM session baseline)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClearSessionStmRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId")
    invalidate_pending_type_a: bool = Field(default=True, alias="invalidatePendingTypeA")


class ClearSessionStmResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="sessionId")
    user_id: str = Field(alias="userId")
    cleared_at: datetime = Field(alias="clearedAt")
    pending_type_a_invalidated: bool = Field(alias="pendingTypeAInvalidated")
    event_name: str | None = Field(default="agent.memory.session_cleared", alias="eventName")


class SemanticNarrativeBlockOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    summary: str | None = None
    proposition_types: list[str] | None = Field(default=None, alias="propositionTypes")
    as_of: datetime | str | None = Field(default=None, alias="asOf")


class AgentRuntimeMemoryContextPreviewOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    semantic_narrative_enabled: bool = Field(alias="semanticNarrativeEnabled")
    semantic_narrative_block: SemanticNarrativeBlockOut | None = Field(
        default=None,
        alias="semanticNarrativeBlock",
    )
    user_memory_revoked_at: datetime | None = Field(default=None, alias="userMemoryRevokedAt")
    session_cleared_at: datetime | str | None = Field(default=None, alias="sessionClearedAt")


class L0MessagePreviewOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role: str
    content_preview: str = Field(alias="contentPreview")


class ClarifySessionSnapshotOut(BaseModel):
    """Write-path clarify snapshot — OpenAPI `ClarifySessionSnapshot` subset."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    session_id: str = Field(alias="sessionId")
    execution_id: str = Field(alias="executionId")
    clarify_turn: int = Field(alias="clarifyTurn")
    resolved_slots_so_far: dict[str, str] = Field(
        default_factory=dict,
        alias="resolvedSlotsSoFar",
    )
    pending_clarify_kind: str | None = Field(default=None, alias="pendingClarifyKind")
    lifecycle_state: str | None = Field(default=None, alias="lifecycleState")
    abandoned: bool | None = None


class MemorySessionContextPreviewOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="sessionId")
    user_id: str = Field(alias="userId")
    l0_message_count: int = Field(alias="l0MessageCount")
    l0_messages_preview: list[L0MessagePreviewOut] = Field(
        default_factory=list,
        alias="l0MessagesPreview",
    )
    pending_type_a_valid: bool | None = Field(default=None, alias="pendingTypeAValid")
    memory_context: AgentRuntimeMemoryContextPreviewOut = Field(alias="memoryContext")
    clarify_session: ClarifySessionSnapshotOut | None = Field(
        default=None,
        alias="clarifySession",
    )
