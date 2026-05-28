"""Write-path pipeline — read_skill + timeline causal order (2026-05-27--runtime-write-path-pipeline)."""

from __future__ import annotations

from urllib.parse import quote

import pytest
from httpx import AsyncClient

from chainup_agent.application.write_path_pipeline import assert_write_path_pipeline_order
from tests.skill_spec_helpers import (
    init_binding_sqlite_with_skill_specs,
    seed_skill_operation_specs_from_bundle,
)


@pytest.fixture(autouse=True)
async def _seed_skill_specs_db() -> None:
    await seed_skill_operation_specs_from_bundle()


def _assert_read_skill_orchestration_step(items: list[dict]) -> None:
    spec_idx = next(i for i, x in enumerate(items) if x["eventName"] == "agent.skill.spec_read")
    read_steps = [
        i
        for i, x in enumerate(items)
        if x["eventName"] == "agent.orchestration.step"
        and (x.get("summary") or {}).get("stepKey") == "read.skill"
    ]
    assert read_steps, "missing agent.orchestration.step read.skill"
    assert min(read_steps) <= spec_idx


@pytest.mark.asyncio
async def test_runtime_skill_operation_spec_effective_200(
    http_client: AsyncClient,
) -> None:
    r = await http_client.get(
        "/api/v1/runtime/skill-operation-spec/effective",
        params={"skillId": "skill.spot.limit_order"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["skillId"] == "skill.spot.limit_order"
    assert body["skillSpecVersion"]
    assert body["specDigest"]
    assert body["lifecycle"] == "PUBLISHED"
    assert isinstance(body["sections"], list)
    assert len(body["sections"]) >= 1


@pytest.mark.asyncio
async def test_runtime_skill_operation_spec_unknown_404(
    http_client: AsyncClient,
) -> None:
    r = await http_client.get(
        "/api/v1/runtime/skill-operation-spec/effective",
        params={"skillId": "skill.unknown.not_published"},
    )
    assert r.status_code == 404
    assert r.json()["code"] == "PROMPT_SKILL_REF_INVALID"


@pytest.mark.asyncio
async def test_http_limit_order_write_path_timeline(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    from tests.test_api import _mock_probe_ok

    key = Fernet.generate_key().decode()
    await init_binding_sqlite_with_skill_specs(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88001"},
            },
        )
    ).status_code == 200

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        AsyncMock(
            return_value={
                "orderIdString": "1",
                "clientOrderId": "cu_agent_limit",
                "status": "0",
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "LIMIT",
                "price": "48000.0",
            }
        ),
    )
    r = await http_client.post(
        "/api/v1/agent/trade/spot/limit-order",
        json={
            "userId": "88001",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "volume": "0.02",
            "price": "48000",
            "timeInForce": "GTC",
        },
    )
    assert r.status_code == 200
    lst = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"userId": "88001", "limit": 1},
    )
    eid = lst.json()["items"][0]["executionId"]
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    items = tl.json()["items"]
    assert_write_path_pipeline_order(items)
    names = [x["eventName"] for x in items]
    assert "agent.skill.spec_read" in names
    _assert_read_skill_orchestration_step(items)


