"""Phase 2.4 — cross margin market/limit order (POST /sapi/v2/margin/order)."""

from __future__ import annotations

import logging
import secrets
from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_api_binding_confirm import (
    decrypt_binding_trade_credentials_for_row,
)
from chainup_agent.application.agent_execution_events import append_execution_timeline_event
from chainup_agent.application.agent_routing_exchange_read import (
    load_binding_row_for_telegram_user,
    parse_telegram_user_id_numeric,
)
from chainup_agent.application.agent_spot_trade import (
    _last_price_from_coobit_ticker,
    _parse_positive_price,
    _parse_positive_volume,
    _quote_volume_for_market_buy,
    fetch_spot_public_ticker_json_with_fallbacks,
    spot_ticker_symbol_candidates,
)
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.domain.canonical_trading import (
    coobit_sapi_v2_margin_order_body,
    timeline_obs_venue_canonical,
)
from chainup_agent.infrastructure.exchange.coobit_openapi import (
    margin_order_response_body_timeline_preview,
    normalize_coobit_spot_order_body_symbol,
    normalize_coobit_spot_order_symbol,
    normalize_coobit_spot_symbol_param,
    post_signed_margin_order_json,
)

logger = logging.getLogger(__name__)

_MAX_NEW_CLIENT_ORDER_ID_LEN = 31
_CU_AGENT_CID_PREFIX = "cu_agent_"


def _resolve_new_client_order_id(new_client_order_id: str | None) -> str:
    raw = (new_client_order_id or "").strip()
    if raw:
        if len(raw) >= 32:
            raise AppError(
                code="VALIDATION_ERROR",
                message="newClientOrderId 长度须小于 32",
                status_code=422,
                details={"field": "newClientOrderId"},
            )
        return raw
    return f"{_CU_AGENT_CID_PREFIX}{secrets.token_hex(11)}"


def _margin_timeline_exchange_outcome(exc: AppError) -> str:
    from chainup_agent.infrastructure.exchange.coobit_openapi import (
        app_error_indicates_exchange_unknown,
    )

    if exc.code == "AGENT_MARGIN_ORDER_REJECTED":
        return "reject"
    if app_error_indicates_exchange_unknown(exc):
        return "unknown"
    if exc.code in ("AGENT_OPENAPI_PROBE_FAILED", "AGENT_MARGIN_ORDER_FAILED"):
        return "fail"
    return "fail"


