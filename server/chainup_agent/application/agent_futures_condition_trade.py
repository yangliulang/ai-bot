"""Phase 2.5 — futures condition order (POST /fapi/v1/conditionOrder)."""

from __future__ import annotations

import logging
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
from chainup_agent.application.agent_futures_trade import (
    futures_cancel_order_for_bound_user,
    futures_open_orders_for_bound_user,
)
from chainup_agent.domain.canonical_trading import (
    coobit_fapi_v1_condition_order_body,
    timeline_obs_venue_canonical,
)
from chainup_agent.infrastructure.exchange.coobit_openapi import (
    futures_condition_order_response_body_timeline_preview,
    normalize_coobit_futures_contract_name,
    post_signed_futures_condition_order_json,
)

logger = logging.getLogger(__name__)

_CONDITION_PREVIEW_KEYS = frozenset(
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
        "triggerPrice",
        "triggerType",
        "volume",
        "open",
    }
)


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


def _sanitize_condition_order_response(data: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k in _CONDITION_PREVIEW_KEYS:
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


def _is_condition_order_row(raw: dict[str, Any]) -> bool:
    """Heuristic filter for plan/condition orders in ``GET /fapi/v1/openOrders``."""
    if raw.get("isConditionOrder") is True:
        return True
    if str(raw.get("triggerType") or "").strip().upper() in ("3UP", "4DOWN"):
        return True
    if str(raw.get("triggerPrice") or "").strip():
        return True
    return False


def _condition_timeline_exchange_outcome(exc: AppError) -> str:
    from chainup_agent.infrastructure.exchange.coobit_openapi import (
        app_error_indicates_exchange_unknown,
    )

    if exc.code == "AGENT_FUTURES_CONDITION_ORDER_REJECTED":
        return "fail"
    if app_error_indicates_exchange_unknown(exc):
        return "unknown"
    if exc.code in ("AGENT_OPENAPI_PROBE_FAILED", "AGENT_FUTURES_CONDITION_ORDER_FAILED"):
        return "unknown"
    return "fail"


async def futures_condition_order_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str,
    side: str,
    order_type: Literal["MARKET", "LIMIT"],
    volume: str,
    trigger_price: str,
    trigger_type: str,
    price: str | None = None,
    open_close: str | None = None,
    position_type: int = 1,
    order_unit: int = 2,
    scenario_id: str = "automation.condition_order",
    timeline_execution_id: str | None = None,
    timeline_channel: str = "http_api",
) -> dict[str, Any]:
    """POST condition order on ``/fapi/v1/conditionOrder`` for a bound Telegram user."""
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
    contract_name = normalize_coobit_futures_contract_name(sym_in)
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
    tp = trigger_price.strip()
    if not tp:
        raise AppError(
            code="VALIDATION_ERROR",
            message="triggerPrice 不可为空",
            status_code=422,
            details={"field": "triggerPrice"},
        )
    tt = trigger_type.strip().upper()
    if tt not in ("3UP", "4DOWN"):
        raise AppError(
            code="VALIDATION_ERROR",
            message="triggerType 须为 3UP 或 4DOWN",
            status_code=422,
            details={"field": "triggerType"},
        )
    price_f: float | None = None
    if ot == "LIMIT":
        if not price or not str(price).strip():
            raise AppError(
                code="VALIDATION_ERROR",
                message="触发后限价单须提供 price",
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

    uid_s = user_id.strip()
    tl_eid = (
        timeline_execution_id.strip()
        if timeline_execution_id and timeline_execution_id.strip()
        else None
    )
    sid = scenario_id.strip() or "automation.condition_order"

    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)
    order_payload = coobit_fapi_v1_condition_order_body(
        contract_name=contract_name,
        side=side_u,  # type: ignore[arg-type]
        order_type=ot,  # type: ignore[arg-type]
        volume=vol_f,
        trigger_price=tp,
        trigger_type=tt,
        price=price_f,
        open_close=oc,
        position_type=position_type,
        order_unit=order_unit,
    )

    try:
        data = await post_signed_futures_condition_order_json(
            openapi_base_url=openapi_base,
            api_key=ak,
            secret_key=sk,
            order_body=order_payload,
        )
    except AppError as exc:
        if tl_eid:
            d = exc.details or {}
            exo = _condition_timeline_exchange_outcome(exc)
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
                    "symbol": contract_name,
                    "side": side_u,
                    "orderType": ot,
                    "triggerPrice": tp,
                    "triggerType": tt,
                    "appErrorCode": exc.code,
                    "transitionTrigger": "futures.condition_order.submit",
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
                    "methodPathSummary": "POST /fapi/v1/conditionOrder",
                    "exchangeOutcome": exo,
                    "appErrorCode": exc.code,
                    "exchangeCode": d.get("exchange_code"),
                    "exchangeMsg": d.get("exchange_msg"),
                    "httpStatus": d.get("http_status"),
                    "symbolOrder": contract_name,
                    "orderRequest": order_payload,
                },
            )
        raise

    preview = _sanitize_condition_order_response(data)
    oid = preview.get("orderIdString") or _order_id_to_str(data)
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
                "symbol": contract_name,
                "side": side_u,
                "orderType": ot,
                "triggerPrice": tp,
                "triggerType": tt,
                "orderId": oid,
                "transitionTrigger": "futures.condition_order.submit",
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
                "methodPathSummary": "POST /fapi/v1/conditionOrder",
                "httpStatus": 200,
                "exchangeOutcome": "success",
                "symbolOrder": preview.get("contractName") or contract_name,
                "orderRequest": order_payload,
                "exchangeResponsePreview": futures_condition_order_response_body_timeline_preview(
                    data
                ),
            },
        )
    return {
        "scenarioId": sid,
        "orderId": _order_id_to_str(data),
        "orderIdString": preview.get("orderIdString") or _order_id_to_str(data),
        "contractName": preview.get("contractName") or contract_name,
        "side": preview.get("side") or side_u,
        "type": preview.get("type") or ot,
        "triggerPrice": preview.get("triggerPrice") or tp,
        "triggerType": preview.get("triggerType") or tt,
        "exchangeOrderPreview": preview,
    }


async def futures_condition_orders_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str | None,
) -> dict[str, Any]:
    """List open condition/plan orders via ``GET /fapi/v1/openOrders`` + filter."""
    payload = await futures_open_orders_for_bound_user(
        session=session,
        settings=settings,
        user_id=user_id,
        symbol=symbol,
    )
    all_rows = payload.get("orders") if isinstance(payload.get("orders"), list) else []
    condition_rows = [r for r in all_rows if isinstance(r, dict) and _is_condition_order_row(r)]
    return {
        "scenarioId": "automation.condition_orders_read",
        "symbol": payload.get("symbol"),
        "contractName": payload.get("contractName"),
        "orders": condition_rows,
        "totalOpenOrders": len(all_rows),
    }


async def futures_condition_order_cancel_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str,
    order_id: str,
    timeline_execution_id: str | None = None,
    timeline_channel: str = "http_api",
) -> dict[str, Any]:
    """Cancel a condition order via ``POST /fapi/v1/cancel`` (same PATH as regular futures cancel)."""
    out = await futures_cancel_order_for_bound_user(
        session=session,
        settings=settings,
        user_id=user_id,
        symbol=symbol,
        order_id=order_id,
        scenario_id="automation.condition_order_cancel",
        timeline_execution_id=timeline_execution_id,
        timeline_channel=timeline_channel,
    )
    out["scenarioId"] = "automation.condition_order_cancel"
    return out
