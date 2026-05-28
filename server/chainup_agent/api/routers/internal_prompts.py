"""Internal runtime read — GET effective published prompt (FR-PM08 slice)."""

from __future__ import annotations

from typing import Annotated

from chainup_agent.api.deps import DbSession
from chainup_agent.api.schemas.prompt_management import EffectivePromptOut
from chainup_agent.application.agent_prompt_effective import build_effective_prompt_view
from chainup_agent.core.errors import AppError
from fastapi import APIRouter, Header, Query, Response

router = APIRouter(prefix="/api/v1/internal/prompts", tags=["Internal — Prompts"])


@router.get(
    "/effective",
    response_model=EffectivePromptOut,
    response_model_by_alias=True,
    summary="运行时生效 Prompt（仅 PUBLISHED）",
)
async def get_effective_prompt(
    db: DbSession,
    response: Response,
    scenario_id: str = Query(..., alias="scenarioId"),
    if_none_match: Annotated[str | None, Header(alias="If-None-Match")] = None,
) -> EffectivePromptOut | Response:
    view = await build_effective_prompt_view(db, scenario_id=scenario_id)
    if view is None:
        raise AppError(
            code="AGENT_PROMPT_PACK_NOT_FOUND",
            message="未找到该 scenarioId 的已发布 Prompt 包。",
            status_code=404,
            details={"scenarioId": scenario_id},
        )
    etag = str(view.get("etag") or "")
    if if_none_match and if_none_match.strip() == etag.strip():
        return Response(status_code=304)
    if etag:
        response.headers["ETag"] = etag
    return EffectivePromptOut.model_validate(view)
