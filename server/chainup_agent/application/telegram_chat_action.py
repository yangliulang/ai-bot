"""Telegram sendChatAction(typing) — SC-CH-TG-09."""

from __future__ import annotations

import logging

from chainup_agent.infrastructure.telegram.bot_api import call_telegram_bot_api

logger = logging.getLogger(__name__)


async def send_telegram_typing(
    bot_token: str,
    chat_id: int,
) -> None:
    try:
        await call_telegram_bot_api(
            bot_token,
            "sendChatAction",
            json_payload={"chat_id": chat_id, "action": "typing"},
        )
    except Exception:
        logger.debug("telegram_send_chat_action_typing_failed chat_id=%s", chat_id)
