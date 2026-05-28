"""Telegram — LLM via Admin AI catalog + gateway defaults.

Supports OpenAI-compatible ``POST …/chat/completions`` and Volcano Ark-style
``POST …/api/v3/responses`` (when Provider ``baseUrl`` host contains ``volces.com``).
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.admin_ai_settings import (
    get_model,
    get_provider,
    read_gateway_defaults_merged,
)
from chainup_agent.application.agent_llm_upstream import (
    UpstreamHttpResult,
    openai_chat_completions_url,
    parse_upstream_http_response,
    upstream_http_error_message,
)
from chainup_agent.application.agent_prompt_assembly import (
    TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS,
    assemble_trading_llm_payload,
)
from chainup_agent.core.config import Settings
from chainup_agent.infrastructure.persistence.models.admin_ai_settings import AdminAiProvider

logger = logging.getLogger(__name__)

_ENV_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_MAX_USER_CHARS = 12_000
_MAX_ASSISTANT_CHARS = 2800


def resolve_provider_bearer_token(settings: Settings, provider: AdminAiProvider) -> str | None:
    """
    Resolve Bearer token for upstream LLM.

    - If ``secret_ref`` matches ``^[A-Za-z_][A-Za-z0-9_]*$``, treat it as an **environment
      variable name** and read ``os.environ[secret_ref]``.
    - Otherwise treat ``secret_ref`` as the **literal API Key / token** pasted from Admin
      (**stored plaintext** in ``admin_ai_provider.secret_ref`` — convenience).
    - If ``secret_ref`` empty: ``Settings.llm_fallback_api_key``.
    """
    ref = (provider.secret_ref or "").strip()
    if ref:
        if _ENV_NAME_RE.match(ref):
            v = os.environ.get(ref)
            if v and v.strip():
                return v.strip()
            return None
        return ref
    fb = (settings.llm_fallback_api_key or "").strip()
    return fb or None


def _pick_scenario_model_id(merged: dict[str, Any]) -> str:
    for key in ("scenarioChatModel", "defaultModelId", "defaultInferenceModel"):
        v = merged.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _use_volcengine_ark_responses(base_url: str) -> bool:
    host = (urlparse(base_url).hostname or "").lower()
    return "volces.com" in host


def _volcengine_ark_responses_url(base: str) -> str:
    """Normalize Provider baseUrl to ``…/api/v3/responses`` (Volcano Ark)."""
    b = base.strip().rstrip("/")
    low = b.lower()
    if low.endswith("/api/v3/responses"):
        return b
    if low.endswith("/api/v3"):
        return f"{b}/responses"
    return f"{b}/api/v3/responses"


@dataclass(frozen=True)
class LlmGatewayContext:
    """Resolved Admin AI catalog + token for one upstream LLM HTTP call."""

    model_id: str  # Catalog PK referenced by gateway_defaults / UI
    upstream_model_id: str  # Value for JSON ``"model"`` field (endpoint wire id)
    provider_id: str
    base_url: str
    token: str
    merged_defaults: dict[str, Any]
    use_ark: bool


def _llm_chat_observability_meta(ctx: LlmGatewayContext) -> dict[str, Any]:
    return {
        "gatewayModelId": ctx.model_id,
        "gatewayUpstreamModel": ctx.upstream_model_id,
        "gatewayProviderId": ctx.provider_id,
        "useArkProtocol": ctx.use_ark,
    }


async def load_llm_gateway_context(
    session: AsyncSession,
    settings: Settings,
) -> tuple[LlmGatewayContext | None, str | None]:
    """
    Same provider/model/token resolution as ``invoke_llm_chat_for_telegram``.

    Returns ``(ctx, None)`` or ``(None, user_safe_error)``.
    """
    merged, _ver = await read_gateway_defaults_merged(session)
    model_id = _pick_scenario_model_id(merged)
    if not model_id:
        return None, (
            "网关默认未配置场景模型（`scenarioChatModel` / `defaultModelId`）。"
            "请在 Admin · AI 运行时策略保存后再试。"
        )

    row = await get_model(session, model_id)
    if row is None:
        return None, (
            f"模型目录中不存在 `{model_id}`。请在 Admin 添加该模型或调整运行时策略中的模型 id。"
        )

    if (row.status or "").strip().lower() != "enabled":
        return None, f"模型 `{model_id}` 当前不可用（status=`{row.status}`）。"

    prov = await get_provider(session, row.provider_id)
    if prov is None:
        return None, f"未找到 Provider `{row.provider_id}`。"

    token = resolve_provider_bearer_token(settings, prov)
    if not token:
        return None, (
            "缺少 LLM API Key：请在 Admin **Provider · secretRef** 填写 API Key"
            "（会明文入库）或 **环境变量名**（仅字母数字下划线且首字符为字母/下划线），"
            "或配置服务端 `CHAINUP_AGENT_LLM_FALLBACK_API_KEY`。"
        )

    base = prov.base_url.strip().rstrip("/")
    if not base:
        return None, "Provider `baseUrl` 为空，无法调用 LLM。"

    use_ark = _use_volcengine_ark_responses(base)
    wire = (row.api_model or "").strip() if row.api_model else ""
    upstream = wire if wire else row.model_id
    return (
        LlmGatewayContext(
            model_id=row.model_id,
            upstream_model_id=upstream,
            provider_id=row.provider_id,
            base_url=base,
            token=token,
            merged_defaults=merged,
            use_ark=use_ark,
        ),
        None,
    )


def _build_ark_responses_payload(model_id: str, user_text: str, *, stream: bool) -> dict[str, Any]:
    """Volcano Ark Responses API — align with ``/api/v3/responses`` JSON shape."""
    return {
        "model": model_id,
        "stream": stream,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": user_text[:_MAX_USER_CHARS],
                    }
                ],
            }
        ],
    }


def _extract_text_from_ark_response(data: dict[str, Any]) -> str:
    """Best-effort parse Ark ``/responses`` JSON (non-stream full body)."""
    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            msg = first.get("message")
            if isinstance(msg, dict):
                c = msg.get("content")
                if isinstance(c, str) and c.strip():
                    return c.strip()

    out = data.get("output")
    if isinstance(out, list):
        chunks: list[str] = []
        for item in out:
            if not isinstance(item, dict):
                continue
            contents = item.get("content")
            if isinstance(contents, list):
                for piece in contents:
                    if not isinstance(piece, dict):
                        continue
                    typ = str(piece.get("type") or "")
                    if typ in ("output_text", "input_text", "text"):
                        tx = piece.get("text")
                        if isinstance(tx, str) and tx.strip():
                            chunks.append(tx.strip())
            elif isinstance(contents, str) and contents.strip():
                chunks.append(contents.strip())
        if chunks:
            return "\n".join(chunks)

    # Some payloads nest text under result / error-less stubs
    for key in ("text", "content", "output_text"):
        v = data.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()

    return ""


def _extract_openai_chat_content(data: dict[str, Any]) -> str:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    msg_block = first.get("message")
    if isinstance(msg_block, dict):
        return str(msg_block.get("content") or "").strip()
    return ""


async def invoke_llm_chat_for_telegram(
    *,
    session: AsyncSession,
    settings: Settings,
    user_text: str,
    scenario_id: str = "chat.faq",
    effective_locale: str | None = None,
    execution_id: str | None = None,
    session_id: str | None = None,
    runtime_context: dict[str, Any] | None = None,
) -> tuple[str | None, str | None, dict[str, Any] | None]:
    """
    Chat completion for Telegram turns wired to **TRADING** prompt assembly.

    Builds **Prompt Assembly** messages (`runtime-injection` §1): platform SYSTEM → SAFETY →
    scenario TRADING strategy + Few-shot → Runtime Context JSON → Tool Spec (JSON Schema SSOT)
    → user turn.

    ``scenario_id`` must be in **TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS**
    (**`chat.faq`**、Telegram **行情公有读**：**`read.market.ticker`** /
    **`read.market.depth`** / **`read.market.trades`**（迁移 **`0014`** / **`0015`**），
    以及 **托管只读**：**`read.account.balance`** / **`wealth.holdings_read`**
    （迁移 **`0016`**）。

    Returns ``(assistant_plain_text, user_safe_error, observability_meta)`` — on the
    assistant/error pair exactly one side is non-None. ``observability_meta`` includes gateway ids
    plus optional ``promptAssembly*`` keys when assembly succeeds.
    """
    raw = user_text.strip()
    if not raw:
        return None, "空消息已忽略。", None

    sid = scenario_id.strip()
    if sid not in TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS:
        allowed = ", ".join(sorted(TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS))
        return (
            None,
            f"场景 `{sid}` 未开放 LLM 拼装（当前允许：{allowed}）。",
            None,
        )

    ctx, err = await load_llm_gateway_context(session, settings)
    if ctx is None:
        return None, err, None

    openai_msgs, ark_flat, asm_extra = await assemble_trading_llm_payload(
        session,
        scenario_id=sid,
        user_text=raw,
        effective_locale=effective_locale,
        execution_id=execution_id,
        session_id=session_id,
        runtime_context=runtime_context,
    )

    timeout_sec = float(ctx.merged_defaults.get("timeoutSec") or 120)
    max_out = int(ctx.merged_defaults.get("maxOutputTokens") or 1024)
    max_out = max(1, min(max_out, 8192))

    meta_out = {**_llm_chat_observability_meta(ctx), **asm_extra}

    if ctx.use_ark:
        # Non-stream for Telegram single reply; Ark defaults stream=false per vendor docs.
        payload: dict[str, Any] = _build_ark_responses_payload(
            ctx.upstream_model_id, ark_flat, stream=False
        )
    else:
        payload = {
            "model": ctx.upstream_model_id,
            "messages": openai_msgs,
            "max_tokens": max_out,
        }

    headers = {
        "Authorization": f"Bearer {ctx.token}",
        "Content-Type": "application/json",
    }

    url = (
        _volcengine_ark_responses_url(ctx.base_url)
        if ctx.use_ark
        else openai_chat_completions_url(ctx.base_url)
    )

    try:
        async with httpx.AsyncClient(timeout=timeout_sec, follow_redirects=True) as client:
            r = await client.post(url, json=payload, headers=headers)
    except httpx.TimeoutException:
        logger.warning(
            "llm_chat_timeout model=%s provider=%s ark=%s",
            ctx.model_id,
            ctx.provider_id,
            ctx.use_ark,
        )
        return (
            None,
            f"调用 LLM 超时（>{int(timeout_sec)}s）。可调大网关 `timeoutSec` 或稍后重试。",
            meta_out,
        )
    except httpx.HTTPError as exc:
        logger.warning(
            "llm_chat_transport model=%s err=%s",
            ctx.model_id,
            type(exc).__name__,
        )
        return None, "调用 LLM 网络失败，请稍后重试。", meta_out

    upstream = parse_upstream_http_response(r)
    if not upstream.is_success:
        if upstream.is_json and upstream.status_code >= 400:
            logger.info(
                "llm_chat_upstream_error status=%s model=%s ark=%s",
                upstream.status_code,
                ctx.model_id,
                ctx.use_ark,
            )
        return None, upstream_http_error_message(upstream), meta_out

    data = upstream.parsed_json or {}
    if ctx.use_ark:
        content = _extract_text_from_ark_response(data)
    else:
        content = _extract_openai_chat_content(data)

    if not content:
        logger.warning(
            "llm_chat_empty_body model=%s ark=%s keys=%s",
            ctx.model_id,
            ctx.use_ark,
            list(data.keys())[:12],
        )
        return (
            None,
            "模型返回空内容（响应结构与预期不一致，请查看服务端日志）。",
            meta_out,
        )

    if len(content) > _MAX_ASSISTANT_CHARS:
        content = content[: _MAX_ASSISTANT_CHARS - 1] + "…"

    logger.info(
        "llm_chat_ok model=%s provider=%s ark=%s assistant_chars=%s",
        ctx.model_id,
        ctx.provider_id,
        ctx.use_ark,
        len(content),
    )
    return content, None, meta_out


_ERROR_REWRITE_SYSTEM = (
    "你是加密货币交易助手。把系统或交易所返回的错误改写成对 Telegram 用户"
    "友好、简洁的中文（1～4 句）。\n"
    "\n"
    "硬性要求：\n"
    "- 只根据输入 JSON 的字段理解含义，不要编造数值、费率、账户状态。\n"
    "- 不要 Markdown、列表符号、代码块。\n"
    "- 语气礼貌；涉及精度/最小下单量/步长时，用「请核对数量小数位或交易所最小下单精度」"
    "等概括表述。\n"
    "- 不要大段照抄英文；可意译要点。\n"
    "- 只输出给用户看的正文，不要包含「错误码」字样（系统会另附）。"
)

_MAX_ERROR_CTX_JSON_CHARS = 6000
_MAX_ERROR_REWRITE_OUT_CHARS = 1200


async def invoke_llm_rewrite_telegram_app_error(
    *,
    session: AsyncSession,
    settings: Settings,
    context_json: dict[str, Any],
) -> tuple[str | None, str | None]:
    """
    Rewrite structured trading error context to friendly Chinese for Telegram.

    Returns ``(text, None)`` or ``(None, short_reason)`` for logging / fallback.
    Unexpected errors (DB, JSON, parsing) are logged and returned as
    ``(None, "internal_error")`` so Telegram replies never depend on LLM not throwing.
    """

    async def _run() -> tuple[str | None, str | None]:
        ctx, err = await load_llm_gateway_context(session, settings)
        if ctx is None:
            return None, err or "no_gateway"

        timeout_sec = min(
            float(settings.telegram_error_llm_timeout_sec),
            float(ctx.merged_defaults.get("timeoutSec") or 120),
        )
        max_out = int(ctx.merged_defaults.get("maxOutputTokens") or 512)
        max_out = max(64, min(max_out, 1024))

        raw = json.dumps(context_json, ensure_ascii=False)
        user_block = raw[:_MAX_ERROR_CTX_JSON_CHARS]

        if ctx.use_ark:
            combined = (
                f"{_ERROR_REWRITE_SYSTEM}\n\n请以输入为唯一依据，输出改写后的中文正文。\n输入（JSON）：\n"
                f"{user_block}"
            )
            payload: dict[str, Any] = _build_ark_responses_payload(
                ctx.upstream_model_id, combined, stream=False
            )
        else:
            payload = {
                "model": ctx.upstream_model_id,
                "messages": [
                    {"role": "system", "content": _ERROR_REWRITE_SYSTEM},
                    {
                        "role": "user",
                        "content": f"请根据下列 JSON 改写为友好中文正文：\n{user_block}",
                    },
                ],
                "max_tokens": max_out,
                "temperature": 0.2,
            }

        headers = {
            "Authorization": f"Bearer {ctx.token}",
            "Content-Type": "application/json",
        }
        url = (
            _volcengine_ark_responses_url(ctx.base_url)
            if ctx.use_ark
            else openai_chat_completions_url(ctx.base_url)
        )

        try:
            async with httpx.AsyncClient(timeout=timeout_sec, follow_redirects=True) as client:
                r = await client.post(url, json=payload, headers=headers)
        except httpx.TimeoutException:
            logger.warning(
                "llm_error_rewrite_timeout model=%s provider=%s",
                ctx.model_id,
                ctx.provider_id,
            )
            return None, "timeout"
        except httpx.HTTPError as exc:
            logger.warning(
                "llm_error_rewrite_transport model=%s err=%s",
                ctx.model_id,
                type(exc).__name__,
            )
            return None, "transport"

        upstream: UpstreamHttpResult = parse_upstream_http_response(r)
        if not upstream.is_success:
            if not upstream.is_json:
                return None, "non_json"
            return None, f"http_{upstream.status_code}"

        data = upstream.parsed_json or {}
        if ctx.use_ark:
            content = _extract_text_from_ark_response(data)
        else:
            content = _extract_openai_chat_content(data)

        if not content or not str(content).strip():
            return None, "empty"

        text = str(content).strip()
        if len(text) > _MAX_ERROR_REWRITE_OUT_CHARS:
            text = text[: _MAX_ERROR_REWRITE_OUT_CHARS - 1] + "…"

        logger.info(
            "llm_error_rewrite_ok model=%s provider=%s ark=%s out_chars=%s",
            ctx.model_id,
            ctx.provider_id,
            ctx.use_ark,
            len(text),
        )
        return text, None

    try:
        return await _run()
    except Exception:
        logger.exception("llm_error_rewrite_unexpected")
        return None, "internal_error"
