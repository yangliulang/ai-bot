"""Pydantic view-models — Prompt Management (同窗 product OpenAPI 子集)。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PromptPackSummaryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt_pack_id: str = Field(alias="promptPackId")
    prompt_pack_type: str = Field(alias="promptPackType")
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    title: str | None = None
    prompt_pack_version: str | None = Field(default=None, alias="promptPackVersion")
    lifecycle: str | None = None
    etag: str | None = None
    updated_at: str | None = Field(default=None, alias="updatedAt")
    row_version: int | None = Field(default=None, alias="rowVersion")


class PromptPackListOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[PromptPackSummaryOut]


class PromptPackDetailOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt_pack_id: str = Field(alias="promptPackId")
    prompt_pack_type: str = Field(alias="promptPackType")
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    title: str | None = None
    prompt_pack_version: str = Field(alias="promptPackVersion")
    lifecycle: str
    etag: str | None = None
    row_version: int | None = Field(default=None, alias="rowVersion")
    updated_at: str | None = Field(default=None, alias="updatedAt")
    placeholder_denylist_revision: str | None = Field(
        default=None, alias="placeholderDenylistRevision"
    )
    safety_phrase_blocklist_revision: str | None = Field(
        default=None, alias="safetyPhraseBlocklistRevision"
    )
    messages: list[dict[str, Any]] = Field(default_factory=list)
    body_markdown: str | None = Field(default=None, alias="bodyMarkdown")
    variable_schema: dict[str, Any] | None = Field(default=None, alias="variableSchema")
    resolved_prompt_binding: dict[str, Any] = Field(
        default_factory=dict,
        alias="resolvedPromptBinding",
    )


class EffectivePromptOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(alias="scenarioId")
    prompt_pack_version: str = Field(alias="promptPackVersion")
    etag: str | None = None
    messages: list[dict[str, Any]] = Field(default_factory=list)
    variable_schema: dict[str, Any] | None = Field(default=None, alias="variableSchema")
    resolved_prompt_binding: dict[str, Any] = Field(
        default_factory=dict,
        alias="resolvedPromptBinding",
    )


class PromptPackMessagesPatchBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    messages: list[dict[str, Any]] | None = None
    variable_schema: dict[str, Any] | None = Field(default=None, alias="variableSchema")

    @model_validator(mode="after")
    def require_messages_or_schema(self) -> PromptPackMessagesPatchBody:
        if self.messages is None and self.variable_schema is None:
            raise ValueError("messages 与 variableSchema 至少提供其一")
        return self


class PromptPackCreateBody(BaseModel):
    """`PromptPackCreateRequest` subset — blank draft or clone from template."""

    model_config = ConfigDict(populate_by_name=True)

    prompt_pack_type: str = Field(alias="promptPackType", min_length=1, max_length=32)
    scenario_id: str | None = Field(default=None, alias="scenarioId", max_length=128)
    prompt_pack_id: str | None = Field(
        default=None,
        alias="promptPackId",
        max_length=128,
        description="Optional stable id; server generates when omitted.",
    )
    source_prompt_pack_id: str | None = Field(
        default=None,
        alias="sourcePromptPackId",
        max_length=128,
        description="Optional template pack id; copies messages/variableSchema into new DRAFT.",
    )


class PromptPublishResultOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt_pack_id: str = Field(alias="promptPackId")
    prompt_pack_version: str = Field(alias="promptPackVersion")
    lifecycle: str


class PromptVersionEntryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt_pack_version: str = Field(alias="promptPackVersion")
    published_at: str = Field(alias="publishedAt")
    lifecycle: str | None = None
    event: str | None = None
    actor: str | None = None
    summary: str | None = None


class PromptVersionHistoryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[PromptVersionEntryOut]


class PromptRollbackBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt_pack_version: str = Field(alias="promptPackVersion", min_length=1, max_length=64)


class PromptPackForkBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt_pack_id: str | None = Field(
        default=None,
        alias="promptPackId",
        max_length=128,
        description="Optional stable id for the new draft line.",
    )
