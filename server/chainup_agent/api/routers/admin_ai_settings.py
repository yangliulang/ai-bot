"""Admin API — AI Settings (providers / models / gateway defaults / health)."""

from __future__ import annotations

from typing import Annotated, Any

from chainup_agent.api.deps import DbSession, require_admin_console_bearer
from chainup_agent.api.schemas.admin_ai_settings import (
    AiHealthProbeResult,
    LlmModelCreateBody,
    LlmModelListResponse,
    LlmModelPatchBody,
    LlmModelSummary,
    LlmProviderDetail,
    LlmProviderListResponse,
    LlmProviderUpsertBody,
    model_to_summary,
    provider_to_detail,
    provider_to_summary,
)
from chainup_agent.application.admin_ai_settings import (
    create_model,
    create_provider,
    delete_model,
    delete_provider,
    ensure_health_policy,
    get_health_policy_document,
    get_model,
    get_provider,
    list_models,
    list_providers,
    patch_gateway_defaults,
    patch_health_policy,
    patch_model,
    patch_provider,
    probe_provider_health,
    read_gateway_defaults_merged,
    seed_demo_ai_catalog,
)
from chainup_agent.core.config import get_settings
from chainup_agent.core.errors import AppError
from fastapi import APIRouter, Body, Depends, Header, Query, Response, status

router = APIRouter(
    prefix="/api/v1/admin/ai",
    tags=["Admin — AI Settings"],
    dependencies=[Depends(require_admin_console_bearer)],
)


async def _maybe_seed_catalog(db: DbSession) -> None:
    """Insert demo catalog only when explicitly enabled (avoid resurrecting after DELETE)."""
    if not get_settings().admin_ai_catalog_seed_demo_if_empty:
        return
    rows = await list_providers(db)
    if not rows:
        await seed_demo_ai_catalog(db)
        await db.commit()


@router.get(
    "/providers",
    response_model=LlmProviderListResponse,
    response_model_by_alias=True,
    summary="Provider 列表 FR-MC401",
)
async def admin_list_ai_providers(db: DbSession) -> LlmProviderListResponse:
    await _maybe_seed_catalog(db)
    rows = await list_providers(db)
    return LlmProviderListResponse(items=[provider_to_summary(r) for r in rows])


@router.post(
    "/providers",
    response_model=LlmProviderDetail,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="创建 Provider FR-MC401",
)
async def admin_create_ai_provider(
    db: DbSession,
    body: LlmProviderUpsertBody,
    response: Response,
    if_match: str | None = Header(default=None, alias="If-Match"),
) -> LlmProviderDetail:
    dn = body.display_name or ""
    bu = body.base_url or ""
    if not dn.strip() or not bu.strip():
        raise AppError(
            code="VALIDATION_ERROR",
            message="displayName 与 baseUrl 不能为空",
            status_code=422,
            details={"fields": ["displayName", "baseUrl"]},
        )
    row = await create_provider(
        db,
        display_name=dn,
        base_url=bu,
        secret_ref=body.secret_ref,
        if_match=if_match,
    )
    await db.commit()
    response.headers["ETag"] = f'"{row.row_version}"'
    return provider_to_detail(row)


@router.get(
    "/providers/{provider_id}",
    response_model=LlmProviderDetail,
    response_model_by_alias=True,
    summary="Provider 详情 FR-MC401",
)
async def admin_get_ai_provider(provider_id: str, db: DbSession) -> LlmProviderDetail:
    await _maybe_seed_catalog(db)
    row = await get_provider(db, provider_id)
    if row is None:
        raise AppError(
            code="AGENT_AI_PROVIDER_NOT_FOUND",
            message="未找到该 LLM Provider",
            status_code=404,
            details={"providerId": provider_id},
        )
    return provider_to_detail(row)


