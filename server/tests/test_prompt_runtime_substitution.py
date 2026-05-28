"""runtime `{{…}}` substitution (`prompt_runtime_substitution` · AC-09h)."""

from __future__ import annotations

import pytest

from chainup_agent.application.prompt_runtime_substitution import substitute_runtime_placeholders
from chainup_agent.core.errors import AppError


def _builtin() -> dict[str, str]:
    return {
        "EFFECTIVE_LOCALE": "en",
        "SCENARIO_ID": "read.market.ticker",
        "EXECUTION_ID": "e1",
        "PROMPT_PACK_VERSION": "3",
        "USER_VISIBLE_MESSAGE": "",
        "REQUIRES_MAIN_SITE": "false",
        "SESSION_ID": "s",
        "AGENT_CONTEXT": "",
    }


def test_platform_slug_skip_mode_strips_unknown() -> None:
    out, stripped = substitute_runtime_placeholders(
        "locale={{effective_locale}} x={{CUSTOM_UNKNOWN}}!",
        variable_schema_json=None,
        builtin_values_upper=_builtin(),
    )
    assert "en" in out
    assert "CUSTOM_UNKNOWN" not in out
    assert stripped == ["CUSTOM_UNKNOWN"]


def test_enforce_mode_accepts_platform_and_schema() -> None:
    out, stripped = substitute_runtime_placeholders(
        "{{ my_var }} / {{scenario_id}}",
        variable_schema_json='{"my_var": {"type": "string"}}',
        builtin_values_upper=_builtin(),
        extra_values_upper={"MY_VAR": "hello"},
    )
    assert stripped == []
    assert "hello" in out
    assert "read.market.ticker" in out


def test_enforce_unknown_slug_raises() -> None:
    with pytest.raises(AppError) as ei:
        substitute_runtime_placeholders(
            "{{not_declared}}",
            variable_schema_json='{"ok": {"type":"string"}}',
            builtin_values_upper=_builtin(),
        )
    assert ei.value.code == "PROMPT_INJECTION_FORBIDDEN"


def test_nested_placeholder_raises() -> None:
    with pytest.raises(AppError) as ei:
        substitute_runtime_placeholders(
            "{{evil{{nested}}}}",
            variable_schema_json=None,
            builtin_values_upper=_builtin(),
        )
    assert ei.value.code == "PROMPT_INJECTION_FORBIDDEN"
