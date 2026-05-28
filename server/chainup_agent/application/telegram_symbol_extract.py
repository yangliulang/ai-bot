"""Extract Coobit spot symbol hints from Telegram user text (keywords router companion)."""

from __future__ import annotations

import re

from chainup_agent.infrastructure.exchange.coobit_openapi import normalize_coobit_spot_symbol_param

# Avoid ``\b`` before BASE — CJK text (e.g. 今天BTC-USDT) is "word" in Unicode and blocks ``\b``.
_PAIR_SEP = re.compile(
    r"(?<![A-Z0-9])([A-Z0-9]{2,15})[-_/](USDT|USDC|BTC|ETH|TRY|EUR|USD|BUSD)(?![A-Z0-9])",
    re.IGNORECASE,
)

_KNOWN_BASES = (
    "BTC",
    "ETH",
    "BCH",
    "SOL",
    "BNB",
    "XRP",
    "DOGE",
    "ADA",
    "TRX",
    "LTC",
    "DOT",
    "MATIC",
    "POL",
)


def extract_symbol_for_ticker(text: str) -> str | None:
    """
    Best-effort trading pair for ``read.market.ticker``.

    Accepts explicit ``BASE-QUOTE`` / ``BASE/QUOTE`` / glued ``BASEQUOTE``,
    or a lone known ``BASE`` → defaults quote ``USDT``.
    """
    raw = text.strip()
    if not raw:
        return None

    upper = raw.upper()
    compact = re.sub(r"\s+", "", upper)

    m = _PAIR_SEP.search(upper)
    if m:
        return normalize_coobit_spot_symbol_param(f"{m.group(1).upper()}-{m.group(2).upper()}")

    for q in ("USDT", "USDC", "BTC", "ETH"):
        m2 = re.search(
            rf"(?<![A-Z0-9])([A-Z][A-Z0-9]{{1,14}}){q}(?![A-Z0-9])",
            compact,
        )
        if m2:
            return normalize_coobit_spot_symbol_param(f"{m2.group(1)}-{q}")

    for b in _KNOWN_BASES:
        if re.search(rf"(?<![A-Z0-9]){b}(?![A-Z0-9])", upper):
            return normalize_coobit_spot_symbol_param(f"{b}-USDT")

    return None
