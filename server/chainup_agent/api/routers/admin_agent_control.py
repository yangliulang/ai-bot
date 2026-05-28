"""Admin — Agent runtime (R01–R06) · G01 read · instance log tabs (L01–L03 Phase1)."""

from __future__ import annotations

from typing import Annotated, Literal

from chainup_agent.api.deps import DbSession, require_admin_console_bearer
from chainup_agent.api.schemas.admin_agent_instances import (
    AdminAgentInstanceItem,
    admin_agent_instance_item_from_rows,
)
from chainup_agent.api.schemas.admin_agent_runtime import (
    AgentBatchFailureItem,
    AgentBatchRuntimeResponse,
    AgentRuntimeBatchRequest,
    GlobalAgentGateResponse,
)
from chainup_agent.api.schemas.admin_instance_logs import (
    InstanceConversationLogItem,
    InstanceConversationLogsResponse,
    InstanceErrorLogItem,
    InstanceErrorLogsResponse,
    InstanceToolLogItem,
    InstanceToolLogsResponse,
)
from chainup_agent.application.admin_agent_instances import get_agent_instance_joined_admin
from chainup_agent.application.admin_agent_runtime import (
    RuntimeAction,
    apply_agent_instance_runtime_action,
)
from chainup_agent.application.admin_instance_logs import (
    count_conversation_logs_for_instance,
    count_tool_logs_for_instance,
    list_conversation_logs_for_instance,
    list_error_logs_for_instance,
    list_tool_logs_for_instance,
    require_instance_user_id_str,
)
from chainup_agent.core.config import get_settings
from chainup_agent.core.errors import AppError
from fastapi import APIRouter, Depends, Path, Query

router = APIRouter(
    prefix="/api/v1/admin/agents",
    tags=["Admin — Agent runtime"],
    dependencies=[Depends(require_admin_console_bearer)],
)


@router.get(
    "/runtime/global-agent-gate",
    response_model=GlobalAgentGateResponse,
    response_model_by_alias=True,
    summary="G01 · 全局门禁只读（横幅数据源）",
)
async def get_global_agent_gate() -> GlobalAgentGateResponse:
    s = get_settings()
    switch_on = not s.agent_runtime_global_disabled
    ops = s.agent_runtime_ops_suspended
    reasons: list[str] = []
    msg: str | None = None
    if not switch_on:
        reasons.append("AGENT_GLOBAL_OFF")
        msg = "GLOBAL_AGENT_SWITCH=OFF（G01）：禁止承接类 Start / Resume；Pause / Stop 仍可用。"
    elif ops:
        reasons.append("AGENT_OPS_SUSPENDED")
        msg = "运维全局暂停（AGENT_OPS_SUSPENDED）。"
    return GlobalAgentGateResponse(
        global_agent_switch_on=switch_on,
        ops_suspended=ops,
        banner_message=msg,
        reason_codes=reasons,
    )


@router.post(
    "/instances/{instance_id}/runtime/{action}",
    response_model=AdminAgentInstanceItem,
    response_model_by_alias=True,
    summary="Runtime 单实例 R01～R05 · post …/runtime/{action}",
)
async def post_instance_runtime_action(
    instance_id: str,
    action: Annotated[
        Literal["start", "pause", "resume", "stop"],
        Path(description="start | pause | resume | stop"),
    ],
    db: DbSession,
) -> AdminAgentInstanceItem:
    settings = get_settings()
    await apply_agent_instance_runtime_action(
        db,
        settings=settings,
        instance_public_id=instance_id,
        action=action,  # type: ignore[arg-type]
    )
    await db.commit()
    pair = await get_agent_instance_joined_admin(db, instance_public_id=instance_id)
    if pair is None:
        raise AppError(
            code="AGENT_ADMIN_INSTANCE_NOT_FOUND",
            message="实例不存在。",
            status_code=404,
            details={"instanceId": instance_id.strip()[:80]},
        )
    ai, tb = pair
    return admin_agent_instance_item_from_rows(
        instance_row=ai, binding_row=tb, settings=settings
    )


