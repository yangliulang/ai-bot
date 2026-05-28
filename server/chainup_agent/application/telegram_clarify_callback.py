"""Telegram clarify callbacks — ``cl:*`` / ``rc:*`` (non write-confirm)."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.clarify_session import (
    apply_clarify_callback,
    is_clarify_callback_data,
)
from chainup_agent.application.read_clarify_session import (
    apply_read_clarify_callback,
    is_read_clarify_callback_data,
)
from chainup_agent.application.telegram_bound_reply import build_telegram_bound_user_reply
from chainup_agent.application.telegram_callback_handler import safe_answer_telegram_callback_query
from chainup_agent.application.telegram_identity import telegram_user_anchor_id
from chainup_agent.core.config import Settings
from chainup_agent.infrastructure.telegram.bot_api import call_telegram_bot_api

logger = logging.getLogger(__name__)


async def handle_clarify_callback_query(
    *,
    settings: Settings,
    session: AsyncSession,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    callback_data: str,
) -> bool:
    """
    Handle ``cl:*`` / ``rc:*`` clarify keyboards.
    Returns True if handled (caller should not fall through to Type-A tokens).
    """
    cd = callback_data.strip()
    session_id = f"tg:{chat_id}"

    if is_read_clarify_callback_data(cd):
        snap, phrase, err = apply_read_clarify_callback(session_id, cd)
        if err:
            await safe_answer_telegram_callback_query(
                bot_token, callback_query_id, text=err[:200]
            )
            return True
        await safe_answer_telegram_callback_query(bot_token, callback_query_id)
        if phrase:
            reply, markup = await build_telegram_bound_user_reply(
                settings=settings,
                session=session,
                anchor_id=from_telegram_user_id,
                chat_id=chat_id,
                user_text=phrase,
            )
            await call_telegram_bot_api(
                bot_token,
                "sendMessage",
                json_payload={
                    "chat_id": chat_id,
                    "text": reply[:4096],
                    **({"reply_markup": markup} if markup else {}),
                },
            )
        _ = snap
        return True

    if not is_clarify_callback_data(cd):
        return False

    snap, phrase, err = apply_clarify_callback(session_id, cd, settings=settings)
    if err:
        await safe_answer_telegram_callback_query(
            bot_token, callback_query_id, text=err[:200]
        )
        if err and "新话题" in err or "聊点别的" in err:
            await call_telegram_bot_api(
                bot_token,
                "sendMessage",
                json_payload={"chat_id": chat_id, "text": err[:4096]},
            )
        return True

    await safe_answer_telegram_callback_query(bot_token, callback_query_id)
    if not phrase:
        return True

    reply, markup = await build_telegram_bound_user_reply(
        settings=settings,
        session=session,
        anchor_id=from_telegram_user_id,
        chat_id=chat_id,
        user_text=phrase,
    )
    await call_telegram_bot_api(
        bot_token,
        "sendMessage",
        json_payload={
            "chat_id": chat_id,
            "text": reply[:4096],
            **({"reply_markup": markup} if markup else {}),
        },
    )
    logger.info(
        "telegram_clarify_callback_handled session=%s data=%s turn=%s",
        session_id,
        cd,
        snap.clarify_turn if snap else "-",
    )
    return True
