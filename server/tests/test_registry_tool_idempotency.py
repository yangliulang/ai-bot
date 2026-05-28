"""Registry toolId/skillId idempotency — 2026-05-28--registry-tool-idempotency."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from chainup_agent.application.registry_idempotency import (
    REGISTRY_AUDIT_VERSION,
    assert_enable_allowed,
    assert_obs_tool_call_scenario_join,
    assert_skill_registry_idempotent,
    assert_tool_registry_idempotent,
    load_registry_mirror,
    ssot_tool_ids_from_exchange_registry,
    ssot_tool_ids_from_manifest,
)
from chainup_agent.application.registry_idempotency import _load_bundle_skill_ids


def test_registry_audit_version_and_mirror_load() -> None:
    assert REGISTRY_AUDIT_VERSION == "0.1.0"
    mirror = load_registry_mirror()
    assert len(mirror.skill_ids) >= 11
    assert len(mirror.tool_ids) == 3
    assert len(mirror.scenario_ids) >= 10
    assert len(mirror.items) == len(mirror.skill_ids) + len(mirror.tool_ids)


def test_skill_registry_idempotent() -> None:
    mirror = load_registry_mirror()
    ssot = _load_bundle_skill_ids()
    assert_skill_registry_idempotent(mirror, ssot)


def test_tool_registry_idempotent() -> None:
    mirror = load_registry_mirror()
    manifest_tools = ssot_tool_ids_from_manifest()
    exchange_tools = ssot_tool_ids_from_exchange_registry()
    assert manifest_tools == exchange_tools
    assert_tool_registry_idempotent(mirror, manifest_tools)


def test_enable_allowed_matrix_gate() -> None:
    assert assert_enable_allowed("frozen").allowed is True
    assert assert_enable_allowed("ready").allowed is True
    blocked = assert_enable_allowed("TBD")
    assert blocked.allowed is False
    assert blocked.code == "REGISTRY_MATRIX_TBD"


def test_enable_allowed_draft_p1() -> None:
    blocked = assert_enable_allowed("draft")
    assert blocked.allowed is False
    assert blocked.code == "REGISTRY_MATRIX_TBD"


def test_obs_join_positive() -> None:
    events = [
        {
            "eventName": "agent.orchestration.step",
            "summary": {"scenarioId": "trade.spot.limit_order", "stepKey": "read.skill"},
        },
        {
            "eventName": "trading.exchange_private",
            "summary": {
                "methodPathSummary": "POST /sapi/v2/order",
                "scenarioId": "trade.spot.limit_order",
            },
        },
    ]
    assert_obs_tool_call_scenario_join(events)


def test_obs_join_missing_scenario_negative() -> None:
    events = [
        {
            "eventName": "trading.exchange_private",
            "summary": {"methodPathSummary": "POST /sapi/v2/order"},
        },
    ]
    with pytest.raises(AssertionError, match="SC-OBS01 violated"):
        assert_obs_tool_call_scenario_join(events)


@pytest.mark.asyncio
async def test_admin_registry_list_api(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/admin/tools/registry")
    assert r.status_code == 200
    body = r.json()
    assert body["registryVersion"] == "0.1.0"
    items = body["items"]
    assert items
    stable_ids = {x["stableId"] for x in items}
    assert "skill.spot.limit_order" in stable_ids
    assert "read.market.ticker" in stable_ids
    a_rows = [x for x in items if x["entryClass"] == "A"]
    assert len(a_rows) >= 11


@pytest.mark.asyncio
async def test_admin_registry_idempotency_audit_api(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/admin/tools/registry/idempotency-audit")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["auditVersion"] == "0.1.0"
    assert body["skillMismatches"]["missingInMirror"] == []
    assert body["skillMismatches"]["extraInMirror"] == []
    assert body["toolMismatches"]["missingInMirror"] == []
    assert body["toolMismatches"]["extraInMirror"] == []


@pytest.mark.asyncio
async def test_admin_registry_filter_entry_class(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/admin/tools/registry", params={"entryClass": "B"})
    assert r.status_code == 200
    items = r.json()["items"]
    assert items
    assert all(x["entryClass"] == "B" for x in items)
