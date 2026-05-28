"""Tests for feature 2026-05-26--nlu-llm-strategy (gateway_defaults.intentNluUseLlm)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from chainup_agent.api.schemas.agent_runtime import (
    IntentNluDraft,
    IntentRecognizeResponse,
    IntentScenarioCandidateDraft,
)
from chainup_agent.application.agent_intent_pipeline import resolve_effective_intent_nlu_use_llm
from chainup_agent.core.config import Settings, reset_settings_cache
from chainup_agent.core.errors import AppError

from tests.test_api import _init_schema_sqlite


def test_resolve_effective_intent_nlu_env_overrides_admin_false() -> None:
    settings = Settings(intent_nlu_use_llm=True)
    assert resolve_effective_intent_nlu_use_llm(settings, {"intentNluUseLlm": False}) is True


def test_resolve_effective_intent_nlu_admin_true_when_env_false() -> None:
    settings = Settings(intent_nlu_use_llm=False)
    assert resolve_effective_intent_nlu_use_llm(settings, {"intentNluUseLlm": True}) is True
    assert resolve_effective_intent_nlu_use_llm(settings, {"intentNluUseLlm": False}) is False
    assert resolve_effective_intent_nlu_use_llm(settings, None) is False


@pytest.mark.asyncio
async def test_admin_defaults_intent_nlu_use_llm_patch_get(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-01: PATCH/GET intentNluUseLlm on gateway defaults."""
    await _init_schema_sqlite(monkeypatch, tmp_path)

    dr = await http_client.get("/api/v1/admin/ai/defaults")
    assert dr.status_code == 200
    assert dr.json().get("intentNluUseLlm") is False

    patch = await http_client.patch(
        "/api/v1/admin/ai/defaults",
        json={"intentNluUseLlm": True},
    )
    assert patch.status_code == 200
    assert patch.json()["intentNluUseLlm"] is True

    again = await http_client.get("/api/v1/admin/ai/defaults")
    assert again.status_code == 200
    assert again.json()["intentNluUseLlm"] is True


@pytest.mark.asyncio
async def test_intent_recognize_llm_via_admin_defaults(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-02 / TC-06: Admin intentNluUseLlm enables LLM branch."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    assert (
        await http_client.patch("/api/v1/admin/ai/defaults", json={"intentNluUseLlm": True})
    ).status_code == 200

    llm_mock = AsyncMock(
        return_value=(
            IntentNluDraft(
                source="llm_structured_v1",
                primary_intent_family="portfolio_read",
                scenario_id_candidates=[
                    IntentScenarioCandidateDraft(
                        scenario_id="read.account.balance",
                        confidence=0.88,
                    ),
                ],
                slots={},
                order_type_hint="unknown",
                clarify_hints=[],
            ),
            [("read.account.balance", 0.88)],
        )
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_llm_intent_nlu.try_llm_intent_nlu_draft",
        llm_mock,
    )

    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "查询 BTC 账户余额", "locale": "zh-Hans"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["nlu"]["source"] == "llm_structured_v1"
    assert body["effectiveIntentNluUseLlm"] is True
    llm_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_intent_recognize_llm_fallback_keyword(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-03: LLM enabled but draft None → keyword_v1, HTTP 200."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    await http_client.patch("/api/v1/admin/ai/defaults", json={"intentNluUseLlm": True})

    llm_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "chainup_agent.application.agent_llm_intent_nlu.try_llm_intent_nlu_draft",
        llm_mock,
    )

    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "查询 BTC 账户余额"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["nlu"]["source"] == "keyword_v1"
    assert body["effectiveIntentNluUseLlm"] is True


