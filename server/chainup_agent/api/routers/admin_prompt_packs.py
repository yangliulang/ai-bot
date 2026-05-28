"""Admin — Prompt packs Phase1（列表/详情/草稿/发布/fork/versions/rollback · messages PATCH）。"""

from __future__ import annotations

from chainup_agent.api.deps import DbSession, require_admin_console_bearer
from chainup_agent.api.schemas.prompt_management import (
    PromptPackCreateBody,
    PromptPackDetailOut,
    PromptPackForkBody,
    PromptPackListOut,
    PromptPackMessagesPatchBody,
    PromptPackSummaryOut,
    PromptPublishResultOut,
    PromptRollbackBody,
    PromptVersionEntryOut,
    PromptVersionHistoryOut,
)
from chainup_agent.application.admin_prompt_packs import (
    create_draft_prompt_pack,
    fork_prompt_pack_from_source,
    get_prompt_pack,
    list_prompt_pack_versions,
    list_prompt_packs,
    pack_to_detail_dict,
    pack_to_summary_dict,
    patch_messages,
    publish_prompt_pack,
    rollback_prompt_pack,
)
from chainup_agent.core.errors import AppError
from fastapi import APIRouter, Depends, Header, Query, Response, status

router = APIRouter(
    prefix="/api/v1/admin/prompt-packs",
    tags=["Admin — Prompt packs"],
    dependencies=[Depends(require_admin_console_bearer)],
)


def _set_row_version_etag(response: Response, row_version: int) -> None:
    response.headers["ETag"] = f'"{row_version}"'


@router.get(
    "",
    response_model=PromptPackListOut,
    response_model_by_alias=True,
    summary="Prompt 包列表（Phase1；可选筛选）",
)
async def admin_list_prompt_packs(
    db: DbSession,
    prompt_pack_type: str | None = Query(None, alias="promptPackType"),
    scenario_id: str | None = Query(None, alias="scenarioId"),
    lifecycle: str | None = Query(None),
) -> PromptPackListOut:
    rows = await list_prompt_packs(
        db,
        prompt_pack_type=prompt_pack_type,
        scenario_id=scenario_id,
        lifecycle=lifecycle,
    )
    return PromptPackListOut(
        items=[PromptPackSummaryOut.model_validate(pack_to_summary_dict(r)) for r in rows],
    )


@router.post(
    "",
    response_model=PromptPackDetailOut,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="创建草稿包（空白或 sourcePromptPackId 模板复制）",
)
async def admin_create_prompt_pack_draft(
    body: PromptPackCreateBody,
    response: Response,
    db: DbSession,
) -> PromptPackDetailOut:
    row = await create_draft_prompt_pack(
        db,
        prompt_pack_type=body.prompt_pack_type,
        scenario_id=body.scenario_id,
        prompt_pack_id=body.prompt_pack_id,
        source_prompt_pack_id=body.source_prompt_pack_id,
    )
    await db.commit()
    await db.refresh(row)
    _set_row_version_etag(response, int(row.row_version))
    return PromptPackDetailOut.model_validate(pack_to_detail_dict(row))


@router.get(
    "/{prompt_pack_id}",
    response_model=PromptPackDetailOut,
    response_model_by_alias=True,
    summary="Prompt 包详情",
)
async def admin_get_prompt_pack(
    prompt_pack_id: str,
    response: Response,
    db: DbSession,
) -> PromptPackDetailOut:
    row = await get_prompt_pack(db, prompt_pack_id)
    if row is None:
        raise AppError(
            code="AGENT_PROMPT_PACK_NOT_FOUND",
            message="未知的 promptPackId。",
            status_code=404,
            details={"promptPackId": prompt_pack_id.strip()},
        )
    _set_row_version_etag(response, int(row.row_version))
    return PromptPackDetailOut.model_validate(pack_to_detail_dict(row))


@router.patch(
    "/{prompt_pack_id}",
    response_model=PromptPackDetailOut,
    response_model_by_alias=True,
    summary="更新包的消息正文（DRAFT / PUBLISHED；LOCKED / 下线禁止 · PM-C03 If-Match）",
)
async def admin_patch_prompt_pack_messages(
    prompt_pack_id: str,
    body: PromptPackMessagesPatchBody,
    response: Response,
    db: DbSession,
    if_match: str | None = Header(default=None, alias="If-Match"),
) -> PromptPackDetailOut:
    try:
        row = await patch_messages(
            db,
            prompt_pack_id=prompt_pack_id,
            messages=body.messages,
            variable_schema=body.variable_schema,
            if_match=if_match,
        )
    except AppError:
        await db.rollback()
        raise
    if row is None:
        raise AppError(
            code="AGENT_PROMPT_PACK_NOT_FOUND",
            message="未知的 promptPackId。",
            status_code=404,
            details={"promptPackId": prompt_pack_id.strip()},
        )
    await db.commit()
    await db.refresh(row)
    _set_row_version_etag(response, int(row.row_version))
    return PromptPackDetailOut.model_validate(pack_to_detail_dict(row))


