"""§6 P0 — 504 / UNKNOWN trading reconcile HTTP."""

from __future__ import annotations

from fastapi import APIRouter, Query

from chainup_agent.api.deps import DbSession
from chainup_agent.api.schemas.agent_trading_reconcile import (
    TradingReconcileRequest,
    TradingReconcileResponse,
    TradingReconcileStatusResponse,
)
from chainup_agent.application.agent_trading_reconcile import (
    trading_reconcile_for_bound_user,
    trading_reconcile_status_for_execution,
)
from chainup_agent.core.config import get_settings

router = APIRouter(
    prefix="/api/v1/agent/trading",
    tags=["Agent — Trading reconcile (§6)"],
)


@router.post(
    "/reconcile",
    response_model=TradingReconcileResponse,
    response_model_by_alias=True,
    summary="发起写路径对账（504/UNKNOWN · 查单闭合终态）",
)
async def trading_reconcile(
    db: DbSession, body: TradingReconcileRequest
) -> TradingReconcileResponse:
    payload = await trading_reconcile_for_bound_user(
        session=db,
        settings=get_settings(),
        user_id=body.user_id,
        execution_id=body.execution_id,
        venue=body.venue,
        symbol=body.symbol,
        order_id=body.order_id,
        client_order_id=body.client_order_id,
        case_kind_override=body.case_kind,
    )
    await db.commit()
    return TradingReconcileResponse.model_validate(payload)


@router.get(
    "/reconcile/status",
    response_model=TradingReconcileStatusResponse,
    response_model_by_alias=True,
    summary="查询 execution 对账状态（最近一次 trading.reconcile 或待对账 UNKNOWN）",
)
async def trading_reconcile_status(
    db: DbSession,
    user_id: str = Query(..., alias="userId"),
    execution_id: str = Query(..., alias="executionId"),
) -> TradingReconcileStatusResponse:
    payload = await trading_reconcile_status_for_execution(
        session=db,
        user_id=user_id,
        execution_id=execution_id,
    )
    return TradingReconcileStatusResponse.model_validate(payload)
