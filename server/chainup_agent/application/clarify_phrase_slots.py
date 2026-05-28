"""Map short user phrases to clarify slot merges (keyboard ``cl:*`` equivalents)."""

from __future__ import annotations

import re

from chainup_agent.application.memory_session_store import merge_clarify_slot_dict

_FLASH_RE = re.compile(
    r"闪[兑隊队]|^市价$|^当前市价$|市价买入|市价卖出|market\s*price",
    re.IGNORECASE,
)
_LIMIT_RE = re.compile(r"限价|挂单|limit\s*order", re.IGNORECASE)
_BUY_RE = re.compile(r"^买入$|^买$|buy", re.IGNORECASE)
_SELL_RE = re.compile(r"^卖出$|^卖$|sell", re.IGNORECASE)

_MAX_PHRASE_LEN = 48


def merge_clarify_phrase_slots(
    text: str,
    slots: dict[str, str] | None,
) -> dict[str, str]:
    """
    Text equivalents of ``cl:fc`` / ``cl:lo`` / ``cl:buy`` / ``cl:sell`` for multi-turn clarify.
    Only applies to short replies (not full new intents).
    """
    raw = text.strip()
    out = dict(slots or {})
    if not raw or len(raw) > _MAX_PHRASE_LEN:
        return out

    extra: dict[str, str] = {}
    has_limit = bool(_LIMIT_RE.search(raw))
    has_flash = bool(_FLASH_RE.search(raw)) and not has_limit

    if has_flash:
        extra["tradeMode"] = "flash_convert"
        extra["type"] = "MARKET"
    elif has_limit:
        extra["tradeMode"] = "limit_order"
        extra["type"] = "LIMIT"

    if _BUY_RE.match(raw):
        extra["side"] = "BUY"
    elif _SELL_RE.match(raw):
        extra["side"] = "SELL"

    if not extra:
        return out
    return merge_clarify_slot_dict(out, extra)


def resolve_spot_trade_scenario_from_slots(slots: dict[str, str]) -> str | None:
    mode = (slots.get("tradeMode") or "").strip()
    if mode == "flash_convert":
        return "trade.spot.flash_convert"
    if mode == "limit_order":
        return "trade.spot.limit_order"
    return None
