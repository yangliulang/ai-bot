"""Telegram AppError LLM rewrite orchestration."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.telegram_app_error_user_message import (
    format_app_error_reply_for_telegram,
)
from chainup_agent.core.config import Settings, reset_settings_cache
from chainup_agent.core.errors import AppError


@pytest.mark.asyncio
async def test_format_app_error_spot_rejected_uses_llm_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_ERROR_LLM_REWRITE", "true")
    reset_settings_cache()
    settings = Settings()

    async def _rewrite(**kwargs):  # type: ignore[no-untyped-def]
        assert kwargs["context_json"]["errorCode"] == "AGENT_SPOT_ORDER_REJECTED"
        return "精度超过该交易对允许的小数位，请减少小数位数后重试。", None

    monkeypatch.setattr(
        "chainup_agent.application.telegram_app_error_user_message.invoke_llm_rewrite_telegram_app_error",
        AsyncMock(side_effect=_rewrite),
    )

    session = AsyncMock(spec=AsyncSession)
    exc = AppError(
        code="AGENT_SPOT_ORDER_REJECTED",
        message="交易所拒绝现货委托：The accuracy exceeds the maximum defined by this asset",
        status_code=400,
        details={"exchange_msg": "The accuracy exceeds the maximum defined by this asset"},
    )
    text = await format_app_error_reply_for_telegram(session, settings, exc)
    assert "精度超过" in text
    assert "AGENT_SPOT_ORDER_REJECTED" in text


@pytest.mark.asyncio
async def test_format_app_error_falls_back_when_rewrite_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_ERROR_LLM_REWRITE", "false")
    reset_settings_cache()
    settings = Settings()
    called = False

    async def _rewrite(**kwargs):  # type: ignore[no-untyped-def]
        nonlocal called
        called = True
        return "should not use", None

    monkeypatch.setattr(
        "chainup_agent.application.telegram_app_error_user_message.invoke_llm_rewrite_telegram_app_error",
        AsyncMock(side_effect=_rewrite),
    )
    session = AsyncMock(spec=AsyncSession)
    exc = AppError(
        code="AGENT_SPOT_ORDER_REJECTED",
        message="交易所拒绝现货委托：bad",
        status_code=400,
    )
    text = await format_app_error_reply_for_telegram(session, settings, exc)
    assert "交易所拒绝" in text
    assert called is False


@pytest.mark.asyncio
async def test_format_app_error_validation_skips_llm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_ERROR_LLM_REWRITE", "true")
    reset_settings_cache()
    settings = Settings()
    mock = AsyncMock()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_app_error_user_message.invoke_llm_rewrite_telegram_app_error",
        mock,
    )
    session = AsyncMock(spec=AsyncSession)
    exc = AppError(
        code="VALIDATION_ERROR",
        message="volume 须大于 0",
        status_code=422,
    )
    text = await format_app_error_reply_for_telegram(session, settings, exc)
    assert text == "volume 须大于 0"
    mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_format_app_error_falls_back_when_rewrite_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_ERROR_LLM_REWRITE", "true")
    reset_settings_cache()
    settings = Settings()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_app_error_user_message.invoke_llm_rewrite_telegram_app_error",
        AsyncMock(side_effect=RuntimeError("simulated gateway bug")),
    )
    session = AsyncMock(spec=AsyncSession)
    exc = AppError(
        code="AGENT_SPOT_ORDER_REJECTED",
        message="交易所拒绝现货委托：bad",
        status_code=400,
    )
    text = await format_app_error_reply_for_telegram(session, settings, exc)
    assert "交易所拒绝" in text
    assert "AGENT_SPOT_ORDER_REJECTED" in text
