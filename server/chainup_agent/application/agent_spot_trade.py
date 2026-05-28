"""Phase 2.1 — spot flash convert: public quote + signed MARKET order."""

from __future__ import annotations

import logging
import secrets
from decimal import ROUND_DOWN, Decimal, InvalidOperation
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_api_binding_confirm import (
    decrypt_binding_trade_credentials_for_row,
)
from chainup_agent.application.agent_execution_events import append_execution_timeline_event
from chainup_agent.application.agent_routing_exchange_read import (
    _sanitize_ticker_preview,
    load_binding_row_for_telegram_user,
    parse_telegram_user_id_numeric,
)
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.domain.canonical_trading import (
    InstrumentRef,
    PlaceOrder,
    coobit_sapi_v2_order_body_from_place_order,
    instrument_ref_from_sym_ticker,
    timeline_obs_venue_canonical,
)
from chainup_agent.infrastructure.exchange.coobit_openapi import (
    fetch_signed_spot_open_orders_json,
    fetch_spot_public_ticker_json_with_fallbacks,
    normalize_coobit_spot_order_body_symbol,
    normalize_coobit_spot_order_symbol,
    normalize_coobit_spot_symbol_param,
    post_signed_spot_cancel_json,
    post_signed_spot_order_json,
    spot_ticker_symbol_candidates,
)

logger = logging.getLogger(__name__)


def _instrument_ref_from_ticker_or_raise(sym_ticker: str) -> InstrumentRef:
    try:
        return instrument_ref_from_sym_ticker(sym_ticker)
    except ValueError as exc:
        raise AppError(
            code="VALIDATION_ERROR",
            message="交易对格式无效，请使用如 BTC-USDT",
            status_code=422,
            details={"field": "symbol"},
        ) from exc


def _with_timeline_canonical(payload: dict[str, Any]) -> dict[str, Any]:
    merged = dict(payload)
    merged.update(timeline_obs_venue_canonical())
    return merged


# Coobit Spot：`newClientOrderId` 须 **严格小于 32**（即的最大长度 31）。
_MAX_NEW_CLIENT_ORDER_ID_LEN = 31
_CU_AGENT_CID_PREFIX = "cu_agent_"


def _resolve_new_client_order_id(new_client_order_id: str | None) -> str:
    """交易所委托幂等键：可选透传；缺省时生成 ``cu_agent_<hex>``，总长不超过 31。"""
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
    # ``len(_CU_AGENT_CID_PREFIX)`` == 9 → 22 hex chars → 总长 31
    return f"{_CU_AGENT_CID_PREFIX}{secrets.token_hex(11)}"


def _flash_timeline_exchange_outcome(exc: AppError) -> str:
    from chainup_agent.infrastructure.exchange.coobit_openapi import (
        app_error_indicates_exchange_unknown,
    )

    if exc.code == "AGENT_SPOT_ORDER_REJECTED":
        return "fail"
    if app_error_indicates_exchange_unknown(exc):
        return "unknown"
    if exc.code in ("AGENT_OPENAPI_PROBE_FAILED", "AGENT_SPOT_ORDER_FAILED"):
        return "unknown"
    return "fail"


