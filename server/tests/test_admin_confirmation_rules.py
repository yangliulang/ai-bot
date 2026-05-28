"""Admin confirmation rules API + runtime evaluation."""

from __future__ import annotations

from decimal import Decimal

import pytest
from chainup_agent.application.confirmation_rules_evaluate import (
    ConfirmationEvalContext,
    evaluate_confirmation_rules_sync,
)
from chainup_agent.domain.confirmation_rules_catalog import BUILTIN_CONFIRMATION_RULES
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_confirmation_rules_list_includes_builtin_and_demo(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/admin/confirmation-rules")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 9
    ids = {item["id"] for item in body["items"]}
    assert "hitl-trade-fund-write" in ids
    assert "custom-demo-flash-convert" in ids
    builtin = next(i for i in body["items"] if i["id"] == "hitl-trade-fund-write")
    assert builtin["isBuiltin"] is True
    assert builtin["enabled"] is True


@pytest.mark.asyncio
async def test_admin_confirmation_rules_custom_crud(http_client: AsyncClient) -> None:
    created = await http_client.post(
        "/api/v1/admin/confirmation-rules",
        json={
            "title": "测试规则",
            "summary": "单元测试自定义规则",
            "riskLevel": "low",
            "triggerConditions": [
                {"fieldKey": "nominal_usdt", "operator": "gt", "value": "1000"},
            ],
            "scenarios": ["spot"],
            "action": "second_confirm",
            "defaultEnabled": True,
        },
    )
    assert created.status_code == 201
    rid = created.json()["id"]
    assert rid.startswith("custom-")

    got = await http_client.get(f"/api/v1/admin/confirmation-rules/{rid}")
    assert got.status_code == 200
    assert got.json()["title"] == "测试规则"

    patched = await http_client.patch(
        f"/api/v1/admin/confirmation-rules/{rid}/enabled",
        json={"enabled": False},
    )
    assert patched.status_code == 200
    assert patched.json()["enabled"] is False

    updated = await http_client.put(
        f"/api/v1/admin/confirmation-rules/{rid}",
        json={
            "title": "测试规则 v2",
            "summary": "更新摘要",
            "riskLevel": "medium",
            "triggerConditions": [
                {"fieldKey": "nominal_usdt", "operator": "gte", "value": "2000"},
            ],
            "scenarios": ["spot", "convert"],
            "action": "second_confirm",
            "defaultEnabled": True,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "测试规则 v2"

    deleted = await http_client.delete(f"/api/v1/admin/confirmation-rules/{rid}")
    assert deleted.status_code == 204

    missing = await http_client.get(f"/api/v1/admin/confirmation-rules/{rid}")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_admin_confirmation_rules_builtin_readonly(http_client: AsyncClient) -> None:
    put = await http_client.put(
        "/api/v1/admin/confirmation-rules/hitl-trade-fund-write",
        json={
            "title": "x",
            "summary": "y",
            "riskLevel": "high",
            "triggerConditions": [
                {"fieldKey": "operation_scope", "operator": "contains", "value": "x"},
            ],
            "scenarios": ["spot"],
            "action": "force_confirm",
            "defaultEnabled": True,
        },
    )
    assert put.status_code == 409
    assert put.json()["code"] == "AGENT_ADMIN_CONFIRMATION_RULE_BUILTIN_READONLY"

    delete = await http_client.delete("/api/v1/admin/confirmation-rules/hitl-trade-fund-write")
    assert delete.status_code == 409


@pytest.mark.asyncio
async def test_admin_confirmation_rules_reset(http_client: AsyncClient) -> None:
    created = await http_client.post(
        "/api/v1/admin/confirmation-rules",
        json={
            "title": "待重置",
            "summary": "将被 reset 清除",
            "riskLevel": "low",
            "triggerConditions": [
                {"fieldKey": "custom", "operator": "eq", "value": "x"},
            ],
            "scenarios": ["spot"],
            "action": "force_confirm",
            "defaultEnabled": False,
        },
    )
    assert created.status_code == 201
    rid = created.json()["id"]

    reset = await http_client.post("/api/v1/admin/confirmation-rules/reset")
    assert reset.status_code == 200
    ids = {item["id"] for item in reset.json()["items"]}
    assert rid not in ids
    assert "custom-demo-flash-convert" in ids


@pytest.mark.asyncio
async def test_internal_confirmation_rules_effective(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/internal/confirmation-rules/effective")
    assert r.status_code == 200
    assert r.json()["total"] >= 9


def test_confirmation_eval_large_notional_second_confirm() -> None:
    rules = [(r, True) for r in BUILTIN_CONFIRMATION_RULES]
    ctx = ConfirmationEvalContext(
        scenario_key="spot",
        nominal_usdt=Decimal("60000"),
        operation_scope="改变持仓、委托或余额 · 现货写路径",
    )
    result = evaluate_confirmation_rules_sync(rules, ctx)
    assert result.requires_second_confirm is True
    assert any(m.rule_id == "hitl-large-notional" for m in result.matched_rules)


def test_confirmation_eval_block_auto_execute() -> None:
    from chainup_agent.domain.confirmation_rules_catalog import DEMO_CUSTOM_CONFIRMATION_RULES

    rules = [(r, True) for r in BUILTIN_CONFIRMATION_RULES]
    rules.append((DEMO_CUSTOM_CONFIRMATION_RULES[2], True))
    ctx = ConfirmationEvalContext(
        scenario_key="futures",
        operation_scope="高频或网格类自动化模板",
    )
    result = evaluate_confirmation_rules_sync(rules, ctx)
    assert result.block_auto_execute is True
