"""Comma-separated Telegram id allowlist (`CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST`)."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def parse_bound_chat_allowlist_ids(raw: str) -> frozenset[int]:
    out: set[int] = set()
    for part in raw.split(","):
        p = part.strip()
        if not p:
            continue
        try:
            out.add(int(p))
        except ValueError:
            logger.warning(
                "telegram_bound_chat_allowlist_invalid_segment",
                extra={"segment": p[:64]},
            )
    return frozenset(out)
