"""Persisted Telegram confirmation tokens for destructive trading actions (inline keyboard)."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import timedelta
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.agent_runtime import utc_now
from chainup_agent.infrastructure.persistence.models.agent_telegram_pending_confirm import (
    AgentTelegramPendingConfirm,
)

logger = logging.getLogger(__name__)

FLASH_PENDING_KIND = "flash_convert"
LIMIT_PENDING_KIND = "spot_limit_order"
AMEND_PENDING_KIND = "spot_amend_limit_order"
FUTURES_MARKET_PENDING_KIND = "futures_market_order"
FUTURES_LIMIT_PENDING_KIND = "futures_limit_order"
CONDITION_PENDING_KIND = "futures_condition_order"
CONDITION_CANCEL_PENDING_KIND = "futures_condition_cancel"
TOKEN_HEX_BYTES = 8

CB_FLASH_CONFIRM = "fcp"
CB_FLASH_CANCEL = "fcx"
# lcp/lcx — limit confirm/cancel; same 19-byte pattern as flash (prefix + 16 hex)
CB_LIMIT_CONFIRM = "lcp"
CB_LIMIT_CANCEL = "lcx"
# smp/smx — spot amend limit (prefix + 16 hex = 19 bytes)
CB_AMEND_CONFIRM = "smp"
CB_AMEND_CANCEL = "smx"
# ump/umx — futures market; ulp/ulx — futures limit (prefix + 16 hex = 19 bytes)
CB_FUTURES_MARKET_CONFIRM = "ump"
CB_FUTURES_MARKET_CANCEL = "umx"
CB_FUTURES_LIMIT_CONFIRM = "ulp"
CB_FUTURES_LIMIT_CANCEL = "ulx"
# cop/cox — futures condition order create (prefix + 16 hex = 19 bytes)
CB_CONDITION_CONFIRM = "cop"
CB_CONDITION_CANCEL = "cox"
# ccp/ccx — futures condition order cancel (prefix + 16 hex = 19 bytes)
CB_CONDITION_CANCEL_CONFIRM = "ccp"
CB_CONDITION_CANCEL_DISMISS = "ccx"
# xm1/xm2 — margin cross market dual Type-A (phase1 → phase2)
CB_MARGIN_MARKET_P1_CONFIRM = "xm1p"
CB_MARGIN_MARKET_P1_CANCEL = "xm1x"
CB_MARGIN_MARKET_P2_CONFIRM = "xm2p"
CB_MARGIN_MARKET_P2_CANCEL = "xm2x"
CB_MARGIN_LIMIT_P1_CONFIRM = "xl1p"
CB_MARGIN_LIMIT_P1_CANCEL = "xl1x"
CB_MARGIN_LIMIT_P2_CONFIRM = "xl2p"
CB_MARGIN_LIMIT_P2_CANCEL = "xl2x"

MARGIN_MARKET_P1_KIND = "margin_cross_market_p1"
MARGIN_MARKET_P2_KIND = "margin_cross_market_p2"
MARGIN_LIMIT_P1_KIND = "margin_cross_limit_p1"
MARGIN_LIMIT_P2_KIND = "margin_cross_limit_p2"


def parse_flash_callback_data(data: str) -> tuple[str, str] | None:
    """
    Returns (action confirm|cancel, token_hex) or None.
    """
    if len(data) != len(CB_FLASH_CONFIRM) + TOKEN_HEX_BYTES * 2:
        return None
    if data.startswith(CB_FLASH_CONFIRM):
        return "confirm", data[len(CB_FLASH_CONFIRM) :]
    if data.startswith(CB_FLASH_CANCEL):
        return "cancel", data[len(CB_FLASH_CANCEL) :]
    return None


def parse_limit_callback_data(data: str) -> tuple[str, str] | None:
    """Same shape as flash; distinct prefix so callbacks never cross wired handlers."""
    if len(data) != len(CB_LIMIT_CONFIRM) + TOKEN_HEX_BYTES * 2:
        return None
    if data.startswith(CB_LIMIT_CONFIRM):
        return "confirm", data[len(CB_LIMIT_CONFIRM) :]
    if data.startswith(CB_LIMIT_CANCEL):
        return "cancel", data[len(CB_LIMIT_CANCEL) :]
    return None


def parse_amend_callback_data(data: str) -> tuple[str, str] | None:
    if len(data) != len(CB_AMEND_CONFIRM) + TOKEN_HEX_BYTES * 2:
        return None
    if data.startswith(CB_AMEND_CONFIRM):
        return "confirm", data[len(CB_AMEND_CONFIRM) :]
    if data.startswith(CB_AMEND_CANCEL):
        return "cancel", data[len(CB_AMEND_CANCEL) :]
    return None


def parse_futures_market_callback_data(data: str) -> tuple[str, str] | None:
    if len(data) != len(CB_FUTURES_MARKET_CONFIRM) + TOKEN_HEX_BYTES * 2:
        return None
    if data.startswith(CB_FUTURES_MARKET_CONFIRM):
        return "confirm", data[len(CB_FUTURES_MARKET_CONFIRM) :]
    if data.startswith(CB_FUTURES_MARKET_CANCEL):
        return "cancel", data[len(CB_FUTURES_MARKET_CANCEL) :]
    return None


def parse_futures_limit_callback_data(data: str) -> tuple[str, str] | None:
    if len(data) != len(CB_FUTURES_LIMIT_CONFIRM) + TOKEN_HEX_BYTES * 2:
        return None
    if data.startswith(CB_FUTURES_LIMIT_CONFIRM):
        return "confirm", data[len(CB_FUTURES_LIMIT_CONFIRM) :]
    if data.startswith(CB_FUTURES_LIMIT_CANCEL):
        return "cancel", data[len(CB_FUTURES_LIMIT_CANCEL) :]
    return None


def parse_condition_callback_data(data: str) -> tuple[str, str] | None:
    if len(data) != len(CB_CONDITION_CONFIRM) + TOKEN_HEX_BYTES * 2:
        return None
    if data.startswith(CB_CONDITION_CONFIRM):
        return "confirm", data[len(CB_CONDITION_CONFIRM) :]
    if data.startswith(CB_CONDITION_CANCEL):
        return "cancel", data[len(CB_CONDITION_CANCEL) :]
    return None


def parse_condition_cancel_callback_data(data: str) -> tuple[str, str] | None:
    if len(data) != len(CB_CONDITION_CANCEL_CONFIRM) + TOKEN_HEX_BYTES * 2:
        return None
    if data.startswith(CB_CONDITION_CANCEL_CONFIRM):
        return "confirm", data[len(CB_CONDITION_CANCEL_CONFIRM) :]
    if data.startswith(CB_CONDITION_CANCEL_DISMISS):
        return "cancel", data[len(CB_CONDITION_CANCEL_DISMISS) :]
    return None


def _parse_dual_margin_callback(
    data: str,
    *,
    confirm_prefix: str,
    cancel_prefix: str,
) -> tuple[str, str] | None:
    if len(data) != len(confirm_prefix) + TOKEN_HEX_BYTES * 2:
        return None
    if data.startswith(confirm_prefix):
        return "confirm", data[len(confirm_prefix) :]
    if data.startswith(cancel_prefix):
        return "cancel", data[len(cancel_prefix) :]
    return None


def parse_margin_market_p1_callback_data(data: str) -> tuple[str, str] | None:
    return _parse_dual_margin_callback(
        data, confirm_prefix=CB_MARGIN_MARKET_P1_CONFIRM, cancel_prefix=CB_MARGIN_MARKET_P1_CANCEL
    )


def parse_margin_market_p2_callback_data(data: str) -> tuple[str, str] | None:
    return _parse_dual_margin_callback(
        data, confirm_prefix=CB_MARGIN_MARKET_P2_CONFIRM, cancel_prefix=CB_MARGIN_MARKET_P2_CANCEL
    )


def parse_margin_limit_p1_callback_data(data: str) -> tuple[str, str] | None:
    return _parse_dual_margin_callback(
        data, confirm_prefix=CB_MARGIN_LIMIT_P1_CONFIRM, cancel_prefix=CB_MARGIN_LIMIT_P1_CANCEL
    )


def parse_margin_limit_p2_callback_data(data: str) -> tuple[str, str] | None:
    return _parse_dual_margin_callback(
        data, confirm_prefix=CB_MARGIN_LIMIT_P2_CONFIRM, cancel_prefix=CB_MARGIN_LIMIT_P2_CANCEL
    )


def _token_hex_ok(tok: str) -> bool:
    if len(tok) != TOKEN_HEX_BYTES * 2:
        return False
    try:
        int(tok, 16)
    except ValueError:
        return False
    return True


async def revoke_flash_pending_for_user(session: AsyncSession, telegram_user_id: int) -> None:
    await session.execute(
        delete(AgentTelegramPendingConfirm).where(
            AgentTelegramPendingConfirm.telegram_user_id == telegram_user_id,
            AgentTelegramPendingConfirm.kind == FLASH_PENDING_KIND,
        )
    )


async def revoke_amend_pending_for_user(session: AsyncSession, telegram_user_id: int) -> None:
    await session.execute(
        delete(AgentTelegramPendingConfirm).where(
            AgentTelegramPendingConfirm.telegram_user_id == telegram_user_id,
            AgentTelegramPendingConfirm.kind == AMEND_PENDING_KIND,
        )
    )


async def revoke_limit_pending_for_user(session: AsyncSession, telegram_user_id: int) -> None:
    await session.execute(
        delete(AgentTelegramPendingConfirm).where(
            AgentTelegramPendingConfirm.telegram_user_id == telegram_user_id,
            AgentTelegramPendingConfirm.kind == LIMIT_PENDING_KIND,
        )
    )


async def revoke_futures_market_pending_for_user(
    session: AsyncSession, telegram_user_id: int
) -> None:
    await session.execute(
        delete(AgentTelegramPendingConfirm).where(
            AgentTelegramPendingConfirm.telegram_user_id == telegram_user_id,
            AgentTelegramPendingConfirm.kind == FUTURES_MARKET_PENDING_KIND,
        )
    )


async def revoke_futures_limit_pending_for_user(
    session: AsyncSession, telegram_user_id: int
) -> None:
    await session.execute(
        delete(AgentTelegramPendingConfirm).where(
            AgentTelegramPendingConfirm.telegram_user_id == telegram_user_id,
            AgentTelegramPendingConfirm.kind == FUTURES_LIMIT_PENDING_KIND,
        )
    )


async def revoke_condition_pending_for_user(
    session: AsyncSession, telegram_user_id: int
) -> None:
    await session.execute(
        delete(AgentTelegramPendingConfirm).where(
            AgentTelegramPendingConfirm.telegram_user_id == telegram_user_id,
            AgentTelegramPendingConfirm.kind == CONDITION_PENDING_KIND,
        )
    )


async def create_flash_convert_pending(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    chat_id: int,
    symbol: str,
    side: str,
    quantity: str,
    execution_id: str | None = None,
) -> str:
    await revoke_flash_pending_for_user(session, telegram_user_id)
    token = uuid.uuid4().hex[: TOKEN_HEX_BYTES * 2]
    payload = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "scenarioId": "trade.spot.flash_convert",
    }
    ex = execution_id.strip() if execution_id and execution_id.strip() else ""
    if ex:
        payload["executionId"] = ex
    row = AgentTelegramPendingConfirm(
        id=f"tgpc_{uuid.uuid4().hex[:24]}",
        public_token=token,
        telegram_user_id=telegram_user_id,
        chat_id=chat_id,
        kind=FLASH_PENDING_KIND,
        payload_json=json.dumps(payload, ensure_ascii=False),
        expires_at=utc_now() + timedelta(minutes=15),
    )
    session.add(row)
    await session.flush()
    logger.info(
        "telegram_flash_pending_created user=%s chat=%s token_tail=%s",
        telegram_user_id,
        chat_id,
        token[-4:],
    )
    return token


async def create_spot_limit_pending(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    chat_id: int,
    symbol: str,
    side: str,
    quantity: str,
    price: str,
    time_in_force: str,
    execution_id: str | None = None,
) -> str:
    await revoke_limit_pending_for_user(session, telegram_user_id)
    token = uuid.uuid4().hex[: TOKEN_HEX_BYTES * 2]
    payload = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price,
        "timeInForce": time_in_force,
        "scenarioId": "trade.spot.limit_order",
    }
    ex = execution_id.strip() if execution_id and execution_id.strip() else ""
    if ex:
        payload["executionId"] = ex
    row = AgentTelegramPendingConfirm(
        id=f"tgpc_{uuid.uuid4().hex[:24]}",
        public_token=token,
        telegram_user_id=telegram_user_id,
        chat_id=chat_id,
        kind=LIMIT_PENDING_KIND,
        payload_json=json.dumps(payload, ensure_ascii=False),
        expires_at=utc_now() + timedelta(minutes=15),
    )
    session.add(row)
    await session.flush()
    logger.info(
        "telegram_limit_pending_created user=%s chat=%s token_tail=%s",
        telegram_user_id,
        chat_id,
        token[-4:],
    )
    return token


async def create_spot_amend_pending(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    chat_id: int,
    symbol: str,
    order_id: str,
    side: str,
    prior_price: str,
    prior_quantity: str,
    price: str,
    quantity: str,
    time_in_force: str,
    execution_id: str | None = None,
) -> str:
    await revoke_amend_pending_for_user(session, telegram_user_id)
    token = uuid.uuid4().hex[: TOKEN_HEX_BYTES * 2]
    payload = {
        "symbol": symbol,
        "orderId": order_id,
        "side": side,
        "priorPrice": prior_price,
        "priorQuantity": prior_quantity,
        "price": price,
        "quantity": quantity,
        "timeInForce": time_in_force,
        "scenarioId": "trade.spot.amend_limit_order",
    }
    ex = execution_id.strip() if execution_id and execution_id.strip() else ""
    if ex:
        payload["executionId"] = ex
    row = AgentTelegramPendingConfirm(
        id=f"tgpc_{uuid.uuid4().hex[:24]}",
        public_token=token,
        telegram_user_id=telegram_user_id,
        chat_id=chat_id,
        kind=AMEND_PENDING_KIND,
        payload_json=json.dumps(payload, ensure_ascii=False),
        expires_at=utc_now() + timedelta(minutes=15),
    )
    session.add(row)
    await session.flush()
    logger.info(
        "telegram_amend_pending_created user=%s chat=%s token_tail=%s",
        telegram_user_id,
        chat_id,
        token[-4:],
    )
    return token


def _optional_open_close_payload(payload: dict[str, Any], open_close: str | None) -> None:
    oc = (open_close or "").strip().upper()
    if oc in ("OPEN", "CLOSE"):
        payload["openClose"] = oc


async def create_futures_market_pending(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    chat_id: int,
    symbol: str,
    side: str,
    quantity: str,
    open_close: str | None = None,
    execution_id: str | None = None,
) -> str:
    await revoke_futures_market_pending_for_user(session, telegram_user_id)
    token = uuid.uuid4().hex[: TOKEN_HEX_BYTES * 2]
    payload: dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "scenarioId": "trade.futures.market_order",
    }
    _optional_open_close_payload(payload, open_close)
    ex = execution_id.strip() if execution_id and execution_id.strip() else ""
    if ex:
        payload["executionId"] = ex
    row = AgentTelegramPendingConfirm(
        id=f"tgpc_{uuid.uuid4().hex[:24]}",
        public_token=token,
        telegram_user_id=telegram_user_id,
        chat_id=chat_id,
        kind=FUTURES_MARKET_PENDING_KIND,
        payload_json=json.dumps(payload, ensure_ascii=False),
        expires_at=utc_now() + timedelta(minutes=15),
    )
    session.add(row)
    await session.flush()
    logger.info(
        "telegram_futures_market_pending_created user=%s chat=%s token_tail=%s",
        telegram_user_id,
        chat_id,
        token[-4:],
    )
    return token


async def create_futures_limit_pending(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    chat_id: int,
    symbol: str,
    side: str,
    quantity: str,
    price: str,
    open_close: str | None = None,
    execution_id: str | None = None,
) -> str:
    await revoke_futures_limit_pending_for_user(session, telegram_user_id)
    token = uuid.uuid4().hex[: TOKEN_HEX_BYTES * 2]
    payload: dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price,
        "scenarioId": "trade.futures.limit_order",
    }
    _optional_open_close_payload(payload, open_close)
    ex = execution_id.strip() if execution_id and execution_id.strip() else ""
    if ex:
        payload["executionId"] = ex
    row = AgentTelegramPendingConfirm(
        id=f"tgpc_{uuid.uuid4().hex[:24]}",
        public_token=token,
        telegram_user_id=telegram_user_id,
        chat_id=chat_id,
        kind=FUTURES_LIMIT_PENDING_KIND,
        payload_json=json.dumps(payload, ensure_ascii=False),
        expires_at=utc_now() + timedelta(minutes=15),
    )
    session.add(row)
    await session.flush()
    logger.info(
        "telegram_futures_limit_pending_created user=%s chat=%s token_tail=%s",
        telegram_user_id,
        chat_id,
        token[-4:],
    )
    return token


async def create_condition_pending(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    chat_id: int,
    symbol: str,
    side: str,
    quantity: str,
    trigger_price: str,
    trigger_type: str,
    order_type: str,
    price: str | None = None,
    open_close: str | None = None,
    execution_id: str | None = None,
) -> str:
    await revoke_condition_pending_for_user(session, telegram_user_id)
    token = uuid.uuid4().hex[: TOKEN_HEX_BYTES * 2]
    payload: dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "triggerPrice": trigger_price,
        "triggerType": trigger_type,
        "orderType": order_type,
        "scenarioId": "automation.condition_order",
    }
    if price and str(price).strip():
        payload["price"] = str(price).strip()
    _optional_open_close_payload(payload, open_close)
    ex = execution_id.strip() if execution_id and execution_id.strip() else ""
    if ex:
        payload["executionId"] = ex
    row = AgentTelegramPendingConfirm(
        id=f"tgpc_{uuid.uuid4().hex[:24]}",
        public_token=token,
        telegram_user_id=telegram_user_id,
        chat_id=chat_id,
        kind=CONDITION_PENDING_KIND,
        payload_json=json.dumps(payload, ensure_ascii=False),
        expires_at=utc_now() + timedelta(minutes=15),
    )
    session.add(row)
    await session.flush()
    logger.info(
        "telegram_condition_pending_created user=%s chat=%s token_tail=%s",
        telegram_user_id,
        chat_id,
        token[-4:],
    )
    return token


async def revoke_condition_cancel_pending_for_user(
    session: AsyncSession, telegram_user_id: int
) -> None:
    await session.execute(
        delete(AgentTelegramPendingConfirm).where(
            AgentTelegramPendingConfirm.telegram_user_id == telegram_user_id,
            AgentTelegramPendingConfirm.kind == CONDITION_CANCEL_PENDING_KIND,
        )
    )


async def create_condition_cancel_pending(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    chat_id: int,
    symbol: str,
    order_id: str,
    execution_id: str | None = None,
) -> str:
    await revoke_condition_cancel_pending_for_user(session, telegram_user_id)
    token = uuid.uuid4().hex[: TOKEN_HEX_BYTES * 2]
    payload: dict[str, Any] = {
        "symbol": symbol,
        "orderId": order_id,
        "scenarioId": "automation.condition_order_cancel",
    }
    ex = execution_id.strip() if execution_id and execution_id.strip() else ""
    if ex:
        payload["executionId"] = ex
    row = AgentTelegramPendingConfirm(
        id=f"tgpc_{uuid.uuid4().hex[:24]}",
        public_token=token,
        telegram_user_id=telegram_user_id,
        chat_id=chat_id,
        kind=CONDITION_CANCEL_PENDING_KIND,
        payload_json=json.dumps(payload, ensure_ascii=False),
        expires_at=utc_now() + timedelta(minutes=15),
    )
    session.add(row)
    await session.flush()
    return token


async def _revoke_margin_pending_for_user(
    session: AsyncSession,
    telegram_user_id: int,
    kinds: tuple[str, ...],
) -> None:
    await session.execute(
        delete(AgentTelegramPendingConfirm).where(
            AgentTelegramPendingConfirm.telegram_user_id == telegram_user_id,
            AgentTelegramPendingConfirm.kind.in_(kinds),
        )
    )


async def revoke_margin_market_pending_for_user(
    session: AsyncSession, telegram_user_id: int
) -> None:
    await _revoke_margin_pending_for_user(
        session,
        telegram_user_id,
        (MARGIN_MARKET_P1_KIND, MARGIN_MARKET_P2_KIND),
    )


async def revoke_margin_limit_pending_for_user(
    session: AsyncSession, telegram_user_id: int
) -> None:
    await _revoke_margin_pending_for_user(
        session,
        telegram_user_id,
        (MARGIN_LIMIT_P1_KIND, MARGIN_LIMIT_P2_KIND),
    )


def _margin_order_payload(
    *,
    scenario_id: str,
    symbol: str,
    side: str,
    quantity: str,
    price: str | None = None,
    execution_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "scenarioId": scenario_id,
    }
    if price is not None:
        payload["price"] = price
    ex = execution_id.strip() if execution_id and execution_id.strip() else ""
    if ex:
        payload["executionId"] = ex
    return payload


async def create_margin_market_pending_phase1(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    chat_id: int,
    symbol: str,
    side: str,
    quantity: str,
    execution_id: str | None = None,
) -> str:
    await revoke_margin_market_pending_for_user(session, telegram_user_id)
    token = uuid.uuid4().hex[: TOKEN_HEX_BYTES * 2]
    payload = _margin_order_payload(
        scenario_id="margin.cross.market_order",
        symbol=symbol,
        side=side,
        quantity=quantity,
        execution_id=execution_id,
    )
    row = AgentTelegramPendingConfirm(
        id=f"tgpc_{uuid.uuid4().hex[:24]}",
        public_token=token,
        telegram_user_id=telegram_user_id,
        chat_id=chat_id,
        kind=MARGIN_MARKET_P1_KIND,
        payload_json=json.dumps(payload, ensure_ascii=False),
        expires_at=utc_now() + timedelta(minutes=15),
    )
    session.add(row)
    await session.flush()
    return token


async def create_margin_market_pending_phase2(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    chat_id: int,
    payload: dict[str, Any],
) -> str:
    await revoke_margin_market_pending_for_user(session, telegram_user_id)
    token = uuid.uuid4().hex[: TOKEN_HEX_BYTES * 2]
    row = AgentTelegramPendingConfirm(
        id=f"tgpc_{uuid.uuid4().hex[:24]}",
        public_token=token,
        telegram_user_id=telegram_user_id,
        chat_id=chat_id,
        kind=MARGIN_MARKET_P2_KIND,
        payload_json=json.dumps(payload, ensure_ascii=False),
        expires_at=utc_now() + timedelta(minutes=15),
    )
    session.add(row)
    await session.flush()
    return token


async def create_margin_limit_pending_phase1(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    chat_id: int,
    symbol: str,
    side: str,
    quantity: str,
    price: str,
    execution_id: str | None = None,
) -> str:
    await revoke_margin_limit_pending_for_user(session, telegram_user_id)
    token = uuid.uuid4().hex[: TOKEN_HEX_BYTES * 2]
    payload = _margin_order_payload(
        scenario_id="margin.cross.limit_order",
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        execution_id=execution_id,
    )
    row = AgentTelegramPendingConfirm(
        id=f"tgpc_{uuid.uuid4().hex[:24]}",
        public_token=token,
        telegram_user_id=telegram_user_id,
        chat_id=chat_id,
        kind=MARGIN_LIMIT_P1_KIND,
        payload_json=json.dumps(payload, ensure_ascii=False),
        expires_at=utc_now() + timedelta(minutes=15),
    )
    session.add(row)
    await session.flush()
    return token


async def create_margin_limit_pending_phase2(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    chat_id: int,
    payload: dict[str, Any],
) -> str:
    await revoke_margin_limit_pending_for_user(session, telegram_user_id)
    token = uuid.uuid4().hex[: TOKEN_HEX_BYTES * 2]
    row = AgentTelegramPendingConfirm(
        id=f"tgpc_{uuid.uuid4().hex[:24]}",
        public_token=token,
        telegram_user_id=telegram_user_id,
        chat_id=chat_id,
        kind=MARGIN_LIMIT_P2_KIND,
        payload_json=json.dumps(payload, ensure_ascii=False),
        expires_at=utc_now() + timedelta(minutes=15),
    )
    session.add(row)
    await session.flush()
    return token


async def load_flash_pending_by_token(
    session: AsyncSession, token: str
) -> AgentTelegramPendingConfirm | None:
    if not _token_hex_ok(token):
        return None
    stmt = select(AgentTelegramPendingConfirm).where(
        AgentTelegramPendingConfirm.public_token == token
    )
    return (await session.execute(stmt)).scalar_one_or_none()


def pending_payload(row: AgentTelegramPendingConfirm) -> dict[str, Any]:
    try:
        raw = json.loads(row.payload_json)
        return raw if isinstance(raw, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


async def delete_pending_row(session: AsyncSession, row: AgentTelegramPendingConfirm) -> None:
    await session.delete(row)
    await session.flush()
