"""Telegram clarify inline_keyboard — port of product-doc clarifyKeyboard.ts."""

from __future__ import annotations

from typing import Any, Literal

EffectiveLocale = Literal["zh-Hans", "zh-Hant", "en"]
ClarifyKeyboardKind = Literal[
    "spot_trade_mode",
    "spot_side",
    "confirm_symbol_default",
    "spot_qty_mode",
    "idle_resume_or_new",
]

ReadClarifyKeyboardKind = Literal[
    "read_scope_portfolio_vs_market",
    "read_multi_symbol",
    "read_monitoring_asset_class",
]

_LABELS: dict[ClarifyKeyboardKind, dict[EffectiveLocale, list[tuple[str, str]]]] = {
    "spot_trade_mode": {
        "zh-Hans": [("闪兑", "cl:fc"), ("限价", "cl:lo")],
        "zh-Hant": [("閃兌", "cl:fc"), ("限價", "cl:lo")],
        "en": [("Flash", "cl:fc"), ("Limit", "cl:lo")],
    },
    "spot_side": {
        "zh-Hans": [("买入", "cl:buy"), ("卖出", "cl:sell")],
        "zh-Hant": [("買入", "cl:buy"), ("賣出", "cl:sell")],
        "en": [("Buy", "cl:buy"), ("Sell", "cl:sell")],
    },
    "confirm_symbol_default": {
        "zh-Hans": [("对的", "cl:sym:ok"), ("换一个", "cl:sym:no")],
        "zh-Hant": [("對的", "cl:sym:ok"), ("換一個", "cl:sym:no")],
        "en": [("Yes", "cl:sym:ok"), ("Change", "cl:sym:no")],
    },
    "idle_resume_or_new": {
        "zh-Hans": [("继续上一笔", "cl:resume"), ("新话题", "cl:new")],
        "zh-Hant": [("繼續上一筆", "cl:resume"), ("新話題", "cl:new")],
        "en": [("Continue", "cl:resume"), ("New topic", "cl:new")],
    },
}


def _normalize_locale(locale: str | None) -> EffectiveLocale:
    raw = (locale or "zh-Hans").strip()
    if raw in ("zh-Hant", "zh-TW", "zh-HK"):
        return "zh-Hant"
    if raw.startswith("en"):
        return "en"
    return "zh-Hans"


def build_spot_qty_mode_labels(
    *,
    base_asset: str | None,
    quote_asset: str | None,
    locale: EffectiveLocale,
) -> list[tuple[str, str]]:
    base = (base_asset or "BNB").strip().upper() or "BNB"
    quote = (quote_asset or "USDT").strip().upper() or "USDT"
    if locale == "en":
        return [
            (f"By {base} size", "cl:qty:base"),
            (f"By {quote} amount", "cl:qty:quote"),
        ]
    if locale == "zh-Hant":
        return [
            (f"按 {base} 數量", "cl:qty:base"),
            (f"按 {quote} 金額", "cl:qty:quote"),
        ]
    return [
        (f"按 {base} 数量", "cl:qty:base"),
        (f"按 {quote} 金额", "cl:qty:quote"),
    ]


def build_clarify_inline_keyboard(
    *,
    kind: ClarifyKeyboardKind,
    effective_locale: str | None = None,
    base_asset: str | None = None,
    quote_asset: str | None = None,
) -> dict[str, Any]:
    """Returns OpenAPI-shaped ``ClarifyInlineKeyboard`` as plain dict."""
    locale = _normalize_locale(effective_locale)
    if kind == "spot_qty_mode":
        buttons = build_spot_qty_mode_labels(
            base_asset=base_asset,
            quote_asset=quote_asset,
            locale=locale,
        )
    else:
        buttons = list(_LABELS[kind][locale])
    row = [{"text": text, "callback_data": cd} for text, cd in buttons]
    return {
        "kind": kind,
        "effectiveLocale": locale,
        "rows": [row],
    }


def clarify_inline_keyboard_to_reply_markup(keyboard: dict[str, Any]) -> dict[str, Any]:
    rows = keyboard.get("rows") or []
    inline = [
        [{"text": btn["text"], "callback_data": btn["callback_data"]} for btn in row]
        for row in rows
    ]
    return {"inline_keyboard": inline}


_READ_LABELS: dict[ReadClarifyKeyboardKind, dict[EffectiveLocale, list[tuple[str, str]]]] = {
    "read_scope_portfolio_vs_market": {
        "zh-Hans": [
            ("看全市场", "rc:scope:market"),
            ("看我的持仓", "rc:scope:portfolio"),
            ("不问了", "rc:cancel"),
        ],
        "zh-Hant": [
            ("看全市場", "rc:scope:market"),
            ("看我的持倉", "rc:scope:portfolio"),
            ("不問了", "rc:cancel"),
        ],
        "en": [
            ("Market overview", "rc:scope:market"),
            ("My positions", "rc:scope:portfolio"),
            ("Cancel", "rc:cancel"),
        ],
    },
    "read_multi_symbol": {
        "zh-Hans": [("BTC", "rc:sym:BTC"), ("ETH", "rc:sym:ETH"), ("不问了", "rc:cancel")],
        "zh-Hant": [("BTC", "rc:sym:BTC"), ("ETH", "rc:sym:ETH"), ("不問了", "rc:cancel")],
        "en": [("BTC", "rc:sym:BTC"), ("ETH", "rc:sym:ETH"), ("Cancel", "rc:cancel")],
    },
    "read_monitoring_asset_class": {
        "zh-Hans": [("现货提醒", "rc:mon:spot"), ("合约提醒", "rc:mon:fut"), ("不问了", "rc:cancel")],
        "zh-Hant": [("現貨提醒", "rc:mon:spot"), ("合約提醒", "rc:mon:fut"), ("不問了", "rc:cancel")],
        "en": [("Spot alert", "rc:mon:spot"), ("Futures alert", "rc:mon:fut"), ("Cancel", "rc:cancel")],
    },
}


def build_read_clarify_inline_keyboard(
    *,
    kind: ReadClarifyKeyboardKind,
    effective_locale: str | None = None,
) -> dict[str, Any]:
    locale = _normalize_locale(effective_locale)
    buttons = list(_READ_LABELS[kind][locale])
    row = [{"text": text, "callback_data": cd} for text, cd in buttons]
    return {
        "kind": kind,
        "effectiveLocale": locale,
        "rows": [row],
    }


def clarify_callback_data_within_limit(data: str) -> bool:
    return len(data.encode("utf-8")) <= 64
