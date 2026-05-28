"""Telegram multi-turn read.depth follow-up (深度数据呢) must not raise."""

from __future__ import annotations

from unittest.mock import AsyncMock
from urllib.parse import quote

import pytest
from httpx import AsyncClient

from chainup_agent.application.memory_session_store import (
    remember_pending_clarify,
    reset_memory_session_store_for_tests,
)
from chainup_agent.core.config import reset_settings_cache

from tests.test_api import _init_binding_sqlite, _mock_probe_ok


@pytest.mark.asyncio
async def test_telegram_depth_followup_after_market_analysis(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    async def fake_depth(*, openapi_base_url: str, symbol_candidates: list[str], limit: int):
        _ = openapi_base_url, symbol_candidates, limit
        return {
            "asks": [["72843.71", "1.2"], ["72844.00", "0.5"]],
            "bids": [["72842.96", "2.1"], ["72842.50", "0.8"]],
        }

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_depth_json_with_fallbacks",
        fake_depth,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY", "true")
    reset_settings_cache()
    assert (await http_client.get("/api/v1/admin/ai/providers")).status_code == 200
    tg_id = "88006"
    chat_id = 424885
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900002",
                "telegram": {"tg_id": tg_id},
            },
        )
    ).status_code == 200

    token = "configured:bbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL", "https://example.com/bind")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_INTENT_NLU_USE_LLM", "false")
    monkeypatch.setenv("CHAINUP_AGENT_INTENT_CLARIFY_USE_LLM", "false")
    reset_settings_cache()
    reset_memory_session_store_for_tests()

    llm_mock = AsyncMock(return_value=("盘面简述：买卖盘均衡。", None, {}))
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        llm_mock,
    )
    sent: list[str] = []

    async def capture_send(*_a, **kw):
        sent.append(kw.get("json_payload", {}).get("text", ""))
        return {"ok": True, "result": {"message_id": 1}}

    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        capture_send,
    )

    enc = quote(token, safe="")
    base = {
        "from": {"id": int(tg_id), "is_bot": False},
        "chat": {"id": chat_id, "type": "private"},
    }

    r1 = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 101,
            "message": {**base, "message_id": 1, "text": "下午盘面怎么样"},
        },
    )
    assert r1.status_code == 200
    assert sent, "first turn should reply"
    assert "内部错误" not in sent[-1]
    assert "ValidationError" not in sent[-1]

    remember_pending_clarify(
        f"tg:{chat_id}",
        scenario_id="read.market.depth",
        slots={"symbol": "BTC-USDT"},
    )

    r2 = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 102,
            "message": {**base, "message_id": 2, "text": "深度数据呢"},
        },
    )
    assert r2.status_code == 200
    assert len(sent) >= 2, "second turn should reply"
    assert "内部错误" not in sent[-1], sent[-1][:500]
    assert "ValidationError" not in sent[-1]
    assert "read.market.depth" in sent[-1] or "盘口" in sent[-1] or "深度" in sent[-1]