@router.patch(
    "/providers/{provider_id}",
    response_model=LlmProviderDetail,
    response_model_by_alias=True,
    summary="更新 Provider FR-MC401",
)
async def admin_patch_ai_provider(
    provider_id: str,
    db: DbSession,
    body: LlmProviderUpsertBody,
    if_match: str | None = Header(default=None, alias="If-Match"),
) -> LlmProviderDetail:
    row = await patch_provider(
        db,
        provider_id,
        display_name=body.display_name,
        base_url=body.base_url,
        secret_ref=body.secret_ref,
        if_match=if_match,
    )
    await db.commit()
    return provider_to_detail(row)


@router.delete(
    "/providers/{provider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除 Provider FR-MC401（扩展；下属模型 CASCADE）",
)
async def admin_delete_ai_provider(
    provider_id: str,
    db: DbSession,
    if_match: str | None = Header(default=None, alias="If-Match"),
) -> Response:
    await delete_provider(db, provider_id, if_match=if_match)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/models",
    response_model=LlmModelListResponse,
    response_model_by_alias=True,
    summary="模型目录 FR-MC402",
)
async def admin_list_ai_models(
    db: DbSession,
    provider_id: str | None = Query(default=None, alias="providerId"),
    model_id: str | None = Query(default=None, alias="modelId"),
) -> LlmModelListResponse:
    """List models, or fetch **one** catalog row when ``modelId`` is set.

    Prefer ``GET …?modelId=`` when ``model_id`` contains ``/`` — path-encoded
    ``%2F`` is mishandled by some reverse proxies and breaks ``…/models/{id}``.
    """
    await _maybe_seed_catalog(db)
    pk = model_id.strip() if model_id and model_id.strip() else ""
    prov = provider_id.strip() if provider_id and provider_id.strip() else ""
    if pk and prov:
        raise AppError(
            code="VALIDATION_ERROR",
            message="GET /models：不可同时使用 Query modelId 与 providerId",
            status_code=422,
            details={"fields": ["modelId", "providerId"]},
        )
    if pk:
        row = await get_model(db, pk)
        if row is None:
            raise AppError(
                code="AGENT_AI_MODEL_NOT_FOUND",
                message="未找到该模型",
                status_code=404,
                details={"modelId": pk},
            )
        return LlmModelListResponse(items=[model_to_summary(row)])
    rows = await list_models(db, provider_id)
    return LlmModelListResponse(items=[model_to_summary(r) for r in rows])


@router.get(
    "/models/{model_id}",
    response_model=LlmModelSummary,
    response_model_by_alias=True,
    summary="模型详情 FR-MC402（扩展）",
)
async def admin_get_ai_model(model_id: str, db: DbSession) -> LlmModelSummary:
    await _maybe_seed_catalog(db)
    row = await get_model(db, model_id)
    if row is None:
        raise AppError(
            code="AGENT_AI_MODEL_NOT_FOUND",
            message="未找到该模型",
            status_code=404,
            details={"modelId": model_id},
        )
    return model_to_summary(row)


@router.post(
    "/models",
    response_model=LlmModelSummary,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="注册模型目录项 FR-MC402（扩展：自定义 modelId）",
)
async def admin_create_ai_model(
    db: DbSession,
    body: LlmModelCreateBody,
    response: Response,
) -> LlmModelSummary:
    await _maybe_seed_catalog(db)
    row = await create_model(
        db,
        provider_id=body.provider_id,
        model_id=body.model_id,
        api_model=body.api_model,
        status=body.status,
        context_window_tokens=body.context_window_tokens,
    )
    await db.commit()
    response.headers["ETag"] = f'"{row.row_version}"'
    return model_to_summary(row)


@router.patch(
    "/models",
    response_model=LlmModelSummary,
    response_model_by_alias=True,
    summary="模型 PATCH（Query modelId；catalog id 含「/」时优先使用）",
)
async def admin_patch_ai_model_by_query(
    model_id: Annotated[str, Query(min_length=1, alias="modelId")],
    db: DbSession,
    body: LlmModelPatchBody,
    if_match: str | None = Header(default=None, alias="If-Match"),
) -> LlmModelSummary:
    """Same semantics as ``PATCH …/models/{modelId}`` but avoids path-slash issues."""
    row = await patch_model(
        db,
        model_id,
        provider_id=body.provider_id,
        status=body.status,
        context_window_tokens=body.context_window_tokens,
        api_model=body.api_model,
        patch_api_model="api_model" in body.model_fields_set,
        if_match=if_match,
    )
    await db.commit()
    return model_to_summary(row)


