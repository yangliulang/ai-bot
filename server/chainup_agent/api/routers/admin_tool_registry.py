"""Admin — Tool Registry mirror + idempotency audit (CC-P1-03 · MR-E)."""

from __future__ import annotations

from chainup_agent.api.deps import require_admin_console_bearer
from chainup_agent.api.schemas.admin_tool_registry import (
    RegistryIdempotencyAuditOut,
    RegistryMismatchOut,
    ToolRegistryMirrorEntryOut,
    ToolRegistryMirrorListOut,
)
from chainup_agent.application.registry_idempotency import (
    compute_idempotency_audit,
    registry_mirror_list_payload,
)
from fastapi import APIRouter, Depends, Query

router = APIRouter(
    prefix="/api/v1/admin/tools",
    tags=["Admin — Tool registry"],
    dependencies=[Depends(require_admin_console_bearer)],
)


@router.get(
    "/registry",
    response_model=ToolRegistryMirrorListOut,
    response_model_by_alias=True,
    summary="Registry 镜像列表",
)
async def list_tool_registry_mirror(
    entry_class: str | None = Query(default=None, alias="entryClass"),
    matrix_status: str | None = Query(default=None, alias="matrixStatus"),
) -> ToolRegistryMirrorListOut:
    payload = registry_mirror_list_payload(
        entry_class=entry_class,
        matrix_status=matrix_status,
    )
    return ToolRegistryMirrorListOut(
        registryVersion=payload["registryVersion"],
        items=[ToolRegistryMirrorEntryOut.model_validate(x) for x in payload["items"]],
    )


@router.get(
    "/registry/idempotency-audit",
    response_model=RegistryIdempotencyAuditOut,
    response_model_by_alias=True,
    summary="SSOT 幂等审计",
)
async def get_tool_registry_idempotency_audit() -> RegistryIdempotencyAuditOut:
    audit = compute_idempotency_audit()
    return RegistryIdempotencyAuditOut(
        ok=audit["ok"],
        auditVersion=audit["auditVersion"],
        skillMismatches=RegistryMismatchOut.model_validate(audit["skillMismatches"]),
        toolMismatches=RegistryMismatchOut.model_validate(audit["toolMismatches"]),
    )
