"""`{{…}}` placeholder checks for Prompt Management Save/Publish (runtime-injection §2.3)."""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from chainup_agent.core.errors import AppError

# Slug body must not contain these (case-insensitive), per product `runtime-injection` §2.3.1.
_DENY_SUBSTRINGS: tuple[str, ...] = (
    "APIKEY",
    "API_KEY",
    "ACCESS_KEY",
    "SECRET",
    "SECRET_KEY",
    "HMAC",
    "SIGNING",
    "PRIVATE_KEY",
    "REFRESH_TOKEN",
    "BEARER",
    "AUTH_TOKEN",
    "PASSWORD",
    "PASSWD",
    "CREDENTIAL",
    "WEBHOOK_SECRET",
    "CLIENT_SECRET",
    "INTERNAL_CONFIG",
    "INTERNALCONFIG",
    "INTERNAL_API",
    "ADMIN_URL",
    "DEBUG_TOKEN",
    "SUBACCOUNT_SECRET",
    "TRADING_API_SECRET",
    "AGENT_TRADING_KEY",
)

PLACEHOLDER_BRACE_PATTERN = re.compile(r"\{\{([^}]*)\}\}")

# Backwards-compat name used inside this module.
_PLACEHOLDER_RE = PLACEHOLDER_BRACE_PATTERN

# Platform built-in keys (normalized UPPER) — ASSEMBLY §2 + runtime-injection §2.4.
# Exported for runtime substitution (`prompt_runtime_substitution`).
PLATFORM_PLACEHOLDER_SLUGS: frozenset[str] = frozenset(
    {
        "EFFECTIVE_LOCALE",
        "SCENARIO_ID",
        "EXECUTION_ID",
        "PROMPT_PACK_VERSION",
        "USER_VISIBLE_MESSAGE",
        "REQUIRES_MAIN_SITE",
        "SESSION_ID",
        "AGENT_CONTEXT",
    }
)


def _normalize_slug(inner: str) -> str:
    return "".join(inner.split()).upper()


def normalize_placeholder_slug(inner: str) -> str:
    """Normalize ``{{ inner }}`` slug for comparison (collapse whitespace, UPPER)."""
    return _normalize_slug(inner)


def variable_schema_placeholder_mode(
    variable_schema_json: str | None,
) -> tuple[Literal["skip", "enforce"], frozenset[str]]:
    """Runtime allowlist: **skip** (no non-empty schema) vs **enforce** (schema object keys)."""
    mode, keys, _ = _parse_variable_schema_keys(variable_schema_json)
    if mode == "error":
        return "skip", frozenset()
    if mode == "enforce":
        return "enforce", keys
    return "skip", frozenset()


def _parse_variable_schema_keys(
    variable_schema_json: str | None,
) -> tuple[str, frozenset[str], str | None]:
    """Returns ``(mode, keys, error_message)``.

    - ``skip``: do not enforce allowlist (compat).
    - ``enforce``: every ``{{slug}}`` must be in ``keys ∪ platform``.
    - ``error``: invalid JSON or type; ``error_message`` is user-safe text.
    """
    if variable_schema_json is None or not str(variable_schema_json).strip():
        return "skip", frozenset(), None
    try:
        obj = json.loads(variable_schema_json)
    except json.JSONDecodeError as exc:
        return "error", frozenset(), f"variableSchema 不是合法 JSON：{exc!s}"[:400]
    if obj is None:
        return "skip", frozenset(), None
    if not isinstance(obj, dict):
        return "error", frozenset(), "variableSchema 根类型须为 JSON 对象。"
    if len(obj) == 0:
        return "skip", frozenset(), None
    keys = frozenset(_normalize_slug(str(k)) for k in obj if str(k).strip())
    return "enforce", keys, None


def _collect_strings_from_messages(messages: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        c = m.get("content")
        if isinstance(c, str) and c.strip():
            out.append(c)
    return out


def validate_prompt_messages_placeholders(
    messages: list[dict[str, Any]],
    *,
    field_label: str = "messages",
) -> None:
    """Raises ``AppError`` **PROMPT_VALIDATION_FAILED** when placeholders violate §2.3."""
    blob = "\n".join(_collect_strings_from_messages(messages))
    pos = 0
    while True:
        m = _PLACEHOLDER_RE.search(blob, pos)
        if m is None:
            break
        inner = m.group(1)
        if "{{" in inner:
            raise AppError(
                code="PROMPT_VALIDATION_FAILED",
                message="占位符语法无效：检测到嵌套的 `{{`。",
                status_code=422,
                details={"field": field_label, "reason": "nested_placeholder"},
            )
        slug_for_compare = "".join(inner.split()).upper()
        if not slug_for_compare.strip():
            raise AppError(
                code="PROMPT_VALIDATION_FAILED",
                message="占位符不能为空：请检查 `{{ }}` 内的键名。",
                status_code=422,
                details={"field": field_label, "reason": "empty_placeholder_slug"},
            )
        for banned in _DENY_SUBSTRINGS:
            if banned.upper() in slug_for_compare:
                raise AppError(
                    code="PROMPT_VALIDATION_FAILED",
                    message=f"占位符命中禁止子串（Secret / 运维面风险）：`{banned}`。",
                    status_code=422,
                    details={
                        "field": field_label,
                        "reason": "placeholder_denylist",
                        "matchedSubstring": banned,
                    },
                )
        pos = m.end()


def validate_prompt_messages_placeholders_with_schema(
    messages: list[dict[str, Any]],
    *,
    variable_schema_json: str | None,
    field_label: str = "messages",
) -> None:
    """§2.3 denylist + §2.1 allowlist when ``variableSchema`` is a **non-empty** object."""
    validate_prompt_messages_placeholders(messages, field_label=field_label)
    mode, schema_keys, json_err = _parse_variable_schema_keys(variable_schema_json)
    if mode == "error":
        raise AppError(
            code="PROMPT_VALIDATION_FAILED",
            message=json_err or "variableSchema 无效。",
            status_code=422,
            details={"field": "variableSchema", "reason": "invalid_variable_schema_json"},
        )
    if mode != "enforce":
        return
    allowed = PLATFORM_PLACEHOLDER_SLUGS | schema_keys
    blob = "\n".join(_collect_strings_from_messages(messages))
    pos = 0
    while True:
        m = _PLACEHOLDER_RE.search(blob, pos)
        if m is None:
            break
        inner = m.group(1)
        if "{{" in inner:
            raise AppError(
                code="PROMPT_VALIDATION_FAILED",
                message="占位符语法无效：检测到嵌套的 `{{`。",
                status_code=422,
                details={"field": field_label, "reason": "nested_placeholder"},
            )
        slug = _normalize_slug(inner)
        if not slug.strip():
            raise AppError(
                code="PROMPT_VALIDATION_FAILED",
                message="占位符不能为空：请检查 `{{ }}` 内的键名。",
                status_code=422,
                details={"field": field_label, "reason": "empty_placeholder_slug"},
            )
        if slug not in allowed:
            raise AppError(
                code="PROMPT_VALIDATION_FAILED",
                message=(
                    "占位符未在 `variableSchema` 或平台内置白名单中声明："
                    f"`{inner.strip()}`。"
                ),
                status_code=422,
                details={
                    "field": field_label,
                    "reason": "placeholder_not_in_schema_or_allowlist",
                    "slug": inner.strip()[:200],
                },
            )
        pos = m.end()
