"""Phase 2.3 — futures order HTTP (POST /fapi/v1/order)."""

from __future__ import annotations

from fastapi import APIRouter, Query

from chainup_agent.api.deps import DbSession
from chainup_agent.api.schemas.agent_futures_trade import (
    FuturesCancelOrderRequest,
    FuturesCancelOrderResponse,
    FuturesOrderRequest,
    FuturesOrderResponse,
)
from chainup_agent.api.schemas.agent_futures_condition_trade import (
    FuturesConditionCancelRequest,
    FuturesConditionCancelResponse,
    FuturesConditionOrderRequest,
    FuturesConditionOrderResponse,
    FuturesConditionOrdersResponse,
)
from chainup_agent.application.agent_trade_http_finalize import finalize_trade_http_on_error
from chainup_agent.application.agent_execution_memory import (
    ExecutionAcceptRequest,
    ExecutionFinalizeRequest,
    execution_accept,
    execution_finalize,
)
from chainup_agent.application.agent_futures_trade import (
    futures_cancel_order_for_bound_user,
    futures_order_for_bound_user,
)
from chainup_agent.application.agent_futures_condition_trade import (
    futures_condition_order_cancel_for_bound_user,
    futures_condition_order_for_bound_user,
    futures_condition_orders_for_bound_user,
)
from chainup_agent.core.config import get_settings
from chainup_agent.core.errors import AppError

router = APIRouter(
    prefix="/api/v1/agent/trade/futures",
    tags=["Agent — Futures trade (Phase 2.3)"],
)


@router.post(
    "/order",
    response_model=FuturesOrderResponse,
    response_model_by_alias=True,
    summary="合约下单（POST 交易所 /fapi/v1/order · MARKET/LIMIT）",
)
async def futures_order(db: DbSession, body: FuturesOrderRequest) -> FuturesOrderResponse:
    settings = get_settings()
    if not settings.feature_agent_futures:
        raise AppError(
            code="FEATURE_AGENT_FUTURES_OFF",
            message="合约 Agent 写能力未开启（CHAINUP_AGENT_FEATURE_AGENT_FUTURES=false）。",
            status_code=403,
        )
    scenario_id = (
        "trade.futures.limit_order"
        if body.order_type == "LIMIT"
        else "trade.futures.market_order"
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
        payload = await futures_order_for_bound_user(
            session=db,
            settings=settings,
            user_id=body.user_id,
            symbol=body.symbol,
            side=body.side,
            order_type=body.order_type,
            volume=body.volume,
            price=body.price,
            open_close=body.open_close,
            reduce_only=body.reduce_only,
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
                note="futures_order_http",
            ),
        )
        await db.commit()
        return FuturesOrderResponse.model_validate(payload)
    except AppError as exc:
        await finalize_trade_http_on_error(db, eid, exc, note_prefix="futures_order_http")
        await db.commit()
        raise


@router.post(
    "/condition-order",
    response_model=FuturesConditionOrderResponse,
    response_model_by_alias=True,
    summary="合约条件单（POST 交易所 /fapi/v1/conditionOrder）",
)
async def futures_condition_order(
    db: DbSession, body: FuturesConditionOrderRequest
) -> FuturesConditionOrderResponse:
    settings = get_settings()
    if not settings.feature_agent_futures:
        raise AppError(
            code="FEATURE_AGENT_FUTURES_OFF",
            message="合约 Agent 写能力未开启（CHAINUP_AGENT_FEATURE_AGENT_FUTURES=false）。",
            status_code=403,
        )
    scenario_id = "automation.condition_order"
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
        payload = await futures_condition_order_for_bound_user(
            session=db,
            settings=settings,
            user_id=body.user_id,
            symbol=body.symbol,
            side=body.side,
            order_type=body.order_type,
            volume=body.volume,
            trigger_price=body.trigger_price,
            trigger_type=body.trigger_type,
            price=body.price,
            open_close=body.open_close,
            position_type=body.position_type,
            order_unit=body.order_unit,
            scenario_id=scenario_id,
            timeline_execution_id=eid,
            timeline_channel="http_api",
        )
        await execution_finalize(
            db,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="SUCCESS",
                note="futures_condition_order_http",
            ),
        )
        await db.commit()
        return FuturesConditionOrderResponse.model_validate(payload)
    except AppError as exc:
        await finalize_trade_http_on_error(db, eid, exc, note_prefix="futures_condition_order_http")
        await db.commit()
        raise


