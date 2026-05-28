"""Tests for Admin-driven LLM chat used by Telegram `chat.faq` path."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from chainup_agent.application.admin_ai_settings import seed_demo_ai_catalog
from chainup_agent.application.agent_llm_chat import (
    _volcengine_ark_responses_url,
    invoke_llm_chat_for_telegram,
    resolve_provider_bearer_token,
)
from chainup_agent.application.agent_llm_upstream import openai_chat_completions_url
from chainup_agent.core.config import get_settings, reset_settings_cache
from chainup_agent.infrastructure.persistence.base import get_engine
from chainup_agent.infrastructure.persistence.models.admin_ai_settings import AdminAiProvider
from httpx import TimeoutException
from sqlalchemy.ext.asyncio import async_sessionmaker
from tests.test_api import _init_schema_sqlite


@pytest.mark.asyncio
async def test_invoke_llm_chat_success(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    monkeypatch.setenv("CHAINUP_AGENT_LLM_FALLBACK_API_KEY", "sk-test-key")
    reset_settings_cache()

    class FakeResponse:
        status_code = 200
        text = ""
        headers = {"content-type": "application/json"}

        def json(self) -> dict:
            return {"choices": [{"message": {"role": "assistant", "content": "你好，我是助手。"}}]}

    class FakeClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *args: object) -> None:
            pass

        async def post(
            self,
            url: str,
            json: dict | None = None,
            headers: dict | None = None,
        ) -> FakeResponse:
            assert "/chat/completions" in url
            assert json is not None
            assert json["model"] == "gpt-4.1-mini"
            assert headers and "Bearer" in headers.get("Authorization", "")
            msgs = json["messages"]
            assert isinstance(msgs, list) and len(msgs) >= 2
            assert msgs[0]["role"] == "system"
            assert "PLATFORM_SYSTEM" in str(msgs[0]["content"])
            assert "SCENARIO_STRATEGY_CHAT_FAQ" in str(msgs[0]["content"])
            assert msgs[-1]["role"] == "user"
            assert msgs[-1]["content"] == "hi"
            return FakeResponse()

    monkeypatch.setattr(
        "chainup_agent.application.agent_llm_chat.httpx.AsyncClient",
        FakeClient,
    )

    factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    async with factory() as session:
        await seed_demo_ai_catalog(session)
        await session.commit()

        reply, err, meta = await invoke_llm_chat_for_telegram(
            session=session,
            settings=get_settings(),
            user_text="hi",
        )

    assert err is None
    assert reply == "你好，我是助手。"
    assert meta is not None
    assert meta.get("gatewayModelId") == "gpt-4.1-mini"
    assert meta.get("promptAssemblyContract")


@pytest.mark.asyncio
async def test_invoke_llm_chat_disallowed_scenario(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """LLM assembly allowlist rejects unknown scenario before gateway lookup."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    monkeypatch.setenv("CHAINUP_AGENT_LLM_FALLBACK_API_KEY", "sk-test-key")
    reset_settings_cache()

    factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    async with factory() as session:
        await seed_demo_ai_catalog(session)
        await session.commit()

        reply, err, meta = await invoke_llm_chat_for_telegram(
            session=session,
            settings=get_settings(),
            user_text="hi",
            scenario_id="trade.margin.market_order",
        )

    assert reply is None
    assert meta is None
    assert err is not None
    assert "未开放" in err
    assert "trade.margin.market_order" in err


@pytest.mark.asyncio
async def test_invoke_llm_chat_missing_key(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    monkeypatch.delenv("CHAINUP_AGENT_LLM_FALLBACK_API_KEY", raising=False)
    reset_settings_cache()

    factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    async with factory() as session:
        await seed_demo_ai_catalog(session)
        await session.commit()

        reply, err, meta = await invoke_llm_chat_for_telegram(
            session=session,
            settings=get_settings(),
            user_text="hi",
        )

    assert reply is None
    assert err is not None
    assert meta is None
    assert "LLM API Key" in err


@pytest.mark.asyncio
async def test_invoke_llm_chat_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    monkeypatch.setenv("CHAINUP_AGENT_LLM_FALLBACK_API_KEY", "sk-test-key")
    reset_settings_cache()

    class FakeClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *args: object) -> None:
            pass

        async def post(
            self,
            url: str,
            json: dict | None = None,
            headers: dict | None = None,
        ) -> None:
            raise TimeoutException("timeout")

    monkeypatch.setattr(
        "chainup_agent.application.agent_llm_chat.httpx.AsyncClient",
        FakeClient,
    )

    factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    async with factory() as session:
        await seed_demo_ai_catalog(session)
        await session.commit()

        reply, err, meta = await invoke_llm_chat_for_telegram(
            session=session,
            settings=get_settings(),
            user_text="hi",
        )

    assert reply is None
    assert err is not None
    assert meta is not None
    assert meta.get("gatewayModelId") == "gpt-4.1-mini"
    assert "超时" in err