async def margin_order_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str,
    side: str,
    order_type: Literal["MARKET", "LIMIT"],
    volume: str,
    price: str | None = None,
    new_client_order_id: str | None = None,
    scenario_id: str = "margin.cross.market_order",
    timeline_execution_id: str | None = None,
    timeline_channel: str = "http_api",
    timeline_include_quote: bool = True,
) -> dict[str, Any]:
    """POST MARKET/LIMIT on ``/sapi/v2/margin/order`` for a bound Telegram user."""
    tg = parse_telegram_user_id_numeric(user_id)
    row = await load_binding_row_for_telegram_user(session, tg)
    if row is None:
        raise AppError(
            code="AGENT_SUBACCOUNT_REQUIRED",
            message="未发现该 Telegram 用户的托管 API 绑定，请先完成 Deeplink 校验与绑定。",
            status_code=403,
        )

    sym_in = symbol.strip()
    if not sym_in:
        raise AppError(
            code="VALIDATION_ERROR",
            message="symbol 不可为空",
            status_code=422,
            details={"field": "symbol"},
        )
    sym_ticker = normalize_coobit_spot_symbol_param(sym_in)
    sym_order = normalize_coobit_spot_order_symbol(sym_in)
    sym_order_body = normalize_coobit_spot_order_body_symbol(sym_in)
    base_vol = _parse_positive_volume(volume)
    side_u = side.strip().upper()
    if side_u not in ("BUY", "SELL"):
        raise AppError(
            code="VALIDATION_ERROR",
            message="side 须为 BUY 或 SELL",
            status_code=422,
            details={"field": "side"},
        )
    ot = order_type.strip().upper()
    if ot not in ("MARKET", "LIMIT"):
        raise AppError(
            code="VALIDATION_ERROR",
            message="orderType 须为 MARKET 或 LIMIT",
            status_code=422,
            details={"field": "orderType"},
        )
    price_f: float | None = None
    if ot == "LIMIT":
        if not price or not str(price).strip():
            raise AppError(
                code="VALIDATION_ERROR",
                message="限价单须提供 price",
                status_code=422,
                details={"field": "price"},
            )
        price_f = float(_parse_positive_price(price))

    cid = _resolve_new_client_order_id(new_client_order_id)
    uid_s = user_id.strip()
    tl_eid = (
        timeline_execution_id.strip()
        if timeline_execution_id and timeline_execution_id.strip()
        else None
    )
    sid = scenario_id.strip() or (
        "margin.cross.limit_order" if ot == "LIMIT" else "margin.cross.market_order"
    )

    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)
    wire_vol = base_vol
    last_price_tl: str | None = None
    if ot == "MARKET" and side_u == "BUY":
        if tl_eid and timeline_include_quote:
            try:
                raw_tick = await fetch_spot_public_ticker_json_with_fallbacks(
                    openapi_base_url=openapi_base,
                    symbol_candidates=spot_ticker_symbol_candidates(sym_ticker, sym_order),
                )
                lp = _last_price_from_coobit_ticker(raw_tick)
                last_price_tl = str(lp)
                wire_vol = _quote_volume_for_market_buy(base_qty=base_vol, last_price=lp)
            except AppError as exc:
                await append_execution_timeline_event(
                    session,
                    execution_id=tl_eid,
                    user_id=uid_s,
                    event_name="agent.execution.step",
                    step_kind="quote",
                    outcome="fail",
                    payload={
                        **timeline_obs_venue_canonical(),
                        "scenarioId": sid,
                        "channel": timeline_channel,
                        "symbol": sym_ticker,
                        "symbolOrder": sym_order,
                        "appErrorCode": exc.code,
                        "transitionTrigger": "margin.quote.public_ticker",
                    },
                )
                raise
        else:
            raw_tick = await fetch_spot_public_ticker_json_with_fallbacks(
                openapi_base_url=openapi_base,
                symbol_candidates=spot_ticker_symbol_candidates(sym_ticker, sym_order),
            )
            lp = _last_price_from_coobit_ticker(raw_tick)
            last_price_tl = str(lp)
            wire_vol = _quote_volume_for_market_buy(base_qty=base_vol, last_price=lp)
    elif tl_eid and timeline_include_quote and ot == "MARKET":
        try:
            raw_tick = await fetch_spot_public_ticker_json_with_fallbacks(
                openapi_base_url=openapi_base,
                symbol_candidates=spot_ticker_symbol_candidates(sym_ticker, sym_order),
            )
            last_price_tl = str(_last_price_from_coobit_ticker(raw_tick))
        except AppError:
            last_price_tl = None

    order_payload = coobit_sapi_v2_margin_order_body(
        coobit_order_body_symbol=sym_order_body,
        side=side_u,  # type: ignore[arg-type]
        order_type=ot,  # type: ignore[arg-type]
        client_order_id=cid,
        volume=wire_vol,
        price=price_f,
    )

    if tl_eid and timeline_include_quote:
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="agent.execution.step",
            step_kind="quote",
            outcome="success",
            payload={
                **timeline_obs_venue_canonical(),
                "scenarioId": sid,
                "channel": timeline_channel,
                "symbol": sym_ticker,
                "symbolOrder": sym_order,
                "lastPrice": last_price_tl,
                "limitPrice": str(price_f) if price_f is not None else None,
                "transitionTrigger": "margin.quote.public_ticker",
            },
        )

    try:
        data = await post_signed_margin_order_json(
            openapi_base_url=openapi_base,
            api_key=ak,
            secret_key=sk,
            order_body=order_payload,
        )
    except AppError as exc:
        if tl_eid:
            exo = _margin_timeline_exchange_outcome(exc)
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="agent.execution.step",
                step_kind="submit_order",
                outcome="fail",
                payload={
                    **timeline_obs_venue_canonical(),
                    "scenarioId": sid,
                    "channel": timeline_channel,
                    "symbol": sym_ticker,
                    "side": side_u,
                    "orderType": ot,
                    "appErrorCode": exc.code,
                    "transitionTrigger": "margin.order.submit",
                },
            )
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="trading.exchange_private",
                step_kind="submit_order",
                outcome=exo,
                payload={
                    **timeline_obs_venue_canonical(),
                    "methodPathSummary": "POST /sapi/v2/margin/order",
                    "exchangeOutcome": exo,
                    "orderRequest": order_payload,
                    "appErrorCode": exc.code,
                },
            )
        raise

    preview = margin_order_response_body_timeline_preview(data)
    oid = preview.get("orderIdString") or preview.get("orderId")
    if tl_eid:
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="agent.execution.step",
            step_kind="submit_order",
            outcome="success",
            payload={
                **timeline_obs_venue_canonical(),
                "scenarioId": sid,
                "channel": timeline_channel,
                "symbol": sym_ticker,
                "side": side_u,
                "orderType": ot,
                "orderId": oid,
                "transitionTrigger": "margin.order.submit",
            },
        )
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="trading.exchange_private",
            step_kind="submit_order",
            outcome="success",
            payload={
                **timeline_obs_venue_canonical(),
                "methodPathSummary": "POST /sapi/v2/margin/order",
                "exchangeOutcome": "success",
                "orderRequest": order_payload,
                "exchangeOrderPreview": preview,
            },
        )

    return {
        "scenarioId": sid,
        "orderId": str(oid) if oid is not None else None,
        "orderIdString": str(oid) if oid is not None else None,
        "clientOrderId": preview.get("clientOrderId") or cid,
        "status": preview.get("status"),
        "symbol": preview.get("symbol") or sym_ticker,
        "side": preview.get("side") or side_u,
        "type": preview.get("type") or ot,
        "exchangeOrderPreview": preview,
    }
