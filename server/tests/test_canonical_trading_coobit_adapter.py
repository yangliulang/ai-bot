"""Unit tests for Canonical → Coobit spot wire mapping (ADR-004)."""

from __future__ import annotations

import pytest

from chainup_agent.domain.canonical_trading import (
    InstrumentRef,
    PlaceOrder,
    coobit_sapi_v2_order_body_from_place_order,
    instrument_ref_from_sym_ticker,
    timeline_obs_venue_canonical,
)


def test_instrument_ref_from_sym_ticker() -> None:
    inst = instrument_ref_from_sym_ticker("BTC-USDT")
    assert inst.base_asset == "BTC"
    assert inst.quote_asset == "USDT"


def test_instrument_ref_rejects_non_hyphenated() -> None:
    with pytest.raises(ValueError):
        instrument_ref_from_sym_ticker("BTCUSDT")


def test_timeline_obs_venue_canonical_defaults() -> None:
    assert timeline_obs_venue_canonical() == {
        "venue": "coobit",
        "canonicalOp": "place_order",
    }


def test_coobit_body_market_buy_uses_quote_amount() -> None:
    inst = InstrumentRef("BTC", "USDT")
    place = PlaceOrder(
        instrument=inst,
        side="BUY",
        order_type="MARKET",
        client_order_id="cu_agent_0123456789abcdefghijk",
        quantity=0.01,
        quote_amount=500.0,
    )
    body = coobit_sapi_v2_order_body_from_place_order(
        place, coobit_order_body_symbol="BTC/USDT"
    )
    assert body == {
        "newClientOrderId": "cu_agent_0123456789abcdefghijk",
        "side": "BUY",
        "symbol": "BTC/USDT",
        "type": "MARKET",
        "volume": 500.0,
    }


def test_coobit_body_market_sell_uses_base_quantity() -> None:
    inst = InstrumentRef("BTC", "USDT")
    place = PlaceOrder(
        instrument=inst,
        side="SELL",
        order_type="MARKET",
        client_order_id="cu_agent_0123456789abcdefghijk",
        quantity=0.05,
        quote_amount=None,
    )
    body = coobit_sapi_v2_order_body_from_place_order(
        place, coobit_order_body_symbol="BTC/USDT"
    )
    assert body["volume"] == 0.05
    assert body["side"] == "SELL"


def test_coobit_body_limit() -> None:
    inst = InstrumentRef("BTC", "USDT")
    place = PlaceOrder(
        instrument=inst,
        side="BUY",
        order_type="LIMIT",
        client_order_id="c1",
        quantity=0.02,
        price=48000.0,
        time_in_force="GTC",
    )
    body = coobit_sapi_v2_order_body_from_place_order(
        place, coobit_order_body_symbol="BTC/USDT"
    )
    assert body["type"] == "LIMIT"
    assert body["volume"] == 0.02
    assert body["price"] == 48000.0
    assert body["timeInForce"] == "GTC"


def test_coobit_body_limit_default_tif() -> None:
    inst = InstrumentRef("ETH", "USDT")
    place = PlaceOrder(
        instrument=inst,
        side="BUY",
        order_type="LIMIT",
        client_order_id="c1",
        quantity=1.0,
        price=2000.0,
        time_in_force=None,
    )
    body = coobit_sapi_v2_order_body_from_place_order(
        place, coobit_order_body_symbol="ETH/USDT"
    )
    assert body["timeInForce"] == "GTC"
