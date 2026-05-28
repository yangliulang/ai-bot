"""Phase 2.3 — futures market/limit order (POST /fapi/v1/order)."""

from __future__ import annotations

import logging
import secrets
from decimal import Decimal, InvalidOperation
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
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.domain.canonical_trading import (
    coobit_fapi_v1_cancel_body,
    coobit_fapi_v1_order_body,
    timeline_obs_venue_canonical,
)
from chainup_agent.infrastructure.exchange.coobit_openapi import (
    fetch_signed_futures_open_orders_json,
    futures_order_response_body_timeline_preview,
    normalize_coobit_futures_contract_name,
    normalize_coobit_futures_symbol,
    post_signed_futures_cancel_json,
    post_signed_futures_order_json,
)

logger = logging.getLogger(__name__)

_MAX_NEW_CLIENT_ORDER_ID_LEN = 31
_CU_AGENT_CID_PREFIX = "cu_agent_"
_FUTURES_PREVIEW_KEYS = frozenset(
    {
        "orderId",
        "orderIdString",
        "clientOrderId",
        "clientorderId",
        "status",
        "symbol",
        "contractName",
        "side",
        "type",
        "price",
        "origQty",
        "executedQty",
        "avgPrice",
        "transactTime",
        "open",
        "action",
        "reduceOnly",
        "triggerPrice",
        "triggerType",
    }
)


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


def _parse_positive_volume(volume_raw: str) -> float:
    try:
        d = Decimal(volume_raw.strip())
    except InvalidOperation as exc:
        raise AppError(
            code="VALIDATION_ERROR",
            message="volume 须为有效正数十进制字符串",
            status_code=422,
            details={"field": "volume"},
        ) from exc
    if d <= 0:
        raise AppError(
            code="VALIDATION_ERROR",
            message="volume 须大于 0",
            status_code=422,
            details={"field": "volume"},
        )
    return float(d)


def _parse_positive_price(price_raw: str) -> float:
    try:
        d = Decimal(str(price_raw).strip())
    except InvalidOperation as exc:
        raise AppError(
            code="VALIDATION_ERROR",
            message="price 须为有效正数十进制字符串",
            status_code=422,
            details={"field": "price"},
        ) from exc
    if d <= 0:
        raise AppError(
            code="VALIDATION_ERROR",
            message="price 须大于 0",
            status_code=422,
            details={"field": "price"},
        )
    return float(d)


