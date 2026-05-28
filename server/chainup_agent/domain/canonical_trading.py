"""Canonical trading model (ADR-004) — pure types and Coobit wire mapping.

Execution Gateway as a deployable is outside this repo; this module is the in-process
semantic boundary: PlaceOrder → Coobit ``POST /sapi/v2/order`` body.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

VENUE_COOBIT = "coobit"
CANONICAL_OP_PLACE_ORDER = "place_order"

Side = Literal["BUY", "SELL"]
OrderType = Literal["MARKET", "LIMIT"]


@dataclass(frozen=True)
class InstrumentRef:
    base_asset: str
    quote_asset: str
    market_kind: str = "SPOT"


@dataclass(frozen=True)
class PlaceOrder:
    instrument: InstrumentRef
    side: Side
    order_type: OrderType
    client_order_id: str
    quantity: float | None = None
    quote_amount: float | None = None
    price: float | None = None
    time_in_force: str | None = None


def instrument_ref_from_sym_ticker(sym_ticker: str) -> InstrumentRef:
    """Parse normalized ticker ``BASE-QUOTE`` (e.g. ``BTC-USDT``) into :class:`InstrumentRef`."""
    raw = sym_ticker.strip().upper()
    if "-" not in raw:
        raise ValueError(f"expected hyphenated spot ticker, got {sym_ticker!r}")
    base, quote = raw.split("-", 1)
    base = base.strip()
    quote = quote.strip()
    if not base or not quote:
        raise ValueError(f"invalid spot ticker: {sym_ticker!r}")
    return InstrumentRef(base_asset=base, quote_asset=quote)


def coobit_sapi_v2_order_body_from_place_order(
    place: PlaceOrder,
    *,
    coobit_order_body_symbol: str,
) -> dict[str, Any]:
    """Map a canonical :class:`PlaceOrder` to Coobit ``/sapi/v2/order`` JSON.

    ``coobit_order_body_symbol`` must already match
    :func:`chainup_agent.infrastructure.exchange.coobit_openapi.normalize_coobit_spot_order_body_symbol`
    (e.g. ``BTC/USDT``).
    """
    sym = coobit_order_body_symbol.strip()
    if not sym:
        raise ValueError("coobit_order_body_symbol is required")

    if place.order_type == "MARKET":
        if place.side == "BUY":
            if place.quote_amount is None:
                raise ValueError("MARKET BUY requires quote_amount")
            vol = place.quote_amount
        else:
            if place.quantity is None:
                raise ValueError("MARKET SELL requires quantity")
            vol = place.quantity
        return {
            "newClientOrderId": place.client_order_id,
            "side": place.side,
            "symbol": sym,
            "type": "MARKET",
            "volume": vol,
        }

    if place.quantity is None or place.price is None:
        raise ValueError("LIMIT requires quantity and price")
    tif = place.time_in_force or "GTC"
    return {
        "newClientOrderId": place.client_order_id,
        "side": place.side,
        "symbol": sym,
        "type": "LIMIT",
        "volume": place.quantity,
        "price": place.price,
        "timeInForce": tif,
    }


def timeline_obs_venue_canonical(
    *, canonical_op: str = CANONICAL_OP_PLACE_ORDER
) -> dict[str, str]:
    """ADR-004 observability hints for execution timeline payloads (summary)."""
    return {"venue": VENUE_COOBIT, "canonicalOp": canonical_op}


def coobit_fapi_v1_order_body(
    *,
    symbol: str,
    side: Side,
    order_type: OrderType,
    client_order_id: str,
    volume: float,
    price: float | None = None,
    open_close: str | None = None,
    reduce_only: bool | None = None,
) -> dict[str, Any]:
    """Map Agent futures order fields to Coobit ``POST /fapi/v1/order`` JSON."""
    sym = symbol.strip()
    if not sym:
        raise ValueError("symbol is required")
    if volume <= 0:
        raise ValueError("volume must be positive")
    body: dict[str, Any] = {
        "newClientOrderId": client_order_id,
        "side": side,
        "symbol": sym,
        "type": order_type,
        "volume": volume,
    }
    if order_type == "LIMIT":
        if price is None or price <= 0:
            raise ValueError("LIMIT requires positive price")
        body["price"] = price
    oc = (open_close or "").strip().upper()
    if oc in ("OPEN", "CLOSE"):
        body["open"] = oc
    if reduce_only is True:
        body["reduceOnly"] = True
    return body


def coobit_fapi_v1_condition_order_body(
    *,
    contract_name: str,
    side: Side,
    order_type: OrderType,
    volume: float,
    trigger_price: str,
    trigger_type: str,
    price: float | None = None,
    open_close: str | None = None,
    position_type: int = 1,
    order_unit: int = 2,
) -> dict[str, Any]:
    """Map Agent condition-order fields to Coobit ``POST /fapi/v1/conditionOrder`` JSON."""
    cn = contract_name.strip()
    if not cn:
        raise ValueError("contract_name is required")
    if volume <= 0:
        raise ValueError("volume must be positive")
    tp = trigger_price.strip()
    if not tp:
        raise ValueError("trigger_price is required")
    tt = trigger_type.strip().upper()
    if tt not in ("3UP", "4DOWN"):
        raise ValueError("trigger_type must be 3UP or 4DOWN")
    body: dict[str, Any] = {
        "contractName": cn,
        "side": side,
        "type": order_type,
        "volume": volume,
        "triggerPrice": tp,
        "triggerType": tt,
        "positionType": position_type,
        "orderUnit": order_unit,
    }
    if order_type == "LIMIT":
        if price is None or price <= 0:
            raise ValueError("LIMIT requires positive price")
        body["price"] = price
    oc = (open_close or "").strip().upper()
    if oc in ("OPEN", "CLOSE"):
        body["open"] = oc
    return body


def coobit_fapi_v1_cancel_body(*, contract_name: str, order_id: str) -> dict[str, Any]:
    """Map Agent futures cancel fields to Coobit ``POST /fapi/v1/cancel`` JSON."""
    cn = contract_name.strip()
    if not cn:
        raise ValueError("contract_name is required")
    oid = order_id.strip()
    if not oid:
        raise ValueError("order_id is required")
    return {"contractName": cn, "orderId": oid}


def coobit_sapi_v2_margin_order_body(
    *,
    coobit_order_body_symbol: str,
    side: Side,
    order_type: OrderType,
    client_order_id: str,
    volume: float,
    price: float | None = None,
) -> dict[str, Any]:
    """Map Agent margin order fields to Coobit ``POST /sapi/v2/margin/order`` JSON."""
    sym = coobit_order_body_symbol.strip()
    if not sym:
        raise ValueError("coobit_order_body_symbol is required")
    if volume <= 0:
        raise ValueError("volume must be positive")
    body: dict[str, Any] = {
        "newClientOrderId": client_order_id,
        "side": side,
        "symbol": sym,
        "type": order_type,
        "volume": volume,
    }
    if order_type == "LIMIT":
        if price is None or price <= 0:
            raise ValueError("LIMIT requires positive price")
        body["price"] = price
    return body
