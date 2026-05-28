"""Upstream LLM HTTP normalization and parsing."""

from __future__ import annotations

from chainup_agent.application.agent_llm_upstream import (
    normalize_openai_compat_base_url,
    openai_chat_completions_url,
    parse_upstream_http_response,
    upstream_http_error_message,
)


def test_normalize_openai_compat_base_url_strips_completions_suffix() -> None:
    assert (
        normalize_openai_compat_base_url("https://api.siliconflow.cn/v1/chat/completions")
        == "https://api.siliconflow.cn/v1"
    )
    assert (
        openai_chat_completions_url("https://api.siliconflow.cn/v1/chat/completions")
        == "https://api.siliconflow.cn/v1/chat/completions"
    )


def test_normalize_openai_compat_base_url_keeps_root() -> None:
    assert normalize_openai_compat_base_url("https://api.openai.com/v1") == "https://api.openai.com/v1"


def test_parse_upstream_html_404() -> None:
    class FakeResp:
        status_code = 404
        headers = {"content-type": "text/html"}

        @property
        def text(self) -> str:
            return "<html><body>Not Found</body></html>"

        def json(self) -> dict:
            raise ValueError("not json")

    result = parse_upstream_http_response(FakeResp())  # type: ignore[arg-type]
    assert not result.is_json
    msg = upstream_http_error_message(result)
    assert "非 JSON" in msg
    assert "404" in msg
    assert "chat/completions" in msg


def test_parse_upstream_json_error_body() -> None:
    class FakeResp:
        status_code = 401
        headers = {"content-type": "application/json"}
        text = '{"error":{"message":"invalid api key"}}'

        def json(self) -> dict:
            return {"error": {"message": "invalid api key"}}

    result = parse_upstream_http_response(FakeResp())  # type: ignore[arg-type]
    assert result.is_json
    assert not result.is_success
    msg = upstream_http_error_message(result)
    assert "401" in msg
    assert "invalid api key" in msg