@router.delete(
    "/models",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除模型目录项（Query modelId；catalog id 含「/」时优先使用）",
)
async def admin_delete_ai_model_by_query(
    model_id: Annotated[str, Query(min_length=1, alias="modelId")],
    db: DbSession,
    if_match: str | None = Header(default=None, alias="If-Match"),
) -> Response:
    await _maybe_seed_catalog(db)
    await delete_model(db, model_id, if_match=if_match)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/models/{model_id}",
    response_model=LlmModelSummary,
    response_model_by_alias=True,
    summary="模型元数据 PATCH FR-MC402（可选 providerId / status / contextWindowTokens）",
)
async def admin_patch_ai_model(
    model_id: str,
    db: DbSession,
    body: LlmModelPatchBody,
    if_match: str | None = Header(default=None, alias="If-Match"),
) -> LlmModelSummary:
    row = await patch_model(
        db,
        model_id,
        provider_id=body.provider_id,
        status=body.status,
        context_window_tokens=body.context_window_tokens,
        api_model=body.api_model,
        patch_api_model="api_model" in body.model_fields_set,
        if_match=if_match,
    )
    await db.commit()
    return model_to_summary(row)


@router.delete(
    "/models/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除模型目录项 FR-MC402（扩展）",
)
async def admin_delete_ai_model(
    model_id: str,
    db: DbSession,
    if_match: str | None = Header(default=None, alias="If-Match"),
) -> Response:
    await _maybe_seed_catalog(db)
    await delete_model(db, model_id, if_match=if_match)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/defaults",
    summary="网关默认 profile FR-MC403～406（含编排预算 FR-MC408 / FR-AO06；兼容原型页 Runtime 策略字段）",
)
async def admin_get_ai_gateway_defaults(db: DbSession) -> dict[str, Any]:
    await _maybe_seed_catalog(db)
    merged, _ver = await read_gateway_defaults_merged(db)
    await db.commit()
    return merged


@router.patch(
    "/defaults",
    summary="更新网关默认 profile",
)
async def admin_patch_ai_gateway_defaults(
    db: DbSession,
    body: dict[str, Any] = Body(...),
    if_match: str | None = Header(default=None, alias="If-Match"),
) -> dict[str, Any]:
    await _maybe_seed_catalog(db)
    merged, _ver = await patch_gateway_defaults(db, body, if_match)
    await db.commit()
    return merged


@router.get(
    "/health-policy",
    summary="Health 策略 FR-MC407",
)
async def admin_get_ai_health_policy(db: DbSession) -> dict[str, Any]:
    _ = await ensure_health_policy(db)
    await db.commit()
    data, _ver = await get_health_policy_document(db)
    return data


@router.patch(
    "/health-policy",
    summary="更新 Health 策略 FR-MC407",
)
async def admin_patch_ai_health_policy(
    db: DbSession,
    body: dict[str, Any] = Body(...),
    if_match: str | None = Header(default=None, alias="If-Match"),
) -> dict[str, Any]:
    merged, _ver = await patch_health_policy(db, body, if_match)
    await db.commit()
    return merged


@router.post(
    "/providers/{provider_id}/health",
    response_model=AiHealthProbeResult,
    response_model_by_alias=True,
    summary="手动 Health 探针 FR-MC407（同步 200）",
)
async def admin_post_ai_provider_health_probe(
    provider_id: str,
    db: DbSession,
) -> AiHealthProbeResult:
    await _maybe_seed_catalog(db)
    raw = await probe_provider_health(db, provider_id)
    return AiHealthProbeResult.model_validate(raw)