@router.post(
    "/instances/runtime/batch",
    response_model=AgentBatchRuntimeResponse,
    response_model_by_alias=True,
    summary="Runtime 批量 R06",
)
async def post_instances_runtime_batch(
    db: DbSession,
    body: AgentRuntimeBatchRequest,
) -> AgentBatchRuntimeResponse:
    settings = get_settings()
    action: RuntimeAction = body.action  # type: ignore[assignment]
    if action in ("start", "resume") and (
        settings.agent_runtime_global_disabled or settings.agent_runtime_ops_suspended
    ):
        if settings.agent_runtime_global_disabled:
            raise AppError(
                code="AGENT_GLOBAL_OFF",
                message="批量 Start / Resume 在 GLOBAL_AGENT_SWITCH=OFF 时被禁止（G01）。",
                status_code=422,
                details={},
            )
        raise AppError(
            code="AGENT_OPS_SUSPENDED",
            message="批量 Start / Resume 在运维全局暂停时被禁止。",
            status_code=422,
            details={},
        )

    seen: set[str] = set()
    uniq: list[str] = []
    for raw in body.instance_ids:
        iid = raw.strip()
        if not iid or iid in seen:
            continue
        seen.add(iid)
        uniq.append(iid)
    if not uniq:
        raise AppError(
            code="VALIDATION_ERROR",
            message="instanceIds 不能为空",
            status_code=422,
            details={"field": "instanceIds"},
        )

    succeeded: list[str] = []
    failures: list[AgentBatchFailureItem] = []
    for iid in uniq:
        try:
            await apply_agent_instance_runtime_action(
                db,
                settings=settings,
                instance_public_id=iid,
                action=action,
            )
            succeeded.append(iid)
        except AppError as exc:
            failures.append(
                AgentBatchFailureItem(
                    instance_id=iid,
                    code=exc.code,
                    message=(exc.message or "")[:1024],
                )
            )
    await db.commit()

    if failures and succeeded:
        return AgentBatchRuntimeResponse(
            code="AGENT_BATCH_PARTIAL",
            message="部分实例未受理，见 failures。",
            succeeded=succeeded,
            failures=failures,
        )
    if failures and not succeeded:
        return AgentBatchRuntimeResponse(
            code="AGENT_BATCH_PARTIAL",
            message="本批全部未受理。",
            succeeded=[],
            failures=failures,
        )
    return AgentBatchRuntimeResponse(
        succeeded=succeeded,
        failures=[],
    )


@router.get(
    "/instances/{instance_id}/logs/conversations",
    response_model=InstanceConversationLogsResponse,
    response_model_by_alias=True,
    summary="实例对话日志 L01（agent_execution 行投影）",
)
async def list_instance_conversation_logs(
    instance_id: str,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> InstanceConversationLogsResponse:
    uid = await require_instance_user_id_str(db, instance_public_id=instance_id)
    total = await count_conversation_logs_for_instance(db, user_id_str=uid)
    raw = await list_conversation_logs_for_instance(
        db, user_id_str=uid, limit=limit, offset=offset
    )
    items = [InstanceConversationLogItem.model_validate(x) for x in raw]
    return InstanceConversationLogsResponse(items=items, total=total)


@router.get(
    "/instances/{instance_id}/logs/tools",
    response_model=InstanceToolLogsResponse,
    response_model_by_alias=True,
    summary="实例 Tool 日志 L02（exchange_public / exchange_private 时间线条目）",
)
async def list_instance_tool_logs(
    instance_id: str,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> InstanceToolLogsResponse:
    uid = await require_instance_user_id_str(db, instance_public_id=instance_id)
    total = await count_tool_logs_for_instance(db, user_id_str=uid)
    raw = await list_tool_logs_for_instance(db, user_id_str=uid, limit=limit, offset=offset)
    items = [InstanceToolLogItem.model_validate(x) for x in raw]
    return InstanceToolLogsResponse(items=items, total=total)


@router.get(
    "/instances/{instance_id}/logs/errors",
    response_model=InstanceErrorLogsResponse,
    response_model_by_alias=True,
    summary="实例错误日志 L03（FAILED 执行 + 失败/unknown 时间线）",
)
async def list_instance_error_logs(
    instance_id: str,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> InstanceErrorLogsResponse:
    uid = await require_instance_user_id_str(db, instance_public_id=instance_id)
    raw, total = await list_error_logs_for_instance(
        db, user_id_str=uid, limit=limit, offset=offset
    )
    items = [InstanceErrorLogItem.model_validate(x) for x in raw]
    return InstanceErrorLogsResponse(items=items, total=total)
