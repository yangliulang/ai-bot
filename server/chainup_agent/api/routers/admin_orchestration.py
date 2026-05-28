"""Admin orchestration API — 运行场景 · 执行策略 (Phase 2)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from chainup_agent.api.deps import DbSession, require_admin_console_bearer
from chainup_agent.api.schemas.admin_orchestration import OrchestrationExecutionPolicyOut
from chainup_agent.application.admin_orchestration_policy import read_orchestration_execution_policy

router = APIRouter(
    prefix="/api/v1/admin/orchestration",
    tags=["Admin — Orchestration"],
    dependencies=[Depends(require_admin_console_bearer)],
)


@router.get(
    "/policy",
    response_model=OrchestrationExecutionPolicyOut,
    response_model_by_alias=True,
    summary="编排执行策略（含 FR-AO06 预算镜像）",
)
async def admin_get_orchestration_policy(db: DbSession) -> OrchestrationExecutionPolicyOut:
    doc = await read_orchestration_execution_policy(db)
    return OrchestrationExecutionPolicyOut.model_validate(doc)
