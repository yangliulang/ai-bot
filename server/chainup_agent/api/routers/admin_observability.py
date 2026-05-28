"""Admin observability — persisted execution list/detail (`agent_execution`)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from chainup_agent.api.deps import DbSession, require_admin_console_bearer
from chainup_agent.api.schemas.admin_agent_executions import (
    AdminAgentExecutionItem,
    AdminAgentExecutionListResponse,
    admin_agent_execution_item_from_row,
)
from chainup_agent.api.schemas.admin_observability_timeline import (
    ObservabilityTimelineResponse,
    observability_timeline_item_from_row,
)
from chainup_agent.application.admin_agent_executions import (
    count_agent_executions_admin,
    delete_agent_execution_admin,
    get_agent_execution_admin,
    list_agent_executions_admin,
)
from chainup_agent.api.schemas.admin_observability_tool_llm import (
    LlmCallItem,
    LlmUsageSummaryResponse,
    ToolCallDetailItem,
    ToolCallsPageResponse,
)
from chainup_agent.application.admin_observability_execution_detail import (
    list_llm_usage_for_execution,
    list_tool_calls_for_execution,
)
from chainup_agent.application.admin_observability_execution_tabs import (
    build_execution_tabs_for_id,
    get_execution_recovery_view,
    list_execution_retries,
    list_execution_runtime_events,
    list_execution_task_queue,
)
from chainup_agent.api.schemas.admin_observability_execution_tabs import (
    ExecutionRecoveryResponse,
    ExecutionRetriesResponse,
    ExecutionRetryItem,
    ExecutionRuntimeEventItem,
    ExecutionRuntimeEventsResponse,
    ExecutionTaskQueueItem,
    ExecutionTaskQueueResponse,
)
from chainup_agent.api.schemas.admin_scenario_skill_scope import ScenarioSkillScopeResponse
from chainup_agent.application.agent_execution_events import list_timeline_events_for_execution
from chainup_agent.application.scenario_skill_scope import resolve_scenario_skill_scope_view
from chainup_agent.core.errors import AppError
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

router = APIRouter(
    prefix="/api/v1/admin/observability",
    tags=["Admin — Observability"],
    dependencies=[Depends(require_admin_console_bearer)],
)

_ALLOWED_EXEC_STATES = frozenset({"ACCEPTED", "SUCCEEDED", "FAILED", "CANCELLED"})


def _optional_state_filter(raw: str | None) -> str | None:
    if raw is None or not str(raw).strip():
        return None
    s = str(raw).strip().upper()
    if s not in _ALLOWED_EXEC_STATES:
        raise AppError(
            code="VALIDATION_ERROR",
            message=("state 须为 ACCEPTED、SUCCEEDED、FAILED、CANCELLED 之一（或不传）"),
            status_code=422,
            details={"field": "state", "value": str(raw).strip()[:64]},
        )
    return s


@router.get(
    "/executions",
    response_model=AdminAgentExecutionListResponse,
    response_model_by_alias=True,
    summary="执行列表（`agent_execution` 分页 + 筛选）",
)
async def list_admin_observability_executions(
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    execution_id: str | None = Query(default=None, alias="executionId"),
    user_id: str | None = Query(default=None, alias="userId"),
    channel: str | None = None,
    scenario_id: str | None = Query(default=None, alias="scenarioId"),
    state: str | None = None,
    keyword: str | None = Query(
        default=None,
        description="模糊匹配 executionId / userId / scenarioId 子串",
        max_length=256,
    ),
    created_after: Annotated[datetime | None, Query(alias="createdAfter")] = None,
    created_before: Annotated[datetime | None, Query(alias="createdBefore")] = None,
) -> AdminAgentExecutionListResponse:
    st = _optional_state_filter(state)
    filt_eid = execution_id.strip() if execution_id and execution_id.strip() else None
    filt_uid = user_id.strip() if user_id and user_id.strip() else None
    filt_ch = channel.strip() if channel and channel.strip() else None
    filt_sid = scenario_id.strip() if scenario_id and scenario_id.strip() else None

    total = await count_agent_executions_admin(
        db,
        execution_id=filt_eid,
        user_id=filt_uid,
        channel=filt_ch,
        scenario_id=filt_sid,
        state=st,
        keyword=keyword,
        created_after=created_after,
        created_before=created_before,
    )
    rows = await list_agent_executions_admin(
        db,
        limit=limit,
        offset=offset,
        execution_id=filt_eid,
        user_id=filt_uid,
        channel=filt_ch,
        scenario_id=filt_sid,
        state=st,
        keyword=keyword,
        created_after=created_after,
        created_before=created_before,
    )
    items = [admin_agent_execution_item_from_row(r) for r in rows]
    return AdminAgentExecutionListResponse(items=items, total=total)


@router.get(
    "/scenarios/{scenario_id}/skill-scope",
    response_model=ScenarioSkillScopeResponse,
    response_model_by_alias=True,
    summary="场景 Skill 范围（治理面板只读 · SC-PM-21）",
)
async def get_admin_observability_scenario_skill_scope(
    scenario_id: str,
    db: DbSession,
) -> ScenarioSkillScopeResponse:
    sid = scenario_id.strip()
    if not sid:
        raise AppError(
            code="VALIDATION_ERROR",
            message="scenarioId 不能为空",
            status_code=422,
            details={"field": "scenarioId"},
        )
    doc = await resolve_scenario_skill_scope_view(db, scenario_id=sid)
    return ScenarioSkillScopeResponse.from_view(doc)


@router.get(
    "/executions/{execution_id}/timeline",
    response_model=ObservabilityTimelineResponse,
    response_model_by_alias=True,
    summary="执行时间线（FR-MC801 下限；从 Telegram 闪兑等写入 agent_execution_event）",
)
async def get_admin_observability_execution_timeline(
    execution_id: str,
    db: DbSession,
) -> ObservabilityTimelineResponse:
    parent = await get_agent_execution_admin(db, execution_public_id=execution_id)
    if parent is None:
        raise AppError(
            code="AGENT_ADMIN_EXECUTION_NOT_FOUND",
            message="未找到该 execution",
            status_code=404,
            details={"executionId": execution_id.strip()[:80]},
        )
    ev_rows = await list_timeline_events_for_execution(db, execution_public_id=execution_id)
    return ObservabilityTimelineResponse(
        items=[observability_timeline_item_from_row(r) for r in ev_rows]
    )


@router.get(
    "/executions/{execution_id}/tool-calls",
    response_model=ToolCallsPageResponse,
    response_model_by_alias=True,
    summary="工具调用明细 FR-MC803（trading.exchange_* · agent.tool.call）",
)
async def get_admin_observability_execution_tool_calls(
    execution_id: str,
    db: DbSession,
) -> ToolCallsPageResponse:
    parent = await get_agent_execution_admin(db, execution_public_id=execution_id)
    if parent is None:
        raise AppError(
            code="AGENT_ADMIN_EXECUTION_NOT_FOUND",
            message="未找到该 execution",
            status_code=404,
            details={"executionId": execution_id.strip()[:80]},
        )
    raw = await list_tool_calls_for_execution(db, execution_public_id=execution_id)
    return ToolCallsPageResponse(
        items=[ToolCallDetailItem.model_validate(x) for x in raw],
    )


async def _require_execution_or_404(db: DbSession, execution_id: str) -> None:
    parent = await get_agent_execution_admin(db, execution_public_id=execution_id)
    if parent is None:
        raise AppError(
            code="AGENT_ADMIN_EXECUTION_NOT_FOUND",
            message="未找到该 execution",
            status_code=404,
            details={"executionId": execution_id.strip()[:80]},
        )


@router.get(
    "/executions/{execution_id}/queue",
    response_model=ExecutionTaskQueueResponse,
    response_model_by_alias=True,
    summary="执行详情 · 任务队列（编排步骤 + 写路径未完成步）",
)
async def get_admin_observability_execution_queue(
    execution_id: str,
    db: DbSession,
) -> ExecutionTaskQueueResponse:
    await _require_execution_or_404(db, execution_id)
    row, events = await build_execution_tabs_for_id(db, execution_public_id=execution_id)
    assert row is not None
    raw = await list_execution_task_queue(db, execution=row, events=events)
    return ExecutionTaskQueueResponse(
        items=[ExecutionTaskQueueItem.model_validate(x) for x in raw],
    )


@router.get(
    "/executions/{execution_id}/events",
    response_model=ExecutionRuntimeEventsResponse,
    response_model_by_alias=True,
    summary="执行详情 · 运行事件摘录（tool/retry/对账等；全量检索走 FR-MC802）",
)
async def get_admin_observability_execution_events(
    execution_id: str,
    db: DbSession,
) -> ExecutionRuntimeEventsResponse:
    await _require_execution_or_404(db, execution_id)
    row, events = await build_execution_tabs_for_id(db, execution_public_id=execution_id)
    assert row is not None
    raw = await list_execution_runtime_events(db, execution=row, events=events)
    return ExecutionRuntimeEventsResponse(
        items=[ExecutionRuntimeEventItem.model_validate(x) for x in raw],
    )


@router.get(
    "/executions/{execution_id}/retries",
    response_model=ExecutionRetriesResponse,
    response_model_by_alias=True,
    summary="执行详情 · 重试历史（由时间线 retry/reconcile/unknown 摘录）",
)
async def get_admin_observability_execution_retries(
    execution_id: str,
    db: DbSession,
) -> ExecutionRetriesResponse:
    await _require_execution_or_404(db, execution_id)
    row, events = await build_execution_tabs_for_id(db, execution_public_id=execution_id)
    assert row is not None
    raw = await list_execution_retries(db, execution=row, events=events)
    return ExecutionRetriesResponse(
        retry_count=raw["retryCount"],
        items=[ExecutionRetryItem.model_validate(x) for x in raw["items"]],
    )


@router.get(
    "/executions/{execution_id}/recovery",
    response_model=ExecutionRecoveryResponse,
    response_model_by_alias=True,
    summary="执行详情 · 恢复与对账（对账状态 + 协查深链）",
)
async def get_admin_observability_execution_recovery(
    execution_id: str,
    db: DbSession,
) -> ExecutionRecoveryResponse:
    await _require_execution_or_404(db, execution_id)
    row, events = await build_execution_tabs_for_id(db, execution_public_id=execution_id)
    assert row is not None
    raw = await get_execution_recovery_view(db, execution=row, events=events)
    return ExecutionRecoveryResponse.model_validate(raw)


@router.get(
    "/executions/{execution_id}/llm",
    response_model=LlmUsageSummaryResponse,
    response_model_by_alias=True,
    summary="LLM 计量明细 FR-MC804（eventName llm.* · 无 messages 全文）",
)
async def get_admin_observability_execution_llm(
    execution_id: str,
    db: DbSession,
) -> LlmUsageSummaryResponse:
    parent = await get_agent_execution_admin(db, execution_public_id=execution_id)
    if parent is None:
        raise AppError(
            code="AGENT_ADMIN_EXECUTION_NOT_FOUND",
            message="未找到该 execution",
            status_code=404,
            details={"executionId": execution_id.strip()[:80]},
        )
    raw = await list_llm_usage_for_execution(db, execution_public_id=execution_id)
    calls = [LlmCallItem.model_validate(c) for c in raw.get("calls", [])]
    return LlmUsageSummaryResponse(
        model_id=raw.get("modelId"),
        input_tokens=raw.get("inputTokens"),
        output_tokens=raw.get("outputTokens"),
        total_tokens=raw.get("totalTokens"),
        calls=calls,
    )


@router.get(
    "/executions/{execution_id}",
    response_model=AdminAgentExecutionItem,
    response_model_by_alias=True,
    summary="执行详情（单条 `agent_execution`）",
)
async def get_admin_observability_execution(
    execution_id: str,
    db: DbSession,
) -> AdminAgentExecutionItem:
    row = await get_agent_execution_admin(db, execution_public_id=execution_id)
    if row is None:
        raise AppError(
            code="AGENT_ADMIN_EXECUTION_NOT_FOUND",
            message="未找到该 execution",
            status_code=404,
            details={"executionId": execution_id.strip()[:80]},
        )
    return admin_agent_execution_item_from_row(row)


@router.delete(
    "/executions/{execution_id}",
    status_code=204,
    summary="删除执行记录（硬删除 `agent_execution`，联调 / 运维清理）",
)
async def delete_admin_observability_execution(
    execution_id: str,
    db: DbSession,
) -> Response:
    deleted = await delete_agent_execution_admin(db, execution_public_id=execution_id)
    if not deleted:
        raise AppError(
            code="AGENT_ADMIN_EXECUTION_NOT_FOUND",
            message="未找到该 execution",
            status_code=404,
            details={"executionId": execution_id.strip()[:80]},
        )
    await db.commit()
    return Response(status_code=204)