@pytest.mark.asyncio
async def test_telegram_limit_webhook_type_a_emits_spec_read(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-02 / TC-04 — full TG turn before Type-A callback."""
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet
    from sqlalchemy import select

    from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution
    from chainup_agent.infrastructure.persistence.base import get_session_factory
    from tests.test_api import _mock_probe_ok

    key = Fernet.generate_key().decode()
    await init_binding_sqlite_with_skill_specs(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88003"},
            },
        )
    ).status_code == 200

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "64000"}),
    )
    bot_tok = "configured:ffffffffffffffffffffffffffff"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 81}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(bot_tok, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 100,
            "message": {
                "message_id": 182,
                "from": {"id": 88003, "is_bot": False},
                "chat": {"id": 534381, "type": "private"},
                "text": "BTC-USDT 限价买入 价格 65000 数量 0.01",
            },
        },
    )
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    assert body.get("reply_markup", {}).get("inline_keyboard")

    factory = get_session_factory()
    async with factory() as session:
        res = await session.execute(
            select(AgentExecution.execution_id)
            .where(AgentExecution.user_id == "88003")
            .order_by(AgentExecution.created_at.desc())
            .limit(1)
        )
        turn_eid = res.scalar_one()

    tl = await http_client.get(
        f"/api/v1/admin/observability/executions/{turn_eid}/timeline"
    )
    items = tl.json()["items"]
    spec = next(x for x in items if x["eventName"] == "agent.skill.spec_read")
    assert spec["summary"]["phase"] == "success"
    assert spec["summary"]["skillId"] == "skill.spot.limit_order"
    _assert_read_skill_orchestration_step(items)
    assert "confirmation.required" in [x["eventName"] for x in items]


@pytest.mark.asyncio
async def test_invalid_skill_blocks_before_type_a_markup(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-06 — no published skill pointer → no Type-A keyboard, no spec_read."""
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet
    from sqlalchemy import delete, select

    from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution
    from chainup_agent.infrastructure.persistence.models.skill_operation_spec import (
        SkillOperationSpecPointer,
    )
    from chainup_agent.infrastructure.persistence.base import get_session_factory
    from tests.test_api import _init_binding_sqlite, _mock_probe_ok

    factory = get_session_factory()
    async with factory() as session:
        await session.execute(
            delete(SkillOperationSpecPointer).where(
                SkillOperationSpecPointer.skill_id == "skill.spot.limit_order"
            )
        )
        await session.commit()

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88004"},
            },
        )
    ).status_code == 200

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "64000"}),
    )
    bot_tok = "configured:bbbbbbbbbbbbbbbbbbbbbbbbbb"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 82}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(bot_tok, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 101,
            "message": {
                "message_id": 183,
                "from": {"id": 88004, "is_bot": False},
                "chat": {"id": 534382, "type": "private"},
                "text": "BTC-USDT 限价买入 价格 65000 数量 0.01",
            },
        },
    )
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    assert not body.get("reply_markup")

    factory = get_session_factory()
    async with factory() as session:
        res = await session.execute(
            select(AgentExecution.execution_id)
            .where(AgentExecution.user_id == "88004")
            .order_by(AgentExecution.created_at.desc())
            .limit(1)
        )
        turn_eid = res.scalar_one()

    tl = await http_client.get(
        f"/api/v1/admin/observability/executions/{turn_eid}/timeline"
    )
    names = [x["eventName"] for x in tl.json()["items"]]
    assert "agent.skill.spec_read" not in names
    assert "trading.exchange_private" not in names


