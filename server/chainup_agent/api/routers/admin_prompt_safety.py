"""Admin Prompt Safety API — ai.prompt-safety."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from chainup_agent.api.deps import DbSession, require_admin_console_bearer
from chainup_agent.api.schemas.admin_prompt_safety import (
    RuntimeSafetyGovernanceResponse,
    SafetyBlocklistOut,
    SafetyInterceptListResponse,
    SafetyOverviewOut,
    SessionSafetyPolicyResponse,
    ToolSafetyPolicyResponse,
)
from chainup_agent.api.schemas.prompt_management import PromptPackListOut, PromptPackSummaryOut
from chainup_agent.application.admin_prompt_packs import list_prompt_packs, pack_to_summary_dict
from chainup_agent.application.admin_prompt_safety import (
    get_runtime_governance_summary,
    get_safety_blocklist,
    get_safety_overview,
    get_session_safety_policy,
    get_tool_safety_policies,
    list_safety_intercepts,
)

router = APIRouter(
    prefix="/api/v1/admin/prompt-safety",
    tags=["Admin — Prompt safety"],
    dependencies=[Depends(require_admin_console_bearer)],
)


@router.get("/overview", response_model=SafetyOverviewOut, response_model_by_alias=True)
async def admin_prompt_safety_overview(db: DbSession) -> SafetyOverviewOut:
    return await get_safety_overview(db)


@router.get("/blocklist", response_model=SafetyBlocklistOut, response_model_by_alias=True)
async def admin_prompt_safety_blocklist() -> SafetyBlocklistOut:
    return await get_safety_blocklist()


@router.get("/prompt-packs", response_model=PromptPackListOut, response_model_by_alias=True)
async def admin_prompt_safety_prompt_packs(db: DbSession) -> PromptPackListOut:
    rows = await list_prompt_packs(db, prompt_pack_type="SAFETY")
    return PromptPackListOut(
        items=[PromptPackSummaryOut.model_validate(pack_to_summary_dict(r)) for r in rows],
    )


@router.get(
    "/runtime-governance",
    response_model=RuntimeSafetyGovernanceResponse,
    response_model_by_alias=True,
)
async def admin_prompt_safety_runtime_governance(db: DbSession) -> RuntimeSafetyGovernanceResponse:
    items = await get_runtime_governance_summary(db)
    return RuntimeSafetyGovernanceResponse(items=items)


@router.get(
    "/tool-policies",
    response_model=ToolSafetyPolicyResponse,
    response_model_by_alias=True,
)
async def admin_prompt_safety_tool_policies() -> ToolSafetyPolicyResponse:
    return get_tool_safety_policies()


@router.get(
    "/session-policy",
    response_model=SessionSafetyPolicyResponse,
    response_model_by_alias=True,
)
async def admin_prompt_safety_session_policy() -> SessionSafetyPolicyResponse:
    return get_session_safety_policy()


@router.get("/intercepts", response_model=SafetyInterceptListResponse, response_model_by_alias=True)
async def admin_prompt_safety_intercepts(
    db: DbSession,
    category: str | None = Query(None, description="runtime | prompt | tool | session"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> SafetyInterceptListResponse:
    return await list_safety_intercepts(db, category=category, limit=limit, offset=offset)