def _trading_exchange_private_fail_payload(
    *,
    d: dict[str, Any],
    exo: str,
    exc: AppError,
    cid: str,
    sym_order: str,
    order_payload: dict[str, Any],
    flash_market_meta: dict[str, Any] | None = None,
    limit_order_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    erp = d.get("exchange_response_preview")
    payload: dict[str, Any] = {
        **timeline_obs_venue_canonical(),
        "methodPathSummary": "POST /sapi/v2/order",
        "exchangeOutcome": exo,
        "appErrorCode": exc.code,
        "exchangeCode": d.get("exchange_code"),
        "exchangeMsg": d.get("exchange_msg"),
        "rejectReason": d.get("reject_reason"),
        "httpStatus": d.get("http_status"),
        "clientOrderRef": cid,
        "symbolOrder": sym_order,
        "orderRequest": _timeline_spot_order_request_for_observability(
            order_payload,
            flash_market_meta=flash_market_meta,
            limit_order_meta=limit_order_meta,
        ),
    }
    if isinstance(erp, dict) and erp:
        payload["exchangeResponsePreview"] = erp
    return payload


_ALLOWED_SPOT_ORDER_PREVIEW_KEYS = frozenset(
    {
        "orderId",
        "orderIdString",
        "clientOrderId",
        "clientorderId",
        "status",
        "symbol",
        "symbolName",
        "side",
        "type",
        "price",
        "origQty",
        "executedQty",
        "avgPrice",
        "transactTime",
    }
)

_OPEN_ORDER_ROW_PREVIEW_KEYS = _ALLOWED_SPOT_ORDER_PREVIEW_KEYS | frozenset(
    {"time", "stopPrice", "isWorking"}
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


def _parse_positive_price(price_raw: str) -> Decimal:
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
    return d


def check_spot_limit_price_agent_band(
    *,
    settings: Settings,
    limit_price: Decimal,
    last_price: Decimal,
) -> dict[str, str]:
    """
    When ``trade_spot_limit_price_band_enabled``, reject limit prices outside ±max_pct
  of ``last_price``. Returns string observability fields for timeline / logs.
    """
    if last_price <= 0:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="行情缺少有效最新价，无法校验限价偏离",
            status_code=502,
            details={"reason": "missing_last_price"},
        )
    lp = str(limit_price)
    lt = str(last_price)
    if not settings.trade_spot_limit_price_band_enabled:
        return {
            "bandCheck": "false",
            "lastPrice": lt,
            "limitPrice": lp,
        }
    dev_pct = abs(limit_price - last_price) / last_price * Decimal(100)
    max_pct = Decimal(str(settings.trade_spot_limit_price_band_max_pct))
    out: dict[str, str] = {
        "bandCheck": "true",
        "lastPrice": lt,
        "limitPrice": lp,
        "deviationPct": str(dev_pct.quantize(Decimal("0.0001"))),
        "maxBandPct": str(max_pct),
    }
    if dev_pct > max_pct:
        raise AppError(
            code="PRICE_REJECTED_AGENT_BAND",
            message=(
                f"限价与最新价偏离过大（约 "
                f"{dev_pct.quantize(Decimal('0.01'))}%，允许 ±{max_pct}%）；请调整价格。"
            ),
            status_code=422,
            details={
                "lastPrice": lt,
                "limitPrice": lp,
                "maxBandPct": str(max_pct),
                "deviationPct": out["deviationPct"],
            },
        )
    return out


def _normalize_limit_time_in_force(raw: str | None) -> str:
    """Coobit / GitBook v2 spot LIMIT: GTC / IOC / FOC (FOK) style; default GTC."""
    if raw is None or not str(raw).strip():
        return "GTC"
    u = str(raw).strip().upper()
    if u in ("GTC", "IOC", "FOK"):
        return u
    if u in ("FOC",):
        return "FOK"
    raise AppError(
        code="VALIDATION_ERROR",
        message="timeInForce 须为 GTC、IOC 或 FOK",
        status_code=422,
        details={"field": "timeInForce"},
    )


def _coobit_unwrap_ticker_field_dict(data: dict[str, Any]) -> dict[str, Any]:
    """网关偶发 ``{code,msg,data:{last,...}}``；取内层报价字段。"""
    for key in ("data", "result", "ticker"):
        inner = data.get(key)
        if isinstance(inner, dict) and any(
            k in inner for k in ("lastPrice", "last", "closePrice", "bidPrice", "askPrice")
        ):
            return inner
    return data


def _last_price_from_coobit_ticker(data: dict[str, Any]) -> Decimal:
    """Best-effort latest trade price from ``GET /sapi/v2/ticker`` JSON (flat or wrapped)."""
    d = _coobit_unwrap_ticker_field_dict(data)
    for key in ("lastPrice", "last", "closePrice"):
        v = d.get(key)
        if v is None:
            continue
        try:
            dec = Decimal(str(v).strip())
        except InvalidOperation:
            continue
        if dec > 0:
            return dec
    raise AppError(
        code="AGENT_OPENAPI_PROBE_FAILED",
        message="行情缺少有效最新价，无法换算市价买单计价数量",
        status_code=502,
        details={"reason": "missing_last_price"},
    )


def _quote_volume_for_market_buy(*, base_qty: float, last_price: Decimal) -> float:
    """
    Coobit GitBook: for MARKET BUY, ``volume`` on the wire is quote **amount**, not base qty.
    User / Telegram NLU quantity is treated as **base** (e.g. BTC in BTC-USDT).

    Quote amount is floored to **2** fractional digits before the wire (product cap).
    """
    q = Decimal(str(base_qty)) * last_price
    q = q.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    if q <= 0:
        raise AppError(
            code="VALIDATION_ERROR",
            message="换算后的计价数量无效，请调整数量或稍后重试",
            status_code=422,
            details={"field": "volume"},
        )
    return float(q)


def _sanitize_spot_order_preview(raw: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k in _ALLOWED_SPOT_ORDER_PREVIEW_KEYS:
        if k not in raw:
            continue
        v = raw[k]
        if v is None:
            continue
        if isinstance(v, (bool, int, float)):
            out[k] = v
        else:
            s = str(v).strip()
            if s:
                out[k] = s[:128]
    return out


def _sanitize_open_order_row_preview(raw: dict[str, Any]) -> dict[str, Any]:
    """Subset of ``GET /sapi/v2/openOrders`` row for Agent JSON (no secrets)."""
    out: dict[str, Any] = {}
    for k in _OPEN_ORDER_ROW_PREVIEW_KEYS:
        if k not in raw:
            continue
        v = raw[k]
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


def _clamp_open_orders_limit(limit_raw: int | None) -> int | None:
    """GitBook: default 100 at exchange; max 1000 — clamp into ``[1, 1000]`` when provided."""
    if limit_raw is None:
        return None
    lim = int(limit_raw)
    return max(1, min(lim, 1000))


def _timeline_spot_cancel_request_for_observability(cancel_body: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"path": "POST /sapi/v2/cancel"}
    for key in ("symbol", "orderId", "newClientOrderId"):
        v = cancel_body.get(key)
        if v is not None and str(v).strip():
            out[key] = str(v).strip()[:128]
    return out


def _cancel_fail_timeline_payload(
    *,
    d: dict[str, Any],
    exo: str,
    exc: AppError,
    cancel_body: dict[str, Any],
    sym_order: str,
) -> dict[str, Any]:
    erp = d.get("exchange_response_preview")
    payload: dict[str, Any] = {
        **timeline_obs_venue_canonical(),
        "methodPathSummary": "POST /sapi/v2/cancel",
        "exchangeOutcome": exo,
        "appErrorCode": exc.code,
        "exchangeCode": d.get("exchange_code"),
        "exchangeMsg": d.get("exchange_msg"),
        "rejectReason": d.get("reject_reason"),
        "httpStatus": d.get("http_status"),
        "symbolOrder": sym_order,
        "cancelRequest": _timeline_spot_cancel_request_for_observability(cancel_body),
    }
    if isinstance(erp, dict) and erp:
        payload["exchangeResponsePreview"] = erp
    return payload


def _flash_market_order_timeline_meta(
    *,
    side: str,
    user_volume_raw: str,
    base_qty: float,
    wire_vol: float,
    last_price: str | None,
) -> dict[str, Any]:
    """
    Explains ``volume`` on the wire vs user intent (GitBook: MARKET BUY ``volume`` = quote amount).
    """
    side_u = side.strip().upper()
    raw_s = (user_volume_raw or "").strip()[:64]
    meta: dict[str, Any] = {
        "baseQtyUserRequested": str(base_qty),
        "userVolumeInput": raw_s,
    }
    if side_u == "BUY":
        meta["volumeSemantics"] = "market_buy_quote_amount"
        meta["volumeSemanticsNote"] = (
            "Coobit v2: MARKET BUY field ``volume`` is quote amount (e.g. USDT), not base ETH; "
            "derived from baseQtyUserRequested × lastPriceUsed"
        )
        meta["quoteAmountOnWire"] = wire_vol
        if last_price:
            meta["lastPriceUsed"] = last_price
    else:
        meta["volumeSemantics"] = "market_sell_base_qty"
        meta["volumeSemanticsNote"] = (
            "MARKET SELL: field ``volume`` is base quantity (same as user intent for this pair)"
        )
        meta["baseQtyOnWire"] = wire_vol
    return meta


def _timeline_spot_order_request_for_observability(
    order_body: dict[str, Any],
    *,
    flash_market_meta: dict[str, Any] | None = None,
    limit_order_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Non-secret POST ``/sapi/v2/order`` body for execution timeline (FR-MC801)."""
    out: dict[str, Any] = {"path": "POST /sapi/v2/order"}
    sym = order_body.get("symbol")
    if sym is not None and str(sym).strip():
        out["symbol"] = str(sym).strip()[:64]
    side = order_body.get("side")
    if side is not None and str(side).strip():
        out["side"] = str(side).strip().upper()[:8]
    typ = order_body.get("type")
    if typ is not None and str(typ).strip():
        out["type"] = str(typ).strip()[:16]
    vol = order_body.get("volume")
    if vol is not None:
        if isinstance(vol, bool):
            pass
        elif isinstance(vol, (int, float)):
            out["volume"] = vol
        else:
            vs = str(vol).strip()
            if vs:
                out["volume"] = vs[:64]
    pr = order_body.get("price")
    if pr is not None and str(pr).strip():
        out["price"] = str(pr).strip()[:64]
    tif = order_body.get("timeInForce")
    if tif is not None and str(tif).strip():
        out["timeInForce"] = str(tif).strip().upper()[:8]
    ncid = order_body.get("newClientOrderId")
    if ncid is not None and str(ncid).strip():
        out["newClientOrderId"] = str(ncid).strip()[:_MAX_NEW_CLIENT_ORDER_ID_LEN]
    if flash_market_meta:
        out["flashMarketMeta"] = flash_market_meta
    if limit_order_meta:
        out["limitOrderMeta"] = limit_order_meta
    return out


def _order_id_to_str(data: dict[str, Any]) -> str | None:
    v = data.get("orderIdString") or data.get("orderId")
    if v is None:
        return None
    return str(v).strip() or None


async def spot_quote_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str,
) -> dict[str, Any]:
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

    openapi_base, _, _ = decrypt_binding_trade_credentials_for_row(settings, row)
    raw = await fetch_spot_public_ticker_json_with_fallbacks(
        openapi_base_url=openapi_base,
        symbol_candidates=spot_ticker_symbol_candidates(sym_ticker, sym_order),
    )
    preview = _sanitize_ticker_preview(raw, sym_ticker)
    return {
        "symbol": sym_ticker,
        "symbolOrder": sym_order,
        "quotePreview": preview,
    }


async def spot_flash_convert_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str,
    side: str,
    volume: str,
    new_client_order_id: str | None,
    timeline_execution_id: str | None = None,
    timeline_channel: str = "http_api",
    timeline_include_quote: bool = True,
) -> dict[str, Any]:
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
    cid = _resolve_new_client_order_id(new_client_order_id)
    uid_s = user_id.strip()
    tl_eid = (
        timeline_execution_id.strip()
        if timeline_execution_id and timeline_execution_id.strip()
        else None
    )
    inst = _instrument_ref_from_ticker_or_raise(sym_ticker)

    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)
    wire_vol: float
    last_price_tl: str | None = None
    if side_u == "BUY":
        try:
            raw_tick = await fetch_spot_public_ticker_json_with_fallbacks(
                openapi_base_url=openapi_base,
                symbol_candidates=spot_ticker_symbol_candidates(sym_ticker, sym_order),
            )
        except AppError as exc:
            if tl_eid and timeline_include_quote:
                await append_execution_timeline_event(
                    session,
                    execution_id=tl_eid,
                    user_id=uid_s,
                    event_name="agent.execution.step",
                    step_kind="quote",
                    outcome="fail",
                    payload=_with_timeline_canonical(
                        {
                            "scenarioId": "trade.spot.flash_convert",
                            "channel": timeline_channel,
                            "symbol": sym_ticker,
                            "symbolOrder": sym_order,
                            "appErrorCode": exc.code,
                            "transitionTrigger": "flash.quote.public_ticker",
                        }
                    ),
                )
            raise
        try:
            lp = _last_price_from_coobit_ticker(raw_tick)
            last_price_tl = str(lp)
            wire_vol = _quote_volume_for_market_buy(base_qty=base_vol, last_price=lp)
        except AppError as exc:
            if tl_eid and timeline_include_quote:
                await append_execution_timeline_event(
                    session,
                    execution_id=tl_eid,
                    user_id=uid_s,
                    event_name="agent.execution.step",
                    step_kind="quote",
                    outcome="fail",
                    payload=_with_timeline_canonical(
                        {
                            "scenarioId": "trade.spot.flash_convert",
                            "channel": timeline_channel,
                            "symbol": sym_ticker,
                            "symbolOrder": sym_order,
                            "appErrorCode": exc.code,
                            "transitionTrigger": "flash.quote.public_ticker",
                        }
                    ),
                )
            raise
        if tl_eid and timeline_include_quote:
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="agent.execution.step",
                step_kind="quote",
                outcome="success",
                payload=_with_timeline_canonical(
                    {
                        "scenarioId": "trade.spot.flash_convert",
                        "channel": timeline_channel,
                        "symbol": sym_ticker,
                        "symbolOrder": sym_order,
                        "side": side_u,
                        "lastPrice": last_price_tl or "",
                        "baseQtyRequested": str(base_vol),
                        "quoteAmountForOrder": wire_vol,
                        "transitionTrigger": "flash.quote.public_ticker",
                    }
                ),
            )
        logger.info(
            "spot_flash_convert market_buy base_to_quote symbol=%s base=%s last=%s quote=%s",
            sym_order,
            base_vol,
            str(lp),
            wire_vol,
        )
    else:
        wire_vol = base_vol
        if tl_eid and timeline_include_quote:
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="agent.execution.step",
                step_kind="quote",
                outcome="success",
                payload=_with_timeline_canonical(
                    {
                        "scenarioId": "trade.spot.flash_convert",
                        "channel": timeline_channel,
                        "symbol": sym_ticker,
                        "symbolOrder": sym_order,
                        "side": side_u,
                        "marketSellUsesBaseQty": True,
                        "baseQty": base_vol,
                        "transitionTrigger": "flash.quote.market_sell_base",
                    }
                ),
            )

    flash_order_meta = _flash_market_order_timeline_meta(
        side=side_u,
        user_volume_raw=volume.strip(),
        base_qty=base_vol,
        wire_vol=wire_vol,
        last_price=last_price_tl,
    )

    if side_u == "BUY":
        place = PlaceOrder(
            instrument=inst,
            side="BUY",
            order_type="MARKET",
            client_order_id=cid,
            quantity=base_vol,
            quote_amount=wire_vol,
            price=None,
            time_in_force=None,
        )
    else:
        place = PlaceOrder(
            instrument=inst,
            side="SELL",
            order_type="MARKET",
            client_order_id=cid,
            quantity=base_vol,
            quote_amount=None,
            price=None,
            time_in_force=None,
        )
    order_payload = coobit_sapi_v2_order_body_from_place_order(
        place, coobit_order_body_symbol=sym_order_body
    )
    try:
        data = await post_signed_spot_order_json(
            openapi_base_url=openapi_base,
            api_key=ak,
            secret_key=sk,
            order_body=order_payload,
        )
    except AppError as exc:
        if tl_eid:
            d = exc.details or {}
            exo = _flash_timeline_exchange_outcome(exc)
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="agent.execution.step",
                step_kind="submit_order",
                outcome="fail",
                payload=_with_timeline_canonical(
                    {
                        "scenarioId": "trade.spot.flash_convert",
                        "channel": timeline_channel,
                        "symbol": sym_ticker,
                        "side": side_u,
                        "quantityRequested": volume.strip(),
                        "appErrorCode": exc.code,
                        "transitionTrigger": "flash.order.submit",
                    }
                ),
            )
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="trading.exchange_private",
                step_kind="submit_order",
                outcome="fail",
                payload=_trading_exchange_private_fail_payload(
                    d=d,
                    exo=exo,
                    exc=exc,
                    cid=cid,
                    sym_order=sym_order,
                    order_payload=order_payload,
                    flash_market_meta=flash_order_meta,
                ),
            )
        raise

    preview = _sanitize_spot_order_response(data)
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
            payload=_with_timeline_canonical(
                {
                    "scenarioId": "trade.spot.flash_convert",
                    "channel": timeline_channel,
                    "symbol": sym_ticker,
                    "side": side_u,
                    "quantityRequested": volume.strip(),
                    "orderId": oid,
                    "transitionTrigger": "flash.order.submit",
                }
            ),
        )
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="trading.exchange_private",
            step_kind="submit_order",
            outcome="success",
            payload=_with_timeline_canonical(
                {
                    "methodPathSummary": "POST /sapi/v2/order",
                    "httpStatus": 200,
                    "exchangeOutcome": "success",
                    "clientOrderRef": pcid,
                    "symbolOrder": preview.get("symbol") or sym_order,
                    "orderRequest": _timeline_spot_order_request_for_observability(
                        order_payload, flash_market_meta=flash_order_meta
                    ),
                    "exchangeResponsePreview": preview,
                }
            ),
        )
    return {
        "orderId": _order_id_to_str(data),
        "orderIdString": preview.get("orderIdString") or _order_id_to_str(data),
        "clientOrderId": pcid,
        "status": preview.get("status"),
        "symbol": preview.get("symbol") or sym_order,
        "side": preview.get("side") or side_u,
        "type": preview.get("type") or "MARKET",
        "exchangeOrderPreview": preview,
    }


async def spot_limit_order_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str,
    side: str,
    volume: str,
    price: str,
    time_in_force: str | None,
    new_client_order_id: str | None,
    timeline_execution_id: str | None = None,
    timeline_channel: str = "http_api",
    timeline_include_quote: bool = True,
) -> dict[str, Any]:
    """POST LIMIT on ``/sapi/v2/order`` for a bound user (base ``volume``, limit ``price``)."""
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
    price_dec = _parse_positive_price(price)
    side_u = side.strip().upper()
    if side_u not in ("BUY", "SELL"):
        raise AppError(
            code="VALIDATION_ERROR",
            message="side 须为 BUY 或 SELL",
            status_code=422,
            details={"field": "side"},
        )
    tif_u = _normalize_limit_time_in_force(time_in_force)
    cid = _resolve_new_client_order_id(new_client_order_id)
    uid_s = user_id.strip()
    tl_eid = (
        timeline_execution_id.strip()
        if timeline_execution_id and timeline_execution_id.strip()
        else None
    )
    inst = _instrument_ref_from_ticker_or_raise(sym_ticker)

    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)

    if settings.trade_spot_limit_price_band_enabled:
        try:
            raw_tick = await fetch_spot_public_ticker_json_with_fallbacks(
                openapi_base_url=openapi_base,
                symbol_candidates=spot_ticker_symbol_candidates(sym_ticker, sym_order),
            )
        except AppError as exc:
            if tl_eid and timeline_include_quote:
                await append_execution_timeline_event(
                    session,
                    execution_id=tl_eid,
                    user_id=uid_s,
                    event_name="agent.execution.step",
                    step_kind="quote",
                    outcome="fail",
                    payload=_with_timeline_canonical(
                        {
                            "scenarioId": "trade.spot.limit_order",
                            "channel": timeline_channel,
                            "symbol": sym_ticker,
                            "symbolOrder": sym_order,
                            "appErrorCode": exc.code,
                            "transitionTrigger": "limit.quote.public_ticker_band",
                        }
                    ),
                )
            raise
        ref = _last_price_from_coobit_ticker(raw_tick)
        try:
            band_obs = check_spot_limit_price_agent_band(
                settings=settings,
                limit_price=price_dec,
                last_price=ref,
            )
        except AppError as exc:
            if tl_eid and timeline_include_quote:
                d = exc.details or {}
                await append_execution_timeline_event(
                    session,
                    execution_id=tl_eid,
                    user_id=uid_s,
                    event_name="agent.execution.step",
                    step_kind="band_check",
                    outcome="fail",
                    payload=_with_timeline_canonical(
                        {
                            "scenarioId": "trade.spot.limit_order",
                            "channel": timeline_channel,
                            "symbol": sym_ticker,
                            "lastPrice": d.get("lastPrice"),
                            "limitPrice": d.get("limitPrice"),
                            "deviationPct": d.get("deviationPct"),
                            "appErrorCode": exc.code,
                            "transitionTrigger": "limit.price_band_rejected",
                        }
                    ),
                )
            raise
        if tl_eid and timeline_include_quote:
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="agent.execution.step",
                step_kind="quote",
                outcome="success",
                payload=_with_timeline_canonical(
                    {
                        "scenarioId": "trade.spot.limit_order",
                        "channel": timeline_channel,
                        "symbol": sym_ticker,
                        "symbolOrder": sym_order,
                        "side": side_u,
                        "lastPrice": band_obs.get("lastPrice"),
                        "limitPrice": band_obs.get("limitPrice"),
                        "deviationPct": band_obs.get("deviationPct"),
                        "bandCheck": band_obs.get("bandCheck") == "true",
                        "transitionTrigger": "limit.quote.public_ticker_band",
                    }
                ),
            )
    elif tl_eid and timeline_include_quote:
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="agent.execution.step",
            step_kind="quote",
            outcome="success",
            payload=_with_timeline_canonical(
                {
                    "scenarioId": "trade.spot.limit_order",
                    "channel": timeline_channel,
                    "symbol": sym_ticker,
                    "symbolOrder": sym_order,
                    "side": side_u,
                    "bandCheck": False,
                    "transitionTrigger": "limit.skip_public_quote",
                }
            ),
        )

    wire_price = float(price_dec)
    limit_meta = {
        "volumeSemantics": "limit_base_qty",
        "limitPriceUserRequested": price.strip(),
        "baseQtyUserRequested": str(base_vol),
        "timeInForce": tif_u,
    }

    place = PlaceOrder(
        instrument=inst,
        side=side_u,
        order_type="LIMIT",
        client_order_id=cid,
        quantity=base_vol,
        quote_amount=None,
        price=wire_price,
        time_in_force=tif_u,
    )
    order_payload = coobit_sapi_v2_order_body_from_place_order(
        place, coobit_order_body_symbol=sym_order_body
    )
    try:
        data = await post_signed_spot_order_json(
            openapi_base_url=openapi_base,
            api_key=ak,
            secret_key=sk,
            order_body=order_payload,
        )
    except AppError as exc:
        if tl_eid:
            d = exc.details or {}
            exo = _flash_timeline_exchange_outcome(exc)
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="agent.execution.step",
                step_kind="submit_order",
                outcome="fail",
                payload=_with_timeline_canonical(
                    {
                        "scenarioId": "trade.spot.limit_order",
                        "channel": timeline_channel,
                        "symbol": sym_ticker,
                        "side": side_u,
                        "quantityRequested": volume.strip(),
                        "limitPrice": str(price_dec),
                        "appErrorCode": exc.code,
                        "transitionTrigger": "limit.order.submit",
                    }
                ),
            )
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="trading.exchange_private",
                step_kind="submit_order",
                outcome="fail",
                payload=_trading_exchange_private_fail_payload(
                    d=d,
                    exo=exo,
                    exc=exc,
                    cid=cid,
                    sym_order=sym_order,
                    order_payload=order_payload,
                    limit_order_meta=limit_meta,
                ),
            )
        raise

    preview = _sanitize_spot_order_response(data)
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
            payload=_with_timeline_canonical(
                {
                    "scenarioId": "trade.spot.limit_order",
                    "channel": timeline_channel,
                    "symbol": sym_ticker,
                    "side": side_u,
                    "quantityRequested": volume.strip(),
                    "limitPrice": str(price_dec),
                    "orderId": oid,
                    "transitionTrigger": "limit.order.submit",
                }
            ),
        )
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="trading.exchange_private",
            step_kind="submit_order",
            outcome="success",
            payload=_with_timeline_canonical(
                {
                    "methodPathSummary": "POST /sapi/v2/order",
                    "httpStatus": 200,
                    "exchangeOutcome": "success",
                    "clientOrderRef": pcid,
                    "symbolOrder": preview.get("symbol") or sym_order,
                    "orderRequest": _timeline_spot_order_request_for_observability(
                        order_payload, limit_order_meta=limit_meta
                    ),
                    "exchangeResponsePreview": preview,
                }
            ),
        )
    return {
        "orderId": _order_id_to_str(data),
        "orderIdString": preview.get("orderIdString") or _order_id_to_str(data),
        "clientOrderId": pcid,
        "status": preview.get("status"),
        "symbol": preview.get("symbol") or sym_order,
        "side": preview.get("side") or side_u,
        "type": preview.get("type") or "LIMIT",
        "exchangeOrderPreview": preview,
    }


async def spot_open_orders_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str | None,
    limit: int | None,
) -> dict[str, Any]:
    """GET ``/sapi/v2/openOrders`` for a bound user (optional pair filter)."""
    tg = parse_telegram_user_id_numeric(user_id)
    row = await load_binding_row_for_telegram_user(session, tg)
    if row is None:
        raise AppError(
            code="AGENT_SUBACCOUNT_REQUIRED",
            message="未发现该 Telegram 用户的托管 API 绑定，请先完成 Deeplink 校验与绑定。",
            status_code=403,
        )

    sym_ticker: str | None = None
    sym_order: str | None = None
    sym_body: str | None = None
    if symbol is not None and str(symbol).strip():
        sym_in = str(symbol).strip()
        sym_ticker = normalize_coobit_spot_symbol_param(sym_in)
        sym_order = normalize_coobit_spot_order_symbol(sym_in)
        sym_body = normalize_coobit_spot_order_body_symbol(sym_in)

    lim_clamped = _clamp_open_orders_limit(limit)

    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)
    rows = await fetch_signed_spot_open_orders_json(
        openapi_base_url=openapi_base,
        api_key=ak,
        secret_key=sk,
        symbol=sym_body,
        limit=lim_clamped,
    )
    sanitized = [_sanitize_open_order_row_preview(r) for r in rows]
    return {
        "symbol": sym_ticker,
        "symbolOrder": sym_order,
        "orders": sanitized,
    }


async def spot_cancel_order_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str,
    order_id: str | None,
    new_client_order_id: str | None,
    timeline_execution_id: str | None = None,
    timeline_channel: str = "http_api",
) -> dict[str, Any]:
    """POST ``/sapi/v2/cancel`` for a bound user."""
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
    oid_raw = (order_id or "").strip()
    ncid_raw = (new_client_order_id or "").strip()
    if not oid_raw and not ncid_raw:
        raise AppError(
            code="VALIDATION_ERROR",
            message="须提供 orderId 或 newClientOrderId 之一",
            status_code=422,
            details={"fields": ["orderId", "newClientOrderId"]},
        )
    if ncid_raw and len(ncid_raw) >= 32:
        raise AppError(
            code="VALIDATION_ERROR",
            message="newClientOrderId 长度须小于 32",
            status_code=422,
            details={"field": "newClientOrderId"},
        )

    sym_ticker = normalize_coobit_spot_symbol_param(sym_in)
    sym_order = normalize_coobit_spot_order_symbol(sym_in)
    sym_order_body = normalize_coobit_spot_order_body_symbol(sym_in)

    cancel_body: dict[str, Any] = {"symbol": sym_order_body}
    if oid_raw:
        cancel_body["orderId"] = oid_raw
    if ncid_raw:
        cancel_body["newClientOrderId"] = ncid_raw

    uid_s = user_id.strip()
    tl_eid = (
        timeline_execution_id.strip()
        if timeline_execution_id and timeline_execution_id.strip()
        else None
    )

    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)
    try:
        data = await post_signed_spot_cancel_json(
            openapi_base_url=openapi_base,
            api_key=ak,
            secret_key=sk,
            cancel_body=cancel_body,
        )
    except AppError as exc:
        if tl_eid:
            d = exc.details or {}
            exo = _flash_timeline_exchange_outcome(exc)
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="agent.execution.step",
                step_kind="cancel_order",
                outcome="fail",
                payload=_with_timeline_canonical(
                    {
                        "scenarioId": "trade.spot.cancel_order",
                        "channel": timeline_channel,
                        "symbol": sym_ticker,
                        "symbolOrder": sym_order,
                        "orderId": oid_raw or None,
                        "newClientOrderId": ncid_raw or None,
                        "appErrorCode": exc.code,
                        "transitionTrigger": "spot.cancel.submit",
                    }
                ),
            )
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="trading.exchange_private",
                step_kind="cancel_order",
                outcome="fail",
                payload=_cancel_fail_timeline_payload(
                    d=d,
                    exo=exo,
                    exc=exc,
                    cancel_body=cancel_body,
                    sym_order=sym_order,
                ),
            )
        raise

    preview = _sanitize_spot_order_response(data)
    oid_out = preview.get("orderIdString") or _order_id_to_str(data)
    pcid = preview.get("clientOrderId") or preview.get("clientorderId")
    if tl_eid:
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="agent.execution.step",
            step_kind="cancel_order",
            outcome="success",
            payload=_with_timeline_canonical(
                {
                    "scenarioId": "trade.spot.cancel_order",
                    "channel": timeline_channel,
                    "symbol": sym_ticker,
                    "symbolOrder": sym_order,
                    "orderId": oid_out,
                    "transitionTrigger": "spot.cancel.submit",
                }
            ),
        )
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="trading.exchange_private",
            step_kind="cancel_order",
            outcome="success",
            payload=_with_timeline_canonical(
                {
                    "methodPathSummary": "POST /sapi/v2/cancel",
                    "httpStatus": 200,
                    "exchangeOutcome": "success",
                    "clientOrderRef": pcid,
                    "symbolOrder": preview.get("symbol") or sym_order,
                    "cancelRequest": _timeline_spot_cancel_request_for_observability(cancel_body),
                    "exchangeResponsePreview": preview,
                }
            ),
        )
    return {
        "orderId": _order_id_to_str(data),
        "orderIdString": preview.get("orderIdString") or _order_id_to_str(data),
        "clientOrderId": pcid,
        "status": preview.get("status"),
        "symbol": preview.get("symbol") or sym_order,
        "side": preview.get("side"),
        "type": preview.get("type"),
        "exchangeOrderPreview": preview,
    }


_AMEND_SCENARIO_ID = "trade.spot.amend_limit_order"


def _order_id_values_equal(left: str, right: Any) -> bool:
    if right is None:
        return False
    return str(left).strip() == str(right).strip()


def _open_order_id_str(row: dict[str, Any]) -> str | None:
    oid = row.get("orderIdString") or row.get("orderId")
    if oid is None:
        return None
    s = str(oid).strip()
    return s or None


def _find_open_limit_order_for_amend(
    orders: list[dict[str, Any]], *, order_id: str
) -> dict[str, Any]:
    oid_need = order_id.strip()
    if not oid_need:
        raise AppError(
            code="VALIDATION_ERROR",
            message="orderId 不可为空",
            status_code=422,
            details={"field": "orderId"},
        )
    for row in orders:
        oid_row = _open_order_id_str(row)
        if oid_row is None or not _order_id_values_equal(oid_need, oid_row):
            continue
        otype = str(row.get("type") or "").strip().upper()
        if otype and otype != "LIMIT":
            raise AppError(
                code="AGENT_SPOT_AMEND_NOT_LIMIT",
                message="仅支持修改在途限价委托；当前订单类型非 LIMIT。",
                status_code=422,
                details={"orderId": oid_need, "type": otype},
            )
        return row
    raise AppError(
        code="AGENT_SPOT_AMEND_ORDER_NOT_FOUND",
        message="未找到匹配的在途委托，请核对交易对与订单号后重试。",
        status_code=404,
        details={"orderId": oid_need},
    )


def _decimal_str_from_order_field(raw: Any) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip()
    return s or None


async def spot_amend_limit_order_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    symbol: str,
    order_id: str,
    price: str | None,
    volume: str | None,
    time_in_force: str | None = None,
    new_client_order_id: str | None = None,
    timeline_execution_id: str | None = None,
    timeline_channel: str = "http_api",
    timeline_include_quote: bool = True,
) -> dict[str, Any]:
    """Logical amend: ``POST /sapi/v2/cancel`` then ``POST /sapi/v2/order`` (CC-P0-02)."""
    tg = parse_telegram_user_id_numeric(user_id)
    row = await load_binding_row_for_telegram_user(session, tg)
    if row is None:
        raise AppError(
            code="AGENT_SUBACCOUNT_REQUIRED",
            message="未发现该 Telegram 用户的托管 API 绑定，请先完成 Deeplink 校验与绑定。",
            status_code=403,
        )

    sym_in = symbol.strip()
    oid_raw = order_id.strip()
    if not sym_in:
        raise AppError(
            code="VALIDATION_ERROR",
            message="symbol 不可为空",
            status_code=422,
            details={"field": "symbol"},
        )
    if not oid_raw:
        raise AppError(
            code="VALIDATION_ERROR",
            message="orderId 不可为空",
            status_code=422,
            details={"field": "orderId"},
        )
    price_in = (price or "").strip()
    vol_in = (volume or "").strip()
    if not price_in and not vol_in:
        raise AppError(
            code="VALIDATION_ERROR",
            message="改单须至少提供新限价或新数量之一",
            status_code=422,
            details={"fields": ["price", "volume"]},
        )

    sym_ticker = normalize_coobit_spot_symbol_param(sym_in)
    sym_order = normalize_coobit_spot_order_symbol(sym_in)
    sym_order_body = normalize_coobit_spot_order_body_symbol(sym_in)
    uid_s = user_id.strip()
    tl_eid = (
        timeline_execution_id.strip()
        if timeline_execution_id and timeline_execution_id.strip()
        else None
    )
    amend_corr = f"amend_{secrets.token_hex(8)}"
    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)

    open_payload = await fetch_signed_spot_open_orders_json(
        openapi_base_url=openapi_base,
        api_key=ak,
        secret_key=sk,
        symbol=sym_order_body,
        limit=None,
    )
    prior_raw = _find_open_limit_order_for_amend(open_payload, order_id=oid_raw)
    prior_preview = _sanitize_open_order_row_preview(prior_raw)

    side_u = str(prior_preview.get("side") or "").strip().upper()
    if side_u not in ("BUY", "SELL"):
        raise AppError(
            code="AGENT_SPOT_AMEND_ORDER_NOT_FOUND",
            message="无法在途委托中读取买卖方向，请查单后重试。",
            status_code=422,
            details={"orderId": oid_raw},
        )

    prior_price = _decimal_str_from_order_field(prior_preview.get("price"))
    prior_qty = _decimal_str_from_order_field(
        prior_preview.get("origQty") or prior_preview.get("executedQty")
    )
    new_price_s = price_in or prior_price
    new_qty_s = vol_in or prior_qty
    if not new_price_s or not new_qty_s:
        raise AppError(
            code="VALIDATION_ERROR",
            message="无法确定新限价或新数量，请显式提供 price/volume。",
            status_code=422,
        )
    if prior_price == new_price_s and prior_qty == new_qty_s:
        raise AppError(
            code="VALIDATION_ERROR",
            message="新参数与原委托相同，无需改单。",
            status_code=422,
            details={"priorPrice": prior_price, "priorQuantity": prior_qty},
        )

    price_dec = _parse_positive_price(new_price_s)
    base_vol = _parse_positive_volume(new_qty_s)
    tif_u = _normalize_limit_time_in_force(
        time_in_force
        or _decimal_str_from_order_field(prior_preview.get("timeInForce"))
        or "GTC"
    )
    cid = _resolve_new_client_order_id(new_client_order_id)
    inst = _instrument_ref_from_ticker_or_raise(sym_ticker)

    amend_base = {
        "scenarioId": _AMEND_SCENARIO_ID,
        "channel": timeline_channel,
        "amendCorrelationId": amend_corr,
        "symbol": sym_ticker,
        "symbolOrder": sym_order,
        "priorOrderId": oid_raw,
        "priorPrice": prior_price,
        "priorQuantity": prior_qty,
        "newLimitPrice": str(price_dec),
        "newQuantity": str(base_vol),
    }

    if settings.trade_spot_limit_price_band_enabled and timeline_include_quote:
        try:
            raw_tick = await fetch_spot_public_ticker_json_with_fallbacks(
                openapi_base_url=openapi_base,
                symbol_candidates=spot_ticker_symbol_candidates(sym_ticker, sym_order),
            )
        except AppError as exc:
            if tl_eid:
                await append_execution_timeline_event(
                    session,
                    execution_id=tl_eid,
                    user_id=uid_s,
                    event_name="agent.execution.step",
                    step_kind="quote",
                    outcome="fail",
                    payload=_with_timeline_canonical(
                        {**amend_base, "appErrorCode": exc.code, "transitionTrigger": "amend.quote.public_ticker_band"}
                    ),
                )
            raise
        ref = _last_price_from_coobit_ticker(raw_tick)
        try:
            band_obs = check_spot_limit_price_agent_band(
                settings=settings,
                limit_price=price_dec,
                last_price=ref,
            )
        except AppError as exc:
            if tl_eid:
                d = exc.details or {}
                await append_execution_timeline_event(
                    session,
                    execution_id=tl_eid,
                    user_id=uid_s,
                    event_name="agent.execution.step",
                    step_kind="band_check",
                    outcome="fail",
                    payload=_with_timeline_canonical(
                        {
                            **amend_base,
                            "lastPrice": d.get("lastPrice"),
                            "limitPrice": d.get("limitPrice"),
                            "deviationPct": d.get("deviationPct"),
                            "appErrorCode": exc.code,
                            "transitionTrigger": "amend.price_band_rejected",
                        }
                    ),
                )
            raise
        if tl_eid:
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="agent.execution.step",
                step_kind="quote",
                outcome="success",
                payload=_with_timeline_canonical(
                    {
                        **amend_base,
                        "side": side_u,
                        "lastPrice": band_obs.get("lastPrice"),
                        "limitPrice": band_obs.get("limitPrice"),
                        "deviationPct": band_obs.get("deviationPct"),
                        "bandCheck": band_obs.get("bandCheck") == "true",
                        "transitionTrigger": "amend.quote.public_ticker_band",
                    }
                ),
            )

    cancel_body: dict[str, Any] = {"symbol": sym_order_body, "orderId": oid_raw}
    try:
        cancel_data = await post_signed_spot_cancel_json(
            openapi_base_url=openapi_base,
            api_key=ak,
            secret_key=sk,
            cancel_body=cancel_body,
        )
    except AppError as exc:
        if tl_eid:
            d = exc.details or {}
            exo = _flash_timeline_exchange_outcome(exc)
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="agent.execution.step",
                step_kind="cancel_order",
                outcome="fail",
                payload=_with_timeline_canonical(
                    {**amend_base, "appErrorCode": exc.code, "transitionTrigger": "spot.amend.cancel"}
                ),
            )
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="trading.exchange_private",
                step_kind="cancel_order",
                outcome="fail",
                payload=_cancel_fail_timeline_payload(
                    d=d,
                    exo=exo,
                    exc=exc,
                    cancel_body=cancel_body,
                    sym_order=sym_order,
                ),
            )
        raise

    cancel_preview = _sanitize_spot_order_response(cancel_data)
    cancel_oid = cancel_preview.get("orderIdString") or _order_id_to_str(cancel_data)
    if tl_eid:
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="agent.execution.step",
            step_kind="cancel_order",
            outcome="success",
            payload=_with_timeline_canonical(
                {
                    **amend_base,
                    "orderId": cancel_oid,
                    "transitionTrigger": "spot.amend.cancel",
                }
            ),
        )
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="trading.exchange_private",
            step_kind="cancel_order",
            outcome="success",
            payload=_with_timeline_canonical(
                {
                    "methodPathSummary": "POST /sapi/v2/cancel",
                    "httpStatus": 200,
                    "exchangeOutcome": "success",
                    "amendCorrelationId": amend_corr,
                    "symbolOrder": cancel_preview.get("symbol") or sym_order,
                    "cancelRequest": _timeline_spot_cancel_request_for_observability(cancel_body),
                    "exchangeResponsePreview": cancel_preview,
                }
            ),
        )

    wire_price = float(price_dec)
    limit_meta = {
        "volumeSemantics": "limit_base_qty",
        "limitPriceUserRequested": new_price_s,
        "baseQtyUserRequested": str(base_vol),
        "timeInForce": tif_u,
        "amendCorrelationId": amend_corr,
        "priorOrderId": oid_raw,
    }
    place = PlaceOrder(
        instrument=inst,
        side=side_u,
        order_type="LIMIT",
        client_order_id=cid,
        quantity=base_vol,
        quote_amount=None,
        price=wire_price,
        time_in_force=tif_u,
    )
    order_payload = coobit_sapi_v2_order_body_from_place_order(
        place, coobit_order_body_symbol=sym_order_body
    )
    try:
        order_data = await post_signed_spot_order_json(
            openapi_base_url=openapi_base,
            api_key=ak,
            secret_key=sk,
            order_body=order_payload,
        )
    except AppError as exc:
        if tl_eid:
            d = exc.details or {}
            exo = _flash_timeline_exchange_outcome(exc)
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="agent.execution.step",
                step_kind="submit_order",
                outcome="fail",
                payload=_with_timeline_canonical(
                    {
                        **amend_base,
                        "side": side_u,
                        "appErrorCode": exc.code,
                        "transitionTrigger": "spot.amend.replace",
                    }
                ),
            )
            await append_execution_timeline_event(
                session,
                execution_id=tl_eid,
                user_id=uid_s,
                event_name="trading.exchange_private",
                step_kind="submit_order",
                outcome="fail",
                payload=_trading_exchange_private_fail_payload(
                    d=d,
                    exo=exo,
                    exc=exc,
                    cid=cid,
                    sym_order=sym_order,
                    order_payload=order_payload,
                    limit_order_meta=limit_meta,
                ),
            )
        raise AppError(
            code="AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED",
            message=(
                "原委托已撤销，但新委托提交失败；请调用对账接口查单后再操作，勿重复撤单或假定为失败。"
            ),
            status_code=502,
            details={
                "amendCorrelationId": amend_corr,
                "cancelledOrderId": cancel_oid,
                "priorOrderPreview": prior_preview,
                "exchangeErrorCode": exc.code,
                "reconcileSuggested": True,
                "reconcileCaseKind": "CANCEL_SUCCEEDED_REPLACE_FAILED",
                "reconcilePath": "/api/v1/agent/trading/reconcile",
            },
        ) from exc

    replace_preview = _sanitize_spot_order_response(order_data)
    new_oid = replace_preview.get("orderIdString") or _order_id_to_str(order_data)
    pcid = replace_preview.get("clientOrderId") or replace_preview.get("clientorderId")
    if tl_eid:
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="agent.execution.step",
            step_kind="submit_order",
            outcome="success",
            payload=_with_timeline_canonical(
                {
                    **amend_base,
                    "side": side_u,
                    "orderId": new_oid,
                    "transitionTrigger": "spot.amend.replace",
                }
            ),
        )
        await append_execution_timeline_event(
            session,
            execution_id=tl_eid,
            user_id=uid_s,
            event_name="trading.exchange_private",
            step_kind="submit_order",
            outcome="success",
            payload=_with_timeline_canonical(
                {
                    "methodPathSummary": "POST /sapi/v2/order",
                    "httpStatus": 200,
                    "exchangeOutcome": "success",
                    "amendCorrelationId": amend_corr,
                    "clientOrderRef": pcid,
                    "symbolOrder": replace_preview.get("symbol") or sym_order,
                    "orderRequestMeta": limit_meta,
                    "exchangeResponsePreview": replace_preview,
                }
            ),
        )

    return {
        "scenarioId": _AMEND_SCENARIO_ID,
        "amendCorrelationId": amend_corr,
        "cancelledOrderId": cancel_oid,
        "cancelledOrderPreview": cancel_preview,
        "priorOrderPreview": prior_preview,
        "orderId": _order_id_to_str(order_data),
        "orderIdString": new_oid,
        "clientOrderId": pcid,
        "status": replace_preview.get("status"),
        "symbol": replace_preview.get("symbol") or sym_order,
        "side": side_u,
        "type": replace_preview.get("type") or "LIMIT",
        "exchangeOrderPreview": replace_preview,
    }


def _sanitize_spot_order_response(raw: dict[str, Any]) -> dict[str, Any]:
    cleaned = _sanitize_spot_order_preview(raw)
    c1 = cleaned.get("clientorderId")
    c2 = cleaned.get("clientOrderId")
    if c1 and not c2:
        cleaned["clientOrderId"] = c1
    return cleaned
