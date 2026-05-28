"""User-visible clarify guards — abandon/read interrupt, jargon filter, outbound dedupe."""

from __future__ import annotations

import re
from typing import Literal

_ABANDON_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"不买了|取消|算了|都不要了|先不买了|不用了", re.IGNORECASE),
)

_READ_INTERRUPT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"只查价|先看看行情|有哪些币可以买|多少钱", re.IGNORECASE),
    re.compile(r"^(?:查|看).*(?:价|行情|余额|持仓)", re.IGNORECASE),
)

_GREETING_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^(?:你好|您好|在吗|hi|hello)\b", re.IGNORECASE),
    re.compile(r"你能做什么|你会什么", re.IGNORECASE),
)

_WRITE_INTENT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"买入|买进|卖出|卖掉|下单|闪兑|限价|开仓|平仓", re.IGNORECASE),
)

_INTERNAL_JARGON = re.compile(
    r"routingHints|orchestrationNextSteps|scenarioId|写路径|INV-\d+|FR-T\d+|"
    r"call_exchange_write|Parser|Gateway|provenance|多主场景|须澄清后再路由",
    re.IGNORECASE,
)

_WHITESPACE_COLLAPSE = re.compile(r"\s+")


def classify_clarify_inbound(text: str) -> Literal[
    "write_followup", "abandon", "read_interrupt", "greeting", "chitchat"
]:
    """clarify-session §2.3 step 2～3 — coarse inbound routing while clarify active."""
    raw = text.strip()
    if not raw:
        return "write_followup"
    if any(p.search(raw) for p in _ABANDON_PATTERNS):
        if not any(p.search(raw) for p in _WRITE_INTENT_PATTERNS):
            return "abandon"
    if any(p.search(raw) for p in _READ_INTERRUPT_PATTERNS):
        if not any(p.search(raw) for p in _WRITE_INTENT_PATTERNS):
            return "read_interrupt"
    if any(p.search(raw) for p in _GREETING_PATTERNS):
        if not any(p.search(raw) for p in _WRITE_INTENT_PATTERNS):
            return "greeting"
    return "write_followup"


def strip_internal_jargon_from_outbound(text: str) -> str:
    """SC-CLARIFY-09 — remove known internal tokens from user-visible body."""
    if not text or not _INTERNAL_JARGON.search(text):
        return text
    lines = []
    for line in text.splitlines():
        if _INTERNAL_JARGON.search(line):
            continue
        lines.append(line)
    cleaned = "\n".join(lines).strip()
    return cleaned or "请补充一下你的需求。"


def normalize_outbound_for_dedupe(text: str) -> str:
    """§2.5 — trim + collapse whitespace for repeat-outbound compare."""
    t = text.strip()
    t = _WHITESPACE_COLLAPSE.sub(" ", t)
    return t.rstrip("。！？.!? ")


def outbound_would_repeat(
    *,
    previous_outbound: str | None,
    candidate_outbound: str,
    inbound_changed: bool,
) -> bool:
    if not previous_outbound or not inbound_changed:
        return False
    return normalize_outbound_for_dedupe(previous_outbound) == normalize_outbound_for_dedupe(
        candidate_outbound
    )


def human_summary_resolved_slots(slots: dict[str, str]) -> str:
    """STM inject — SC-CLARIFY-03."""
    if not slots:
        return ""
    parts: list[str] = []
    side = slots.get("side", "").upper()
    if side == "BUY":
        parts.append("买入")
    elif side == "SELL":
        parts.append("卖出")
    sym = slots.get("symbol") or slots.get("baseAsset") or ""
    if sym:
        parts.append(str(sym).replace("-", "/"))
    mode = slots.get("tradeMode", "")
    if mode == "flash_convert":
        parts.append("闪兑")
    elif mode == "limit_order":
        parts.append("限价")
    if slots.get("quoteQty"):
        parts.append(f"金额 {slots['quoteQty']}")
    elif slots.get("quantity"):
        parts.append(f"数量 {slots['quantity']}")
    return "已确认：" + " · ".join(parts) if parts else ""
