"""Guardrails: explicit balance/asset phrasing overrides chat.faq-heavy NLU."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from chainup_agent.application.agent_intent_pipeline import _prefer_read_balance_on_explicit_phrase


def test_prefer_balance_coerces_over_chat_faq() -> None:
    best, ranked = _prefer_read_balance_on_explicit_phrase(
        "我想查下账户余额",
        "chat.faq",
        [("chat.faq", 1.0), ("read.account.balance", 0.35)],
    )
    assert best == "read.account.balance"
    assert ranked[0][0] == "read.account.balance"


def test_prefer_balance_noop_for_generic_hi() -> None:
    best, ranked = _prefer_read_balance_on_explicit_phrase(
        "你好",
        "chat.faq",
        [("chat.faq", 1.0)],
    )
    assert best == "chat.faq"


@pytest.mark.asyncio
async def test_intent_recognize_balance_zh_alias(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "我想查下账户余额"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "read.account.balance"
    assert body.get("plan", {}).get("nextStep") == "ROUTE_READ_SKILL"
