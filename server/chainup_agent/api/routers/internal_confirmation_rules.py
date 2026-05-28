"""Internal runtime read — effective confirmation rules."""

from __future__ import annotations

from fastapi import APIRouter

from chainup_agent.api.deps import DbSession
from chainup_agent.api.schemas.admin_confirmation_rules import ConfirmationRuleListResponse
from chainup_agent.application.admin_confirmation_rules import list_confirmation_rules

router = APIRouter(
    prefix="/api/v1/internal/confirmation-rules",
    tags=["Internal — Confirmation rules"],
)


@router.get(
    "/effective",
    response_model=ConfirmationRuleListResponse,
    response_model_by_alias=True,
    summary="运行时生效的人工确认规则（含启用态）",
)
async def get_effective_confirmation_rules(db: DbSession) -> ConfirmationRuleListResponse:
    return await list_confirmation_rules(db)
