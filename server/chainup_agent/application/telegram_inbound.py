"""Inbound Telegram webhook: binding hint + optional Coobit bind URL button."""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlsplit, urlunsplit

from sqlalchemy.exc import OperationalError

from chainup_agent.application.agent_api_binding_confirm import (
    is_telegram_user_agent_hosted_bound,
)
from chainup_agent.application.telegram_bound_reply import build_telegram_bound_user_reply
from chainup_agent.application.telegram_callback_handler import (
    handle_telegram_callback_query_update,
)
from chainup_agent.application.telegram_identity import telegram_user_anchor_id
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.base import get_session_factory
from chainup_agent.infrastructure.telegram.bot_api import call_telegram_bot_api

logger = logging.getLogger(__name__)

_MAX_PREFILL_STR = 128
_MAX_USERNAME_LEN = 64
_MAX_LANG_LEN = 16


def _bind_guide_with_inline_button() -> str:
    """User-facing copy when HTTPS bind URL supports InlineKeyboard."""
    return (
        "要使用交易助手，请先完成账户绑定。\n\n"
        "请点击下方「前往绑定页面」，按页面指引登录并授权交易 API。"
        "绑定成功后，即可在此使用行情查询、账户与交易相关能力。"
    )


def _bind_guide_with_plaintext_url(bind_page_url: str) -> str:
    """Fallback when Telegram rejects inline URL buttons (http / localhost)."""
    url = bind_page_url.strip()
    return (
        "要使用交易助手，请先完成账户绑定。\n\n"
        "Telegram 内暂无法直接打开该链接，请复制下方地址到浏览器中打开并完成授权：\n"
        f"{url}"
    )


def merge_bind_url_with_tg_prefill(base_bind_url: str, prefill: dict[str, str]) -> str:
    """
    Append OR merge query parameters onto the configured bind URL (UTF-8, RFC 3986 query).

    Prefill keys overwrite existing keys with the same name. Used for H5 UX only;
    not a signed trust boundary (see BACKEND_SPEC §3.1).
    """
    raw = base_bind_url.strip()
    if not prefill or not raw:
        return raw
    parts = urlsplit(raw)
    merged = dict(parse_qsl(parts.query, keep_blank_values=True))
    for k, v in prefill.items():
        if v != "":
            merged[k] = v
    new_query = urlencode(list(merged.items()), encoding="utf-8")
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))


def _telegram_query_prefill_from_envelope(envelope: dict[str, Any], chat_id: int) -> dict[str, str]:
    """Map ``message`` / ``edited_message`` envelope to H5 query keys (prefill)."""
    out: dict[str, str] = {}
    chat = envelope.get("chat")
    from_user = envelope.get("from")

    if isinstance(from_user, dict):
        uid = from_user.get("id")
        if isinstance(uid, int):
            out["tg_id"] = str(uid)
        uname = from_user.get("username")
        if isinstance(uname, str) and uname.strip():
            out["tg_username"] = uname.strip()[:_MAX_USERNAME_LEN]
        fn = from_user.get("first_name")
        if isinstance(fn, str) and fn.strip():
            out["tg_first_name"] = fn.strip()[:_MAX_PREFILL_STR]
        ln = from_user.get("last_name")
        if isinstance(ln, str) and ln.strip():
            out["tg_last_name"] = ln.strip()[:_MAX_PREFILL_STR]
        lang = from_user.get("language_code")
        if isinstance(lang, str) and lang.strip():
            out["tg_lang"] = lang.strip()[:_MAX_LANG_LEN]

    if "tg_id" not in out and isinstance(chat, dict) and chat.get("type") == "private":
        out["tg_id"] = str(chat_id)

    return out


def _bind_url_allows_telegram_inline_url_button(bind_page_url: str) -> bool:
    """
    Telegram rejects many http / localhost URLs for inline_keyboard url buttons
    ("Wrong HTTP URL"). Only attach a button when the URL looks like a normal HTTPS deeplink.
    """
    raw = bind_page_url.strip()
    parsed = urlparse(raw)
    if parsed.scheme.lower() != "https":
        return False
    host = (parsed.hostname or "").lower()
    if host in ("localhost", "127.0.0.1", "::1"):
        return False
    if host.endswith(".localhost"):
        return False
    return bool(host)


