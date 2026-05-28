"""Runtime ``{{…}}`` substitution for prompt snippets (runtime-injection §2 / AC-09h)."""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping

from chainup_agent.application.prompt_placeholder_validation import (
    PLATFORM_PLACEHOLDER_SLUGS,
    PLACEHOLDER_BRACE_PATTERN,
    normalize_placeholder_slug,
    variable_schema_placeholder_mode,
)
from chainup_agent.core.errors import AppError

logger = logging.getLogger(__name__)


def substitute_runtime_placeholders(
    text: str,
    *,
    variable_schema_json: str | None,
    builtin_values_upper: Mapping[str, str],
    extra_values_upper: Mapping[str, str] | None = None,
    observability_context: str | None = None,
) -> tuple[str, list[str]]:
    """
    Substitute placeholders in arbitrary prompt text.

    Returns ``(resolved_text, unresolved_or_stripped_slug_norms)``.
    Raises ``AppError`` **PROMPT_INJECTION_FORBIDDEN** when **variableSchema** is in
    **enforce** mode and a slug is not in ``platform ∪ schema`` or placeholders are malformed.
    In **skip** mode, unknown slugs are stripped to empty string and listed (observable).
    """
    vs_mode, schema_keys = variable_schema_placeholder_mode(variable_schema_json)
    enforce_allowlist = vs_mode == "enforce"
    allowed = PLATFORM_PLACEHOLDER_SLUGS | schema_keys

    values_upper: dict[str, str] = {
        normalize_placeholder_slug(k): str(v) for k, v in builtin_values_upper.items()
    }
    for plat in PLATFORM_PLACEHOLDER_SLUGS:
        values_upper.setdefault(plat, "")
    for sk in schema_keys:
        values_upper.setdefault(sk, "")
    if extra_values_upper:
        for raw_k, raw_v in extra_values_upper.items():
            values_upper[normalize_placeholder_slug(str(raw_k))] = str(raw_v)

    stripped: list[str] = []

    def repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        if "{{" in inner:
            raise AppError(
                code="PROMPT_INJECTION_FORBIDDEN",
                message="运行时占位符非法：检测到嵌套的 `{{`。",
                status_code=400,
                details={"reason": "nested_placeholder"},
            )
        slug = normalize_placeholder_slug(inner)
        if not slug:
            if enforce_allowlist:
                raise AppError(
                    code="PROMPT_INJECTION_FORBIDDEN",
                    message="运行时占位符非法：空占位符键名。",
                    status_code=400,
                    details={"reason": "empty_placeholder_slug"},
                )
            stripped.append("(EMPTY_SLUG)")
            return ""
        if slug not in allowed:
            if enforce_allowlist:
                raise AppError(
                    code="PROMPT_INJECTION_FORBIDDEN",
                    message=f"运行时占位符未获准：`{slug}`（须属于 variableSchema ∪ 平台白名单）。",
                    status_code=400,
                    details={"reason": "placeholder_not_allowlisted_runtime", "slug": slug[:200]},
                )
            stripped.append(slug)
            return ""
        return values_upper.get(slug, "")

    out = PLACEHOLDER_BRACE_PATTERN.sub(repl, text)
    if stripped:
        logger.warning(
            "prompt_runtime_placeholder_stripped stripped=%s ctx=%s enforce=%s",
            stripped[:48],
            observability_context or "-",
            enforce_allowlist,
        )
    return out, stripped
