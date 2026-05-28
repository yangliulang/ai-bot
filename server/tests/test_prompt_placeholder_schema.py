"""``variableSchema`` + platform allowlist (runtime-injection §2.1 / §8 AC-09f)."""

from __future__ import annotations

import pytest
from chainup_agent.application.prompt_placeholder_validation import (
    validate_prompt_messages_placeholders_with_schema,
)
from chainup_agent.core.errors import AppError


def test_schema_enforce_accepts_declared_slug() -> None:
    validate_prompt_messages_placeholders_with_schema(
        [{"role": "system", "content": "x {{my_var}} y"}],
        variable_schema_json='{"my_var": {"type": "string"}}',
    )


def test_schema_enforce_rejects_unknown_slug() -> None:
    with pytest.raises(AppError) as ei:
        validate_prompt_messages_placeholders_with_schema(
            [{"role": "system", "content": "{{not_declared}}"}],
            variable_schema_json='{"other": {}}',
        )
    assert ei.value.code == "PROMPT_VALIDATION_FAILED"


def test_platform_allowlist_without_schema() -> None:
    validate_prompt_messages_placeholders_with_schema(
        [{"role": "system", "content": "{{ effective_locale }}"}],
        variable_schema_json=None,
    )


def test_unknown_slug_ok_when_no_schema_object() -> None:
    validate_prompt_messages_placeholders_with_schema(
        [{"role": "system", "content": "{{anything}}"}],
        variable_schema_json=None,
    )


def test_bad_json_schema_raises() -> None:
    with pytest.raises(AppError) as ei:
        validate_prompt_messages_placeholders_with_schema(
            [{"role": "system", "content": "hi"}],
            variable_schema_json="{not json",
        )
    assert ei.value.code == "PROMPT_VALIDATION_FAILED"
