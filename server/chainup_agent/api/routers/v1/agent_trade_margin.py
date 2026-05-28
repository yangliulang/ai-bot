"""Phase 2.4 — cross margin order HTTP (POST /sapi/v2/margin/order)."""

from __future__ import annotations

from fastapi import APIRouter

from chainup_agent.api.deps import DbSession
from chainup_agent.api.schemas.agent_margin_trade import (
    MarginOrderRequest,
    MarginOrderResponse,
)
from chainup_agent.application.agent_trade_http_finalize import finalize_trade_http_on_error
from chainup_agent.application.agent_execution_memory import (
    ExecutionAcceptRequest,
    ExecutionFinalizeRequest,
    execution_accept,
    execution_finalize,
)
from chainup_agent.application.agent_margin_trade import margin_order_for_bound_user
from chainup_agent.core.config import get_settings
from chainup_agent.core.errors import AppError

router = APIRouter(
    prefix="/api/v1/agent/trade/margin",
    tags=["Agent — Margin trade (Phase 2.4)"],
)


@router.post(
    "/order",
    response_model=MarginOrderResponse,
    response_model_by_alias=True,
    summary="全仓杠杆下单（POST 交易所 /sapi/v2/margin/order · MARKET/LIMIT）",
)
async def margin_order(db: DbSession, body: MarginOrderRequest) -> MarginOrderResponse:
    settings = get_settings()
    if not settings.feature_agent_margin:
        raise AppError(
            code="FEATURE_AGENT_MARGIN_OFF",
            message="全仓杠杆 Agent 写能力未开启（CHAINUP_AGENT_FEATURE_AGENT_MARGIN=false）。",
            status_code=403,
        )
    scenario_id = (
        "margin.cross.limit_order"
        if body.order_type == "LIMIT"
        else "margin.cross.market_order"
    )
    acc = await execution_accept(
        db,
        ExecutionAcceptRequest(
            user_id=body.user_id,
            scenario_id=scenario_id,
            channel="http",
        ),
        source="http_api",
    )
    eid = acc.execution_id
    try:
        payload = await margin_order_for_bound_user(
            session=db,
            settings=settings,
            user_id=body.user_id,
            symbol=body.symbol,
            side=body.side,
            order_type=body.order_type,
            volume=body.volume,
            price=body.price,
            new_client_order_id=body.new_client_order_id,
            scenario_id=scenario_id,
            timeline_execution_id=eid,
            timeline_channel="http_api",
        )
        await execution_finalize(
            db,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="SUCCESS",
                note="margin_order_http",
            ),
        )
        await db.commit()
        return MarginOrderResponse.model_validate(payload)
    except AppError as exc:
        await finalize_trade_http_on_error(db, eid, exc, note_prefix="margin_order_http")
        await db.commit()
        raise
