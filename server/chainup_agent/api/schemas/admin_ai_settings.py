"""Pydantic DTOs for Admin AI Settings (`admin/ai-settings.yaml`)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LlmProviderSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    provider_id: str = Field(alias="providerId")
    display_name: str = Field(alias="displayName")
    base_url: str = Field(alias="baseUrl")
    secret_ref: str | None = Field(default=None, alias="secretRef")
    configured: bool


class LlmProviderDetail(LlmProviderSummary):
    pass


class LlmProviderUpsertBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    display_name: str | None = Field(default=None, alias="displayName")
    base_url: str | None = Field(default=None, alias="baseUrl")
    secret_ref: str | None = Field(default=None, alias="secretRef")


class LlmProviderListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[LlmProviderSummary]


class LlmModelSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    model_id: str = Field(alias="modelId")
    provider_id: str = Field(alias="providerId")
    api_model: str | None = Field(default=None, alias="apiModel")
    status: str
    context_window_tokens: int | None = Field(default=None, alias="contextWindowTokens")


class LlmModelListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[LlmModelSummary]


class LlmModelPatchBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    provider_id: str | None = Field(default=None, alias="providerId")
    status: str | None = None
    context_window_tokens: int | None = Field(default=None, alias="contextWindowTokens")
    api_model: str | None = Field(default=None, alias="apiModel")


class LlmModelCreateBody(BaseModel):
    """extension: OpenAI YAML had PATCH-only models; runtime UI needs register model."""

    model_config = ConfigDict(populate_by_name=True)

    provider_id: str = Field(alias="providerId")
    model_id: str = Field(alias="modelId")
    api_model: str | None = Field(default=None, alias="apiModel")
    status: str | None = Field(default=None)
    context_window_tokens: int | None = Field(default=None, alias="contextWindowTokens")


class AiHealthProbeResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ok: bool
    latency_ms: int = Field(alias="latencyMs")
    checked_at: str = Field(alias="checkedAt")
    message: str | None = None


def provider_to_detail(row: object) -> LlmProviderDetail:
    """Build Detail from ORM row (Pydantic v2 rejects Summary→Detail via model_validate)."""
    summary = provider_to_summary(row)
    return LlmProviderDetail.model_validate(summary.model_dump(mode="python"))


def provider_to_summary(row: object) -> LlmProviderSummary:
    from chainup_agent.infrastructure.persistence.models.admin_ai_settings import AdminAiProvider

    assert isinstance(row, AdminAiProvider)
    ref = (row.secret_ref or "").strip()
    return LlmProviderSummary(
        providerId=row.provider_id,
        displayName=row.display_name,
        baseUrl=row.base_url,
        secretRef=row.secret_ref if ref else None,
        configured=bool(ref),
    )


def model_to_summary(row: object) -> LlmModelSummary:
    from chainup_agent.infrastructure.persistence.models.admin_ai_settings import AdminAiModel

    assert isinstance(row, AdminAiModel)
    return LlmModelSummary(
        modelId=row.model_id,
        providerId=row.provider_id,
        apiModel=row.api_model,
        status=row.status,
        contextWindowTokens=row.context_window_tokens,
    )