def _sanitize_futures_order_response(data: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k in _FUTURES_PREVIEW_KEYS:
        if k not in data:
            continue
        v = data[k]
        if v is None:
            continue
        if isinstance(v, bool):
            out[k] = v
        elif isinstance(v, (int, float)):
            out[k] = v
        else:
            s = str(v).strip()
            if s:
                out[k] = s[:128]
    return out


def _order_id_to_str(data: dict[str, Any]) -> str | None:
    for k in ("orderIdString", "orderId"):
        v = data.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return None


def _futures_timeline_exchange_outcome(exc: AppError) -> str:
    from chainup_agent.infrastructure.exchange.coobit_openapi import (
        app_error_indicates_exchange_unknown,
    )

    if exc.code == "AGENT_FUTURES_ORDER_REJECTED":
        return "fail"
    if app_error_indicates_exchange_unknown(exc):
        return "unknown"
    if exc.code in ("AGENT_OPENAPI_PROBE_FAILED", "AGENT_FUTURES_ORDER_FAILED"):
        return "unknown"
    return "fail"


async def futures_order_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str,
    side: str,
    order_type: Literal["MARKET", "LIMIT"],
    volume: str,
    price: str | None = None,
    open_close: str | None = None,
    reduce_only: bool | None = None,
    new_client_order_id: str | None = None,
    scenario_id: str = "trade.futures.market_order",
    timeline_execution_id: str | None = None,
    timeline_channel: str = "http_api",
) -> dict[str, Any]:
    """POST MARKET/LIMIT on ``/fapi/v1/order`` for a bound Telegram user."""
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
    sym_futures = normalize_coobit_futures_symbol(sym_in)
    vol_f = _parse_positive_volume(volume)
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
        price_f = _parse_positive_price(price)

    oc = (open_close or "").strip().upper() or None
    if oc and oc not in ("OPEN", "CLOSE"):
        raise AppError(
            code="VALIDATION_ERROR",
            message="openClose 须为 OPEN 或 CLOSE",
            status_code=422,
            details={"field": "openClose"},
        )

    cid = _resolve_new_client_order_id(new_client_order_id)
    uid_s = user_id.strip()
    tl_eid = (
        timeline_execution_id.strip()
        if timeline_execution_id and timeline_execution_id.strip()
        else None
    )
    sid = scenario_id.strip() or (
        "trade.futures.limit_order" if ot == "LIMIT" else "trade.futures.market_order"
    )

    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)
    order_payload = coobit_fapi_v1_order_body(
        symbol=sym_futures,
        side=side_u,  # type: ignore[arg-type]
        order_type=ot,  # type: ignore[arg-type]
        client_order_id=cid,
        volume=vol_f,
        price=price_f,
        open_close=oc,
        reduce_only=reduce_only,
    )

    try:
        data = await post_signed_futures_order_json(
            openapi_base_url=openapi_base,
            api_key=ak,
            secret_key=sk,
            order_body=order_payload,
        )
    except AppError as exc:
        if tl_eid:
            d = exc.details or {}
            exo = _futures_timeline_exchange_outcome(exc)
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
                    "symbol": sym_futures,
                    "side": side_u,
                    "orderType": ot,
                    "appErrorCode": exc.code,
                    "transitionTrigger": "futures.order.submit",
                },
            )
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="trading.exchange_private",
                step_kind="submit_order",
                outcome="fail",
                payload={
                    **timeline_obs_venue_canonical(),
                    "methodPathSummary": "POST /fapi/v1/order",
                    "exchangeOutcome": exo,
                    "appErrorCode": exc.code,
                    "exchangeCode": d.get("exchange_code"),
                    "exchangeMsg": d.get("exchange_msg"),
                    "rejectReason": d.get("reject_reason"),
                    "httpStatus": d.get("http_status"),
                    "clientOrderRef": cid,
                    "symbolOrder": sym_futures,
                    "orderRequest": order_payload,
                },
            )
        raise

    preview = _sanitize_futures_order_response(data)
    oid = preview.get("orderIdString") or _order_id_to_str(data)
    pcid = preview.get("clientOrderId") or preview.get("clientorderId")
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
                "symbol": sym_futures,
                "side": side_u,
                "orderType": ot,
                "orderId": oid,
                "transitionTrigger": "futures.order.submit",
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
                "methodPathSummary": "POST /fapi/v1/order",
                "httpStatus": 200,
                "exchangeOutcome": "success",
                "clientOrderRef": pcid,
                "symbolOrder": preview.get("symbol") or sym_futures,
                "orderRequest": order_payload,
                "exchangeResponsePreview": futures_order_response_body_timeline_preview(data),
            },
        )
    return {
        "scenarioId": sid,
        "orderId": _order_id_to_str(data),
        "orderIdString": preview.get("orderIdString") or _order_id_to_str(data),
        "clientOrderId": pcid,
        "status": preview.get("status"),
        "symbol": preview.get("symbol") or sym_futures,
        "side": preview.get("side") or side_u,
        "type": preview.get("type") or ot,
        "exchangeOrderPreview": preview,
    }


def _sanitize_futures_open_order_row(raw: dict[str, Any]) -> dict[str, Any]:
    return _sanitize_futures_order_response(raw)


def _futures_cancel_timeline_exchange_outcome(exc: AppError) -> str:
    from chainup_agent.infrastructure.exchange.coobit_openapi import (
        app_error_indicates_exchange_unknown,
    )

    if exc.code == "AGENT_FUTURES_CANCEL_REJECTED":
        return "fail"
    if app_error_indicates_exchange_unknown(exc):
        return "unknown"
    if exc.code in ("AGENT_OPENAPI_PROBE_FAILED", "AGENT_FUTURES_ORDER_FAILED"):
        return "unknown"
    return "fail"