def _message_plain_text(envelope: dict[str, Any]) -> str | None:
    """replies only against user-visible textual payload (text or photo caption)."""
    text = envelope.get("text")
    if isinstance(text, str):
        stripped = text.strip()
        if stripped:
            return stripped
    cap = envelope.get("caption")
    if isinstance(cap, str):
        stripped = cap.strip()
        if stripped:
            return stripped
    return None


def _extract_callback_query(update: dict[str, Any]) -> tuple[int, int, str | int, str] | None:
    """Return chat_id, from_user_id, callback_query_id, callback_data."""
    cq = update.get("callback_query")
    if not isinstance(cq, dict):
        return None
    cq_id = cq.get("id")
    data = cq.get("data")
    if cq_id is None or not isinstance(data, str) or not data.strip():
        return None
    from_u = cq.get("from")
    msg = cq.get("message")
    if not isinstance(from_u, dict) or not isinstance(msg, dict):
        return None
    uid = from_u.get("id")
    chat = msg.get("chat")
    if not isinstance(chat, dict):
        return None
    cid = chat.get("id")
    try:
        return int(cid), int(uid), cq_id, data.strip()
    except (TypeError, ValueError):
        return None


def _extract_user_turn(update: dict[str, Any]) -> tuple[int, str, dict[str, Any]] | None:
    """Return chat_id, plaintext, envelope for inbound handling."""
    for key in ("message", "edited_message", "channel_post"):
        envelope = update.get(key)
        if not isinstance(envelope, dict):
            continue
        chat = envelope.get("chat")
        if not isinstance(chat, dict):
            continue
        chat_id_raw = chat.get("id")
        plain = _message_plain_text(envelope)
        if chat_id_raw is None or plain is None:
            continue
        try:
            return int(chat_id_raw), plain, envelope
        except (TypeError, ValueError):
            continue
    return None


async def _build_bound_user_reply(
    *,
    settings: Settings,
    chat_id: int,
    user_text: str,
    envelope: dict[str, Any],
) -> tuple[str, dict[str, Any] | None]:
    bind_base = settings.telegram_bind_page_url.strip()
    prefill = _telegram_query_prefill_from_envelope(envelope, chat_id)
    bind_url = merge_bind_url_with_tg_prefill(bind_base, prefill) if bind_base else ""

    anchor_id = telegram_user_anchor_id(envelope, chat_id)
    hosted_bound = False
    try:
        factory = get_session_factory()
        async with factory() as session:
            hosted_bound = await is_telegram_user_agent_hosted_bound(session, anchor_id)
    except OperationalError as exc:
        logger.warning(
            "telegram_trading_binding_lookup_operational_error code=%s msg=%s",
            type(exc.orig).__name__ if getattr(exc, "orig", None) else "unknown",
            str(exc)[:200],
        )
    except Exception:
        logger.exception("telegram_trading_binding_lookup_failed")

    if hosted_bound:
        try:
            factory = get_session_factory()
            async with factory() as session:
                text, markup = await build_telegram_bound_user_reply(
                    settings=settings,
                    session=session,
                    anchor_id=anchor_id,
                    chat_id=chat_id,
                    user_text=user_text,
                )
            return text, markup
        except OperationalError as exc:
            logger.warning(
                "telegram_bound_reply_operational_error code=%s msg=%s",
                type(exc.orig).__name__ if getattr(exc, "orig", None) else "unknown",
                str(exc)[:200],
            )
            fallback = (
                "暂时无法加载门禁或路由（数据库不可用）；请稍后重试。\n"
                "（运维：`POST /api/v1/agent/access/evaluate` · "
                "`POST /api/v1/agent/routing/execute`）"
            )
            return fallback, None
        except Exception as exc:
            logger.exception("telegram_bound_reply_failed")
            fallback = (
                "处理消息时发生内部错误，请稍后重试。\n"
                f"（运维：{type(exc).__name__} · "
                "`POST /api/v1/agent/access/evaluate` · "
                "`POST /api/v1/agent/routing/execute`）"
            )
            return fallback, None

    if bind_url:
        inline_btn_ok = _bind_url_allows_telegram_inline_url_button(bind_url)
        if inline_btn_ok:
            text = _bind_guide_with_inline_button()
            markup: dict[str, Any] = {
                "inline_keyboard": [
                    [{"text": "前往绑定页面", "url": bind_url}],
                ],
            }
            return text, markup

        logger.info(
            "telegram_skip_inline_keyboard_url",
            extra={
                "hint": "telegram_rejects_inline_url_for_http_or_localhost",
                "scheme": urlparse(bind_url).scheme or "",
            },
        )
        return _bind_guide_with_plaintext_url(bind_url), None

    logger.warning("telegram_bind_page_url_missing")
    text = (
        "要使用交易助手，请先完成账户绑定。\n\n"
        "当前暂未配置绑定页地址，请联系运维设置 CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL 后重试。"
    )
    return text, None


