"""Phase 2.1 — spot flash convert HTTP (quote + MARKET order)."""

from __future__ import annotations

from fastapi import APIRouter, Query

from chainup_agent.api.deps import DbSession
from chainup_agent.api.schemas.agent_spot_trade import (
    SpotAmendLimitOrderRequest,
    SpotAmendLimitOrderResponse,
    SpotCancelOrderRequest,
    SpotCancelOrderResponse,
    SpotFlashConvertRequest,
    SpotFlashConvertResponse,
    SpotLimitOrderRequest,
    SpotLimitOrderResponse,
    SpotOpenOrdersResponse,
    SpotQuoteResponse,
)
from chainup_agent.application.agent_execution_memory import (
    ExecutionAcceptRequest,
    ExecutionFinalizeRequest,
    execution_accept,
    execution_finalize,
)
from chainup_agent.application.agent_trade_http_finalize import finalize_trade_http_on_error
from chainup_agent.application.write_path_pipeline import (
    append_confirmation_required,
    append_user_confirmed,
    ensure_write_path_skill_spec_read,
)
from chainup_agent.application.agent_spot_trade import (
    spot_amend_limit_order_for_bound_user,
    spot_cancel_order_for_bound_user,
    spot_flash_convert_for_bound_user,
    spot_limit_order_for_bound_user,
    spot_open_orders_for_bound_user,
    spot_quote_for_bound_user,
)
from chainup_agent.core.config import get_settings
from chainup_agent.core.errors import AppError

router = APIRouter(prefix="/api/v1/agent/trade/spot", tags=["Agent — Spot trade (Phase 2.1)"])


@router.get(
    "/open-orders",
    response_model=SpotOpenOrdersResponse,
    response_model_by_alias=True,
    summary="现货当前委托（GET 交易所 /sapi/v2/openOrders）",
)
async def spot_open_orders(
    db: DbSession,
    user_id: str = Query(..., alias="userId", description="Telegram tg_id"),
    symbol: str | None = Query(None, description="可选；不传则返回全交易对（权重较高）"),
    limit: int | None = Query(
        None,
        ge=1,
        le=1000,
        description="可选；默认由交易所决定（文档默认 100）；最大 1000",
    ),
) -> SpotOpenOrdersResponse:
    payload = await spot_open_orders_for_bound_user(
        session=db,
        settings=get_settings(),
        user_id=user_id,
        symbol=symbol,
        limit=limit,
    )
    return SpotOpenOrdersResponse.model_validate(payload)


@router.get(
    "/quote",
    response_model=SpotQuoteResponse,
    response_model_by_alias=True,
    summary="现货闪兑询价（公开 ticker，须已完成托管绑定）",
)
async def spot_quote(
    db: DbSession,
    user_id: str = Query(..., alias="userId", description="Telegram tg_id"),
    symbol: str = Query(..., description="交易对，如 BTC-USDT"),
) -> SpotQuoteResponse:
    payload = await spot_quote_for_bound_user(
        session=db,
        settings=get_settings(),
        user_id=user_id,
        symbol=symbol,
    )
    return SpotQuoteResponse.model_validate(payload)


@router.post(
    "/flash-convert",
    response_model=SpotFlashConvertResponse,
    response_model_by_alias=True,
    summary="现货闪兑下单（POST 交易所 /sapi/v2/order · MARKET）",
)
async def spot_flash_convert(
    db: DbSession, body: SpotFlashConvertRequest
) -> SpotFlashConvertResponse:
    settings = get_settings()
    acc = await execution_accept(
        db,
        ExecutionAcceptRequest(
            user_id=body.user_id,
            scenario_id="trade.spot.flash_convert",
            channel="http",
        ),
        source="http_api",
    )
    eid = acc.execution_id
    try:
        await ensure_write_path_skill_spec_read(
            db,
            execution_id=eid,
            user_id=body.user_id,
            scenario_id="trade.spot.flash_convert",
            channel="http",
        )
        await append_confirmation_required(
            db,
            execution_id=eid,
            user_id=body.user_id,
            scenario_id="trade.spot.flash_convert",
            channel="http",
            confirm_kind="type_a_http_body",
            extra={
                "symbol": body.symbol,
                "side": body.side,
                "quantityRequested": body.volume,
            },
        )
        await append_user_confirmed(
            db,
            execution_id=eid,
            user_id=body.user_id,
            scenario_id="trade.spot.flash_convert",
            channel="http_api",
            extra={"implicitConfirm": True},
        )
        payload = await spot_flash_convert_for_bound_user(
            session=db,
            settings=settings,
            user_id=body.user_id,
            symbol=body.symbol,
            side=body.side,
            volume=body.volume,
            new_client_order_id=body.new_client_order_id,
            timeline_execution_id=eid,
            timeline_channel="http_api",
            timeline_include_quote=True,
        )
        await execution_finalize(
            db,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="SUCCESS", note="flash_convert_http"
            ),
        )
        await db.commit()
        return SpotFlashConvertResponse.model_validate(payload)
    except AppError as exc:
        await finalize_trade_http_on_error(db, eid, exc, note_prefix="flash_convert_http")
        await db.commit()
        raise


