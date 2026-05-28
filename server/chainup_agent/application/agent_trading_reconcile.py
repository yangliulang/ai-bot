"""§6 P0 — 504 / UNKNOWN trading reconcile (query order to resolve terminal state)."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_api_binding_confirm import (
    decrypt_binding_trade_credentials_for_row,
)
from chainup_agent.application.agent_execution_events import (
    append_execution_timeline_event,
    list_timeline_events_for_execution,
)
from chainup_agent.application.agent_routing_exchange_read import (
    load_binding_row_for_telegram_user,
    parse_telegram_user_id_numeric,
)
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.domain.canonical_trading import timeline_obs_venue_canonical
from chainup_agent.domain.trading_reconcile import (
    CanonicalReconcileStatus,
    OrderQueryTarget,
    ReconcileCaseKind,
    build_query_targets,
    infer_reconcile_case_from_timeline,
    map_coobit_order_status_to_canonical,
    venue_from_method_path,
)
from chainup_agent.infrastructure.exchange.coobit_openapi import (
    fetch_signed_futures_order_json,
    fetch_signed_spot_order_json,
    futures_order_response_body_timeline_preview,
    normalize_coobit_futures_contract_name,
    normalize_coobit_spot_order_body_symbol,
    spot_order_response_body_timeline_preview,
)
from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution

logger = logging.getLogger(__name__)


def _sanitize_order_preview(venue: str, raw: dict[str, Any]) -> dict[str, Any]:
    if venue == "futures":
        return futures_order_response_body_timeline_preview(raw)
    return spot_order_response_body_timeline_preview(raw)


async def _query_one_order(
    *,
    openapi_base: str,
    api_key: str,
    secret_key: str,
    target: OrderQueryTarget,
) -> dict[str, Any]:
    if target.venue == "futures":
        cn = normalize_coobit_futures_contract_name(target.symbol)
        raw = await fetch_signed_futures_order_json(
            openapi_base_url=openapi_base,
            api_key=api_key,
            secret_key=secret_key,
            contract_name=cn,
            order_id=target.order_id,
            client_order_id=target.client_order_id,
        )
        status_raw = raw.get("status")
        preview = _sanitize_order_preview("futures", raw)
        oid = preview.get("orderIdString") or raw.get("orderId")
        return {
            "role": target.role,
            "venue": "futures",
            "contractName": preview.get("contractName") or cn,
            "orderId": oid,
            "exchangeStatus": status_raw,
            "canonicalStatus": map_coobit_order_status_to_canonical(
                str(status_raw) if status_raw is not None else None
            ),
            "exchangeOrderPreview": preview,
        }

    sym_body = normalize_coobit_spot_order_body_symbol(target.symbol)
    raw = await fetch_signed_spot_order_json(
        openapi_base_url=openapi_base,
        api_key=api_key,
        secret_key=secret_key,
        symbol=target.symbol,
        order_id=target.order_id,
        client_order_id=target.client_order_id,
    )
    status_raw = raw.get("status")
    preview = _sanitize_order_preview("spot", raw)
    oid = preview.get("orderIdString") or raw.get("orderId")
    return {
        "role": target.role,
        "venue": "spot",
        "symbol": preview.get("symbol") or sym_body,
        "orderId": oid,
        "exchangeStatus": status_raw,
        "canonicalStatus": map_coobit_order_status_to_canonical(
            str(status_raw) if status_raw is not None else None
        ),
        "exchangeOrderPreview": preview,
    }


def _aggregate_resolution(
    *,
    case_kind: ReconcileCaseKind,
    lookups: list[dict[str, Any]],
) -> tuple[CanonicalReconcileStatus, str]:
    if not lookups:
        return "INCONCLUSIVE", "未能从交易所拉取到委托信息，请核对订单号后重试对账。"

    if case_kind == "CANCEL_SUCCEEDED_REPLACE_FAILED":
        prior = next((x for x in lookups if x.get("role") == "prior_cancelled"), None)
        repl = next((x for x in lookups if x.get("role") == "replace_submit"), None)
        if prior and prior.get("canonicalStatus") == "CANCELLED":
            if repl and repl.get("canonicalStatus") in ("OPEN", "FILLED"):
                return (
                    "OPEN",
                    "原单已撤销；新委托已在交易所生效（对账已闭合）。",
                )
            if repl and repl.get("canonicalStatus") == "CANCELLED":
                return "CANCELLED", "原单与新单均未在途（对账显示已撤销）。"
            return (
                "PARTIAL_FAILURE",
                "原委托已撤销，但新委托未在交易所找到或未成交；请勿重复撤单，可发起新限价或联系客服。",
            )
        return (
            "PARTIAL_FAILURE",
            "改单可能处于中间态：请根据下列查单结果人工确认，勿断言已成交。",
        )

    primary = lookups[0]
    cs = primary.get("canonicalStatus") or "INCONCLUSIVE"
    if cs == "FILLED":
        return "FILLED", "对账显示委托已成交。"
    if cs == "CANCELLED":
        return "CANCELLED", "对账显示委托已撤销。"
    if cs == "REJECTED":
        return "REJECTED", "对账显示委托已被交易所拒绝。"
    if cs == "OPEN":
        return "OPEN", "对账显示委托仍在交易所挂单中。"
    if cs == "INCONCLUSIVE":
        return "INCONCLUSIVE", "查单结果无法映射为明确终态，请稍后重试或到主站查看。"
    return cs, "对账已完成，请查看订单摘要。"


def _neutral_message_for_case(case_kind: ReconcileCaseKind) -> str:
    if case_kind in ("EXCHANGE_WRITE_UNKNOWN", "SUBMIT_UNKNOWN", "CANCEL_UNKNOWN"):
        return "上次提交因超时或 504 仍处于确认中；对账将查询交易所真实状态，不会假定为失败或成功。"
    if case_kind == "CANCEL_SUCCEEDED_REPLACE_FAILED":
        return "改单流程为先撤后挂；若撤单已成功而挂单失败，对账将分别核对两笔委托。"
    return "将查询交易所订单状态以闭合 UNKNOWN。"


async def trading_reconcile_for_bound_user(
    *,
    session: AsyncSession,
    settings: Settings,
    user_id: str,
    execution_id: str | None = None,
    venue: str | None = None,
    symbol: str | None = None,
    order_id: str | None = None,
    client_order_id: str | None = None,
    case_kind_override: str | None = None,
) -> dict[str, Any]:
    """Run reconcile queries and return Agent-facing summary (camelCase keys)."""
    tg = parse_telegram_user_id_numeric(user_id)
    row = await load_binding_row_for_telegram_user(session, tg)
    if row is None:
        raise AppError(
            code="AGENT_SUBACCOUNT_REQUIRED",
            message="未发现该 Telegram 用户的托管 API 绑定，请先完成 Deeplink 校验与绑定。",
            status_code=403,
        )

    uid_s = user_id.strip()
    eid = execution_id.strip() if execution_id and execution_id.strip() else None
    scenario_id: str | None = None
    hints: dict[str, Any] = {}

    if eid:
        ex_row = await session.get(AgentExecution, eid)
        if ex_row is None or ex_row.user_id != uid_s:
            raise AppError(
                code="AGENT_RECONCILE_EXECUTION_NOT_FOUND",
                message="未找到该 executionId 或用户不匹配",
                status_code=404,
            )
        scenario_id = ex_row.scenario_id
        events = await list_timeline_events_for_execution(session, execution_public_id=eid)
        inferred, hints = infer_reconcile_case_from_timeline(events, scenario_id=scenario_id)
    else:
        inferred = "UNSPECIFIED"
        events = []

    case_kind: ReconcileCaseKind
    if case_kind_override and case_kind_override.strip():
        ck = case_kind_override.strip()
        allowed = {
            "EXCHANGE_WRITE_UNKNOWN",
            "CANCEL_SUCCEEDED_REPLACE_FAILED",
            "SUBMIT_UNKNOWN",
            "CANCEL_UNKNOWN",
            "UNSPECIFIED",
        }
        if ck not in allowed:
            raise AppError(
                code="VALIDATION_ERROR",
                message="caseKind 不在允许枚举内",
                status_code=422,
                details={"field": "caseKind"},
            )
        case_kind = ck  # type: ignore[assignment]
    else:
        case_kind = inferred

    ven_override = venue.strip().lower() if venue and venue.strip() else None
    if ven_override and ven_override not in ("spot", "futures"):
        raise AppError(
            code="VALIDATION_ERROR",
            message="venue 须为 spot 或 futures",
            status_code=422,
            details={"field": "venue"},
        )

    targets = build_query_targets(
        case_kind=case_kind,
        hints=hints,
        venue=ven_override,  # type: ignore[arg-type]
        symbol=symbol,
        order_id=order_id,
        client_order_id=client_order_id,
    )
    if not targets and hints.get("methodPathSummary"):
        ven_guess = venue_from_method_path(str(hints.get("methodPathSummary")))
        sym_guess = (symbol or hints.get("symbol") or "").strip()
        if ven_guess and sym_guess and (order_id or hints.get("orderId")):
            targets = [
                OrderQueryTarget(
                    venue=ven_guess,
                    symbol=sym_guess,
                    order_id=(order_id or hints.get("orderId") or "").strip() or None,
                    client_order_id=client_order_id,
                    role="primary",
                )
            ]

    if not targets:
        raise AppError(
            code="AGENT_RECONCILE_NO_QUERY_TARGETS",
            message="缺少对账查单参数：请提供 executionId，或 symbol 与 orderId/clientOrderId",
            status_code=422,
        )

    reconcile_id = eid or f"recon-{uuid.uuid4().hex[:12]}"
    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)

    lookups: list[dict[str, Any]] = []
    for t in targets:
        try:
            lookups.append(
                await _query_one_order(
                    openapi_base=openapi_base,
                    api_key=ak,
                    secret_key=sk,
                    target=t,
                )
            )
        except AppError as exc:
            if exc.code in ("AGENT_SPOT_ORDER_NOT_FOUND", "AGENT_FUTURES_ORDER_NOT_FOUND"):
                lookups.append(
                    {
                        "role": t.role,
                        "venue": t.venue,
                        "orderId": t.order_id,
                        "clientOrderId": t.client_order_id,
                        "canonicalStatus": "INCONCLUSIVE",
                        "exchangeStatus": None,
                        "notFound": True,
                    }
                )
                continue
            raise

    resolution_status, user_message = _aggregate_resolution(
        case_kind=case_kind, lookups=lookups
    )
    still_unknown = resolution_status in ("UNKNOWN", "INCONCLUSIVE", "PARTIAL_FAILURE")

    if eid:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid_s,
            event_name="trading.reconcile",
            step_kind="query_order",
            outcome="unknown" if still_unknown else "success",
            payload={
                **timeline_obs_venue_canonical(),
                "reconcileId": reconcile_id,
                "caseKind": case_kind,
                "resolutionStatus": resolution_status,
                "lookupCount": len(lookups),
                "lookups": lookups[:8],
                "transitionTrigger": "reconcile.query_order",
            },
        )
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id=uid_s,
            event_name="agent.execution.step",
            step_kind="query_order",
            outcome="unknown" if still_unknown else "success",
            payload={
                **timeline_obs_venue_canonical(),
                "scenarioId": scenario_id,
                "reconcileId": reconcile_id,
                "caseKind": case_kind,
                "resolutionStatus": resolution_status,
                "transitionTrigger": "reconcile.closed",
            },
        )

    return {
        "reconcileId": reconcile_id,
        "executionId": eid,
        "scenarioId": scenario_id,
        "caseKind": case_kind,
        "resolutionStatus": resolution_status,
        "stillUnknown": still_unknown,
        "neutralHint": _neutral_message_for_case(case_kind),
        "userMessage": user_message,
        "orderLookups": lookups,
        "partialFailureCode": (
            "AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED"
            if case_kind == "CANCEL_SUCCEEDED_REPLACE_FAILED" and still_unknown
            else None
        ),
    }


async def trading_reconcile_status_for_execution(
    *,
    session: AsyncSession,
    user_id: str,
    execution_id: str,
) -> dict[str, Any]:
    """Return last reconcile outcome from timeline (or pending UNKNOWN)."""
    uid_s = user_id.strip()
    eid = execution_id.strip()
    ex_row = await session.get(AgentExecution, eid)
    if ex_row is None or ex_row.user_id != uid_s:
        raise AppError(
            code="AGENT_RECONCILE_EXECUTION_NOT_FOUND",
            message="未找到该 executionId 或用户不匹配",
            status_code=404,
        )

    events = await list_timeline_events_for_execution(session, execution_public_id=eid)
    case_kind, hints = infer_reconcile_case_from_timeline(events, scenario_id=ex_row.scenario_id)

    last_reconcile: dict[str, Any] | None = None
    last_reconcile_seq: int | None = None
    has_unknown_write = False
    for ev in reversed(events):
        if ev.event_type == "trading.reconcile" and last_reconcile is None:
            try:
                last_reconcile = json.loads(ev.payload_json or "{}")
            except json.JSONDecodeError:
                last_reconcile = {}
            last_reconcile_seq = ev.seq
        if ev.event_type == "trading.exchange_private":
            if (ev.outcome or "").strip() == "unknown":
                has_unknown_write = True
            else:
                try:
                    priv = json.loads(ev.payload_json or "{}")
                except json.JSONDecodeError:
                    priv = {}
                if priv.get("exchangeOutcome") == "unknown" or priv.get("appErrorCode") in (
                    "AGENT_EXCHANGE_WRITE_UNKNOWN",
                    "AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED",
                ):
                    has_unknown_write = True

    if last_reconcile:
        rs = last_reconcile.get("resolutionStatus") or "UNKNOWN"
        return {
            "executionId": eid,
            "scenarioId": ex_row.scenario_id,
            "state": ex_row.state,
            "caseKind": last_reconcile.get("caseKind") or case_kind,
            "resolutionStatus": rs,
            "stillUnknown": rs in ("UNKNOWN", "INCONCLUSIVE", "PARTIAL_FAILURE"),
            "lastReconcileAtSeq": last_reconcile_seq,
            "reconcileId": last_reconcile.get("reconcileId") or eid,
            "userMessage": None,
            "hints": hints,
        }

    return {
        "executionId": eid,
        "scenarioId": ex_row.scenario_id,
        "state": ex_row.state,
        "caseKind": case_kind,
        "resolutionStatus": "UNKNOWN" if has_unknown_write else "PENDING",
        "stillUnknown": has_unknown_write or case_kind != "UNSPECIFIED",
        "lastReconcileAtSeq": None,
        "reconcileId": eid,
        "userMessage": (
            _neutral_message_for_case(case_kind) if has_unknown_write else "尚未发起对账查单。"
        ),
        "hints": hints,
    }
