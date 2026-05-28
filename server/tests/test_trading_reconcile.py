"""§6 P0 — trading reconcile (504/UNKNOWN + amend partial failure)."""

from __future__ import annotations

import json

import pytest
from httpx import AsyncClient

from chainup_agent.application.agent_execution_events import append_execution_timeline_event
from chainup_agent.domain.trading_reconcile import (
    build_query_targets,
    infer_reconcile_case_from_timeline,
    map_coobit_order_status_to_canonical,
)


class _FakeEvent:
    def __init__(
        self,
        *,
        event_type: str,
        step_kind: str | None = None,
        outcome: str | None = None,
        payload: dict | None = None,
    ) -> None:
        self.event_type = event_type
        self.step_kind = step_kind
        self.outcome = outcome
        self.payload_json = json.dumps(payload or {}, ensure_ascii=False)


def test_infer_amend_cancel_ok_replace_fail() -> None:
    events = [
        _FakeEvent(
            event_type="agent.execution.step",
            step_kind="cancel_order",
            outcome="success",
            payload={"orderId": "111", "symbol": "BTC-USDT"},
        ),
        _FakeEvent(
            event_type="trading.exchange_private",
            step_kind="submit_order",
            outcome="fail",
            payload={
                "methodPathSummary": "POST /sapi/v2/order",
                "exchangeOutcome": "fail",
                "clientOrderRef": "cu_agent_new1",
            },
        ),
    ]
    kind, hints = infer_reconcile_case_from_timeline(
        events, scenario_id="trade.spot.amend_limit_order"
    )
    assert kind == "CANCEL_SUCCEEDED_REPLACE_FAILED"
    targets = build_query_targets(
        case_kind=kind,
        hints=hints,
        venue="spot",
        symbol="BTC-USDT",
        order_id=None,
        client_order_id=None,
    )
    assert len(targets) == 2
    assert targets[0].role == "prior_cancelled"
    assert targets[0].order_id == "111"


def test_map_coobit_status() -> None:
    assert map_coobit_order_status_to_canonical("CANCELLED") == "CANCELLED"
    assert map_coobit_order_status_to_canonical("NEW") == "OPEN"