@router.post(
    "/limit-order",
    response_model=SpotLimitOrderResponse,
    response_model_by_alias=True,
    summary="现货限价下单（POST 交易所 /sapi/v2/order · LIMIT）",
)
async def spot_limit_order(
    db: DbSession, body: SpotLimitOrderRequest
) -> SpotLimitOrderResponse:
    settings = get_settings()
    acc = await execution_accept(
        db,
        ExecutionAcceptRequest(
            user_id=body.user_id,
            scenario_id="trade.spot.limit_order",
            channel="http",
        ),
        source="http_api",
    )
    eid = acc.execution_id
    try:
        await ensure_write_path_skill_spec_read(
            db,
            execution_id=eid,
            user_id=body.user_id,
            scenario_id="trade.spot.limit_order",
            channel="http",
        )
        await append_confirmation_required(
            db,
            execution_id=eid,
            user_id=body.user_id,
            scenario_id="trade.spot.limit_order",
            channel="http",
            confirm_kind="type_a_http_body",
            extra={
                "symbol": body.symbol,
                "side": body.side,
                "limitPrice": body.price,
                "quantityRequested": body.volume,
            },
        )
        await append_user_confirmed(
            db,
            execution_id=eid,
            user_id=body.user_id,
            scenario_id="trade.spot.limit_order",
            channel="http_api",
            extra={"implicitConfirm": True},
        )
        payload = await spot_limit_order_for_bound_user(
            session=db,
            settings=settings,
            user_id=body.user_id,
            symbol=body.symbol,
            side=body.side,
            volume=body.volume,
            price=body.price,
            time_in_force=body.time_in_force,
            new_client_order_id=body.new_client_order_id,
            timeline_execution_id=eid,
            timeline_channel="http_api",
            timeline_include_quote=True,
        )
        await execution_finalize(
            db,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="SUCCESS", note="limit_order_http"
            ),
        )
        await db.commit()
        return SpotLimitOrderResponse.model_validate(payload)
    except AppError as exc:
        await finalize_trade_http_on_error(db, eid, exc, note_prefix="limit_order_http")
        await db.commit()
        raise


@router.post(
    "/amend-limit-order",
    response_model=SpotAmendLimitOrderResponse,
    response_model_by_alias=True,
    summary="现货逻辑改单（cancel→order · CC-P0-02）",
)
async def spot_amend_limit_order(
    db: DbSession, body: SpotAmendLimitOrderRequest
) -> SpotAmendLimitOrderResponse:
    settings = get_settings()
    acc = await execution_accept(
        db,
        ExecutionAcceptRequest(
            user_id=body.user_id,
            scenario_id="trade.spot.amend_limit_order",
            channel="http",
        ),
        source="http_api",
    )
    eid = acc.execution_id
    try:
        payload = await spot_amend_limit_order_for_bound_user(
            session=db,
            settings=settings,
            user_id=body.user_id,
            symbol=body.symbol,
            order_id=body.order_id,
            price=body.price,
            volume=body.volume,
            time_in_force=body.time_in_force,
            new_client_order_id=body.new_client_order_id,
            timeline_execution_id=eid,
            timeline_channel="http_api",
            timeline_include_quote=True,
        )
        await execution_finalize(
            db,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="SUCCESS", note="spot_amend_http"
            ),
        )
        await db.commit()
        return SpotAmendLimitOrderResponse.model_validate(payload)
    except AppError as exc:
        await finalize_trade_http_on_error(db, eid, exc, note_prefix="spot_amend_http")
        await db.commit()
        raise


@router.post(
    "/cancel",
    response_model=SpotCancelOrderResponse,
    response_model_by_alias=True,
    summary="现货撤单（POST 交易所 /sapi/v2/cancel）",
)
async def spot_cancel_order(
    db: DbSession, body: SpotCancelOrderRequest
) -> SpotCancelOrderResponse:
    settings = get_settings()
    acc = await execution_accept(
        db,
        ExecutionAcceptRequest(
            user_id=body.user_id,
            scenario_id="trade.spot.cancel_order",
            channel="http",
        ),
        source="http_api",
    )
    eid = acc.execution_id
    try:
        payload = await spot_cancel_order_for_bound_user(
            session=db,
            settings=settings,
            user_id=body.user_id,
            symbol=body.symbol,
            order_id=body.order_id,
            new_client_order_id=body.new_client_order_id,
            timeline_execution_id=eid,
            timeline_channel="http_api",
        )
        await execution_finalize(
            db,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="SUCCESS", note="spot_cancel_http"
            ),
        )
        await db.commit()
        return SpotCancelOrderResponse.model_validate(payload)
    except AppError as exc:
        await finalize_trade_http_on_error(db, eid, exc, note_prefix="spot_cancel_http")
        await db.commit()
        raise
