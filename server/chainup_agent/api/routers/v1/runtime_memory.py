"""Runtime — STM session memory (clear-stm · context preview)."""

from __future__ import annotations

from chainup_agent.api.schemas.runtime_memory import (
    AgentRuntimeMemoryContextPreviewOut,
    ClarifySessionSnapshotOut,
    ClearSessionStmRequest,
    ClearSessionStmResponse,
    L0MessagePreviewOut,
    MemorySessionContextPreviewOut,
    SemanticNarrativeBlockOut,
)
from chainup_agent.application.clarify_session import get_clarify_session_raw
from chainup_agent.application.eval_memory_stm import build_session_cleared_event
from chainup_agent.application.memory_session_store import (
    clear_session_stm,
    get_session_context_preview,
)
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/runtime/memory", tags=["Runtime — Memory"])


def _clarify_session_out(session_id: str) -> ClarifySessionSnapshotOut | None:
    snap = get_clarify_session_raw(session_id)
    if snap is None:
        return None
    d = snap.to_dict()
    return ClarifySessionSnapshotOut(
        sessionId=d["sessionId"],
        executionId=d["executionId"],
        clarifyTurn=d["clarifyTurn"],
        resolvedSlotsSoFar=d.get("resolvedSlotsSoFar") or {},
        pendingClarifyKind=d.get("pendingClarifyKind"),
        lifecycleState=d.get("lifecycleState"),
        abandoned=d.get("abandoned"),
    )


def _to_context_out(raw: dict, *, session_id: str) -> MemorySessionContextPreviewOut:
    mem = raw["memoryContext"]
    block = mem.get("semanticNarrativeBlock")
    block_out = SemanticNarrativeBlockOut(**block) if block else None
    return MemorySessionContextPreviewOut(
        sessionId=raw["sessionId"],
        userId=raw["userId"],
        l0MessageCount=raw["l0MessageCount"],
        l0MessagesPreview=[
            L0MessagePreviewOut(role=p["role"], contentPreview=p["contentPreview"])
            for p in raw.get("l0MessagesPreview") or []
        ],
        pendingTypeAValid=raw.get("pendingTypeAValid"),
        memoryContext=AgentRuntimeMemoryContextPreviewOut(
            semanticNarrativeEnabled=mem["semanticNarrativeEnabled"],
            semanticNarrativeBlock=block_out,
            userMemoryRevokedAt=mem.get("userMemoryRevokedAt"),
            sessionClearedAt=mem.get("sessionClearedAt"),
        ),
        clarifySession=_clarify_session_out(session_id),
    )


@router.post(
    "/sessions/{session_id}/clear-stm",
    response_model=ClearSessionStmResponse,
    response_model_by_alias=True,
    summary="清空本会话 STM（FR-STM01）",
)
async def post_runtime_memory_session_clear_stm(
    session_id: str,
    body: ClearSessionStmRequest,
) -> ClearSessionStmResponse:
    cleared_at, pending_invalidated = clear_session_stm(
        session_id,
        body.user_id,
        invalidate_pending_type_a=body.invalidate_pending_type_a,
    )
    event = build_session_cleared_event(body.user_id, session_id, cleared_at)
    return ClearSessionStmResponse(
        sessionId=session_id,
        userId=body.user_id,
        clearedAt=cleared_at,
        pendingTypeAInvalidated=pending_invalidated,
        eventName=event["eventName"],
    )


@router.get(
    "/sessions/{session_id}/context",
    response_model=MemorySessionContextPreviewOut,
    response_model_by_alias=True,
    summary="会话记忆装配预览",
)
async def get_runtime_memory_session_context(
    session_id: str,
    user_id: str = Query(..., alias="userId"),
    semantic_narrative_enabled: bool = Query(
        default=False,
        alias="semanticNarrativeEnabled",
    ),
) -> MemorySessionContextPreviewOut:
    raw = get_session_context_preview(
        session_id,
        user_id,
        semantic_narrative_enabled=semantic_narrative_enabled,
    )
    return _to_context_out(raw, session_id=session_id)