async def futures_open_orders_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str | None,
) -> dict[str, Any]:
    """GET ``/fapi/v1/openOrders`` for a bound user (optional contract filter)."""
    tg = parse_telegram_user_id_numeric(user_id)
    row = await load_binding_row_for_telegram_user(session, tg)
    if row is None:
        raise AppError(
            code="AGENT_SUBACCOUNT_REQUIRED",
            message="未发现该 Telegram 用户的托管 API 绑定，请先完成 Deeplink 校验与绑定。",
            status_code=403,
        )

    sym_futures: str | None = None
    contract_name: str | None = None
    if symbol is not None and str(symbol).strip():
        sym_in = str(symbol).strip()
        sym_futures = normalize_coobit_futures_symbol(sym_in)
        contract_name = normalize_coobit_futures_contract_name(sym_in)

    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)
    rows = await fetch_signed_futures_open_orders_json(
        openapi_base_url=openapi_base,
        api_key=ak,
        secret_key=sk,
        contract_name=contract_name,
    )
    sanitized = [_sanitize_futures_open_order_row(r) for r in rows]
    return {
        "symbol": sym_futures,
        "contractName": contract_name,
        "orders": sanitized,
    }


async def futures_cancel_order_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str,
    order_id: str,
    scenario_id: str = "trade.futures.cancel_order",
    timeline_execution_id: str | None = None,
    timeline_channel: str = "http_api",
) -> dict[str, Any]:
    """POST ``/fapi/v1/cancel`` for a bound user."""
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
    oid_raw = order_id.strip()
    if not oid_raw:
        raise AppError(
            code="VALIDATION_ERROR",
            message="须提供 orderId",
            status_code=422,
            details={"field": "orderId"},
        )

    sym_futures = normalize_coobit_futures_symbol(sym_in)
    contract_name = normalize_coobit_futures_contract_name(sym_in)
    cancel_body = coobit_fapi_v1_cancel_body(contract_name=contract_name, order_id=oid_raw)
    uid_s = user_id.strip()
    sid = scenario_id.strip() or "trade.futures.cancel_order"
    tl_eid = (
        timeline_execution_id.strip()
        if timeline_execution_id and timeline_execution_id.strip()
        else None
    )

    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)
    try:
        data = await post_signed_futures_cancel_json(
            openapi_base_url=openapi_base,
            api_key=ak,
            secret_key=sk,
            cancel_body=cancel_body,
        )
    except AppError as exc:
        if tl_eid:
            d = exc.details or {}
            exo = _futures_cancel_timeline_exchange_outcome(exc)
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="agent.execution.step",
                step_kind="cancel_order",
                outcome="fail",
                payload={
                    **timeline_obs_venue_canonical(),
                    "scenarioId": sid,
                    "channel": timeline_channel,
                    "symbol": sym_futures,
                    "contractName": contract_name,
                    "orderId": oid_raw,
                    "appErrorCode": exc.code,
                    "transitionTrigger": "futures.cancel.submit",
                },
            )
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="trading.exchange_private",
                step_kind="cancel_order",
                outcome="fail",
                payload={
                    **timeline_obs_venue_canonical(),
                    "methodPathSummary": "POST /fapi/v1/cancel",
                    "exchangeOutcome": exo,
                    "appErrorCode": exc.code,
                    "exchangeCode": d.get("exchange_code"),
                    "exchangeMsg": d.get("exchange_msg"),
                    "httpStatus": d.get("http_status"),
                    "symbolOrder": sym_futures,
                    "cancelRequest": cancel_body,
                },
            )
        raise

    preview = _sanitize_futures_order_response(data)
    oid_out = preview.get("orderIdString") or _order_id_to_str(data)
    if tl_eid:
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="agent.execution.step",
            step_kind="cancel_order",
            outcome="success",
            payload={
                **timeline_obs_venue_canonical(),
                "scenarioId": sid,
                "channel": timeline_channel,
                "symbol": sym_futures,
                "contractName": contract_name,
                "orderId": oid_out,
                "transitionTrigger": "futures.cancel.submit",
            },
        )
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="trading.exchange_private",
            step_kind="cancel_order",
            outcome="success",
            payload={
                **timeline_obs_venue_canonical(),
                "methodPathSummary": "POST /fapi/v1/cancel",
                "httpStatus": 200,
                "exchangeOutcome": "success",
                "symbolOrder": sym_futures,
                "cancelRequest": cancel_body,
                "exchangeResponsePreview": futures_order_response_body_timeline_preview(data),
            },
        )
    return {
        "scenarioId": sid,
        "orderId": _order_id_to_str(data),
        "orderIdString": oid_out,
        "contractName": preview.get("contractName") or contract_name,
        "symbol": preview.get("symbol") or sym_futures,
        "status": preview.get("status"),
        "exchangeOrderPreview": preview,
    }
