"""SC-PM-22 resolved prompt binding + timeline ``agent.prompt.binding_resolved``."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from chainup_agent.application.resolved_prompt_binding import (
    PROMPT_BINDING_RESOLVED_EVENT,
    build_resolved_prompt_binding,
)
from chainup_agent.core.config import reset_settings_cache
from chainup_agent.infrastructure.persistence.base import get_session_factory
from tests.prompt_write_path_helpers import seed_write_path_trading_prompt_packs
from tests.skill_spec_helpers import seed_skill_operation_specs_from_bundle
from tests.test_api import _init_schema_sqlite


@pytest.mark.asyncio
async def test_build_resolved_prompt_binding_platform_and_trading(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    factory = get_session_factory()
    async with factory() as session:
        await seed_write_path_trading_prompt_packs(session)
        await session.commit()
    async with factory() as session:
        bind = await build_resolved_prompt_binding(
            session, scenario_id="trade.spot.limit_order"
        )
    assert bind is not None
    assert bind["scenarioId"] == "trade.spot.limit_order"
    assert bind["systemPromptPackId"] == "pack_platform_system_v1"
    assert bind["safetyPromptPackId"] == "pack_platform_safety_v1"
    assert bind["tradingPromptPackId"] == "pack_trading_spot_limit_order_v1"
    assert bind["tradingPromptPackVersion"] == "1"
    assert bind.get("fewShotDigest")


@pytest.mark.asyncio
async def test_execution_accept_emits_binding_resolved_timeline(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    reset_settings_cache()
    factory = get_session_factory()
    async with factory() as session:
        await seed_write_path_trading_prompt_packs(session)
        await session.commit()

    r = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={
            "userId": "u-binding-1",
            "scenarioId": "trade.spot.limit_order",
            "channel": "admin_test",
        },
    )
    assert r.status_code == 200
    eid = r.json()["executionId"]

    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    items = tl.json()["items"]
    bind_ev = next(
        (x for x in items if x["eventName"] == PROMPT_BINDING_RESOLVED_EVENT),
        None,
    )
    assert bind_ev is not None
    summary = bind_ev["summary"]
    assert summary.get("promptBindingResolved") or summary.get("resolvedPromptBinding")
    hoisted = summary.get("promptBindingResolved") or summary["resolvedPromptBinding"]
    assert hoisted["systemPromptPackId"] == "pack_platform_system_v1"
    assert hoisted["tradingPromptPackId"] == "pack_trading_spot_limit_order_v1"


@pytest.mark.asyncio
async def test_scenario_skill_scope_endpoint(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await seed_skill_operation_specs_from_bundle()
    await _init_schema_sqlite(monkeypatch, tmp_path)
    factory = get_session_factory()
    async with factory() as session:
        await seed_write_path_trading_prompt_packs(session)
        await session.commit()

    r = await http_client.get(
        "/api/v1/admin/observability/scenarios/trade.spot.limit_order/skill-scope"
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.spot.limit_order"
    assert body["mode"] == "write_skill"
    assert body["promptStrategyPackId"] == "pack_trading_spot_limit_order_v1"
    assert len(body["skills"]) >= 1
    assert body["skills"][0]["skillId"] == "skill.spot.limit_order"