def test_volcengine_ark_responses_url_normalizes_base() -> None:
    assert (
        _volcengine_ark_responses_url("https://ark.cn-beijing.volces.com")
        == "https://ark.cn-beijing.volces.com/api/v3/responses"
    )
    assert (
        _volcengine_ark_responses_url("https://ark.cn-beijing.volces.com/api/v3")
        == "https://ark.cn-beijing.volces.com/api/v3/responses"
    )
    assert (
        _volcengine_ark_responses_url("https://ark.cn-beijing.volces.com/api/v3/responses/")
        == "https://ark.cn-beijing.volces.com/api/v3/responses"
    )


def test_resolve_provider_bearer_literal_uuid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Non-env-shaped secret_ref is used as the Bearer token (plaintext in DB)."""
    monkeypatch.delenv("CHAINUP_AGENT_LLM_FALLBACK_API_KEY", raising=False)
    reset_settings_cache()
    token = "c00a9861-8a98-4881-90e9-1705b526758f"
    prov = SimpleNamespace(secret_ref=token)
    assert resolve_provider_bearer_token(get_settings(), prov) == token


def test_resolve_provider_bearer_env_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_LLM_KEY", "sk-from-env")
    reset_settings_cache()
    prov = SimpleNamespace(secret_ref="MY_LLM_KEY")
    assert resolve_provider_bearer_token(get_settings(), prov) == "sk-from-env"


@pytest.mark.asyncio
async def test_invoke_llm_chat_volcengine_ark(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    monkeypatch.delenv("CHAINUP_AGENT_LLM_FALLBACK_API_KEY", raising=False)
    reset_settings_cache()

    captured: dict[str, object] = {}

    class FakeResponse:
        status_code = 200
        text = ""
        headers = {"content-type": "application/json"}

        def json(self) -> dict:
            return {
                "output": [
                    {
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "方舟答复"}],
                    }
                ]
            }

    class FakeClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *args: object) -> None:
            pass

        async def post(
            self,
            url: str,
            json: dict | None = None,
            headers: dict | None = None,
        ) -> FakeResponse:
            captured["url"] = url
            captured["json"] = json
            captured["headers"] = headers
            return FakeResponse()

    monkeypatch.setattr(
        "chainup_agent.application.agent_llm_chat.httpx.AsyncClient",
        FakeClient,
    )

    factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    async with factory() as session:
        await seed_demo_ai_catalog(session)
        prov = await session.get(AdminAiProvider, "demo")
        assert prov is not None
        prov.base_url = "https://ark.cn-beijing.volces.com"
        prov.secret_ref = "literal-ark-key"
        await session.commit()

        reply, err, meta = await invoke_llm_chat_for_telegram(
            session=session,
            settings=get_settings(),
            user_text=" 今天热点 ",
        )

    assert err is None
    assert reply == "方舟答复"
    assert meta is not None
    assert meta.get("useArkProtocol") is True
    assert meta.get("promptAssemblyContract")
    assert str(captured["url"]).endswith("/api/v3/responses")
    body = captured["json"]
    assert isinstance(body, dict)
    assert body.get("stream") is False
    assert body.get("model") == "gpt-4.1-mini"
    inp = body.get("input")
    assert isinstance(inp, list) and inp
    content = inp[0]["content"]
    assert content[0]["type"] == "input_text"
    flat = content[0]["text"]
    assert "PLATFORM_SYSTEM" in flat
    assert "TOOL_SPEC_JSON_SCHEMA_SSOT" in flat
    assert "今天热点" in flat
    hdrs = captured["headers"]
    assert isinstance(hdrs, dict)
    assert hdrs.get("Authorization") == "Bearer literal-ark-key"


@pytest.mark.asyncio
async def test_invoke_llm_chat_html_404_non_json(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """SiliconFlow-style misconfigured baseUrl returns HTML 404 — user sees actionable hint."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    monkeypatch.setenv("CHAINUP_AGENT_LLM_FALLBACK_API_KEY", "sk-test-key")
    reset_settings_cache()

    class FakeResponse:
        status_code = 404
        headers = {"content-type": "text/html"}
        text = "<html>404</html>"

        def json(self) -> dict:
            raise ValueError("not json")

    class FakeClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *args: object) -> None:
            pass

        async def post(
            self,
            url: str,
            json: dict | None = None,
            headers: dict | None = None,
        ) -> FakeResponse:
            assert url == openai_chat_completions_url("https://api.siliconflow.cn/v1")
            return FakeResponse()

    monkeypatch.setattr(
        "chainup_agent.application.agent_llm_chat.httpx.AsyncClient",
        FakeClient,
    )

    factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    async with factory() as session:
        await seed_demo_ai_catalog(session)
        from chainup_agent.infrastructure.persistence.models.admin_ai_settings import AdminAiProvider

        prov = await session.get(AdminAiProvider, "demo")
        assert prov is not None
        prov.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        await session.commit()

        reply, err, meta = await invoke_llm_chat_for_telegram(
            session=session,
            settings=get_settings(),
            user_text="hi",
        )

    assert reply is None
    assert err is not None
    assert meta is not None
    assert "非 JSON" in err
    assert "chat/completions" in err
