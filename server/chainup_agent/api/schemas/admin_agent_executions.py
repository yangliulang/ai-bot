"""Admin DTOs for persisted agent executions (observability Phase1)."""

from __future__ import annotations

from datetime import datetime

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution


class AdminAgentExecutionItem(BaseModel):
    """One row from ``agent_execution`` (camelCase for Admin SPA)."""

    model_config = ConfigDict(populate_by_name=True)

    execution_id: str = Field(alias="executionId")
    user_id: str = Field(alias="userId")
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    channel: str | None = None
    state: str
    source: str | None = None
    idempotency_key: str | None = Field(default=None, alias="idempotencyKey")
    note: str | None = None
    prompt_pack_version: str | None = Field(default=None, alias="promptPackVersion")
    resolved_prompt_binding: dict[str, Any] | None = Field(
        default=None, alias="resolvedPromptBinding"
    )
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")


class AdminAgentExecutionListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[AdminAgentExecutionItem]
    total: int


def admin_agent_execution_item_from_row(row: AgentExecution) -> AdminAgentExecutionItem:
    return AdminAgentExecutionItem(
        execution_id=row.execution_id,
        user_id=row.user_id,
        scenario_id=row.scenario_id,
        channel=row.channel,
        state=row.state,
        source=row.source,
        idempotency_key=row.idempotency_key,
        note=row.note,
        prompt_pack_version=row.prompt_pack_version,
        resolved_prompt_binding=row.resolved_prompt_binding,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
