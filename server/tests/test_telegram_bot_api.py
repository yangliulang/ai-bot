"""Tests for Telegram Bot API client (transport vs logical errors)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.telegram.bot_api import call_telegram_bot_api


@pytest.mark.asyncio
async def test_call_telegram_bot_api_transport_error_includes_details() -> None:
    inner = AsyncMock()
    inner.post = AsyncMock(
        side_effect=httpx.ConnectError(
            "Connection refused",
            request=httpx.Request("POST", "https://api.telegram.org/botfoo/setWebhook"),
        )
    )

    cm = AsyncMock()
    cm.__aenter__.return_value = inner
    cm.__aexit__.return_value = None

    with patch("chainup_agent.infrastructure.telegram.bot_api.httpx.AsyncClient", return_value=cm):
        with pytest.raises(AppError) as ei:
            await call_telegram_bot_api(
                "tok",
                "setWebhook",
                json_payload={"url": "https://x/y"},
                transport_retries=0,
            )

    err = ei.value
    assert err.code == "ADMIN_TELEGRAM_TRANSPORT_ERROR"
    assert err.details["telegram_method"] == "setWebhook"
    assert err.details["transport_error_type"] == "ConnectError"
    assert err.details.get("transport_attempts") == 1
    assert "Connection refused" in (err.details.get("transport_error_message") or "")


@pytest.mark.asyncio
async def test_call_telegram_bot_api_retries_recover_from_connect_error() -> None:
    ok = httpx.Response(200, json={"ok": True, "result": True})
    inner = AsyncMock()
    inner.post = AsyncMock(
        side_effect=[
            httpx.ConnectError(
                "refused",
                request=httpx.Request("POST", "https://api.telegram.org/botx/y"),
            ),
            ok,
        ],
    )
    cm = AsyncMock()
    cm.__aenter__.return_value = inner
    cm.__aexit__.return_value = None

    with patch("chainup_agent.infrastructure.telegram.bot_api.httpx.AsyncClient", return_value=cm):
        data = await call_telegram_bot_api(
            "tok",
            "sendMessage",
            json_payload={"chat_id": 1, "text": "hi"},
            transport_retries=1,
        )
    assert data.get("ok") is True
    assert inner.post.await_count == 2
