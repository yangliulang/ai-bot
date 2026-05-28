"""Tests for feature 2026-05-27--admin-ai-settings-gateway-ui (defaults gateway policy regression)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from chainup_agent.application.telegram_llm_narrate_policy import (
    TELEGRAM_LLM_NARRATE_SCENARIO_KEYS,
)
from tests.test_api import _init_schema_sqlite

NARRATE_KEYS = set(TELEGRAM_LLM_NARRATE_SCENARIO_KEYS)


@pytest.mark.asyncio
async def test_gateway_ui_tc01_get_defaults_has_gateway_fields(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-01 / AC-2: GET defaults includes intentNluUseLlm + 9 narrate booleans."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    r = await http_client.get("/api/v1/admin/ai/defaults")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body.get("intentNluUseLlm"), bool)
    narrate = body.get("telegramLlmNarrate")
    assert isinstance(narrate, dict)
    assert set(narrate.keys()) >= NARRATE_KEYS
    for key in TELEGRAM_LLM_NARRATE_SCENARIO_KEYS:
        assert isinstance(narrate[key], bool)


@pytest.mark.asyncio
async def test_gateway_ui_tc02_patch_intent_nlu_use_llm(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-02 / AC-3: PATCH intentNluUseLlm toggles and persists."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    cur = (await http_client.get("/api/v1/admin/ai/defaults")).json()
    target = not bool(cur.get("intentNluUseLlm"))

    patch = await http_client.patch(
        "/api/v1/admin/ai/defaults",
        json={"intentNluUseLlm": target},
    )
    assert patch.status_code == 200
    assert patch.json()["intentNluUseLlm"] is target

    again = await http_client.get("/api/v1/admin/ai/defaults")
    assert again.status_code == 200
    assert again.json()["intentNluUseLlm"] is target


@pytest.mark.asyncio
async def test_gateway_ui_tc03_patch_narrate_partial_merge(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-03 / AC-4: PATCH single narrate field leaves other keys unchanged."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    before = (await http_client.get("/api/v1/admin/ai/defaults")).json()
    snap = dict(before.get("telegramLlmNarrate") or {})

    patch = await http_client.patch(
        "/api/v1/admin/ai/defaults",
        json={"telegramLlmNarrate": {"readMarketDepth": True}},
    )
    assert patch.status_code == 200
    after = patch.json()["telegramLlmNarrate"]
    assert after["readMarketDepth"] is True
    for key in TELEGRAM_LLM_NARRATE_SCENARIO_KEYS:
        if key == "readMarketDepth":
            continue
        assert after[key] == snap.get(key)


@pytest.mark.asyncio
async def test_gateway_ui_tc04_patch_unknown_narrate_field_422(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-04 / AC-5 (P1): unknown telegramLlmNarrate key → 422."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    r = await http_client.patch(
        "/api/v1/admin/ai/defaults",
        json={"telegramLlmNarrate": {"notAField": True}},
    )
    assert r.status_code == 422
    assert r.json()["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_gateway_ui_tc05_patch_scenario_chat_model(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-05 / AC-7: scenarioChatModel PATCH with catalog model id."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    model_id = "gpt-4.1-mini"
    patch = await http_client.patch(
        "/api/v1/admin/ai/defaults",
        json={"scenarioChatModel": model_id},
    )
    assert patch.status_code == 200
    assert patch.json()["scenarioChatModel"] == model_id
    again = await http_client.get("/api/v1/admin/ai/defaults")
    assert again.json()["scenarioChatModel"] == model_id