@router.post(
    "/cancel",
    response_model=FuturesCancelOrderResponse,
    response_model_by_alias=True,
    summary="合约撤单（POST 交易所 /fapi/v1/cancel）",
)
async def futures_cancel_order(
    db: DbSession, body: FuturesCancelOrderRequest
) -> FuturesCancelOrderResponse:
    settings = get_settings()
    if not settings.feature_agent_futures:
        raise AppError(
            code="FEATURE_AGENT_FUTURES_OFF",
            message="合约 Agent 写能力未开启（CHAINUP_AGENT_FEATURE_AGENT_FUTURES=false）。",
            status_code=403,
        )
    scenario_id = "trade.futures.cancel_order"
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
        payload = await futures_cancel_order_for_bound_user(
            session=db,
            settings=settings,
            user_id=body.user_id,
            symbol=body.symbol,
            order_id=body.order_id,
            scenario_id=scenario_id,
            timeline_execution_id=eid,
            timeline_channel="http_api",
        )
        await execution_finalize(
            db,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="SUCCESS",
                note="futures_cancel_http",
            ),
        )
        await db.commit()
        return FuturesCancelOrderResponse.model_validate(payload)
    except AppError as exc:
        await finalize_trade_http_on_error(db, eid, exc, note_prefix="futures_cancel_http")
        await db.commit()
        raise


@router.get(
    "/condition-orders",
    response_model=FuturesConditionOrdersResponse,
    response_model_by_alias=True,
    summary="查询合约条件单/计划委托（GET /fapi/v1/openOrders 过滤）",
)
async def futures_condition_orders(
    db: DbSession,
    user_id: str = Query(..., alias="userId", description="Telegram tg_id"),
    symbol: str | None = Query(None, description="可选合约标的（如 BTC-USDT）"),
) -> FuturesConditionOrdersResponse:
    settings = get_settings()
    if not settings.feature_agent_futures:
        raise AppError(
            code="FEATURE_AGENT_FUTURES_OFF",
            message="合约 Agent 能力未开启（CHAINUP_AGENT_FEATURE_AGENT_FUTURES=false）。",
            status_code=403,
        )
    payload = await futures_condition_orders_for_bound_user(
        session=db,
        settings=settings,
        user_id=user_id,
        symbol=symbol,
    )
    await db.commit()
    return FuturesConditionOrdersResponse.model_validate(payload)


@router.post(
    "/cancel-condition",
    response_model=FuturesConditionCancelResponse,
    response_model_by_alias=True,
    summary="撤销合约条件单（POST 交易所 /fapi/v1/cancel）",
)
async def futures_cancel_condition_order(
    db: DbSession, body: FuturesConditionCancelRequest
) -> FuturesConditionCancelResponse:
    settings = get_settings()
    if not settings.feature_agent_futures:
        raise AppError(
            code="FEATURE_AGENT_FUTURES_OFF",
            message="合约 Agent 写能力未开启（CHAINUP_AGENT_FEATURE_AGENT_FUTURES=false）。",
            status_code=403,
        )
    scenario_id = "automation.condition_order_cancel"
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
        payload = await futures_condition_order_cancel_for_bound_user(
            session=db,
            settings=settings,
            user_id=body.user_id,
            symbol=body.symbol,
            order_id=body.order_id,
            timeline_execution_id=eid,
            timeline_channel="http_api",
        )
        await execution_finalize(
            db,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="SUCCESS",
                note="futures_condition_cancel_http",
            ),
        )
        await db.commit()
        return FuturesConditionCancelResponse.model_validate(payload)
    except AppError as exc:
        await finalize_trade_http_on_error(
            db, eid, exc, note_prefix="futures_condition_cancel_http"
        )
        await db.commit()
        raise