async def acknowledge_inbound_webhook(settings: Settings, bot_token: str, body: bytes) -> None:
    """
    Best-effort: never raises — Telegram should always get HTTP 200 from the route
    (unless auth/path failed earlier).
    """
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        logger.warning("telegram_webhook_invalid_json")
        return
    if not isinstance(data, dict):
        logger.warning("telegram_webhook_non_object_json")
        return

    uid = data.get("update_id")
    top_keys = ",".join(sorted(data.keys()))

    from chainup_agent.application.session_concurrency import remember_telegram_update_id

    if not remember_telegram_update_id(bot_token, uid if isinstance(uid, int) else None):
        return

    cb = _extract_callback_query(data)
    if cb is not None:
        c_chat_id, from_uid, cq_id, cb_data = cb
        try:
            await handle_telegram_callback_query_update(
                settings=settings,
                bot_token=bot_token,
                callback_query_id=cq_id,
                chat_id=c_chat_id,
                from_telegram_user_id=from_uid,
                callback_data=cb_data,
            )
        except Exception:
            logger.exception(
                "telegram_callback_dispatch_failed update_id=%s chat_id=%s",
                uid,
                c_chat_id,
            )
        return

    extracted = _extract_user_turn(data)
    if extracted is None:
        logger.info(
            "telegram_webhook_skip_no_plaintext update_id=%s keys=%s",
            uid,
            top_keys,
        )
        return
    chat_id, text, envelope = extracted
    from chainup_agent.application.session_concurrency import run_serial_per_session
    from chainup_agent.application.telegram_chat_action import send_telegram_typing
    from chainup_agent.application.telegram_stm import telegram_session_id

    try:

        async def _run() -> tuple[str, dict[str, Any] | None]:
            await send_telegram_typing(bot_token, chat_id)
            return await _build_bound_user_reply(
                settings=settings,
                chat_id=chat_id,
                user_text=text,
                envelope=envelope,
            )

        reply_text, reply_markup = await run_serial_per_session(
            telegram_session_id(chat_id),
            settings=settings,
            coro_factory=_run,
        )
    except Exception:
        logger.exception(
            "telegram_webhook_build_reply_failed update_id=%s chat_id=%s",
            uid,
            chat_id,
        )
        reply_text = "暂时无法处理你的消息（服务端异常）。请稍后重试；若持续出现请联系运维。"
        reply_markup = None
    payload: dict[str, Any] = {
        "chat_id": chat_id,
        "text": reply_text[:4096],
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    try:
        logger.info(
            "telegram_webhook_reply update_id=%s text_len=%s has_markup=%s",
            uid,
            len(reply_text),
            reply_markup is not None,
        )
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload=payload,
        )
    except AppError as exc:
        logger.error(
            "telegram_send_message_failed code=%s message=%s details=%s",
            exc.code,
            exc.message,
            exc.details or {},
        )
    except Exception:
        logger.exception("telegram_send_message_failed")
