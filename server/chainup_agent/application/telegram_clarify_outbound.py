"""Infer clarify keyboards + outbound hints for Telegram CLARIFY turns."""

from __future__ import annotations

from typing import Any

from chainup_agent.application.clarify_session import get_clarify_session_raw
from chainup_agent.application.trade_slot_clarify import (
    has_qty_or_quote,
    split_spot_pair_assets,
)
from chainup_agent.application.read_clarify_session import get_read_clarify_session
from chainup_agent.application.telegram_clarify_keyboard import (
    ClarifyKeyboardKind,
    ReadClarifyKeyboardKind,
    build_clarify_inline_keyboard,
    build_read_clarify_inline_keyboard,
    clarify_inline_keyboard_to_reply_markup,
)
from chainup_agent.core.config import Settings


def _symbol_label(slots: dict[str, str]) -> str | None:
    sym = (slots.get("symbol") or "").strip()
    if sym:
        base, _ = split_spot_pair_assets(sym)
        return base or sym.split("-")[0].split("/")[0]
    base = (slots.get("baseAsset") or "").strip()
    return base.upper() if base else None


def infer_clarify_keyboard_kind(
    *,
    scenario_id: str | None,
    slots: dict[str, str],
    policy_codes: list[str] | None,
    session_id: str | None = None,
    settings: Settings,
) -> ClarifyKeyboardKind | None:
    """Map resolver/policy state → keyboard kind (telegram/overview §2.3.2)."""
    codes = set(policy_codes or [])
    s = {k: str(v) for k, v in slots.items() if v is not None and str(v).strip()}

    snap = get_clarify_session_raw(session_id or "") if session_id else None
    if snap and snap.lifecycle_state == "stale":
        if settings.stm_idle_default_policy == "prompt_resume_or_new":
            return "idle_resume_or_new"
        return None

    if "QUOTE_PAIR_NOT_FROZEN" in codes:
        return "confirm_symbol_default"

    sid = (scenario_id or "").strip()
    if sid.startswith("trade.spot"):
        mode = (s.get("tradeMode") or "").strip()
        if s.get("side") and (s.get("symbol") or s.get("baseAsset")):
            if mode in ("flash_convert", "limit_order"):
                if not has_qty_or_quote(s) and not s.get("notionalMode"):
                    return "spot_qty_mode"
            else:
                return "spot_trade_mode"
        if (s.get("symbol") or s.get("baseAsset")) and not s.get("side"):
            return "spot_side"

    label = _symbol_label(s)
    if label and not s.get("side") and sid.startswith("trade."):
        return "spot_side"
    if label and s.get("side") and sid.startswith("trade.spot") and not s.get("tradeMode"):
        return "spot_trade_mode"
    _ = label
    return None


def build_clarify_reply_markup(
    *,
    scenario_id: str | None,
    slots: dict[str, str],
    policy_codes: list[str] | None,
    effective_locale: str | None,
    session_id: str | None,
    settings: Settings,
) -> dict[str, Any] | None:
    kind = infer_clarify_keyboard_kind(
        scenario_id=scenario_id,
        slots=slots,
        policy_codes=policy_codes,
        session_id=session_id,
        settings=settings,
    )
    if kind is None:
        return None
    sym = (slots.get("symbol") or "").strip()
    base_a, quote_a = split_spot_pair_assets(sym) if sym else (None, None)
    if not base_a:
        base_a = slots.get("baseAsset")
    keyboard = build_clarify_inline_keyboard(
        kind=kind,
        effective_locale=effective_locale,
        base_asset=base_a,
        quote_asset=quote_a,
    )
    return clarify_inline_keyboard_to_reply_markup(keyboard)


_READ_CLARIFY_BODY: dict[str, str] = {
    "scope_portfolio_vs_market": "你想看全市场行情，还是你自己的持仓盈亏？",
    "multi_symbol_compare": "你想先比较 BTC 还是 ETH？点选后继续。",
    "monitoring_asset_class": "这是现货还是合约的到价提醒？",
}


def infer_read_clarify_keyboard_kind(
    pending_kind: str | None,
) -> ReadClarifyKeyboardKind | None:
    kind = (pending_kind or "").strip()
    if kind == "scope_portfolio_vs_market":
        return "read_scope_portfolio_vs_market"
    if kind == "multi_symbol_compare":
        return "read_multi_symbol"
    if kind in ("monitoring_asset_class", "monitoring_draft"):
        return "read_monitoring_asset_class"
    return None


def build_read_clarify_reply_markup(
    *,
    pending_kind: str | None,
    effective_locale: str | None,
) -> dict[str, Any] | None:
    rk = infer_read_clarify_keyboard_kind(pending_kind)
    if rk is None:
        return None
    keyboard = build_read_clarify_inline_keyboard(kind=rk, effective_locale=effective_locale)
    return clarify_inline_keyboard_to_reply_markup(keyboard)


def read_clarify_outbound_body(pending_kind: str | None) -> str:
    return _READ_CLARIFY_BODY.get(
        (pending_kind or "").strip(),
        "请点选下方选项，或直接用一句话说明你想查什么。",
    )


def try_read_clarify_telegram_reply(
    *,
    session_id: str,
    effective_locale: str | None,
) -> tuple[str, dict[str, Any] | None] | None:
    """When ReadClarifySession is active, return scope/symbol keyboard outbound."""
    snap = get_read_clarify_session(session_id)
    if snap is None:
        return None
    kind = snap.pending_read_clarify_kind
    markup = build_read_clarify_reply_markup(
        pending_kind=kind,
        effective_locale=effective_locale,
    )
    if markup is None:
        return None
    return read_clarify_outbound_body(kind), markup
