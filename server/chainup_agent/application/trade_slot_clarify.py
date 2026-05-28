"""
S11-style trade slot clarification — rule-based messages; optional LLM polish in ``agent_llm_clarify``.

Covers spot flash/limit, margin cross, futures; pair/quote freeze; quantity|quoteQty; notional resolve.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_api_binding_confirm import (
    decrypt_binding_trade_credentials_for_row,
)
from chainup_agent.application.agent_routing_exchange_read import (
    load_binding_row_for_telegram_user,
)
from chainup_agent.application.agent_spot_trade import spot_quote_for_bound_user
from chainup_agent.application.telegram_symbol_extract import extract_symbol_for_ticker
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.domain.canonical_trading import instrument_ref_from_sym_ticker
from chainup_agent.infrastructure.exchange.coobit_openapi import (
    fetch_signed_spot_account_json,
)

_PAIR_SEP = re.compile(
    r"\b([A-Z0-9]{2,15})[-_/](USDT|USDC|BTC|ETH|TRY|EUR|USD|BUSD)\b",
    re.IGNORECASE,
)

_AFFIRM_QUOTE_FROZEN = re.compile(
    r"^(?:是|对|嗯|好|可以|确认|ok|yes|y|就用usdt|usdt计价)$",
    re.IGNORECASE,
)

_ALL_QUOTE_BUY = re.compile(
    r"全部(?:买入|买进|买|购入)|全(?:部)?(?:仓)?买|all\s*in\s*(?:买|buy)?",
    re.IGNORECASE,
)
_ALL_BASE_SELL = re.compile(
    r"全部(?:卖出|卖出|卖|抛售)|全(?:部)?(?:仓)?卖",
    re.IGNORECASE,
)
_PERCENT = re.compile(
    r"(?:余额的|可用的|可用余额的)?\s*(\d+(?:\.\d+)?)\s*%|百分之\s*(\d+(?:\.\d+)?)",
)


def split_spot_pair_assets(symbol: str) -> tuple[str | None, str | None]:
    raw = (symbol or "").strip().upper().replace("/", "-")
    if not raw or "-" not in raw:
        return None, None
    try:
        ref = instrument_ref_from_sym_ticker(raw)
    except ValueError:
        return None, None
    return ref.base_asset, ref.quote_asset


def text_has_explicit_spot_pair(text: str) -> bool:
    upper = text.upper()
    if _PAIR_SEP.search(upper):
        return True
    compact = re.sub(r"\s+", "", upper)
    for q in ("USDT", "USDC", "BTC", "ETH"):
        if re.search(rf"\b[A-Z][A-Z0-9]{{1,14}}{q}\b", compact):
            return True
    return False


def text_mentions_quote_currency(text: str) -> bool:
    return bool(
        re.search(
            r"USDT|USDC|U\b|美元|块钱|计价",
            text,
            re.IGNORECASE,
        )
    )


def lone_base_inferred_pair(text: str, symbol: str | None) -> bool:
    """Symbol came from lone-base default (e.g. BCH → BCH-USDT) without explicit pair in text."""
    if not symbol:
        return False
    if text_has_explicit_spot_pair(text):
        return False
    base, _ = split_spot_pair_assets(symbol)
    if not base:
        return False
    return bool(re.search(rf"\b{re.escape(base)}\b", text.upper()))


def extract_quote_qty_from_text(text: str) -> str | None:
    m = re.search(
        r"(?:花费|用|出|买)\s*(\d+(?:\.\d+)?)\s*(?:U|USDT|USDC|美元|块)?",
        text,
        re.IGNORECASE,
    )
    if m:
        return m.group(1)
    m = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:U|USDT|USDC|美元|块)\b",
        text,
        re.IGNORECASE,
    )
    if m:
        return m.group(1)
    return None


def extract_balance_percent(text: str) -> str | None:
    m = _PERCENT.search(text)
    if not m:
        return None
    return m.group(1) or m.group(2)


def extract_notional_mode(text: str, side: str | None) -> str | None:
    """``all_quote`` | ``all_base`` | ``percent`` (needs percent slot)."""
    if _ALL_QUOTE_BUY.search(text):
        return "all_quote"
    if _ALL_BASE_SELL.search(text):
        return "all_base"
    if extract_balance_percent(text):
        return "percent"
    if side == "BUY" and re.search(r"全部|全仓|all\s*in", text, re.IGNORECASE):
        return "all_quote"
    if side == "SELL" and re.search(r"全部|全仓", text, re.IGNORECASE):
        return "all_base"
    return None


def enrich_trade_slots_from_text(text: str, slots: dict[str, str]) -> dict[str, str]:
    """Deterministic slot enrichment for trade clarify / notional (merge into NLU slots)."""
    out = dict(slots)
    if _AFFIRM_QUOTE_FROZEN.match(text.strip()):
        out["quoteNotionalFrozen"] = "yes"
    if "quoteQty" not in out:
        qq = extract_quote_qty_from_text(text)
        if qq:
            out["quoteQty"] = qq
    side = out.get("side")
    mode = extract_notional_mode(text, side)
    if mode and "notionalMode" not in out:
        out["notionalMode"] = mode
    pct = extract_balance_percent(text)
    if pct and "balancePercent" not in out:
        out["balancePercent"] = pct
    return out


def has_qty_or_quote(slots: dict[str, str]) -> bool:
    q = (slots.get("quantity") or "").strip()
    qq = (slots.get("quoteQty") or "").strip()
    return bool(q or qq)


def flash_slots_complete(slots: dict[str, str]) -> bool:
    return bool(
        (slots.get("symbol") or "").strip()
        and (slots.get("side") or "").strip()
        and has_qty_or_quote(slots)
        and not (slots.get("price") or "").strip()
    )


def limit_slots_complete(slots: dict[str, str]) -> bool:
    return bool(
        (slots.get("symbol") or "").strip()
        and (slots.get("side") or "").strip()
        and (slots.get("price") or "").strip()
        and has_qty_or_quote(slots)
    )


def needs_quote_pair_clarify(text: str, slots: dict[str, str]) -> bool:
    if slots.get("quoteNotionalFrozen") == "yes":
        return False
    if has_qty_or_quote(slots):
        return False
    if not lone_base_inferred_pair(text, slots.get("symbol")):
        return False
    if text_mentions_quote_currency(text):
        return False
    return True


def build_quote_pair_clarify_line(slots: dict[str, str]) -> str:
    sym = (slots.get("symbol") or "该交易对").strip()
    base, quote = split_spot_pair_assets(sym)
    pair = sym if sym else f"{base}-{quote or 'USDT'}"
    q = quote or "USDT"
    return (
        f"是否使用 `{pair}`，并以 **{q}** 作为花费/成交额计价？"
        f"回复「是」继续，或直接说明交易对与数量（如「{pair} 用 100 {q} 买入」）。"
    )


def build_flash_clarify_lines(text: str, slots: dict[str, str]) -> list[str]:
    lines: list[str] = []
    if needs_quote_pair_clarify(text, slots):
        lines.append(build_quote_pair_clarify_line(slots))
    if not (slots.get("symbol") or "").strip():
        lines.append("请说明交易对（如 BCH-USDT、BTC-USDT）。")
    if not (slots.get("side") or "").strip():
        lines.append("请说明买入还是卖出。")
    if (
        (slots.get("symbol") or "").strip()
        and (slots.get("side") or "").strip()
        and not has_qty_or_quote(slots)
        and not slots.get("notionalMode")
    ):
        lines.append(
            "请说明数量：币的数量（如 0.01 BCH）、花费的 USDT（如 100 USDT），"
            "或「全部买入/全部卖出」/「余额的 50%」。"
        )
    if slots.get("price"):
        lines.append("闪兑为市价，请勿附带限价；若要挂单请说「限价」。")
    return lines


def build_limit_clarify_lines(text: str, slots: dict[str, str]) -> list[str]:
    lines: list[str] = []
    if needs_quote_pair_clarify(text, slots):
        lines.append(build_quote_pair_clarify_line(slots))
    if not (slots.get("symbol") or "").strip():
        lines.append("请说明交易对（如 BTC-USDT）。")
    if not (slots.get("side") or "").strip():
        lines.append("请说明买入还是卖出。")
    if not (slots.get("price") or "").strip():
        lines.append("请说明限价（具体价格数字）。")
    if (
        (slots.get("symbol") or "").strip()
        and (slots.get("side") or "").strip()
        and (slots.get("price") or "").strip()
        and not has_qty_or_quote(slots)
    ):
        lines.append(
            "请说明数量：标的币数量，或花费/成交的 USDT 金额（如 100 USDT）；"
            "不够明确将不会猜测下单。"
        )
    return lines


def flash_needs_notional_resolve(slots: dict[str, str]) -> bool:
    if not (slots.get("symbol") and slots.get("side")):
        return False
    if has_qty_or_quote(slots):
        return False
    return bool(slots.get("notionalMode") or slots.get("balancePercent"))


def _decimal_free_balance(items: list[dict[str, str]], asset: str) -> Decimal | None:
    want = asset.strip().upper()
    for row in items:
        if str(row.get("asset", "")).upper() != want:
            continue
        try:
            free = Decimal(str(row.get("free", "0")).strip())
        except InvalidOperation:
            continue
        return free
    return Decimal("0")


async def _fetch_spot_balance_items(
    session: AsyncSession,
    settings: Settings,
    telegram_user_id: int,
) -> list[dict[str, str]]:
    row = await load_binding_row_for_telegram_user(session, telegram_user_id)
    if row is None:
        raise AppError(
            code="AGENT_SUBACCOUNT_REQUIRED",
            message="未发现该 Telegram 用户的托管 API 绑定，请先完成 Deeplink 校验与绑定。",
            status_code=403,
        )
    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)
    raw = await fetch_signed_spot_account_json(
        openapi_base_url=openapi_base,
        api_key=ak,
        secret_key=sk,
    )
    balances = raw.get("balances") if isinstance(raw, dict) else None
    if not isinstance(balances, list):
        return []
    items: list[dict[str, str]] = []
    for b in balances[:64]:
        if not isinstance(b, dict):
            continue
        asset = str(b.get("asset", "")).strip().upper()
        if not asset:
            continue
        items.append(
            {
                "asset": asset,
                "free": str(b.get("free", "0"))[:64],
                "locked": str(b.get("locked", "0"))[:64],
            }
        )
    return items


def _base_qty_from_quote_amount(*, quote_amount: Decimal, last_price: Decimal) -> str:
    if last_price <= 0:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="行情缺少有效最新价，无法按 USDT 金额换算买入数量",
            status_code=502,
        )
    base = (quote_amount / last_price).quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
    if base <= 0:
        raise AppError(
            code="VALIDATION_ERROR",
            message="换算后的买入数量过小，请减少花费或稍后重试",
            status_code=422,
        )
    return format(base, "f").rstrip("0").rstrip(".") or "0"


async def resolve_flash_notional_slots(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    slots: dict[str, str],
) -> tuple[dict[str, str], str | None]:
    """
    Fill ``quantity`` (base) from balance + notionalMode / balancePercent / quoteQty.

    Returns (updated_slots, user_visible_error).
    """
    sym = (slots.get("symbol") or "").strip()
    side = (slots.get("side") or "").strip().upper()
    if not sym or side not in ("BUY", "SELL"):
        return slots, "闪兑参数不完整，请补充交易对与买卖方向。"

    base_a, quote_a = split_spot_pair_assets(sym)
    if not base_a or not quote_a:
        return slots, "无法解析交易对，请使用如 BCH-USDT 的格式。"

    out = dict(slots)
    tg = int(user_id)
    items = await _fetch_spot_balance_items(session, settings, tg)

    mode = (out.get("notionalMode") or "").strip()
    pct_raw = (out.get("balancePercent") or "").strip()
    quote_qty_raw = (out.get("quoteQty") or "").strip()

    try:
        if side == "BUY":
            quote_free = _decimal_free_balance(items, quote_a) or Decimal("0")
            spend: Decimal | None = None
            if quote_qty_raw:
                spend = Decimal(quote_qty_raw)
            elif mode == "all_quote":
                spend = quote_free
            elif mode == "percent" and pct_raw:
                spend = quote_free * (Decimal(pct_raw) / Decimal(100))
            if spend is None:
                return out, (
                    f"请说明买入数量，或花费多少 {quote_a}，"
                    f"或说「全部买入」/「余额的 xx%」。"
                )
            if spend <= 0:
                return (
                    out,
                    f"可用 {quote_a} 不足，无法按您的描述买入。"
                    f"当前可用约 0；请充值或改说具体数量。",
                )
            qp = await spot_quote_for_bound_user(
                session=session,
                settings=settings,
                user_id=user_id,
                symbol=sym,
            )
            prev = qp.get("quotePreview") if isinstance(qp.get("quotePreview"), dict) else {}
            lp = last_price_decimal_from_ticker_preview(prev)
            if lp is None:
                raise AppError(
                    code="AGENT_OPENAPI_PROBE_FAILED",
                    message="行情缺少有效最新价，无法按 USDT 金额换算买入数量",
                    status_code=502,
                )
            out["quantity"] = _base_qty_from_quote_amount(quote_amount=spend, last_price=lp)
            out.pop("quoteQty", None)
            out.pop("notionalMode", None)
            out.pop("balancePercent", None)
            return out, None

        base_free = _decimal_free_balance(items, base_a) or Decimal("0")
        qty: Decimal | None = None
        if (out.get("quantity") or "").strip():
            qty = Decimal(str(out["quantity"]).strip())
        elif mode == "all_base":
            qty = base_free
        elif mode == "percent" and pct_raw:
            qty = base_free * (Decimal(pct_raw) / Decimal(100))
        if qty is None:
            return out, (
                f"请说明卖出数量，或说「全部卖出 {base_a}」/「余额的 xx%」。"
            )
        if qty <= 0:
            return (
                out,
                f"可用 {base_a} 不足，无法按您的描述卖出。"
                f"请充值或改说具体数量。",
            )
        out["quantity"] = format(qty, "f").rstrip("0").rstrip(".") or "0"
        out.pop("notionalMode", None)
        out.pop("balancePercent", None)
        return out, None
    except AppError as exc:
        return out, exc.message
    except (InvalidOperation, ValueError):
        return out, "数量格式无效，请用数字说明买入或卖出数量。"


def quote_qty_to_base_quantity(
    *,
    quote_qty: str,
    last_price: Decimal,
) -> str:
    return _base_qty_from_quote_amount(quote_amount=Decimal(quote_qty.strip()), last_price=last_price)


def infer_symbol_for_clarify(text: str) -> str | None:
    return extract_symbol_for_ticker(text)


def last_price_decimal_from_ticker_preview(prev: dict[str, Any]) -> Decimal | None:
    for key in ("lastPrice", "last", "closePrice"):
        v = prev.get(key)
        if v is None:
            continue
        try:
            d = Decimal(str(v).strip())
        except InvalidOperation:
            continue
        if d > 0:
            return d
    return None


def quote_qty_to_base_at_limit_price(*, quote_qty: str, limit_price: Decimal) -> str:
    return _base_qty_from_quote_amount(quote_amount=Decimal(quote_qty.strip()), last_price=limit_price)


_FUTURES_NOMINAL_U = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:U|USDT)\b",
    re.IGNORECASE,
)


def needs_futures_nominal_clarify(text: str, slots: dict[str, str]) -> bool:
    """「100U 开多」类：有 U 口径但无明确 quantity/quoteQty 分拆。"""
    if has_qty_or_quote(slots):
        return False
    if not _FUTURES_NOMINAL_U.search(text):
        return False
    if re.search(r"开仓|平仓|开多|开空|做多|做空", text):
        return True
    return bool(slots.get("side"))


def build_futures_nominal_clarify_line() -> str:
    return (
        "请确认数量口径：是 **合约张数/币数**，还是 **USDT 名义仓位**？"
        "请直接说明，例如「0.1 BTC 开多」或「用 100 USDT 名义开多」。"
    )


def margin_market_slots_complete(slots: dict[str, str]) -> bool:
    return bool(
        (slots.get("symbol") or "").strip()
        and (slots.get("side") or "").strip()
        and has_qty_or_quote(slots)
        and not (slots.get("price") or "").strip()
    )


def margin_limit_slots_complete(slots: dict[str, str]) -> bool:
    return limit_slots_complete(slots)


def futures_market_slots_complete(slots: dict[str, str]) -> bool:
    return bool(
        (slots.get("symbol") or "").strip()
        and (slots.get("side") or "").strip()
        and has_qty_or_quote(slots)
        and not (slots.get("price") or "").strip()
    )


def futures_limit_slots_complete(slots: dict[str, str]) -> bool:
    return bool(
        (slots.get("symbol") or "").strip()
        and (slots.get("side") or "").strip()
        and (slots.get("price") or "").strip()
        and has_qty_or_quote(slots)
    )


def build_margin_market_clarify_lines(text: str, slots: dict[str, str]) -> list[str]:
    lines = build_flash_clarify_lines(text, slots)
    if "全仓" in text or "杠杆" in text:
        lines.append("当前为全仓杠杆市价路径；请确认数量或 USDT 花费口径。")
    return _dedupe_lines(lines)


def build_margin_limit_clarify_lines(text: str, slots: dict[str, str]) -> list[str]:
    return build_limit_clarify_lines(text, slots)


def build_futures_market_clarify_lines(text: str, slots: dict[str, str]) -> list[str]:
    lines: list[str] = []
    if not (slots.get("symbol") or "").strip():
        lines.append("请说明合约标的（如 BTC-USDT）。")
    if not (slots.get("side") or "").strip():
        lines.append("请说明方向（开多/开空/买入/卖出）。")
    if needs_futures_nominal_clarify(text, slots):
        lines.append(build_futures_nominal_clarify_line())
    elif (
        (slots.get("symbol") or "").strip()
        and (slots.get("side") or "").strip()
        and not has_qty_or_quote(slots)
        and not slots.get("notionalMode")
    ):
        lines.append("请说明下单数量（张数/币量），或 USDT 名义并写清口径。")
    if slots.get("price"):
        lines.append("永续市价不需要限价；若要挂单请说「限价」。")
    return lines


def build_futures_limit_clarify_lines(text: str, slots: dict[str, str]) -> list[str]:
    lines: list[str] = []
    if not (slots.get("symbol") or "").strip():
        lines.append("请说明合约标的（如 BTC-USDT）。")
    if not (slots.get("side") or "").strip():
        lines.append("请说明方向（买/卖）。")
    if not (slots.get("price") or "").strip():
        lines.append("请说明限价（具体价格数字）。")
    if needs_futures_nominal_clarify(text, slots):
        lines.append(build_futures_nominal_clarify_line())
    elif (
        (slots.get("symbol") or "").strip()
        and (slots.get("side") or "").strip()
        and (slots.get("price") or "").strip()
        and not has_qty_or_quote(slots)
    ):
        lines.append("请说明数量或 USDT 名义（须写清是仓位名义还是保证金）。")
    return lines


def _dedupe_lines(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for ln in lines:
        if ln in seen:
            continue
        seen.add(ln)
        out.append(ln)
    return out


def trade_needs_notional_resolve(scenario_id: str, slots: dict[str, str]) -> bool:
    if scenario_id in ("trade.spot.flash_convert", "margin.cross.market_order"):
        return flash_needs_notional_resolve(slots)
    return False


SCENARIOS_USING_SPOT_NOTIONAL_RESOLVE = frozenset(
    {"trade.spot.flash_convert", "margin.cross.market_order"}
)


@dataclass(frozen=True)
class TradeWriteClarifyDecision:
    next_step: Literal["CLARIFY", "CONFIRM_TYPE_A", "RESOLVE_TRADE_NOTIONAL"]
    clarify: tuple[str, ...]
    policy_codes: tuple[str, ...]
    note: str


def evaluate_trade_write_clarify(
    scenario_id: str,
    text: str,
    slots: dict[str, str],
    *,
    base_policy_codes: list[str] | None = None,
) -> TradeWriteClarifyDecision:
    """Unified S11 policy for spot flash/limit, margin cross, futures market/limit."""
    codes = list(base_policy_codes or [])
    s = {k: str(v) for k, v in slots.items()}

    builders: dict[str, Any] = {
        "trade.spot.flash_convert": (build_flash_clarify_lines, flash_slots_complete),
        "trade.spot.limit_order": (build_limit_clarify_lines, limit_slots_complete),
        "margin.cross.market_order": (build_margin_market_clarify_lines, margin_market_slots_complete),
        "margin.cross.limit_order": (build_margin_limit_clarify_lines, margin_limit_slots_complete),
        "trade.futures.market_order": (build_futures_market_clarify_lines, futures_market_slots_complete),
        "trade.futures.limit_order": (build_futures_limit_clarify_lines, futures_limit_slots_complete),
    }
    pair = builders.get(scenario_id)
    if pair is None:
        return TradeWriteClarifyDecision(
            next_step="CONFIRM_TYPE_A",
            clarify=(),
            policy_codes=tuple(codes),
            note="未注册 clarify 分支，按可执行处理。",
        )

    build_lines, is_complete = pair
    clarify_lines = build_lines(text, s)
    if needs_quote_pair_clarify(text, s):
        codes.append("QUOTE_PAIR_NOT_FROZEN")
    if needs_futures_nominal_clarify(text, s) and scenario_id.startswith("trade.futures"):
        codes.append("FUTURES_NOMINAL_AMBIGUOUS")

    if clarify_lines or not is_complete(s):
        if not needs_quote_pair_clarify(text, s) and trade_needs_notional_resolve(
            scenario_id, s
        ):
            return TradeWriteClarifyDecision(
                next_step="RESOLVE_TRADE_NOTIONAL",
                clarify=tuple(clarify_lines),
                policy_codes=tuple(codes or ["TRADE_NOTIONAL_PENDING"]),
                note="须只读现货余额换算数量；禁止猜测 quantity/quoteQty。",
            )
        return TradeWriteClarifyDecision(
            next_step="CLARIFY",
            clarify=tuple(clarify_lines)
            or ("请补充交易参数后再继续。",),
            policy_codes=tuple(codes or ["SLOT_TRADE_INCOMPLETE"]),
            note="写路径禁止猜测缺失字段；信息不足仅澄清。",
        )

    if trade_needs_notional_resolve(scenario_id, s):
        return TradeWriteClarifyDecision(
            next_step="RESOLVE_TRADE_NOTIONAL",
            clarify=tuple(clarify_lines),
            policy_codes=tuple(codes or ["TRADE_NOTIONAL_PENDING"]),
            note="须只读现货余额换算数量；禁止猜测 quantity/quoteQty。",
        )

    notes = {
        "trade.spot.flash_convert": "槽位齐全：闪兑须类型 A 确认后再写。",
        "trade.spot.limit_order": "槽位齐全：限价单须类型 A 确认后再写。",
        "margin.cross.market_order": "槽位齐全：全仓杠杆市价须双次类型 A 确认后再写。",
        "margin.cross.limit_order": "槽位齐全：全仓杠杆限价须双次类型 A 确认后再写。",
        "trade.futures.market_order": "槽位齐全：合约市价须类型 A 确认后再写。",
        "trade.futures.limit_order": "槽位齐全：合约限价须类型 A 确认后再写。",
    }
    return TradeWriteClarifyDecision(
        next_step="CONFIRM_TYPE_A",
        clarify=(),
        policy_codes=tuple(codes),
        note=notes.get(scenario_id, "槽位齐全：须类型 A 确认后再写。"),
    )


# Back-compat alias for Telegram / tests
resolve_trade_notional_slots = resolve_flash_notional_slots