@pytest.mark.asyncio
async def test_reconcile_http_with_execution(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    from chainup_agent.application.agent_execution_memory import execution_accept
    from chainup_agent.api.schemas.agent_runtime import ExecutionAcceptRequest
    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    async def fake_spot_order(**kwargs: object) -> dict:
        oid = kwargs.get("order_id")
        if oid == "111":
            return {"orderId": "111", "status": "CANCELLED", "symbol": "BTC/USDT"}
        return {"orderId": "222", "status": "NEW", "clientOrderId": "cu_agent_new1"}

    monkeypatch.setattr(
        "chainup_agent.application.agent_trading_reconcile.fetch_signed_spot_order_json",
        fake_spot_order,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)

    from chainup_agent.infrastructure.persistence.base import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id="93",
                scenario_id="trade.spot.amend_limit_order",
                channel="http",
            ),
            source="test",
        )
        eid = acc.execution_id
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id="93",
            event_name="agent.execution.step",
            step_kind="cancel_order",
            outcome="success",
            payload={"orderId": "111", "symbol": "BTC-USDT"},
        )
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id="93",
            event_name="trading.exchange_private",
            step_kind="submit_order",
            outcome="fail",
            payload={"clientOrderRef": "cu_agent_new1", "symbolOrder": "BTCUSDT"},
        )
        await session.commit()

    await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900093",
            "telegram": {"tg_id": "93"},
        },
    )

    r = await http_client.post(
        "/api/v1/agent/trading/reconcile",
        json={
            "userId": "93",
            "executionId": eid,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["reconcileId"]
    assert body["caseKind"] == "CANCEL_SUCCEEDED_REPLACE_FAILED"
    assert body["resolutionStatus"] in ("OPEN", "PARTIAL_FAILURE")
    assert "stillUnknown" in body
    assert body.get("userMessage")
    assert body.get("neutralHint")
    assert isinstance(body.get("orderLookups"), list) and len(body["orderLookups"]) >= 1
    assert body["stillUnknown"] is False or body["resolutionStatus"] == "PARTIAL_FAILURE"

    from chainup_agent.application.agent_execution_events import (
        list_timeline_events_for_execution,
    )
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        events = await list_timeline_events_for_execution(
            session, execution_public_id=eid
        )
    reconcile_events = [ev for ev in events if ev.event_type == "trading.reconcile"]
    assert reconcile_events, "expected trading.reconcile timeline event (AC-7)"
    payload = json.loads(reconcile_events[-1].payload_json or "{}")
    assert payload.get("reconcileId") == body["reconcileId"]
    assert payload.get("caseKind") == body["caseKind"]
    assert payload.get("resolutionStatus") == body["resolutionStatus"]

    st = await http_client.get(
        "/api/v1/agent/trading/reconcile/status",
        params={"userId": "93", "executionId": eid},
    )
    assert st.status_code == 200
    assert st.json()["lastReconcileAtSeq"] is not None


@pytest.mark.asyncio
async def test_reconcile_status_pending_unknown(http_client: AsyncClient, tmp_path, monkeypatch) -> None:
    from cryptography.fernet import Fernet

    from chainup_agent.application.agent_execution_memory import execution_accept
    from chainup_agent.api.schemas.agent_runtime import ExecutionAcceptRequest
    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)

    from chainup_agent.infrastructure.persistence.base import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id="94",
                scenario_id="trade.spot.limit_order",
                channel="http",
            ),
            source="test",
        )
        eid = acc.execution_id
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id="94",
            event_name="trading.exchange_private",
            step_kind="submit_order",
            outcome="unknown",
            payload={
                "methodPathSummary": "POST /sapi/v2/order",
                "exchangeOutcome": "unknown",
                "httpStatus": 504,
            },
        )
        await session.commit()

    st = await http_client.get(
        "/api/v1/agent/trading/reconcile/status",
        params={"userId": "94", "executionId": eid},
    )
    assert st.status_code == 200
    body = st.json()
    assert body["resolutionStatus"] == "UNKNOWN"
    assert body["stillUnknown"] is True
    assert body["caseKind"] == "SUBMIT_UNKNOWN"


@pytest.mark.asyncio
async def test_reconcile_unbound_user_403(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/trading/reconcile",
        json={"userId": "99999901", "executionId": "exec-does-not-matter"},
    )
    assert r.status_code == 403
    assert r.json()["code"] == "AGENT_SUBACCOUNT_REQUIRED"


@pytest.mark.asyncio
async def test_reconcile_execution_not_found_404(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900095",
            "telegram": {"tg_id": "95"},
        },
    )

    post_r = await http_client.post(
        "/api/v1/agent/trading/reconcile",
        json={"userId": "95", "executionId": "exec-nonexistent-id"},
    )
    assert post_r.status_code == 404
    assert post_r.json()["code"] == "AGENT_RECONCILE_EXECUTION_NOT_FOUND"

    get_r = await http_client.get(
        "/api/v1/agent/trading/reconcile/status",
        params={"userId": "95", "executionId": "exec-nonexistent-id"},
    )
    assert get_r.status_code == 404
    assert get_r.json()["code"] == "AGENT_RECONCILE_EXECUTION_NOT_FOUND"


@pytest.mark.asyncio
async def test_reconcile_no_query_targets_422(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900096",
            "telegram": {"tg_id": "96"},
        },
    )

    r = await http_client.post(
        "/api/v1/agent/trading/reconcile",
        json={"userId": "96"},
    )
    assert r.status_code == 422
    assert r.json()["code"] == "AGENT_RECONCILE_NO_QUERY_TARGETS"


@pytest.mark.asyncio
async def test_reconcile_invalid_case_kind_422(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900097",
            "telegram": {"tg_id": "97"},
        },
    )

    r = await http_client.post(
        "/api/v1/agent/trading/reconcile",
        json={
            "userId": "97",
            "caseKind": "INVALID",
            "venue": "spot",
            "symbol": "BTC-USDT",
            "orderId": "1",
        },
    )
    assert r.status_code == 422
    assert r.json()["code"] == "VALIDATION_ERROR"
