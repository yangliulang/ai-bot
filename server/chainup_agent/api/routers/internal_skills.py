"""Internal — effective skill operation spec (read_skill)."""

from __future__ import annotations

from typing import Annotated

from chainup_agent.api.deps import DbSession
from chainup_agent.api.schemas.skill_operation_spec import EffectiveSkillBodyOut
from chainup_agent.application.skill_operation_spec_store import get_effective_body_response
from chainup_agent.core.errors import AppError
from fastapi import APIRouter, Header, Query, Response

router = APIRouter(prefix="/api/v1/internal/skills", tags=["Internal — Skill specs"])


@router.get(
    "/effective",
    response_model=EffectiveSkillBodyOut,
    response_model_by_alias=True,
    summary="运行时 read_skill · 仅 PUBLISHED",
)
async def get_internal_effective_skill(
    db: DbSession,
    response: Response,
    skill_id: str = Query(..., alias="skillId"),
    skill_spec_version: str = Query(..., alias="skillSpecVersion"),
    if_none_match: Annotated[str | None, Header(alias="If-None-Match")] = None,
) -> EffectiveSkillBodyOut | Response:
    try:
        payload, etag = await get_effective_body_response(
            db,
            skill_id=skill_id,
            skill_spec_version=skill_spec_version,
            if_none_match=if_none_match,
        )
    except AppError:
        raise
    if payload is None:
        if etag:
            response.headers["ETag"] = etag
        return Response(status_code=304)
    if etag:
        response.headers["ETag"] = etag
    return EffectiveSkillBodyOut.model_validate(payload)
