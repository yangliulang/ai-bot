"""Telegram ``callback_query`` — flash-convert confirm / cancel (DB-backed tokens)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.agent_runtime import utc_now
from chainup_agent.application.agent_execution_events import (
    append_execution_timeline_event,
    list_timeline_events_for_execution,
)
from chainup_agent.application.agent_execution_memory import (
    ExecutionAcceptRequest,
    ExecutionFinalizeRequest,
    execution_accept,
    execution_finalize,
)
from chainup_agent.application.agent_futures_trade import futures_order_for_bound_user
from chainup_agent.application.agent_futures_condition_trade import (
    futures_condition_order_cancel_for_bound_user,
    futures_condition_order_for_bound_user,
)
from chainup_agent.application.agent_margin_trade import margin_order_for_bound_user
from chainup_agent.application.agent_spot_trade import (
    spot_amend_limit_order_for_bound_user,
    spot_flash_convert_for_bound_user,
    spot_limit_order_for_bound_user,
)
from chainup_agent.application.telegram_app_error_user_message import (
    format_app_error_reply_for_telegram,
)
from chainup_agent.application.write_path_pipeline import (
    append_confirmation_required,
    append_user_confirmed,
    ensure_write_path_skill_spec_read_if_missing,
)
from chainup_agent.application.telegram_flash_pending import (
    AMEND_PENDING_KIND,
    FLASH_PENDING_KIND,
    CONDITION_CANCEL_PENDING_KIND,
    CONDITION_PENDING_KIND,
    FUTURES_LIMIT_PENDING_KIND,
    FUTURES_MARKET_PENDING_KIND,
    LIMIT_PENDING_KIND,
    delete_pending_row,
    load_flash_pending_by_token,
    parse_amend_callback_data,
    parse_flash_callback_data,
    parse_futures_limit_callback_data,
    parse_futures_market_callback_data,
    parse_condition_callback_data,
    parse_condition_cancel_callback_data,
    parse_limit_callback_data,
    parse_margin_limit_p1_callback_data,
    parse_margin_limit_p2_callback_data,
    parse_margin_market_p1_callback_data,
    parse_margin_market_p2_callback_data,
    pending_payload,
    create_margin_limit_pending_phase2,
    create_margin_market_pending_phase2,
    CB_MARGIN_LIMIT_P1_CANCEL,
    CB_MARGIN_LIMIT_P1_CONFIRM,
    CB_MARGIN_LIMIT_P2_CANCEL,
    CB_MARGIN_LIMIT_P2_CONFIRM,
    CB_MARGIN_MARKET_P1_CANCEL,
    CB_MARGIN_MARKET_P1_CONFIRM,
    CB_MARGIN_MARKET_P2_CANCEL,
    CB_MARGIN_MARKET_P2_CONFIRM,
    MARGIN_LIMIT_P1_KIND,
    MARGIN_LIMIT_P2_KIND,
    MARGIN_MARKET_P1_KIND,
    MARGIN_MARKET_P2_KIND,
)
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.domain.canonical_trading import timeline_obs_venue_canonical
from chainup_agent.infrastructure.persistence.base import get_session_factory
from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution
from chainup_agent.infrastructure.persistence.models.agent_telegram_pending_confirm import (
    AgentTelegramPendingConfirm,
)
from chainup_agent.infrastructure.telegram.bot_api import call_telegram_bot_api

logger = logging.getLogger(__name__)


def _telegram_callback_answer_expired_or_invalid(exc: AppError) -> bool:
    """Telegram rejects late or duplicate ``answerCallbackQuery`` calls."""
    msg = (exc.message or "").lower()
    return (
        "query is too old" in msg
        or "response timeout expired" in msg
        or "query id is invalid" in msg
    )


async def safe_answer_telegram_callback_query(
    bot_token: str,
    callback_query_id: str | int,
    *,
    text: str | None = None,
    show_alert: bool = False,
) -> None:
    """Same as ``answer_telegram_callback_query`` but ignores expired query ids."""
    try:
        await answer_telegram_callback_query(
            bot_token, callback_query_id, text=text, show_alert=show_alert
        )
    except AppError as exc:
        if _telegram_callback_answer_expired_or_invalid(exc):
            logger.warning(
                "telegram_callback_query_answer_expired_or_duplicate",
                extra={"detail": (exc.message or "")[:200]},
            )
            return
        raise


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


async def answer_telegram_callback_query(
    bot_token: str,
    callback_query_id: str | int,
    *,
    text: str | None = None,
    show_alert: bool = False,
) -> None:
    payload: dict[str, Any] = {"callback_query_id": str(callback_query_id)}
    if text:
        payload["text"] = text[:200]
    if show_alert:
        payload["show_alert"] = True
    await call_telegram_bot_api(bot_token, "answerCallbackQuery", json_payload=payload)


async def handle_telegram_callback_query_update(
    *,
    settings: Settings,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    callback_data: str,
) -> None:
    cd = callback_data.strip()
    from chainup_agent.application.telegram_clarify_callback import (
        handle_clarify_callback_query,
    )

    factory = get_session_factory()
    async with factory() as session:
        if await handle_clarify_callback_query(
            settings=settings,
            session=session,
            bot_token=bot_token,
            callback_query_id=callback_query_id,
            chat_id=chat_id,
            from_telegram_user_id=from_telegram_user_id,
            callback_data=cd,
        ):
            return

    handler: str | None = None
    parsed = parse_flash_callback_data(cd)
    if parsed is not None:
        handler = "flash"
    if parsed is None:
        parsed = parse_limit_callback_data(cd)
        if parsed is not None:
            handler = "limit"
    if parsed is None:
        parsed = parse_amend_callback_data(cd)
        if parsed is not None:
            handler = "amend"
    if parsed is None:
        parsed = parse_futures_market_callback_data(cd)
        if parsed is not None:
            handler = "futures_market"
    if parsed is None:
        parsed = parse_futures_limit_callback_data(cd)
        if parsed is not None:
            handler = "futures_limit"
    if parsed is None:
        parsed = parse_condition_cancel_callback_data(cd)
        if parsed is not None:
            handler = "condition_cancel"
    if parsed is None:
        parsed = parse_condition_callback_data(cd)
        if parsed is not None:
            handler = "condition_order"
    if parsed is None:
        parsed = parse_margin_market_p1_callback_data(cd)
        if parsed is not None:
            handler = "margin_market_p1"
    if parsed is None:
        parsed = parse_margin_market_p2_callback_data(cd)
        if parsed is not None:
            handler = "margin_market_p2"
    if parsed is None:
        parsed = parse_margin_limit_p1_callback_data(cd)
        if parsed is not None:
            handler = "margin_limit_p1"
    if parsed is None:
        parsed = parse_margin_limit_p2_callback_data(cd)
        if parsed is not None:
            handler = "margin_limit_p2"
    if parsed is None or handler is None:
        await safe_answer_telegram_callback_query(
            bot_token,
            callback_query_id,
            text="无法识别该操作，请重新发起。",
        )
        return

    action, token = parsed
    factory = get_session_factory()

    async with factory() as session:
        try:
            row = await load_flash_pending_by_token(session, token)
            if row is None:
                await safe_answer_telegram_callback_query(
                    bot_token,
                    callback_query_id,
                    text="该确认已失效，请重新发起。",
                )
                return
            if row.kind not in (
                FLASH_PENDING_KIND,
                LIMIT_PENDING_KIND,
                AMEND_PENDING_KIND,
                FUTURES_MARKET_PENDING_KIND,
                FUTURES_LIMIT_PENDING_KIND,
                CONDITION_PENDING_KIND,
                MARGIN_MARKET_P1_KIND,
                MARGIN_MARKET_P2_KIND,
                MARGIN_LIMIT_P1_KIND,
                MARGIN_LIMIT_P2_KIND,
            ):
                await safe_answer_telegram_callback_query(
                    bot_token,
                    callback_query_id,
                    text="无法识别该操作，请重新发起。",
                )
                return
            if row.telegram_user_id != from_telegram_user_id or row.chat_id != chat_id:
                await safe_answer_telegram_callback_query(
                    bot_token, callback_query_id, text="身份与会话不匹配。"
                )
                return

            if _as_utc(row.expires_at) < utc_now():
                await delete_pending_row(session, row)
                await safe_answer_telegram_callback_query(
                    bot_token,
                    callback_query_id,
                    text="确认已过期，请重新发起。",
                )
                await session.commit()
                return

            if row.kind == FLASH_PENDING_KIND:
                await _dispatch_flash_callback(
                    session=session,
                    settings=settings,
                    bot_token=bot_token,
                    callback_query_id=callback_query_id,
                    chat_id=chat_id,
                    from_telegram_user_id=from_telegram_user_id,
                    action=action,
                    row=row,
                )
            elif row.kind == LIMIT_PENDING_KIND:
                await _dispatch_limit_callback(
                    session=session,
                    settings=settings,
                    bot_token=bot_token,
                    callback_query_id=callback_query_id,
                    chat_id=chat_id,
                    from_telegram_user_id=from_telegram_user_id,
                    action=action,
                    row=row,
                )
            elif row.kind == AMEND_PENDING_KIND:
                await _dispatch_amend_callback(
                    session=session,
                    settings=settings,
                    bot_token=bot_token,
                    callback_query_id=callback_query_id,
                    chat_id=chat_id,
                    from_telegram_user_id=from_telegram_user_id,
                    action=action,
                    row=row,
                )
            elif row.kind == FUTURES_MARKET_PENDING_KIND:
                await _dispatch_futures_market_callback(
                    session=session,
                    settings=settings,
                    bot_token=bot_token,
                    callback_query_id=callback_query_id,
                    chat_id=chat_id,
                    from_telegram_user_id=from_telegram_user_id,
                    action=action,
                    row=row,
                )
            elif row.kind == FUTURES_LIMIT_PENDING_KIND:
                await _dispatch_futures_limit_callback(
                    session=session,
                    settings=settings,
                    bot_token=bot_token,
                    callback_query_id=callback_query_id,
                    chat_id=chat_id,
                    from_telegram_user_id=from_telegram_user_id,
                    action=action,
                    row=row,
                )
            elif row.kind == CONDITION_CANCEL_PENDING_KIND:
                await _dispatch_condition_cancel_callback(
                    session=session,
                    settings=settings,
                    bot_token=bot_token,
                    callback_query_id=callback_query_id,
                    chat_id=chat_id,
                    from_telegram_user_id=from_telegram_user_id,
                    action=action,
                    row=row,
                )
            elif row.kind == CONDITION_PENDING_KIND:
                await _dispatch_condition_order_callback(
                    session=session,
                    settings=settings,
                    bot_token=bot_token,
                    callback_query_id=callback_query_id,
                    chat_id=chat_id,
                    from_telegram_user_id=from_telegram_user_id,
                    action=action,
                    row=row,
                )
            elif row.kind == MARGIN_MARKET_P1_KIND:
                await _dispatch_margin_market_p1_callback(
                    session=session,
                    settings=settings,
                    bot_token=bot_token,
                    callback_query_id=callback_query_id,
                    chat_id=chat_id,
                    from_telegram_user_id=from_telegram_user_id,
                    action=action,
                    row=row,
                )
            elif row.kind == MARGIN_MARKET_P2_KIND:
                await _dispatch_margin_market_p2_callback(
                    session=session,
                    settings=settings,
                    bot_token=bot_token,
                    callback_query_id=callback_query_id,
                    chat_id=chat_id,
                    from_telegram_user_id=from_telegram_user_id,
                    action=action,
                    row=row,
                )
            elif row.kind == MARGIN_LIMIT_P1_KIND:
                await _dispatch_margin_limit_p1_callback(
                    session=session,
                    settings=settings,
                    bot_token=bot_token,
                    callback_query_id=callback_query_id,
                    chat_id=chat_id,
                    from_telegram_user_id=from_telegram_user_id,
                    action=action,
                    row=row,
                )
            else:
                await _dispatch_margin_limit_p2_callback(
                    session=session,
                    settings=settings,
                    bot_token=bot_token,
                    callback_query_id=callback_query_id,
                    chat_id=chat_id,
                    from_telegram_user_id=from_telegram_user_id,
                    action=action,
                    row=row,
                )
            await session.commit()
        except OperationalError:
            logger.warning("telegram_callback_db_operational_error")
            await session.rollback()
            await safe_answer_telegram_callback_query(
                bot_token,
                callback_query_id,
                text="服务暂时不可用，请稍后重试。",
            )
        except Exception:
            logger.exception("telegram_callback_unhandled")
            await session.rollback()
            await safe_answer_telegram_callback_query(
                bot_token,
                callback_query_id,
                text="处理失败，请稍后重试。",
            )


async def _dispatch_flash_callback(
    *,
    session: AsyncSession,
    settings: Settings,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    action: str,
    row: AgentTelegramPendingConfirm,
) -> None:
    if action == "cancel":
        from chainup_agent.application.session_concurrency import release_session_write_gates

        release_session_write_gates(f"tg:{chat_id}")
        await delete_pending_row(session, row)
        await safe_answer_telegram_callback_query(bot_token, callback_query_id, text="已取消")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "已取消本次现货闪兑，未向交易所提交订单。",
            },
        )
        return

    # confirm
    pay = pending_payload(row)
    sym = str(pay.get("symbol") or "").strip()
    side = str(pay.get("side") or "").strip().upper()
    qty = str(pay.get("quantity") or "").strip()
    uid = str(from_telegram_user_id)
    pending_eid = str(pay.get("executionId") or "").strip()

    reuse_turn = False
    if pending_eid:
        ex_row = await session.get(AgentExecution, pending_eid)
        if (
            ex_row is not None
            and ex_row.user_id == uid
            and ex_row.state == "ACCEPTED"
            and ex_row.scenario_id == "trade.spot.flash_convert"
        ):
            eid = pending_eid
            reuse_turn = True
        else:
            acc = await execution_accept(
                session,
                ExecutionAcceptRequest(
                    user_id=uid,
                    scenario_id="trade.spot.flash_convert",
                    channel="telegram",
                ),
                source="telegram_callback",
            )
            eid = acc.execution_id
    else:
        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id=uid,
                scenario_id="trade.spot.flash_convert",
                channel="telegram",
            ),
            source="telegram_callback",
        )
        eid = acc.execution_id

    try:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="confirm_accept",
            outcome="success",
            payload={
                "scenarioId": "trade.spot.flash_convert",
                "channel": "telegram_callback",
                "symbol": sym,
                "side": side,
                "quantityRequested": qty,
                "reuseTurnExecution": reuse_turn,
                "transitionTrigger": "confirmation.type_a_callback",
            },
        )
        # One successful answer per callback; do this before the exchange round-trip.
        await safe_answer_telegram_callback_query(bot_token, callback_query_id)
        out = await spot_flash_convert_for_bound_user(
            session=session,
            settings=settings,
            user_id=uid,
            symbol=sym,
            side=side,
            volume=qty,
            new_client_order_id=None,
            timeline_execution_id=eid,
            timeline_channel="telegram_callback",
            timeline_include_quote=not reuse_turn,
        )
        oid = out.get("orderIdString") or out.get("orderId")
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="SUCCESS", note="flash_convert_telegram_cb"
            ),
        )
        lines = [
            "—— 现货闪兑已提交 ——",
            f"交易对：`{out.get('symbol') or sym}`",
            f"方向：`{side}`",
            f"数量：`{qty}`",
            f"订单号：`{oid}`",
        ]
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={"chat_id": chat_id, "text": "\n".join(lines)[:4096]},
        )
    except AppError as exc:
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="FAILED",
                note=f"{exc.code}:{exc.message[:500]}",
            ),
        )
        user_txt = await format_app_error_reply_for_telegram(session, settings, exc)
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": user_txt[:4096],
            },
        )
    except Exception:
        logger.exception("telegram_flash_convert_callback_failed exec_id=%s", eid)
        await delete_pending_row(session, row)
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="submit_order",
            outcome="unknown",
            payload={
                **timeline_obs_venue_canonical(),
                "scenarioId": "trade.spot.flash_convert",
                "channel": "telegram_callback",
                "symbol": sym,
                "side": side,
                "quantityRequested": qty,
                "note": "flash_convert_exception",
            },
        )
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="trading.exchange_private",
            step_kind="submit_order",
            outcome="unknown",
            payload={
                **timeline_obs_venue_canonical(),
                "methodPathSummary": "POST /sapi/v2/order",
                "exchangeOutcome": "unknown",
                "note": "flash_convert_exception",
            },
        )
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="FAILED", note="flash_convert_exception"
            ),
        )
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "现货闪兑提交时出现异常，请稍后重试；若持续发生请联系运维。",
            },
        )


async def _dispatch_limit_callback(
    *,
    session: AsyncSession,
    settings: Settings,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    action: str,
    row: AgentTelegramPendingConfirm,
) -> None:
    if action == "cancel":
        from chainup_agent.application.session_concurrency import release_session_write_gates

        release_session_write_gates(f"tg:{chat_id}")
        await delete_pending_row(session, row)
        await safe_answer_telegram_callback_query(bot_token, callback_query_id, text="已取消")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "已取消本次现货限价委托，未向交易所提交订单。",
            },
        )
        return

    pay = pending_payload(row)
    sym = str(pay.get("symbol") or "").strip()
    side = str(pay.get("side") or "").strip().upper()
    qty = str(pay.get("quantity") or "").strip()
    price = str(pay.get("price") or "").strip()
    tif = str(pay.get("timeInForce") or "GTC").strip() or "GTC"
    uid = str(from_telegram_user_id)
    pending_eid = str(pay.get("executionId") or "").strip()

    reuse_turn = False
    if pending_eid:
        ex_row = await session.get(AgentExecution, pending_eid)
        if (
            ex_row is not None
            and ex_row.user_id == uid
            and ex_row.state == "ACCEPTED"
            and ex_row.scenario_id == "trade.spot.limit_order"
        ):
            eid = pending_eid
            reuse_turn = True
        else:
            acc = await execution_accept(
                session,
                ExecutionAcceptRequest(
                    user_id=uid,
                    scenario_id="trade.spot.limit_order",
                    channel="telegram",
                ),
                source="telegram_callback",
            )
            eid = acc.execution_id
    else:
        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id=uid,
                scenario_id="trade.spot.limit_order",
                channel="telegram",
            ),
            source="telegram_callback",
        )
        eid = acc.execution_id

    try:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="confirm_accept",
            outcome="success",
            payload={
                "scenarioId": "trade.spot.limit_order",
                "channel": "telegram_callback",
                "symbol": sym,
                "side": side,
                "quantityRequested": qty,
                "limitPrice": price,
                "timeInForce": tif,
                "reuseTurnExecution": reuse_turn,
                "transitionTrigger": "confirmation.type_a_callback",
            },
        )
        await safe_answer_telegram_callback_query(bot_token, callback_query_id)
        await ensure_write_path_skill_spec_read_if_missing(
            session,
            execution_id=eid,
            user_id=uid,
            scenario_id="trade.spot.limit_order",
            channel="telegram_callback",
        )
        rows = await list_timeline_events_for_execution(session, execution_public_id=eid)
        if not any(r.event_type == "confirmation.required" for r in rows):
            await append_confirmation_required(
                session,
                execution_id=eid,
                user_id=uid,
                scenario_id="trade.spot.limit_order",
                channel="telegram_callback",
            )
        await append_user_confirmed(
            session,
            execution_id=eid,
            user_id=uid,
            scenario_id="trade.spot.limit_order",
            channel="telegram_callback",
            extra={
                "symbol": sym,
                "side": side,
                "quantityRequested": qty,
                "limitPrice": price,
            },
        )
        out = await spot_limit_order_for_bound_user(
            session=session,
            settings=settings,
            user_id=uid,
            symbol=sym,
            side=side,
            volume=qty,
            price=price,
            time_in_force=tif,
            new_client_order_id=None,
            timeline_execution_id=eid,
            timeline_channel="telegram_callback",
            timeline_include_quote=not reuse_turn,
        )
        oid = out.get("orderIdString") or out.get("orderId")
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="SUCCESS", note="limit_order_telegram_cb"
            ),
        )
        lines = [
            "—— 现货限价单已提交 ——",
            f"交易对：`{out.get('symbol') or sym}`",
            f"方向：`{side}`",
            f"数量：`{qty}`",
            f"限价：`{price}`",
            f"时效：`{tif}`",
            f"订单号：`{oid}`",
        ]
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={"chat_id": chat_id, "text": "\n".join(lines)[:4096]},
        )
    except AppError as exc:
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="FAILED",
                note=f"{exc.code}:{exc.message[:500]}",
            ),
        )
        user_txt = await format_app_error_reply_for_telegram(session, settings, exc)
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": user_txt[:4096],
            },
        )
    except Exception:
        logger.exception("telegram_limit_order_callback_failed exec_id=%s", eid)
        await delete_pending_row(session, row)
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="submit_order",
            outcome="unknown",
            payload={
                **timeline_obs_venue_canonical(),
                "scenarioId": "trade.spot.limit_order",
                "channel": "telegram_callback",
                "symbol": sym,
                "side": side,
                "quantityRequested": qty,
                "limitPrice": price,
                "note": "limit_order_exception",
            },
        )
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="trading.exchange_private",
            step_kind="submit_order",
            outcome="unknown",
            payload={
                **timeline_obs_venue_canonical(),
                "methodPathSummary": "POST /sapi/v2/order",
                "exchangeOutcome": "unknown",
                "note": "limit_order_exception",
            },
        )
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="FAILED", note="limit_order_exception"
            ),
        )
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "现货限价单提交时出现异常，请稍后重试；若持续发生请联系运维。",
            },
        )


async def _dispatch_amend_callback(
    *,
    session: AsyncSession,
    settings: Settings,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    action: str,
    row: AgentTelegramPendingConfirm,
) -> None:
    if action == "cancel":
        from chainup_agent.application.session_concurrency import release_session_write_gates

        release_session_write_gates(f"tg:{chat_id}")
        await delete_pending_row(session, row)
        await safe_answer_telegram_callback_query(bot_token, callback_query_id, text="已取消")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "已取消本次现货改单，未向交易所提交撤单/挂单。",
            },
        )
        return

    pay = pending_payload(row)
    sym = str(pay.get("symbol") or "").strip()
    oid = str(pay.get("orderId") or "").strip()
    price = str(pay.get("price") or "").strip()
    qty = str(pay.get("quantity") or "").strip()
    tif = str(pay.get("timeInForce") or "GTC").strip() or "GTC"
    uid = str(from_telegram_user_id)
    pending_eid = str(pay.get("executionId") or "").strip()

    reuse_turn = False
    if pending_eid:
        ex_row = await session.get(AgentExecution, pending_eid)
        if (
            ex_row is not None
            and ex_row.user_id == uid
            and ex_row.state == "ACCEPTED"
            and ex_row.scenario_id == "trade.spot.amend_limit_order"
        ):
            eid = pending_eid
            reuse_turn = True
        else:
            acc = await execution_accept(
                session,
                ExecutionAcceptRequest(
                    user_id=uid,
                    scenario_id="trade.spot.amend_limit_order",
                    channel="telegram",
                ),
                source="telegram_callback",
            )
            eid = acc.execution_id
    else:
        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id=uid,
                scenario_id="trade.spot.amend_limit_order",
                channel="telegram",
            ),
            source="telegram_callback",
        )
        eid = acc.execution_id

    try:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="confirm_accept",
            outcome="success",
            payload={
                "scenarioId": "trade.spot.amend_limit_order",
                "channel": "telegram_callback",
                "symbol": sym,
                "orderId": oid,
                "limitPrice": price,
                "quantityRequested": qty,
                "timeInForce": tif,
                "reuseTurnExecution": reuse_turn,
                "transitionTrigger": "confirmation.type_a_callback",
            },
        )
        await safe_answer_telegram_callback_query(bot_token, callback_query_id)
        await ensure_write_path_skill_spec_read_if_missing(
            session,
            execution_id=eid,
            user_id=uid,
            scenario_id="trade.spot.amend_limit_order",
            channel="telegram_callback",
        )
        rows_amend = await list_timeline_events_for_execution(session, execution_public_id=eid)
        if not any(r.event_type == "confirmation.required" for r in rows_amend):
            await append_confirmation_required(
                session,
                execution_id=eid,
                user_id=uid,
                scenario_id="trade.spot.amend_limit_order",
                channel="telegram_callback",
            )
        await append_user_confirmed(
            session,
            execution_id=eid,
            user_id=uid,
            scenario_id="trade.spot.amend_limit_order",
            channel="telegram_callback",
            extra={"symbol": sym, "orderId": oid},
        )
        out = await spot_amend_limit_order_for_bound_user(
            session=session,
            settings=settings,
            user_id=uid,
            symbol=sym,
            order_id=oid,
            price=price,
            volume=qty,
            time_in_force=tif,
            new_client_order_id=None,
            timeline_execution_id=eid,
            timeline_channel="telegram_callback",
            timeline_include_quote=not reuse_turn,
        )
        new_oid = out.get("orderIdString") or out.get("orderId")
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="SUCCESS", note="spot_amend_telegram_cb"
            ),
        )
        lines = [
            "修改现货限价挂单 · 新委托已挂上",
            f"交易对：`{out.get('symbol') or sym}`",
            f"方向：`{out.get('side') or pay.get('side')}`",
            f"数量：`{qty}`",
            f"限价：`{price}`",
            f"新订单号：`{new_oid}`",
            f"原订单号：`{oid}`",
        ]
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={"chat_id": chat_id, "text": "\n".join(lines)[:4096]},
        )
    except AppError as exc:
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="FAILED",
                note=f"{exc.code}:{exc.message[:500]}",
            ),
        )
        user_txt = await format_app_error_reply_for_telegram(session, settings, exc)
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": user_txt[:4096],
            },
        )
    except Exception:
        logger.exception("telegram_spot_amend_callback_failed exec_id=%s", eid)
        await delete_pending_row(session, row)
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="submit_order",
            outcome="unknown",
            payload={
                **timeline_obs_venue_canonical(),
                "scenarioId": "trade.spot.amend_limit_order",
                "channel": "telegram_callback",
                "symbol": sym,
                "orderId": oid,
                "limitPrice": price,
                "quantityRequested": qty,
                "note": "spot_amend_exception",
            },
        )
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="FAILED", note="spot_amend_exception"
            ),
        )
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "现货改单提交时出现异常，请稍后查单；若持续发生请联系运维。",
            },
        )


async def _dispatch_futures_market_callback(
    *,
    session: AsyncSession,
    settings: Settings,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    action: str,
    row: AgentTelegramPendingConfirm,
) -> None:
    scenario_id = "trade.futures.market_order"
    if action == "cancel":
        from chainup_agent.application.session_concurrency import release_session_write_gates

        release_session_write_gates(f"tg:{chat_id}")
        await delete_pending_row(session, row)
        await safe_answer_telegram_callback_query(bot_token, callback_query_id, text="已取消")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "已取消本次合约市价委托，未向交易所提交订单。",
            },
        )
        return

    pay = pending_payload(row)
    sym = str(pay.get("symbol") or "").strip()
    side = str(pay.get("side") or "").strip().upper()
    qty = str(pay.get("quantity") or "").strip()
    oc_raw = pay.get("openClose")
    open_close = str(oc_raw).strip().upper() if oc_raw else None
    uid = str(from_telegram_user_id)
    pending_eid = str(pay.get("executionId") or "").strip()

    reuse_turn = False
    if pending_eid:
        ex_row = await session.get(AgentExecution, pending_eid)
        if (
            ex_row is not None
            and ex_row.user_id == uid
            and ex_row.state == "ACCEPTED"
            and ex_row.scenario_id == scenario_id
        ):
            eid = pending_eid
            reuse_turn = True
        else:
            acc = await execution_accept(
                session,
                ExecutionAcceptRequest(
                    user_id=uid,
                    scenario_id=scenario_id,
                    channel="telegram",
                ),
                source="telegram_callback",
            )
            eid = acc.execution_id
    else:
        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id=uid,
                scenario_id=scenario_id,
                channel="telegram",
            ),
            source="telegram_callback",
        )
        eid = acc.execution_id

    try:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="confirm_accept",
            outcome="success",
            payload={
                "scenarioId": scenario_id,
                "channel": "telegram_callback",
                "symbol": sym,
                "side": side,
                "quantityRequested": qty,
                "openClose": open_close,
                "reuseTurnExecution": reuse_turn,
                "transitionTrigger": "confirmation.type_a_callback",
            },
        )
        await safe_answer_telegram_callback_query(bot_token, callback_query_id)
        out = await futures_order_for_bound_user(
            session=session,
            settings=settings,
            user_id=uid,
            symbol=sym,
            side=side,
            order_type="MARKET",
            volume=qty,
            open_close=open_close,
            scenario_id=scenario_id,
            timeline_execution_id=eid,
            timeline_channel="telegram_callback",
        )
        oid = out.get("orderIdString") or out.get("orderId")
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="SUCCESS", note="futures_market_telegram_cb"
            ),
        )
        lines = [
            "—— 合约市价单已提交 ——",
            f"合约：`{out.get('symbol') or sym}`",
            f"方向：`{side}`",
            f"数量：`{qty}`",
        ]
        if open_close:
            lines.append(f"开平：`{open_close}`")
        lines.append(f"订单号：`{oid}`")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={"chat_id": chat_id, "text": "\n".join(lines)[:4096]},
        )
    except AppError as exc:
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="FAILED",
                note=f"{exc.code}:{exc.message[:500]}",
            ),
        )
        user_txt = await format_app_error_reply_for_telegram(session, settings, exc)
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": user_txt[:4096],
            },
        )
    except Exception:
        logger.exception("telegram_futures_market_callback_failed exec_id=%s", eid)
        await delete_pending_row(session, row)
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="submit_order",
            outcome="unknown",
            payload={
                **timeline_obs_venue_canonical(),
                "scenarioId": scenario_id,
                "channel": "telegram_callback",
                "symbol": sym,
                "side": side,
                "quantityRequested": qty,
                "note": "futures_market_exception",
            },
        )
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="FAILED", note="futures_market_exception"
            ),
        )
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "合约市价单提交时出现异常，请稍后重试；若持续发生请联系运维。",
            },
        )


async def _dispatch_futures_limit_callback(
    *,
    session: AsyncSession,
    settings: Settings,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    action: str,
    row: AgentTelegramPendingConfirm,
) -> None:
    scenario_id = "trade.futures.limit_order"
    if action == "cancel":
        from chainup_agent.application.session_concurrency import release_session_write_gates

        release_session_write_gates(f"tg:{chat_id}")
        await delete_pending_row(session, row)
        await safe_answer_telegram_callback_query(bot_token, callback_query_id, text="已取消")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "已取消本次合约限价委托，未向交易所提交订单。",
            },
        )
        return

    pay = pending_payload(row)
    sym = str(pay.get("symbol") or "").strip()
    side = str(pay.get("side") or "").strip().upper()
    qty = str(pay.get("quantity") or "").strip()
    price = str(pay.get("price") or "").strip()
    oc_raw = pay.get("openClose")
    open_close = str(oc_raw).strip().upper() if oc_raw else None
    uid = str(from_telegram_user_id)
    pending_eid = str(pay.get("executionId") or "").strip()

    reuse_turn = False
    if pending_eid:
        ex_row = await session.get(AgentExecution, pending_eid)
        if (
            ex_row is not None
            and ex_row.user_id == uid
            and ex_row.state == "ACCEPTED"
            and ex_row.scenario_id == scenario_id
        ):
            eid = pending_eid
            reuse_turn = True
        else:
            acc = await execution_accept(
                session,
                ExecutionAcceptRequest(
                    user_id=uid,
                    scenario_id=scenario_id,
                    channel="telegram",
                ),
                source="telegram_callback",
            )
            eid = acc.execution_id
    else:
        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id=uid,
                scenario_id=scenario_id,
                channel="telegram",
            ),
            source="telegram_callback",
        )
        eid = acc.execution_id

    try:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="confirm_accept",
            outcome="success",
            payload={
                "scenarioId": scenario_id,
                "channel": "telegram_callback",
                "symbol": sym,
                "side": side,
                "quantityRequested": qty,
                "limitPrice": price,
                "openClose": open_close,
                "reuseTurnExecution": reuse_turn,
                "transitionTrigger": "confirmation.type_a_callback",
            },
        )
        await safe_answer_telegram_callback_query(bot_token, callback_query_id)
        out = await futures_order_for_bound_user(
            session=session,
            settings=settings,
            user_id=uid,
            symbol=sym,
            side=side,
            order_type="LIMIT",
            volume=qty,
            price=price,
            open_close=open_close,
            scenario_id=scenario_id,
            timeline_execution_id=eid,
            timeline_channel="telegram_callback",
        )
        oid = out.get("orderIdString") or out.get("orderId")
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="SUCCESS", note="futures_limit_telegram_cb"
            ),
        )
        lines = [
            "—— 合约限价单已提交 ——",
            f"合约：`{out.get('symbol') or sym}`",
            f"方向：`{side}`",
            f"数量：`{qty}`",
            f"限价：`{price}`",
        ]
        if open_close:
            lines.append(f"开平：`{open_close}`")
        lines.append(f"订单号：`{oid}`")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={"chat_id": chat_id, "text": "\n".join(lines)[:4096]},
        )
    except AppError as exc:
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="FAILED",
                note=f"{exc.code}:{exc.message[:500]}",
            ),
        )
        user_txt = await format_app_error_reply_for_telegram(session, settings, exc)
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": user_txt[:4096],
            },
        )
    except Exception:
        logger.exception("telegram_futures_limit_callback_failed exec_id=%s", eid)
        await delete_pending_row(session, row)
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="submit_order",
            outcome="unknown",
            payload={
                **timeline_obs_venue_canonical(),
                "scenarioId": scenario_id,
                "channel": "telegram_callback",
                "symbol": sym,
                "side": side,
                "quantityRequested": qty,
                "limitPrice": price,
                "note": "futures_limit_exception",
            },
        )
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="FAILED", note="futures_limit_exception"
            ),
        )
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "合约限价单提交时出现异常，请稍后重试；若持续发生请联系运维。",
            },
        )


async def _dispatch_condition_cancel_callback(
    *,
    session: AsyncSession,
    settings: Settings,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    action: str,
    row: AgentTelegramPendingConfirm,
) -> None:
    scenario_id = "automation.condition_order_cancel"
    if action == "cancel":
        from chainup_agent.application.session_concurrency import release_session_write_gates

        release_session_write_gates(f"tg:{chat_id}")
        await delete_pending_row(session, row)
        await safe_answer_telegram_callback_query(bot_token, callback_query_id, text="已取消")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "已取消本次条件单撤销，未向交易所提交撤单。",
            },
        )
        return

    pay = pending_payload(row)
    sym = str(pay.get("symbol") or "").strip()
    oid = str(pay.get("orderId") or "").strip()
    uid = str(from_telegram_user_id)
    pending_eid = str(pay.get("executionId") or "").strip()

    reuse_turn = False
    if pending_eid:
        ex_row = await session.get(AgentExecution, pending_eid)
        if (
            ex_row is not None
            and ex_row.user_id == uid
            and ex_row.state == "ACCEPTED"
            and ex_row.scenario_id == scenario_id
        ):
            eid = pending_eid
            reuse_turn = True
        else:
            acc = await execution_accept(
                session,
                ExecutionAcceptRequest(
                    user_id=uid,
                    scenario_id=scenario_id,
                    channel="telegram",
                ),
                source="telegram_callback",
            )
            eid = acc.execution_id
    else:
        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id=uid,
                scenario_id=scenario_id,
                channel="telegram",
            ),
            source="telegram_callback",
        )
        eid = acc.execution_id

    try:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="confirm_accept",
            outcome="success",
            payload={
                "scenarioId": scenario_id,
                "channel": "telegram_callback",
                "symbol": sym,
                "orderId": oid,
                "reuseTurnExecution": reuse_turn,
                "transitionTrigger": "confirmation.type_a_callback",
            },
        )
        await safe_answer_telegram_callback_query(bot_token, callback_query_id)
        out = await futures_condition_order_cancel_for_bound_user(
            session=session,
            settings=settings,
            user_id=uid,
            symbol=sym,
            order_id=oid,
            timeline_execution_id=eid,
            timeline_channel="telegram_callback",
        )
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="SUCCESS",
                note="condition_cancel_telegram_cb",
            ),
        )
        oid_out = out.get("orderIdString") or out.get("orderId") or "—"
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": (
                    f"条件单已撤销。\n"
                    f"合约：`{out.get('contractName') or sym}`\n"
                    f"订单号：`{oid_out}`"
                ),
            },
        )
    except AppError as exc:
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="FAILED", note="condition_cancel_telegram_rejected"
            ),
        )
        msg = await format_app_error_reply_for_telegram(session, settings, exc)
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={"chat_id": chat_id, "text": msg},
        )
    except Exception:
        logger.exception("telegram_condition_cancel_callback_failed exec_id=%s", eid)
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="FAILED", note="condition_cancel_exception"
            ),
        )
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "条件单撤销时出现异常，请稍后重试；若持续发生请联系运维。",
            },
        )


async def _dispatch_condition_order_callback(
    *,
    session: AsyncSession,
    settings: Settings,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    action: str,
    row: AgentTelegramPendingConfirm,
) -> None:
    scenario_id = "automation.condition_order"
    if action == "cancel":
        from chainup_agent.application.session_concurrency import release_session_write_gates

        release_session_write_gates(f"tg:{chat_id}")
        await delete_pending_row(session, row)
        await safe_answer_telegram_callback_query(bot_token, callback_query_id, text="已取消")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "已取消本次条件单，未向交易所提交委托。",
            },
        )
        return

    pay = pending_payload(row)
    sym = str(pay.get("symbol") or "").strip()
    side = str(pay.get("side") or "").strip().upper()
    qty = str(pay.get("quantity") or "").strip()
    tp = str(pay.get("triggerPrice") or "").strip()
    tt = str(pay.get("triggerType") or "").strip().upper()
    ot = str(pay.get("orderType") or "MARKET").strip().upper()
    price_raw = pay.get("price")
    price = str(price_raw).strip() if price_raw else None
    oc_raw = pay.get("openClose")
    open_close = str(oc_raw).strip().upper() if oc_raw else None
    uid = str(from_telegram_user_id)
    pending_eid = str(pay.get("executionId") or "").strip()

    reuse_turn = False
    if pending_eid:
        ex_row = await session.get(AgentExecution, pending_eid)
        if (
            ex_row is not None
            and ex_row.user_id == uid
            and ex_row.state == "ACCEPTED"
            and ex_row.scenario_id == scenario_id
        ):
            eid = pending_eid
            reuse_turn = True
        else:
            acc = await execution_accept(
                session,
                ExecutionAcceptRequest(
                    user_id=uid,
                    scenario_id=scenario_id,
                    channel="telegram",
                ),
                source="telegram_callback",
            )
            eid = acc.execution_id
    else:
        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id=uid,
                scenario_id=scenario_id,
                channel="telegram",
            ),
            source="telegram_callback",
        )
        eid = acc.execution_id

    try:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="confirm_accept",
            outcome="success",
            payload={
                "scenarioId": scenario_id,
                "channel": "telegram_callback",
                "symbol": sym,
                "side": side,
                "quantityRequested": qty,
                "triggerPrice": tp,
                "triggerType": tt,
                "orderType": ot,
                "openClose": open_close,
                "reuseTurnExecution": reuse_turn,
                "transitionTrigger": "confirmation.type_a_callback",
            },
        )
        await safe_answer_telegram_callback_query(bot_token, callback_query_id)
        out = await futures_condition_order_for_bound_user(
            session=session,
            settings=settings,
            user_id=uid,
            symbol=sym,
            side=side,  # type: ignore[arg-type]
            order_type=ot,  # type: ignore[arg-type]
            volume=qty,
            trigger_price=tp,
            trigger_type=tt,  # type: ignore[arg-type]
            price=price,
            open_close=open_close,
            scenario_id=scenario_id,
            timeline_execution_id=eid,
            timeline_channel="telegram_callback",
        )
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="SUCCESS", note="condition_order_telegram_cb"
            ),
        )
        oid = out.get("orderIdString") or out.get("orderId") or "—"
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": (
                    f"条件单已提交。\n"
                    f"合约：`{out.get('contractName') or sym}`\n"
                    f"触发价：`{tp}`（`{tt}`）\n"
                    f"订单号：`{oid}`"
                ),
            },
        )
    except AppError as exc:
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="FAILED", note="condition_order_telegram_rejected"
            ),
        )
        msg = await format_app_error_reply_for_telegram(session, settings, exc)
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={"chat_id": chat_id, "text": msg},
        )
    except Exception:
        logger.exception("telegram_condition_order_callback_failed exec_id=%s", eid)
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="FAILED", note="condition_order_exception"
            ),
        )
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "条件单提交时出现异常，请稍后重试；若持续发生请联系运维。",
            },
        )


def _margin_side_zh(side: str) -> str:
    return "借钱买入" if side == "BUY" else "卖出/还款" if side == "SELL" else side


def _format_margin_phase2_body(pay: dict[str, Any], *, order_type: str) -> str:
    sym = str(pay.get("symbol") or "?")
    side = str(pay.get("side") or "?").upper()
    qty = str(pay.get("quantity") or "?")
    lines = [
        "—— 全仓杠杆 · 第二次确认 ——",
        "模式：`全仓 cross`",
        f"交易对：`{sym}`",
        f"方向：`{_margin_side_zh(side)}`（`{side}`）",
        f"类型：`{order_type}`",
        f"数量：`{qty}`",
    ]
    if order_type == "LIMIT":
        lines.append(f"限价：`{pay.get('price') or '?'}`")
    lines.extend(
        [
            "",
            "借币计息：默认自动借入（浮动利率，以所内为准）。",
            "",
            "请再次核对；确认后将向交易所提交全仓杠杆订单。",
        ]
    )
    return "\n".join(lines)


async def _dispatch_margin_market_p1_callback(
    *,
    session: AsyncSession,
    settings: Settings,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    action: str,
    row: AgentTelegramPendingConfirm,
) -> None:
    if action == "cancel":
        from chainup_agent.application.session_concurrency import release_session_write_gates

        release_session_write_gates(f"tg:{chat_id}")
        await delete_pending_row(session, row)
        await safe_answer_telegram_callback_query(bot_token, callback_query_id, text="已取消")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "已取消本次全仓杠杆市价单，未向交易所提交订单。",
            },
        )
        return

    pay = pending_payload(row)
    pending_eid = str(pay.get("executionId") or "").strip()
    uid = str(from_telegram_user_id)
    if pending_eid:
        await append_execution_timeline_event(
            session,
            execution_id=pending_eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="confirm_gate",
            outcome="success",
            payload={
                "scenarioId": "margin.cross.market_order",
                "channel": "telegram_callback",
                "confirmPhase": 1,
                "transitionTrigger": "margin.confirm.phase1_accepted",
            },
        )
    await safe_answer_telegram_callback_query(bot_token, callback_query_id)
    await delete_pending_row(session, row)
    token2 = await create_margin_market_pending_phase2(
        session,
        telegram_user_id=from_telegram_user_id,
        chat_id=chat_id,
        payload=pay,
    )
    body = _format_margin_phase2_body(pay, order_type="MARKET")
    markup = {
        "inline_keyboard": [
            [
                {"text": "确认提交", "callback_data": f"{CB_MARGIN_MARKET_P2_CONFIRM}{token2}"},
                {"text": "取消", "callback_data": f"{CB_MARGIN_MARKET_P2_CANCEL}{token2}"},
            ],
        ],
    }
    await call_telegram_bot_api(
        bot_token,
        "sendMessage",
        json_payload={"chat_id": chat_id, "text": body[:4096], "reply_markup": markup},
    )


async def _dispatch_margin_market_p2_callback(
    *,
    session: AsyncSession,
    settings: Settings,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    action: str,
    row: AgentTelegramPendingConfirm,
) -> None:
    scenario_id = "margin.cross.market_order"
    if action == "cancel":
        from chainup_agent.application.session_concurrency import release_session_write_gates

        release_session_write_gates(f"tg:{chat_id}")
        await delete_pending_row(session, row)
        await safe_answer_telegram_callback_query(bot_token, callback_query_id, text="已取消")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "已取消第二次确认，未向交易所提交全仓杠杆订单。",
            },
        )
        return

    pay = pending_payload(row)
    sym = str(pay.get("symbol") or "").strip()
    side = str(pay.get("side") or "").strip().upper()
    qty = str(pay.get("quantity") or "").strip()
    uid = str(from_telegram_user_id)
    pending_eid = str(pay.get("executionId") or "").strip()
    eid = pending_eid
    reuse_turn = bool(pending_eid)
    if not pending_eid:
        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id=uid,
                scenario_id=scenario_id,
                channel="telegram",
            ),
            source="telegram_callback",
        )
        eid = acc.execution_id
        reuse_turn = False

    try:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="confirm_accept",
            outcome="success",
            payload={
                "scenarioId": scenario_id,
                "channel": "telegram_callback",
                "confirmPhase": 2,
                "symbol": sym,
                "side": side,
                "quantityRequested": qty,
                "reuseTurnExecution": reuse_turn,
                "transitionTrigger": "margin.confirm.phase2_callback",
            },
        )
        await safe_answer_telegram_callback_query(bot_token, callback_query_id)
        out = await margin_order_for_bound_user(
            session=session,
            settings=settings,
            user_id=uid,
            symbol=sym,
            side=side,
            order_type="MARKET",
            volume=qty,
            scenario_id=scenario_id,
            timeline_execution_id=eid,
            timeline_channel="telegram_callback",
            timeline_include_quote=not reuse_turn,
        )
        oid = out.get("orderIdString") or out.get("orderId")
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="SUCCESS", note="margin_market_telegram_cb"
            ),
        )
        lines = [
            "—— 全仓杠杆市价单已提交 ——",
            f"交易对：`{out.get('symbol') or sym}`",
            f"方向：`{side}`",
            f"数量：`{qty}`",
            f"订单号：`{oid}`",
        ]
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={"chat_id": chat_id, "text": "\n".join(lines)[:4096]},
        )
    except AppError as exc:
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="FAILED",
                note=f"{exc.code}:{exc.message[:500]}",
            ),
        )
        user_txt = await format_app_error_reply_for_telegram(session, settings, exc)
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={"chat_id": chat_id, "text": user_txt[:4096]},
        )


async def _dispatch_margin_limit_p1_callback(
    *,
    session: AsyncSession,
    settings: Settings,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    action: str,
    row: AgentTelegramPendingConfirm,
) -> None:
    if action == "cancel":
        from chainup_agent.application.session_concurrency import release_session_write_gates

        release_session_write_gates(f"tg:{chat_id}")
        await delete_pending_row(session, row)
        await safe_answer_telegram_callback_query(bot_token, callback_query_id, text="已取消")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "已取消本次全仓杠杆限价单，未向交易所提交订单。",
            },
        )
        return

    pay = pending_payload(row)
    pending_eid = str(pay.get("executionId") or "").strip()
    uid = str(from_telegram_user_id)
    if pending_eid:
        await append_execution_timeline_event(
            session,
            execution_id=pending_eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="confirm_gate",
            outcome="success",
            payload={
                "scenarioId": "margin.cross.limit_order",
                "channel": "telegram_callback",
                "confirmPhase": 1,
                "transitionTrigger": "margin.confirm.phase1_accepted",
            },
        )
    await safe_answer_telegram_callback_query(bot_token, callback_query_id)
    await delete_pending_row(session, row)
    token2 = await create_margin_limit_pending_phase2(
        session,
        telegram_user_id=from_telegram_user_id,
        chat_id=chat_id,
        payload=pay,
    )
    body = _format_margin_phase2_body(pay, order_type="LIMIT")
    markup = {
        "inline_keyboard": [
            [
                {"text": "确认提交", "callback_data": f"{CB_MARGIN_LIMIT_P2_CONFIRM}{token2}"},
                {"text": "取消", "callback_data": f"{CB_MARGIN_LIMIT_P2_CANCEL}{token2}"},
            ],
        ],
    }
    await call_telegram_bot_api(
        bot_token,
        "sendMessage",
        json_payload={"chat_id": chat_id, "text": body[:4096], "reply_markup": markup},
    )


async def _dispatch_margin_limit_p2_callback(
    *,
    session: AsyncSession,
    settings: Settings,
    bot_token: str,
    callback_query_id: str | int,
    chat_id: int,
    from_telegram_user_id: int,
    action: str,
    row: AgentTelegramPendingConfirm,
) -> None:
    scenario_id = "margin.cross.limit_order"
    if action == "cancel":
        from chainup_agent.application.session_concurrency import release_session_write_gates

        release_session_write_gates(f"tg:{chat_id}")
        await delete_pending_row(session, row)
        await safe_answer_telegram_callback_query(bot_token, callback_query_id, text="已取消")
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={
                "chat_id": chat_id,
                "text": "已取消第二次确认，未向交易所提交全仓杠杆限价单。",
            },
        )
        return

    pay = pending_payload(row)
    sym = str(pay.get("symbol") or "").strip()
    side = str(pay.get("side") or "").strip().upper()
    qty = str(pay.get("quantity") or "").strip()
    price = str(pay.get("price") or "").strip()
    uid = str(from_telegram_user_id)
    pending_eid = str(pay.get("executionId") or "").strip()
    eid = pending_eid
    reuse_turn = bool(pending_eid)
    if not pending_eid:
        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id=uid,
                scenario_id=scenario_id,
                channel="telegram",
            ),
            source="telegram_callback",
        )
        eid = acc.execution_id
        reuse_turn = False

    try:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="confirm_accept",
            outcome="success",
            payload={
                "scenarioId": scenario_id,
                "channel": "telegram_callback",
                "confirmPhase": 2,
                "symbol": sym,
                "side": side,
                "quantityRequested": qty,
                "limitPrice": price,
                "reuseTurnExecution": reuse_turn,
                "transitionTrigger": "margin.confirm.phase2_callback",
            },
        )
        await safe_answer_telegram_callback_query(bot_token, callback_query_id)
        out = await margin_order_for_bound_user(
            session=session,
            settings=settings,
            user_id=uid,
            symbol=sym,
            side=side,
            order_type="LIMIT",
            volume=qty,
            price=price,
            scenario_id=scenario_id,
            timeline_execution_id=eid,
            timeline_channel="telegram_callback",
            timeline_include_quote=not reuse_turn,
        )
        oid = out.get("orderIdString") or out.get("orderId")
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid, outcome="SUCCESS", note="margin_limit_telegram_cb"
            ),
        )
        lines = [
            "—— 全仓杠杆限价单已提交 ——",
            f"交易对：`{out.get('symbol') or sym}`",
            f"方向：`{side}`",
            f"数量：`{qty}`",
            f"限价：`{price}`",
            f"订单号：`{oid}`",
        ]
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={"chat_id": chat_id, "text": "\n".join(lines)[:4096]},
        )
    except AppError as exc:
        await delete_pending_row(session, row)
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="FAILED",
                note=f"{exc.code}:{exc.message[:500]}",
            ),
        )
        user_txt = await format_app_error_reply_for_telegram(session, settings, exc)
        await call_telegram_bot_api(
            bot_token,
            "sendMessage",
            json_payload={"chat_id": chat_id, "text": user_txt[:4096]},
        )