@pytest.mark.asyncio
async def test_intent_recognize_keyword_only_skips_llm(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-04: defaults false + env false → no LLM call."""
    await _init_schema_sqlite(monkeypatch, tmp_path)

    llm_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "chainup_agent.application.agent_llm_intent_nlu.try_llm_intent_nlu_draft",
        llm_mock,
    )

    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "查询 BTC 账户余额"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["nlu"]["source"] == "keyword_v1"
    assert body["effectiveIntentNluUseLlm"] is False
    llm_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_intent_recognize_env_overrides_admin_defaults(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-05: env true forces LLM even when admin intentNluUseLlm=false."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    await http_client.patch("/api/v1/admin/ai/defaults", json={"intentNluUseLlm": False})
    monkeypatch.setenv("CHAINUP_AGENT_INTENT_NLU_USE_LLM", "true")
    reset_settings_cache()

    llm_mock = AsyncMock(
        return_value=(
            IntentNluDraft(
                source="llm_structured_v1",
                primary_intent_family="chat",
                scenario_id_candidates=[
                    IntentScenarioCandidateDraft(scenario_id="chat.faq", confidence=0.9),
                ],
                slots={},
                order_type_hint="unknown",
                clarify_hints=[],
            ),
            [("chat.faq", 0.9)],
        )
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_llm_intent_nlu.try_llm_intent_nlu_draft",
        llm_mock,
    )

    r = await http_client.post("/api/v1/agent/intent/recognize", json={"text": "hello"})
    assert r.status_code == 200
    assert r.json()["nlu"]["source"] == "llm_structured_v1"
    assert r.json()["effectiveIntentNluUseLlm"] is True


@pytest.mark.asyncio
async def test_intent_recognize_prompt_injection_forbidden_fallback(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """TC-08: PROMPT_INJECTION_FORBIDDEN → keyword_v1, 200."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    monkeypatch.setenv("CHAINUP_AGENT_INTENT_NLU_USE_LLM", "true")
    reset_settings_cache()

    async def _raise_injection(*_a, **_k):
        raise AppError(
            code="PROMPT_INJECTION_FORBIDDEN",
            message="blocked",
            status_code=400,
            details={},
        )

    monkeypatch.setattr(
        "chainup_agent.application.agent_llm_intent_nlu.assemble_intent_nlu_system_prompt",
        _raise_injection,
    )

    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "查询余额"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["nlu"]["source"] == "keyword_v1"
    assert body["effectiveIntentNluUseLlm"] is True


@pytest.mark.asyncio
async def test_telegram_timeline_intent_nlu_llm_enabled_uses_effective(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-07: prompt.snapshot intentNluLlmEnabled follows effectiveIntentNluUseLlm."""
    from chainup_agent.application.telegram_bound_reply import _append_intent_nlu_prompt_timeline

    captured: dict = {}

    async def _capture_append(_session, **kwargs):
        captured.update(kwargs.get("payload") or {})

    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.append_execution_timeline_event",
        _capture_append,
    )
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.effective_prompt_snapshot_for_scenario",
        AsyncMock(return_value=("v1", "default")),
    )

    settings = Settings(intent_nlu_use_llm=False)
    ir_on = IntentRecognizeResponse(
        scenario_id="chat.faq",
        confidence=0.5,
        nlu_source="llm_structured_v1",
        effective_intent_nlu_use_llm=True,
    )
    await _append_intent_nlu_prompt_timeline(
        MagicMock(),
        settings,
        execution_id="e1",
        user_id="1",
        ir=ir_on,
        plan=None,
        exec_scenario_id="chat.faq",
    )
    assert captured["intentNluLlmEnabled"] is True

    captured.clear()
    ir_off = IntentRecognizeResponse(
        scenario_id="chat.faq",
        confidence=0.5,
        nlu_source="keyword_v1",
        effective_intent_nlu_use_llm=False,
    )
    await _append_intent_nlu_prompt_timeline(
        MagicMock(),
        settings,
        execution_id="e2",
        user_id="1",
        ir=ir_off,
        plan=None,
        exec_scenario_id="chat.faq",
    )
    assert captured["intentNluLlmEnabled"] is False
