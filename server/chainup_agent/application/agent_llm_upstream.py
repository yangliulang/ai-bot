"""Shared upstream HTTP parsing for Admin AI gateway LLM calls (OpenAI-compat + Ark)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Only strip the completions path segment; keep ``/v1`` API version on the base URL.
_OPENAI_CHAT_SUFFIX = "/chat/completions"


@dataclass(frozen=True)
class UpstreamHttpResult:
    """Normalized outcome of one upstream LLM HTTP response."""

    status_code: int
    content_type: str
    body_text: str
    parsed_json: dict[str, Any] | None

    @property
    def is_json(self) -> bool:
        return self.parsed_json is not None

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300 and self.is_json


def normalize_openai_compat_base_url(base: str) -> str:
    """
    Strip trailing ``/chat/completions`` (or ``/v1/chat/completions``) so Provider
    ``baseUrl`` may be either API root or a full completions URL (avoids double path).
    """
    b = base.strip().rstrip("/")
    if b.lower().endswith(_OPENAI_CHAT_SUFFIX):
        return b[: -len(_OPENAI_CHAT_SUFFIX)].rstrip("/")
    return b


def openai_chat_completions_url(base: str) -> str:
    root = normalize_openai_compat_base_url(base)
    return f"{root}/chat/completions"


def _looks_like_json_body(text: str) -> bool:
    s = text.lstrip()
    return bool(s) and s[0] in "{["


def parse_upstream_http_response(response: httpx.Response) -> UpstreamHttpResult:
    """Parse body as JSON when Content-Type or shape suggests JSON; never raises."""
    status = int(response.status_code)
    ctype = (response.headers.get("content-type") or "").split(";")[0].strip().lower()
    try:
        text = response.text or ""
    except Exception:
        text = ""

    parsed: dict[str, Any] | None = None
    if "json" in ctype or _looks_like_json_body(text):
        try:
            data = response.json()
            if isinstance(data, dict):
                parsed = data
        except (ValueError, json.JSONDecodeError):
            parsed = None

    if parsed is None and text:
        preview = text[:160].replace("\n", " ")
        logger.debug(
            "upstream_non_json status=%s ctype=%s preview=%s",
            status,
            ctype or "(none)",
            preview,
        )

    return UpstreamHttpResult(
        status_code=status,
        content_type=ctype,
        body_text=text,
        parsed_json=parsed,
    )


def upstream_http_error_message(
    result: UpstreamHttpResult,
    *,
    label: str = "LLM",
) -> str:
    """User-safe one-liner for failed upstream (HTTP error or non-JSON body)."""
    if not result.is_json:
        hint = ""
        if result.status_code == 404:
            hint = "（请检查 Provider baseUrl 是否为 API 根路径，勿重复填写 /chat/completions）"
        elif result.body_text and "<html" in result.body_text[:200].lower():
            hint = "（上游返回 HTML 页面，多为 URL 或鉴权配置错误）"
        return f"{label} 返回非 JSON（HTTP {result.status_code}）{hint}"

    data = result.parsed_json or {}
    err_payload = data.get("error")
    msg = ""
    if isinstance(err_payload, dict):
        msg = str(err_payload.get("message") or err_payload.get("code") or "")[:400]
    if not msg:
        msg = str(data.get("message") or data.get("msg") or "")[:400]
    if not msg:
        msg = result.body_text[:400] if result.body_text else f"HTTP {result.status_code}"
    return f"{label} 返回错误（HTTP {result.status_code}）：{msg}"