@pytest.mark.asyncio
async def test_telegram_amend_confirm_write_path_timeline(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-07 — amend Type-A callback + five-segment order."""
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    from chainup_agent.application.telegram_flash_pending import create_spot_amend_pending
    from chainup_agent.core.config import reset_settings_cache
    from chainup_agent.infrastructure.persistence.base import get_session_factory
    from tests.test_api import _mock_probe_ok

    prior_oid = "256609229205684228"

    async def fake_cancel(**kwargs: object) -> dict:
        _ = kwargs
        return {"orderId": prior_oid, "status": "CANCELED"}

    async def fake_order(**kwargs: object) -> dict:
        _ = kwargs
        return {"orderId": "256609229205684229", "status": "NEW", "type": "LIMIT"}

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_cancel_json",
        fake_cancel,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        fake_order,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_signed_spot_open_orders_json",
        AsyncMock(
            return_value=[
                {
                    "orderIdString": prior_oid,
                    "symbol": "BTCUSDT",
                    "status": "NEW",
                    "type": "LIMIT",
                    "side": "BUY",
                    "price": "64000",
                    "origQty": "0.01",
                    "timeInForce": "GTC",
                }
            ]
        ),
    )

    key = Fernet.generate_key().decode()
    await init_binding_sqlite_with_skill_specs(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88005"},
            },
        )
    ).status_code == 200

    turn_eid = ""
    factory = get_session_factory()
    async with factory() as session:
        from chainup_agent.application.agent_execution_memory import (
            ExecutionAcceptRequest,
            execution_accept,
        )
        from chainup_agent.application.write_path_pipeline import (
            append_confirmation_required,
            ensure_write_path_skill_spec_read,
        )

        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id="88005",
                scenario_id="trade.spot.amend_limit_order",
                channel="telegram",
            ),
            source="telegram_webhook",
        )
        turn_eid = acc.execution_id
        await ensure_write_path_skill_spec_read(
            session,
            execution_id=turn_eid,
            user_id="88005",
            scenario_id="trade.spot.amend_limit_order",
            channel="telegram",
        )
        token = await create_spot_amend_pending(
            session,
            telegram_user_id=88005,
            chat_id=2,
            symbol="BTC-USDT",
            order_id=prior_oid,
            side="BUY",
            prior_price="64000",
            prior_quantity="0.01",
            price="65000",
            quantity="0.01",
            time_in_force="GTC",
            execution_id=turn_eid,
        )
        await append_confirmation_required(
            session,
            execution_id=turn_eid,
            user_id="88005",
            scenario_id="trade.spot.amend_limit_order",
            channel="telegram",
        )
        await session.commit()

    bot_tok = "configured:cccccccccccccccccccccccccc"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_callback_handler.call_telegram_bot_api",
        AsyncMock(return_value={"ok": True}),
    )

    enc = quote(bot_tok, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 102,
            "callback_query": {
                "id": "cq-wp-amend",
                "from": {"id": 88005, "is_bot": False},
                "message": {"message_id": 2, "chat": {"id": 2, "type": "private"}},
                "data": f"smp{token}",
            },
        },
    )
    assert r.status_code == 200

    tl = await http_client.get(
        f"/api/v1/admin/observability/executions/{turn_eid}/timeline"
    )
    items = tl.json()["items"]
    assert_write_path_pipeline_order(items)
    spec = next(x for x in items if x["eventName"] == "agent.skill.spec_read")
    assert spec["summary"]["skillId"] == "skill.spot.amend_limit_order"
    _assert_read_skill_orchestration_step(items)


@pytest.mark.asyncio
async def test_telegram_limit_confirm_write_path_timeline(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    from chainup_agent.application.telegram_flash_pending import create_spot_limit_pending
    from chainup_agent.core.config import reset_settings_cache
    from chainup_agent.infrastructure.persistence.base import get_session_factory
    from tests.test_api import _mock_probe_ok

    key = Fernet.generate_key().decode()
    await init_binding_sqlite_with_skill_specs(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88002"},
            },
        )
    ).status_code == 200

    turn_eid = ""
    factory = get_session_factory()
    async with factory() as session:
        from chainup_agent.application.agent_execution_memory import (
            ExecutionAcceptRequest,
            execution_accept,
        )

        acc = await execution_accept(
            session,
            ExecutionAcceptRequest(
                user_id="88002",
                scenario_id="trade.spot.limit_order",
                channel="telegram",
            ),
            source="telegram_webhook",
        )
        turn_eid = acc.execution_id
        from chainup_agent.application.write_path_pipeline import (
            append_confirmation_required,
            ensure_write_path_skill_spec_read,
        )

        await ensure_write_path_skill_spec_read(
            session,
            execution_id=turn_eid,
            user_id="88002",
            scenario_id="trade.spot.limit_order",
            channel="telegram",
        )
        token = await create_spot_limit_pending(
            session,
            telegram_user_id=88002,
            chat_id=1,
            symbol="BTC-USDT",
            side="BUY",
            quantity="0.01",
            price="65000",
            time_in_force="GTC",
            execution_id=turn_eid,
        )
        await append_confirmation_required(
            session,
            execution_id=turn_eid,
            user_id="88002",
            scenario_id="trade.spot.limit_order",
            channel="telegram",
        )
        await session.commit()

    bot_tok = "configured:eeeeeeeeeeeeeeeeeeeeeeeeee"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_callback_handler.call_telegram_bot_api",
        AsyncMock(return_value={"ok": True}),
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        AsyncMock(
            return_value={
                "orderIdString": "2",
                "clientOrderId": "cu_agent_limit_cb",
                "status": "0",
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "LIMIT",
                "price": "65000",
            }
        ),
    )

    enc = quote(bot_tok, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 99,
            "callback_query": {
                "id": "cq-wp1",
                "from": {"id": 88002, "is_bot": False},
                "message": {"message_id": 1, "chat": {"id": 1, "type": "private"}},
                "data": f"lcp{token}",
            },
        },
    )
    assert r.status_code == 200

    tl = await http_client.get(
        f"/api/v1/admin/observability/executions/{turn_eid}/timeline"
    )
    assert tl.status_code == 200
    items = tl.json()["items"]
    assert_write_path_pipeline_order(items)
    spec = next(x for x in items if x["eventName"] == "agent.skill.spec_read")
    assert spec["summary"]["phase"] == "success"
    assert spec["summary"]["skillId"] == "skill.spot.limit_order"
    assert "bodyMarkdown" not in spec["summary"]
    _assert_read_skill_orchestration_step(items)
