"""Onboarding helpers: binding lookup, initiate; subaccount status ~= sealed binding."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.agent_api_binding import TelegramInboundPayload
from chainup_agent.api.schemas.agent_onboarding import (
    ApiBindingStatusResponse,
    OnboardingInitiateRequest,
    OnboardingInitiateResponse,
    SubaccountStatusResponse,
)
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.models.telegram_agent_trading_binding import (
    TelegramAgentTradingBinding,
)


def parse_telegram_user_id_query(user_id: str) -> int:
    raw = user_id.strip()
    if not raw.isdigit():
        raise AppError(
            code="VALIDATION_ERROR",
            message="Query userId（Telegram）须为非空数值字符串。",
            status_code=422,
            details={"field": "userId"},
        )
    return int(raw)


def _telegram_user_id_from_payload(tg: TelegramInboundPayload | None) -> int:
    if tg is None or not tg.tg_id:
        raise AppError(
            code="AGENT_TELEGRAM_CONTEXT_REQUIRED",
            message="onboarding/initiate 须携带 telegram.tg_id。",
            status_code=400,
        )
    tid = str(tg.tg_id).strip()
    if not tid.isdigit():
        raise AppError(
            code="AGENT_TELEGRAM_CONTEXT_INVALID",
            message="telegram.tg_id 须为数值字符串。",
            status_code=400,
            details={"tg_id": tid[:32]},
        )
    return int(tid)


async def load_trading_binding_row(
    session: AsyncSession,
    telegram_user_id: int,
) -> TelegramAgentTradingBinding | None:
    stmt = select(TelegramAgentTradingBinding).where(
        TelegramAgentTradingBinding.telegram_user_id == telegram_user_id,
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


def row_to_api_binding_status(row: TelegramAgentTradingBinding) -> ApiBindingStatusResponse:
    return ApiBindingStatusResponse(
        telegram_user_id=row.telegram_user_id,
        agent_trading_api_binding_status="BOUND",
        openapi_base_url=row.openapi_base_url,
        binding_id=row.id,
        tg_username=row.tg_username,
        updated_at=row.updated_at,
    )


async def api_binding_status_for_user(
    session: AsyncSession,
    telegram_user_id: int,
) -> ApiBindingStatusResponse:
    row = await load_trading_binding_row(session, telegram_user_id)
    if row is None:
        return ApiBindingStatusResponse(
            telegram_user_id=telegram_user_id,
            agent_trading_api_binding_status="NONE",
        )
    return row_to_api_binding_status(row)


async def subaccount_status(
    session: AsyncSession,
    telegram_user_id: int,
) -> SubaccountStatusResponse:
    row = await load_trading_binding_row(session, telegram_user_id)
    bound = row is not None
    return SubaccountStatusResponse(
        telegram_user_id=telegram_user_id,
        subaccount_ready=bound,
        agent_sub_account_id=None,
        trading_api_binding_status="BOUND" if bound else "NONE",
    )


async def onboarding_initiate(
    session: AsyncSession,
    body: OnboardingInitiateRequest,
) -> OnboardingInitiateResponse:
    tg_user = _telegram_user_id_from_payload(body.telegram)
    oid = uuid.uuid4().hex
    row = await load_trading_binding_row(session, tg_user)
    if row is None:
        return OnboardingInitiateResponse(
            onboarding_id=oid,
            telegram_user_id=tg_user,
            next_step="bind_trading_api",
            agent_trading_api_binding_status="NONE",
        )
    return OnboardingInitiateResponse(
        onboarding_id=oid,
        telegram_user_id=tg_user,
        next_step="complete",
        agent_trading_api_binding_status="BOUND",
    )
