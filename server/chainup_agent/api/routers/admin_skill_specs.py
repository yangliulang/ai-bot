"""Admin — skill operation specs (Publish chain)."""

from __future__ import annotations

from chainup_agent.api.deps import DbSession, require_admin_console_bearer
from chainup_agent.api.schemas.skill_operation_spec import (
    SkillOperationSpecBodyOut,
    SkillOperationSpecListOut,
    SkillOperationSpecSummaryOut,
    SkillSpecPublishRequestIn,
    SkillSpecPublishResultOut,
    SkillSpecVersionHistoryOut,
)
from chainup_agent.application.skill_operation_spec_store import (
    get_skill_spec_summary,
    get_version_body,
    list_skill_specs,
    list_versions,
    publish_skill_spec,
)
from chainup_agent.core.errors import AppError
from fastapi import APIRouter, Depends, Query

router = APIRouter(
    prefix="/api/v1/admin/skill-specs",
    tags=["Admin — Skill specs"],
    dependencies=[Depends(require_admin_console_bearer)],
)


@router.get(
    "",
    response_model=SkillOperationSpecListOut,
    response_model_by_alias=True,
    summary="技能操作规范列表",
)
async def admin_list_skill_specs(
    db: DbSession,
    lifecycle: str | None = Query(None),
) -> SkillOperationSpecListOut:
    items = await list_skill_specs(db, lifecycle=lifecycle)
    return SkillOperationSpecListOut(
        items=[SkillOperationSpecSummaryOut.model_validate(x) for x in items],
    )


@router.get(
    "/{skill_id}",
    response_model=SkillOperationSpecSummaryOut,
    response_model_by_alias=True,
    summary="技能规范摘要 + 生效指针",
)
async def admin_get_skill_spec(
    skill_id: str,
    db: DbSession,
) -> SkillOperationSpecSummaryOut:
    summary = await get_skill_spec_summary(db, skill_id)
    if summary is None:
        raise AppError(
            "PROMPT_SKILL_REF_INVALID",
            f"未找到技能：{skill_id}",
            status_code=404,
        )
    return SkillOperationSpecSummaryOut.model_validate(summary)


@router.get(
    "/{skill_id}/versions",
    response_model=SkillSpecVersionHistoryOut,
    response_model_by_alias=True,
    summary="版本履历",
)
async def admin_get_skill_spec_versions(
    skill_id: str,
    db: DbSession,
) -> SkillSpecVersionHistoryOut:
    hist = await list_versions(db, skill_id)
    if hist is None:
        raise AppError(
            "PROMPT_SKILL_REF_INVALID",
            f"未找到技能：{skill_id}",
            status_code=404,
        )
    return SkillSpecVersionHistoryOut.model_validate(hist)


@router.get(
    "/{skill_id}/versions/{skill_spec_version}",
    response_model=SkillOperationSpecBodyOut,
    response_model_by_alias=True,
    summary="指定版本正文",
)
async def admin_get_skill_spec_version_body(
    skill_id: str,
    skill_spec_version: str,
    db: DbSession,
) -> SkillOperationSpecBodyOut:
    body = await get_version_body(db, skill_id, skill_spec_version)
    if body is None:
        raise AppError(
            "PROMPT_SKILL_REF_INVALID",
            "未找到该版本",
            status_code=404,
        )
    return SkillOperationSpecBodyOut.model_validate(body)


@router.post(
    "/{skill_id}/publish",
    response_model=SkillSpecPublishResultOut,
    response_model_by_alias=True,
    summary="发布技能规范",
)
async def admin_publish_skill_spec(
    skill_id: str,
    body: SkillSpecPublishRequestIn,
    db: DbSession,
) -> SkillSpecPublishResultOut:
    result = await publish_skill_spec(
        db,
        skill_id=skill_id,
        skill_spec_version=body.skill_spec_version,
        body_markdown=body.body_markdown,
        spec_digest=body.spec_digest,
        source_git_ref=body.source_git_ref,
    )
    await db.commit()
    return SkillSpecPublishResultOut.model_validate(result)
