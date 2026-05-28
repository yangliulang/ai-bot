"""Telegram Type-A confirmation copy (quote notional, 2 decimal display)."""

from __future__ import annotations

from decimal import Decimal

from chainup_agent.application.telegram_bound_reply import (
    _format_flash_type_a_confirmation,
    _format_limit_type_a_confirmation,
    _format_quote_estimate_amount,
    _last_price_decimal_from_ticker_preview,
    _spot_base_quote_assets,
)


def test_spot_base_quote_assets_parses_slash() -> None:
    assert _spot_base_quote_assets("bnb/usdt") == ("BNB", "USDT")


def test_format_quote_estimate_two_decimals() -> None:
    assert _format_quote_estimate_amount("USDT", Decimal("630.004")) == "USDT:630.00"
    assert _format_quote_estimate_amount("USDT", Decimal("630.996")) == "USDT:631.00"


def test_last_price_from_preview() -> None:
    assert _last_price_decimal_from_ticker_preview({"lastPrice": "612.5"}) == Decimal(
        "612.5"
    )
    assert _last_price_decimal_from_ticker_preview({}) is None


def test_flash_confirm_includes_qty_base_and_usdt_line() -> None:
    slots = {"symbol": "BNB-USDT", "side": "BUY", "quantity": "1"}
    text = _format_flash_type_a_confirmation(
        slots,
        base_asset="BNB",
        quote_asset="USDT",
        notional_quote=Decimal("630"),
    )
    assert "数量：`1` BNB" in text
    assert "USDT:630.00" in text
    assert "现货闪兑（市价）" in text


def test_limit_confirm_includes_notional_line() -> None:
    slots = {
        "symbol": "BNB-USDT",
        "side": "SELL",
        "quantity": "2",
        "price": "600",
        "timeInForce": "GTC",
    }
    text = _format_limit_type_a_confirmation(
        slots,
        base_asset="BNB",
        quote_asset="USDT",
        notional_quote=Decimal("1200"),
    )
    assert "USDT:1200.00" in text
    assert "数量：`2` BNB" in text
