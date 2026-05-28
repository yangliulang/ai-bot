"""Agent activation welcome message — telegram/overview §2.1.1."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.effective_locale import (
    EFFECTIVE_LOCALE_EN,
    EFFECTIVE_LOCALE_ZH_HANS,
    EFFECTIVE_LOCALE_ZH_HANT,
    normalize_effective_locale,
)
from chainup_agent.application.telegram_runtime_config import load_runtime_params
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.models.agent_instance import AgentInstance
from chainup_agent.infrastructure.persistence.models.telegram_agent_trading_binding import (
    TelegramAgentTradingBinding,
)
from chainup_agent.infrastructure.telegram.bot_api import call_telegram_bot_api

logger = logging.getLogger(__name__)

KEY_WELCOME_ZH_CN = "TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_CN"
KEY_WELCOME_ZH_TW = "TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_TW"
KEY_WELCOME_EN = "TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_EN"
KEY_WELCOME_LEGACY = "TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT"
KEY_DEFAULT_LOCALE = "TELEGRAM_DEFAULT_LOCALE"

_BUCKET_TO_KEY: dict[str, str] = {
    EFFECTIVE_LOCALE_ZH_HANS: KEY_WELCOME_ZH_CN,
    EFFECTIVE_LOCALE_ZH_HANT: KEY_WELCOME_ZH_TW,
    EFFECTIVE_LOCALE_EN: KEY_WELCOME_EN,
}

_FALLBACK_KEY_ORDER: tuple[str, ...] = (
    KEY_WELCOME_ZH_CN,
    KEY_WELCOME_EN,
    KEY_WELCOME_ZH_TW,
    KEY_WELCOME_LEGACY,
)


@dataclass(frozen=True)
class ActivationWelcomeOutcome:
    sent: bool
    skip_reason: str | None = None


def _param_text(params: dict[str, Any], key: str) -> str | None:
    raw = params.get(key)
    if raw is None:
        return None
    if not isinstance(raw, str):
        raw = str(raw)
    text = raw if key == KEY_WELCOME_LEGACY else raw.strip()
    return text if text.strip() else None


def resolve_locale_bucket(
    runtime_params: dict[str, Any],
    *,
    tg_lang: str | None,
) -> str:
    bucket = normalize_effective_locale(tg_lang)
    if bucket:
        return bucket
    default_raw = runtime_params.get(KEY_DEFAULT_LOCALE)
    bucket = normalize_effective_locale(
        str(default_raw).strip() if default_raw is not None else None
    )
    return bucket or EFFECTIVE_LOCALE_EN


def resolve_activation_welcome_text(
    runtime_params: dict[str, Any],
    *,
    tg_lang: str | None,
) -> str | None:
    """
    Language bucket + fallback chain: hit bucket → 简体 → 英文 → 繁体 → 遗留键.
    """
    bucket = resolve_locale_bucket(runtime_params, tg_lang=tg_lang)
    ordered_keys: list[str] = []
    primary = _BUCKET_TO_KEY.get(bucket)
    if primary:
        ordered_keys.append(primary)
    for key in _FALLBACK_KEY_ORDER:
        if key not in ordered_keys:
            ordered_keys.append(key)
    for key in ordered_keys:
        text = _param_text(runtime_params, key)
        if text:
            return text
    return None


def render_activation_welcome_text(
    template: str,
    *,
    tg_first_name: str | None = None,
    tg_username: str | None = None,
    telegram: dict[str, str] | None = None,
) -> str:
    """Render ``{displayName}``; pass explicit names or a ``telegram`` dict."""
    tg = telegram or {}
    first = (tg_first_name or tg.get("tg_first_name") or "").strip()
    username = (tg_username or tg.get("tg_username") or "").strip()
    if first:
        display = first
    elif username:
        display = username if username.startswith("@") else f"@{username}"
    else:
        display = "用户"
    return template.replace("{displayName}", display)


def render_activation_welcome(template: str, telegram: dict[str, str] | None) -> str:
    tg = telegram or {}
    first = (tg.get("tg_first_name") or "").strip()
    username = (tg.get("tg_username") or "").strip()
    if first:
        display = first
    elif username:
        display = username if username.startswith("@") else f"@{username}"
    else:
        display = "用户"
    return template.replace("{displayName}", display)


async def dispatch_activation_welcome(
    session: AsyncSession,
    settings: Settings,
    *,
    telegram_user_id: int,
    telegram: dict[str, str] | None,
) -> ActivationWelcomeOutcome:
    """Best-effort send after binding confirm; must run after binding commit."""
    if telegram is None or not str(telegram.get("tg_id") or "").strip():
        return ActivationWelcomeOutcome(sent=False, skip_reason="no_telegram_context")

    token = (settings.telegram_bot_token or "").strip()
    if not token:
        return ActivationWelcomeOutcome(sent=False, skip_reason="no_bot_token")

    stmt = select(AgentInstance).where(AgentInstance.telegram_user_id == telegram_user_id).limit(1)
    res = await session.execute(stmt)
    inst = res.scalar_one_or_none()
    if inst is None:
        return ActivationWelcomeOutcome(sent=False, skip_reason="no_telegram_context")

    if inst.activation_welcome_sent_at is not None:
        return ActivationWelcomeOutcome(sent=False, skip_reason="already_sent")

    bind_stmt = select(TelegramAgentTradingBinding).where(
        TelegramAgentTradingBinding.telegram_user_id == telegram_user_id
    )
    bind_res = await session.execute(bind_stmt)
    bind_row = bind_res.scalar_one_or_none()

    runtime_params, _ver = await load_runtime_params(session)
    tg_lang = (telegram.get("tg_lang") or "").strip() or None
    if not tg_lang and bind_row and bind_row.tg_lang:
        tg_lang = bind_row.tg_lang.strip()
    template = resolve_activation_welcome_text(runtime_params, tg_lang=tg_lang)
    if not template:
        return ActivationWelcomeOutcome(sent=False, skip_reason="no_template")

    merged_tg = dict(telegram)
    if bind_row:
        for key, attr in (
            ("tg_first_name", "tg_first_name"),
            ("tg_username", "tg_username"),
            ("tg_lang", "tg_lang"),
        ):
            if not merged_tg.get(key) and getattr(bind_row, attr, None):
                merged_tg[key] = str(getattr(bind_row, attr))
    body = render_activation_welcome(template, merged_tg)
    chat_id = telegram_user_id

    try:
        await call_telegram_bot_api(
            token,
            "sendMessage",
            json_payload={"chat_id": chat_id, "text": body},
            timeout_seconds=float(settings.telegram_activation_welcome_timeout_sec),
            transport_retries=0,
        )
    except AppError as exc:
        logger.warning(
            "activation_welcome_send_failed tg_id=%s code=%s",
            telegram_user_id,
            exc.code,
        )
        return ActivationWelcomeOutcome(sent=False, skip_reason="send_failed")
    except Exception:
        logger.exception(
            "activation_welcome_send_failed tg_id=%s",
            telegram_user_id,
        )
        return ActivationWelcomeOutcome(sent=False, skip_reason="send_failed")

    inst.activation_welcome_sent_at = datetime.now(UTC)
    await session.flush()
    logger.info(
        "activation_welcome_sent tg_id=%s text_len=%s",
        telegram_user_id,
        len(body),
    )
    return ActivationWelcomeOutcome(sent=True, skip_reason=None)
