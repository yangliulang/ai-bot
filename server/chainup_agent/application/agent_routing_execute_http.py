"""HTTP ``POST /routing/execute`` — ``agent_execution`` + Admin timeline (read / stub)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.agent_runtime import (
    ExecutionAcceptRequest,
    ExecutionFinalizeRequest,
    RoutingExecuteRequest,
    RoutingExecuteResponse,
)
from chainup_agent.application.agent_execution_events import append_execution_timeline_event
from chainup_agent.application.orchestration_steps import append_routing_orchestration_steps
from chainup_agent.application.agent_execution_memory import execution_accept, execution_finalize
from chainup_agent.application.agent_routing_exchange_read import (
    routing_execute_exchange_reads,
)
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError


def routing_telegram_read_request(
    *,
    telegram_user_id: int,
    user_text: str,
    scenario_id: str,
    symbol: str | None = None,
    market_data_limit: int | None = None,
) -> RoutingExecuteRequest:
    """Shared DTO shape for Telegram read turns (``ROUTE_READ_SKILL``)."""
    return RoutingExecuteRequest(
        scenario_id=scenario_id,
        user_id=str(telegram_user_id),
        channel="telegram",
        utterance_snapshot=user_text[:512],
        symbol=symbol,
        market_data_limit=market_data_limit,
    )


def summarize_exchange_read_preview_for_timeline(preview: dict[str, Any] | None) -> dict[str, Any]:
    """Small summary for ``payload.exchangeReadPreviewSummary`` (Admin 协查，控 payload 体积)."""
    if not isinstance(preview, dict):
        return {}
    kind = preview.get("kind")
    out: dict[str, Any] = {"previewKind": kind}
    if kind == "spot_ticker_v2_filtered":
        for k in ("symbolRequested", "lastPrice", "bidPrice", "askPrice", "priceChangePercent"):
            if k in preview:
                out[k] = preview[k]
    elif kind == "spot_depth_v2_filtered":
        for k in ("symbolRequested", "limitRequested"):
            if k in preview:
                out[k] = preview[k]
        asks = preview.get("asks")
        bids = preview.get("bids")
        out["askLevels"] = len(asks) if isinstance(asks, list) else 0
        out["bidLevels"] = len(bids) if isinstance(bids, list) else 0
    elif kind == "spot_trades_v2_filtered":
        if "symbolRequested" in preview:
            out["symbolRequested"] = preview["symbolRequested"]
        items = preview.get("items")
        out["tradeCount"] = len(items) if isinstance(items, list) else 0
    elif kind == "spot_account_balances_filtered":
        items = preview.get("items")
        out["assetCount"] = len(items) if isinstance(items, list) else 0
        if preview.get("accountTypeHint"):
            out["accountTypeHint"] = preview["accountTypeHint"]
    elif kind == "wealth_holdings_otc_v1":
        items = preview.get("items")
        out["assetCount"] = len(items) if isinstance(items, list) else 0
        if preview.get("accountTypeRequested") is not None:
            out["accountTypeRequested"] = preview["accountTypeRequested"]
        ac = preview.get("assetRowCount")
        if isinstance(ac, int):
            out["assetRowCount"] = ac
    elif kind == "spot_open_orders_v1":
        if preview.get("symbolFilter"):
            out["symbolFilter"] = preview["symbolFilter"]
        oc = preview.get("orderCount")
        if isinstance(oc, int):
            out["orderCount"] = oc
    return out


def _routing_obs_meta(scenario_id: str) -> tuple[str, str, str] | None:
    """``(event_name, method_path_summary, transition_trigger)`` for wired read scenarios."""
    m: dict[str, tuple[str, str, str]] = {
        "read.market.ticker": (
            "trading.exchange_public",
            "GET /sapi/v2/ticker",
            "routing.read.public_ticker",
        ),
        "read.market.depth": (
            "trading.exchange_public",
            "GET /sapi/v2/depth",
            "routing.read.public_depth",
        ),
        "read.market.trades": (
            "trading.exchange_public",
            "GET /sapi/v2/trades",
            "routing.read.public_trades",
        ),
        "read.account.balance": (
            "trading.exchange_private",
            "GET /sapi/v1/account",
            "routing.read.private_account",
        ),
        "wealth.holdings_read": (
            "trading.exchange_private",
            "POST /sapi/v1/asset/account/by_type",
            "routing.read.private_wealth",
        ),
        "trade.spot.open_orders": (
            "trading.exchange_private",
            "GET /sapi/v2/openOrders",
            "routing.read.spot_open_orders",
        ),
    }
    return m.get(scenario_id)


def _slim_payload_base(body: RoutingExecuteRequest) -> dict[str, Any]:
    out: dict[str, Any] = {
        "scenarioId": (body.scenario_id or "").strip(),
        "channel": (body.channel or "").strip() or None,
    }
    sym = (body.symbol or "").strip()
    if sym:
        out["symbol"] = sym
    if body.market_data_limit is not None:
        out["marketDataLimit"] = body.market_data_limit
    return out


async def append_routing_execute_timeline(
    session: AsyncSession,
    *,
    execution_id: str,
    user_id: str,
    body: RoutingExecuteRequest,
    response: RoutingExecuteResponse | None,
    outcome: str,
    app_error: AppError | None = None,
) -> None:
    """
    One timeline row for a routing/execute exchange call (HTTP or Telegram).

    **Failure**（``app_error``）: ``agent.execution.step`` · ``exchange_read``，便于与 **SUCCEEDED**
    的 Telegram 轮次（用户可见错误正文）对照协查。
    """
    uid = user_id.strip()
    eid = execution_id.strip()
    base_payload = _slim_payload_base(body)

    if app_error is not None:
        detail_keys = ("field", "scenarioId", "exchange_code", "exchange_msg", "http_status")
        details = app_error.details or {}
        slim_details = {k: details[k] for k in detail_keys if k in details}
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="exchange_read",
            outcome="failure",
            payload={
                **base_payload,
                "appErrorCode": app_error.code,
                "appErrorMessage": app_error.message[:512],
                "appErrorDetails": slim_details,
                "transitionTrigger": "routing.read.failed",
                "httpStatus": app_error.status_code,
            },
        )
        return

    if response is None:
        return

    r_sid = (response.scenario_id or base_payload.get("scenarioId") or "").strip()

    if r_sid == "trade.spot.flash_convert":
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="orchestration",
            outcome=outcome,
            payload={
                **base_payload,
                "transitionTrigger": "routing.flash_convert_http_guidance",
                "notePreview": (response.note or "")[:400],
            },
        )
        return

    if r_sid == "trade.spot.limit_order":
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="orchestration",
            outcome=outcome,
            payload={
                **base_payload,
                "transitionTrigger": "routing.limit_order_http_guidance",
                "notePreview": (response.note or "")[:400],
            },
        )
        return

    if r_sid == "trade.spot.cancel_order":
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="orchestration",
            outcome=outcome,
            payload={
                **base_payload,
                "transitionTrigger": "routing.spot_cancel_http_guidance",
                "notePreview": (response.note or "")[:400],
            },
        )
        return

    meta = _routing_obs_meta(r_sid)
    if meta is None:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid,
            event_name="agent.execution.step",
            step_kind="routing_note",
            outcome=outcome,
            payload={
                **base_payload,
                "transitionTrigger": "routing.scenario_placeholder",
                "notePreview": (response.note or "")[:400],
            },
        )
        return

    event_name, method_path, trigger = meta
    preview = response.exchange_read_preview
    await append_execution_timeline_event(
        session,
        execution_id=eid,
        user_id=uid,
        event_name=event_name,
        step_kind="exchange_read",
        outcome=outcome,
        payload={
            **base_payload,
            "methodPathSummary": method_path,
            "httpStatus": 200,
            "exchangeOutcome": "success" if outcome == "success" else outcome,
            "exchangeReadPreviewSummary": summarize_exchange_read_preview_for_timeline(
                preview if isinstance(preview, dict) else None
            ),
            "transitionTrigger": trigger,
        },
    )


async def routing_execute_http_with_execution(
    *,
    session: AsyncSession,
    settings: Settings,
    body: RoutingExecuteRequest,
) -> RoutingExecuteResponse:
    """``execution_accept`` → routing → timeline → ``finalize`` + ``commit``."""
    uid = body.user_id.strip()
    sid = body.scenario_id.strip()
    chan = body.channel.strip() if body.channel and body.channel.strip() else "http"

    acc = await execution_accept(
        session,
        ExecutionAcceptRequest(user_id=uid, scenario_id=sid, channel=chan),
        source="http_api",
    )
    eid = acc.execution_id

    try:
        out = await routing_execute_exchange_reads(
            session=session,
            settings=settings,
            body=body,
        )
        await append_routing_execute_timeline(
            session,
            execution_id=eid,
            user_id=uid,
            body=body,
            response=out,
            outcome="success",
        )
        await append_routing_orchestration_steps(
            session,
            execution_id=eid,
            user_id=uid,
            scenario_id=sid,
            outcome="success",
        )
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="SUCCESS",
                note="routing_execute_http",
            ),
        )
        await session.commit()
        return RoutingExecuteResponse(
            routed=out.routed,
            scenario_id=out.scenario_id,
            note=out.note,
            exchange_read_preview=out.exchange_read_preview,
            execution_id=eid,
        )
    except AppError as exc:
        await append_routing_execute_timeline(
            session,
            execution_id=eid,
            user_id=uid,
            body=body,
            response=None,
            outcome="failure",
            app_error=exc,
        )
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(
                execution_id=eid,
                outcome="FAILED",
                note=f"routing_execute_http:{exc.code}",
            ),
        )
        await session.commit()
        raise
