"""Write-path TRADING prompt assembly audit (2026-05-28--prompt-runtime-assembly-write)."""

from __future__ import annotations

from urllib.parse import quote

import pytest
from httpx import AsyncClient

from chainup_agent.application.agent_prompt_assembly import assemble_trading_llm_payload
from chainup_agent.application.prompt_assembly_write_path_audit import (
    WRITE_PATH_TRADING_SCENARIO_IDS,
    assert_few_shot_before_context_tools_user,
    assert_trading_write_assembly_order,
)
from chainup_agent.core.config import reset_settings_cache
from chainup_agent.infrastructure.persistence.base import get_session_factory
from tests.prompt_write_path_helpers import seed_write_path_trading_prompt_packs
from tests.skill_spec_helpers import (
    init_binding_sqlite_with_skill_specs,
    seed_skill_operation_specs_from_bundle,
)
from tests.test_api import _init_schema_sqlite, _mock_probe_ok

_WRITE_SCENARIOS = tuple(sorted(WRITE_PATH_TRADING_SCENARIO_IDS))


@pytest.fixture(autouse=True)
async def _seed_skill_specs_db() -> None:
    await seed_skill_operation_specs_from_bundle()


@pytest.mark.asyncio
@pytest.mark.parametrize("scenario_id", _WRITE_SCENARIOS)
async def test_write_path_assembly_order_ac1_ac3(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    scenario_id: str,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    reset_settings_cache()
    factory = get_session_factory()
    async with factory() as session:
        await seed_write_path_trading_prompt_packs(session)
        await session.commit()
    async with factory() as session:
        messages, _ark, meta = await assemble_trading_llm_payload(
            session,
            scenario_id=scenario_id,
            user_text="用户写路径示例",
            effective_locale="zh-Hans",
            execution_id="exec_test_1",
            session_id=None,
            runtime_context={"symbol": "BTC-USDT"},
        )
        assert_trading_write_assembly_order(messages, meta, scenario_id=scenario_id)
        assert_few_shot_before_context_tools_user(messages)


@pytest.mark.asyncio
@pytest.mark.parametrize("scenario_id", _WRITE_SCENARIOS)
async def test_internal_prompt_effective_write_scenarios_ac4(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    scenario_id: str,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    factory = get_session_factory()
    async with factory() as session:
        await seed_write_path_trading_prompt_packs(session)
        await session.commit()

    r = await http_client.get(
        "/api/v1/internal/prompts/effective",
        params={"scenarioId": scenario_id},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == scenario_id
    assert body["promptPackVersion"]
    bind = body["resolvedPromptBinding"]
    assert bind["scenarioId"] == scenario_id
    assert bind["systemPromptPackId"] == "pack_platform_system_v1"
    assert bind["safetyPromptPackId"] == "pack_platform_safety_v1"
    assert bind["tradingPromptPackId"]
    assert isinstance(body["messages"], list)
    assert body["messages"]


def _timeline_step_kind(item: dict) -> str | None:
    sk = item.get("stepKind")
    if sk:
        return str(sk)
    summary = item.get("summary") or {}
    sk2 = summary.get("stepKind")
    return str(sk2) if sk2 else None


def _assert_trading_write_snapshot(items: list[dict], *, scenario_id: str) -> dict:
    snap = next(
        (
            x
            for x in items
            if x["eventName"] == "prompt.snapshot"
            and _timeline_step_kind(x) == "trading_write"
        ),
        None,
    )
    assert snap is not None, "missing prompt.snapshot trading_write"
    payload = snap.get("summary") or {}
    assert payload.get("scenarioId") == scenario_id
    assert payload.get("promptPackVersion")
    assert payload.get("resolvedPromptBinding")
    return payload


@pytest.mark.asyncio
async def test_telegram_limit_trading_write_prompt_snapshot_ac5_ac6(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from cryptography.fernet import Fernet
    from sqlalchemy import select

    from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution

    key = Fernet.generate_key().decode()
    await init_binding_sqlite_with_skill_specs(monkeypatch, tmp_path, key)
    factory = get_session_factory()
    async with factory() as session:
        await seed_write_path_trading_prompt_packs(session)
        await session.commit()
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "88050"},
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
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 91}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(bot_tok, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 150,
            "message": {
                "message_id": 192,
                "from": {"id": 88050, "is_bot": False},
                "chat": {"id": 534450, "type": "private"},
                "text": "BTC-USDT 限价买入 价格 65000 数量 0.01",
            },
        },
    )
    assert r.status_code == 200

    async with factory() as session:
        res = await session.execute(
            select(AgentExecution.execution_id)
            .where(AgentExecution.user_id == "88050")
            .order_by(AgentExecution.created_at.desc())
            .limit(1)
        )
        turn_eid = res.scalar_one()

    effective = await http_client.get(
        "/api/v1/internal/prompts/effective",
        params={"scenarioId": "trade.spot.limit_order"},
    )
    assert effective.status_code == 200
    eff_body = effective.json()

    tl = await http_client.get(
        f"/api/v1/admin/observability/executions/{turn_eid}/timeline"
    )
    assert tl.status_code == 200
    items = tl.json()["items"]
    snap_payload = _assert_trading_write_snapshot(
        items, scenario_id="trade.spot.limit_order"
    )
    assert snap_payload["promptPackVersion"] == eff_body["promptPackVersion"]
    assert snap_payload["resolvedPromptBinding"]["scenarioId"] == "trade.spot.limit_order"

    exec_row = await http_client.get(f"/api/v1/agent/execution/{turn_eid}")
    assert exec_row.status_code == 200
    exec_body = exec_row.json()
    assert exec_body["promptPackVersion"] == eff_body["promptPackVersion"]
    assert exec_body["resolvedPromptBinding"]["scenarioId"] == "trade.spot.limit_order"

    confirm_idx = next(
        i
        for i, x in enumerate(items)
        if x.get("eventName") == "agent.execution.step"
        and _timeline_step_kind(x) == "confirm_prompt"
    )
    snap_idx = next(
        i
        for i, x in enumerate(items)
        if x["eventName"] == "prompt.snapshot"
        and _timeline_step_kind(x) == "trading_write"
    )
    assert snap_idx < confirm_idx