@router.post(
    "/{prompt_pack_id}/fork",
    response_model=PromptPackDetailOut,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="从已有包快照复制为新草稿版本线（SYSTEM LOCKED → 新版本编辑路径）",
)
async def admin_fork_prompt_pack(
    prompt_pack_id: str,
    response: Response,
    db: DbSession,
    body: PromptPackForkBody | None = None,
) -> PromptPackDetailOut:
    new_id = body.prompt_pack_id if body is not None else None
    try:
        row = await fork_prompt_pack_from_source(
            db,
            source_prompt_pack_id=prompt_pack_id,
            new_prompt_pack_id=new_id,
        )
    except AppError:
        await db.rollback()
        raise
    await db.commit()
    await db.refresh(row)
    _set_row_version_etag(response, int(row.row_version))
    return PromptPackDetailOut.model_validate(pack_to_detail_dict(row))


@router.get(
    "/{prompt_pack_id}/versions",
    response_model=PromptVersionHistoryOut,
    response_model_by_alias=True,
    summary="版本履历（Publish / Rollback 快照）",
)
async def admin_get_prompt_pack_versions(
    prompt_pack_id: str,
    db: DbSession,
) -> PromptVersionHistoryOut:
    row = await get_prompt_pack(db, prompt_pack_id)
    if row is None:
        raise AppError(
            code="AGENT_PROMPT_PACK_NOT_FOUND",
            message="未知的 promptPackId。",
            status_code=404,
            details={"promptPackId": prompt_pack_id.strip()},
        )
    items = await list_prompt_pack_versions(db, prompt_pack_id=prompt_pack_id)
    return PromptVersionHistoryOut(
        items=[PromptVersionEntryOut.model_validate(x) for x in items],
    )


@router.post(
    "/{prompt_pack_id}/publish",
    response_model=PromptPublishResultOut,
    response_model_by_alias=True,
    summary="发布草稿（FR-PM07 · SYSTEM→LOCKED；场景族→PUBLISHED 并顶替同 scenario 旧版）",
)
async def admin_publish_prompt_pack(
    prompt_pack_id: str,
    db: DbSession,
) -> PromptPublishResultOut:
    try:
        row = await publish_prompt_pack(db, prompt_pack_id=prompt_pack_id)
    except AppError as exc:
        if exc.code == "PROMPT_SAFETY_VIOLATION":
            await db.commit()
        else:
            await db.rollback()
        raise
    if row is None:
        raise AppError(
            code="AGENT_PROMPT_PACK_NOT_FOUND",
            message="未知的 promptPackId。",
            status_code=404,
            details={"promptPackId": prompt_pack_id.strip()},
        )
    await db.commit()
    await db.refresh(row)
    return PromptPublishResultOut(
        promptPackId=row.prompt_pack_id,
        promptPackVersion=row.prompt_pack_version,
        lifecycle=row.lifecycle,
    )


@router.post(
    "/{prompt_pack_id}/rollback",
    response_model=PromptPublishResultOut,
    response_model_by_alias=True,
    summary="回滚生效指针至历史版本快照（FR-PM · 指针回指）",
)
async def admin_rollback_prompt_pack(
    prompt_pack_id: str,
    body: PromptRollbackBody,
    db: DbSession,
) -> PromptPublishResultOut:
    try:
        row = await rollback_prompt_pack(
            db,
            prompt_pack_id=prompt_pack_id,
            target_version=body.prompt_pack_version,
        )
    except AppError:
        await db.rollback()
        raise
    if row is None:
        raise AppError(
            code="AGENT_PROMPT_PACK_NOT_FOUND",
            message="未知的 promptPackId。",
            status_code=404,
            details={"promptPackId": prompt_pack_id.strip()},
        )
    await db.commit()
    await db.refresh(row)
    return PromptPublishResultOut(
        promptPackId=row.prompt_pack_id,
        promptPackVersion=row.prompt_pack_version,
        lifecycle=row.lifecycle,
    )
