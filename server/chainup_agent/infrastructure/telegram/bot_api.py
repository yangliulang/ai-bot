from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from chainup_agent.core.config import get_settings
from chainup_agent.core.errors import AppError

logger = logging.getLogger(__name__)

TELEGRAM_API_ORIGIN = "https://api.telegram.org"


async def call_telegram_bot_api(
    bot_token: str,
    telegram_method: str,
    *,
    http_method: str = "POST",
    json_payload: dict[str, Any] | None = None,
    timeout_seconds: float = 30.0,
    transport_retries: int | None = None,
) -> dict[str, Any]:
    """
    Call Telegram Bot HTTPS API. Never logs ``bot_token`` or full URLs.

    Retries ``httpx.RequestError`` (connection / timeout / proxy) with short backoff
    when ``transport_retries`` is omitted (uses :attr:`Settings.telegram_bot_api_transport_retries`).
    Pass ``transport_retries=0`` to disable retries for a single call.
    """
    extra = (
        transport_retries
        if transport_retries is not None
        else get_settings().telegram_bot_api_transport_retries
    )
    max_attempts = max(1, int(extra) + 1)

    path = f"bot{bot_token}/{telegram_method}"
    url = f"{TELEGRAM_API_ORIGIN}/{path}"
    timeout = httpx.Timeout(timeout_seconds)

    last_req_err: httpx.RequestError | None = None
    r: httpx.Response | None = None
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if http_method.upper() == "GET":
                    r = await client.get(url)
                else:
                    r = await client.post(
                        url, json=json_payload if json_payload is not None else {}
                    )
            last_req_err = None
            break
        except httpx.RequestError as e:
            last_req_err = e
            if attempt + 1 < max_attempts:
                delay = min(2.0, 0.4 * (2**attempt))
                logger.warning(
                    "telegram_bot_api_transport_retry method=%s attempt=%s/%s delay_s=%s err_type=%s",
                    telegram_method,
                    attempt + 1,
                    max_attempts,
                    delay,
                    type(e).__name__,
                )
                await asyncio.sleep(delay)

    if last_req_err is not None:
        e = last_req_err
        err_type = type(e).__name__
        err_msg = (str(e) or "").strip()
        if len(err_msg) > 512:
            err_msg = f"{err_msg[:509]}..."
        log_frag = err_msg[:256] if err_msg else ""
        logger.warning(
            "telegram_bot_api_transport method=%s error_type=%s error=%s attempts=%s",
            telegram_method,
            err_type,
            log_frag,
            max_attempts,
        )
        detail: dict[str, Any] = {
            "telegram_method": telegram_method,
            "transport_error_type": err_type,
            "transport_attempts": max_attempts,
        }
        if err_msg:
            detail["transport_error_message"] = err_msg
        raise AppError(
            code="ADMIN_TELEGRAM_TRANSPORT_ERROR",
            message="Telegram Bot API request failed",
            status_code=502,
            details=detail,
        ) from e

    assert r is not None

    try:
        data = r.json()
    except ValueError as e:
        raise AppError(
            code="ADMIN_TELEGRAM_INVALID_RESPONSE",
            message="Telegram Bot API returned non-JSON",
            status_code=502,
            details={"telegram_method": telegram_method, "http_status": r.status_code},
        ) from e

    if not isinstance(data, dict):
        raise AppError(
            code="ADMIN_TELEGRAM_INVALID_RESPONSE",
            message="Telegram Bot API returned unexpected JSON shape",
            status_code=502,
            details={"telegram_method": telegram_method},
        )

    if data.get("ok") is True:
        return data

    desc = data.get("description") or "Telegram Bot API error"
    tg_err = data.get("error_code")
    http_status = r.status_code
    status = 400 if http_status < 500 else 502
    code = (
        "ADMIN_TELEGRAM_BOT_API_REJECTED"
        if http_status < 500
        else "ADMIN_TELEGRAM_BOT_API_UNAVAILABLE"
    )
    raise AppError(
        code=code,
        message=str(desc),
        status_code=status,
        details={"telegram_error_code": tg_err, "telegram_method": telegram_method},
    )
