"""Runtime — effective skill operation spec (read_skill_operation_spec)."""

from __future__ import annotations

from chainup_agent.api.deps import DbSession
from chainup_agent.api.schemas.runtime_skill import (
    SkillOperationSpecEffectiveOut,
    SkillOperationSpecSectionOut,
)
from chainup_agent.application.skill_operation_spec_store import get_effective_from_db
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/runtime", tags=["Runtime — Skill operation spec"])


@router.get(
    "/skill-operation-spec/effective",
    response_model=SkillOperationSpecEffectiveOut,
    response_model_by_alias=True,
    summary="读取已发布技能操作规范（类型 A 前）",
)
async def get_skill_operation_spec_effective(
    db: DbSession,
    skill_id: str = Query(..., alias="skillId"),
    scenario_id: str | None = Query(default=None, alias="scenarioId"),
) -> SkillOperationSpecEffectiveOut:
    spec = await get_effective_from_db(db, skill_id=skill_id, scenario_id=scenario_id)
    return SkillOperationSpecEffectiveOut(
        skillId=spec.skill_id,
        skillSpecVersion=spec.skill_spec_version,
        specDigest=spec.spec_digest,
        lifecycle=spec.lifecycle,
        scenarioId=spec.scenario_id,
        sections=[
            SkillOperationSpecSectionOut(
                id=s.id,
                title=s.title,
                bodyMarkdown=s.body_markdown,
            )
            for s in spec.sections
        ],
    )
