"""Telegram user-visible text for :class:`AppError` — optional LLM-friendly rewrite."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_llm_chat import invoke_llm_rewrite_telegram_app_error
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError

logger = logging.getLogger(__name__)

# Errors that often carry raw English exchange `msg`; LLM rewrite adds the most value here.
_TELEGRAM_ERROR_LLM_CODES = frozenset(
    {
        "AGENT_SPOT_ORDER_REJECTED",
        "AGENT_SPOT_ORDER_FAILED",
        "PRICE_REJECTED_AGENT_BAND",
    }
)


def format_app_error_reply_plain(exc: AppError) -> str:
    """Deterministic Telegram copy (no LLM)."""
    if exc.code in (
        "AGENT_SUBACCOUNT_REQUIRED",
        "VALIDATION_ERROR",
        "AGENT_OPENAPI_PROBE_FAILED",
    ):
        return exc.message
    return f"{exc.message}\n（错误码：`{exc.code}`）"


def _error_context_payload(exc: AppError) -> dict[str, Any]:
    """Structured, truncated context for the rewrite prompt (no secrets)."""
    d = exc.details or {}
    out: dict[str, Any] = {
        "errorCode": exc.code,
        "serverMessage": (exc.message or "").strip()[:2000],
    }
    em = d.get("exchange_msg")
    if em is not None and str(em).strip():
        out["exchangeMessage"] = str(em).strip()[:1500]
    rr = d.get("reject_reason")
    if rr is not None and str(rr).strip():
        out["rejectReason"] = str(rr).strip()[:200]
    erp = d.get("exchange_response_preview")
    if isinstance(erp, dict) and "exchangeMessage" not in out:
        msg = erp.get("msg")
        if msg is not None and str(msg).strip():
            out["exchangeMessage"] = str(msg).strip()[:1500]
    return out


async def format_app_error_reply_for_telegram(
    session: AsyncSession,
    settings: Settings,
    exc: AppError,
) -> str:
    """
    User-facing Telegram text for an :class:`AppError`.

    When ``settings.telegram_error_llm_rewrite`` is true and ``exc.code`` is in the
    trading-error allowlist, tries Admin AI gateway LLM to rewrite to concise friendly
    Chinese; on any failure or unexpected error, falls back to
    :func:`format_app_error_reply_plain`.
    """
    plain = format_app_error_reply_plain(exc)
    if not settings.telegram_error_llm_rewrite:
        return plain
    if exc.code not in _TELEGRAM_ERROR_LLM_CODES:
        return plain

    ctx_payload = _error_context_payload(exc)
    try:
        rewritten, reason = await invoke_llm_rewrite_telegram_app_error(
            session=session,
            settings=settings,
            context_json=ctx_payload,
        )
    except Exception:
        logger.exception(
            "telegram_app_error_llm_rewrite_exception code=%s",
            exc.code,
        )
        return plain
    if not rewritten:
        logger.info(
            "telegram_app_error_llm_rewrite_fallback code=%s reason=%s",
            exc.code,
            (reason or "")[:120],
        )
        return plain

    body = rewritten.strip()
    if len(body) > 3500:
        body = body[:3499] + "…"
    return f"{body}\n（错误码：`{exc.code}`）"
