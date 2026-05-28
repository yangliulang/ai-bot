"""504 / UNKNOWN reconciliation — case kinds and exchange status mapping (§6 P0)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

ReconcileCaseKind = Literal[
    "EXCHANGE_WRITE_UNKNOWN",
    "CANCEL_SUCCEEDED_REPLACE_FAILED",
    "SUBMIT_UNKNOWN",
    "CANCEL_UNKNOWN",
    "UNSPECIFIED",
]

CanonicalReconcileStatus = Literal[
    "UNKNOWN",
    "OPEN",
    "FILLED",
    "CANCELLED",
    "REJECTED",
    "PARTIAL_FAILURE",
    "INCONCLUSIVE",
]

VenueKind = Literal["spot", "futures"]


@dataclass(frozen=True, slots=True)
class OrderQueryTarget:
    """One GET order / openOrders lookup for reconcile."""

    venue: VenueKind
    symbol: str
    order_id: str | None = None
    client_order_id: str | None = None
    role: str = "primary"


def _parse_payload(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def map_coobit_order_status_to_canonical(status_raw: str | None) -> CanonicalReconcileStatus:
    s = (status_raw or "").strip().upper()
    if not s:
        return "INCONCLUSIVE"
    if s in ("FILLED", "FULL_FILLED"):
        return "FILLED"
    if s in ("CANCELLED", "CANCELED", "CANCEL"):
        return "CANCELLED"
    if s in ("REJECTED", "REJECT", "EXPIRED"):
        return "REJECTED"
    if s in (
        "NEW",
        "INIT",
        "PARTIALLY_FILLED",
        "PART_FILLED",
        "PARTIAL_FILLED",
        "OPEN",
        "PENDING",
    ):
        return "OPEN"
    return "INCONCLUSIVE"


def venue_from_method_path(method_path: str | None) -> VenueKind | None:
    mp = (method_path or "").strip()
    if "/fapi/" in mp:
        return "futures"
    if "/sapi/" in mp:
        return "spot"
    return None


def infer_reconcile_case_from_timeline(
    events: list[Any],
    *,
    scenario_id: str | None = None,
) -> tuple[ReconcileCaseKind, dict[str, Any]]:
    """
    Infer reconcile case from ``agent_execution_event`` rows (newest hints win).

    ``events`` items need ``event_type``, ``step_kind``, ``outcome``, ``payload_json``.
    """
    hints: dict[str, Any] = {"scenarioId": scenario_id}
    last_unknown: dict[str, Any] | None = None
    cancel_ok = False
    submit_fail = False
    amend_corr: str | None = None

    for ev in events:
        payload = _parse_payload(getattr(ev, "payload_json", "") or "")
        et = (getattr(ev, "event_type", "") or "").strip()
        sk = (getattr(ev, "step_kind", "") or "").strip()
        oc = (getattr(ev, "outcome", "") or "").strip()

        if payload.get("amendCorrelationId"):
            amend_corr = str(payload["amendCorrelationId"])
            hints["amendCorrelationId"] = amend_corr

        if payload.get("appErrorCode") == "AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED":
            hints["appErrorCode"] = payload["appErrorCode"]
            hints["cancelledOrderId"] = payload.get("cancelledOrderId")
            return "CANCEL_SUCCEEDED_REPLACE_FAILED", hints

        if et == "trading.exchange_private" and payload.get("exchangeOutcome") == "unknown":
            last_unknown = {
                "methodPathSummary": payload.get("methodPathSummary"),
                "stepKind": sk,
                "appErrorCode": payload.get("appErrorCode"),
            }

        if sk == "cancel_order" and oc == "success":
            cancel_ok = True
            if payload.get("orderId"):
                hints["cancelledOrderId"] = payload.get("orderId")
            if payload.get("symbol") or payload.get("symbolOrder"):
                hints["symbol"] = payload.get("symbol") or payload.get("symbolOrder")

        if sk == "submit_order" and oc in ("fail", "unknown"):
            submit_fail = True
            if payload.get("clientOrderRef"):
                hints["newClientOrderId"] = payload.get("clientOrderRef")
            if payload.get("symbolOrder") or payload.get("symbol"):
                hints["symbol"] = payload.get("symbolOrder") or payload.get("symbol")

    if cancel_ok and submit_fail:
        hints.setdefault("partialLeg", "cancel_ok_replace_fail")
        return "CANCEL_SUCCEEDED_REPLACE_FAILED", hints

    if last_unknown:
        hints.update(last_unknown)
        sk = last_unknown.get("stepKind") or ""
        if sk == "cancel_order":
            return "CANCEL_UNKNOWN", hints
        if sk == "submit_order":
            return "SUBMIT_UNKNOWN", hints
        return "EXCHANGE_WRITE_UNKNOWN", hints

    sid = (scenario_id or "").strip()
    if sid.startswith("trade.futures.") or sid.startswith("automation."):
        hints.setdefault("venue", "futures")
    elif sid.startswith("trade.spot."):
        hints.setdefault("venue", "spot")

    return "UNSPECIFIED", hints


def build_query_targets(
    *,
    case_kind: ReconcileCaseKind,
    hints: dict[str, Any],
    venue: VenueKind | None,
    symbol: str | None,
    order_id: str | None,
    client_order_id: str | None,
) -> list[OrderQueryTarget]:
    """Merge explicit request fields with timeline hints."""
    sym = (symbol or hints.get("symbol") or "").strip()
    ven: VenueKind | None = venue or hints.get("venue")  # type: ignore[assignment]
    if ven is None and hints.get("methodPathSummary"):
        ven = venue_from_method_path(str(hints.get("methodPathSummary")))
    if ven is None:
        ven = "spot"

    targets: list[OrderQueryTarget] = []

    def add(
        *,
        role: str,
        oid: str | None = None,
        cid: str | None = None,
        sym_in: str | None = None,
    ) -> None:
        s = (sym_in or sym).strip()
        if not s:
            return
        if not oid and not cid:
            return
        targets.append(
            OrderQueryTarget(
                venue=ven,
                symbol=s,
                order_id=oid,
                client_order_id=cid,
                role=role,
            )
        )

    oid_in = (order_id or "").strip() or None
    cid_in = (client_order_id or "").strip() or None

    if case_kind == "CANCEL_SUCCEEDED_REPLACE_FAILED":
        add(role="prior_cancelled", oid=(hints.get("cancelledOrderId") or oid_in), sym_in=sym)
        add(
            role="replace_submit",
            cid=(hints.get("newClientOrderId") or cid_in),
            sym_in=sym,
        )
        if not targets and oid_in:
            add(role="primary", oid=oid_in)
        return targets

    add(role="primary", oid=oid_in or hints.get("orderId"), cid=cid_in or hints.get("newClientOrderId"))
    return targets
