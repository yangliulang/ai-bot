"""Telegram envelope → stable numeric user anchor (private chat; matches deeplink ``tg_id``)."""

from __future__ import annotations

from typing import Any


def telegram_user_anchor_id(envelope: dict[str, Any], chat_id: int) -> int:
    """
    Prefer ``from.id``; for private chats without ``from``, use ``chat.id``; else ``chat_id``.
    """
    from_user = envelope.get("from")
    if isinstance(from_user, dict):
        uid = from_user.get("id")
        if isinstance(uid, int):
            return uid
    chat = envelope.get("chat")
    if isinstance(chat, dict) and chat.get("type") == "private":
        cid = chat.get("id")
        if isinstance(cid, int):
            return cid
    return chat_id
