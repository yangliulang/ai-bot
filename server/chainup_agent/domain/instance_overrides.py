"""I05 instanceOverrides whitelist (agent-management §2.2)."""

from __future__ import annotations

from typing import Any

INSTANCE_OVERRIDE_ALLOWED_KEYS = frozenset(
    {
        "preferredLanguage",
        "cooldownPreferenceSec",
        "symbolPreference",
        "voiceOutputEnabled",
    }
)


def parse_instance_overrides_json(raw: str | None) -> dict[str, Any]:
    import json

    if not raw or not str(raw).strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def validate_instance_overrides_patch(
    patch: dict[str, Any] | None,
    *,
    existing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Merge ``existing`` with ``patch``; reject unknown keys (field-level 422).
    """
    base = dict(existing or {})
    if patch is None:
        return base
    if not isinstance(patch, dict):
        raise ValueError("instanceOverrides must be an object")
    unknown = [k for k in patch if k not in INSTANCE_OVERRIDE_ALLOWED_KEYS]
    if unknown:
        from chainup_agent.core.errors import AppError

        raise AppError(
            code="VALIDATION_ERROR",
            message="instanceOverrides 含未登记键",
            status_code=422,
            details={
                "field": "instanceOverrides",
                "unknownKeys": unknown[:20],
                "allowedKeys": sorted(INSTANCE_OVERRIDE_ALLOWED_KEYS),
            },
        )
    merged = {**base, **patch}
    # Type sanity for known keys
    if "cooldownPreferenceSec" in merged and merged["cooldownPreferenceSec"] is not None:
        try:
            sec = int(merged["cooldownPreferenceSec"])
        except (TypeError, ValueError) as e:
            from chainup_agent.core.errors import AppError

            raise AppError(
                code="VALIDATION_ERROR",
                message="cooldownPreferenceSec 须为整数",
                status_code=422,
                details={"field": "cooldownPreferenceSec"},
            ) from e
        if sec < 0 or sec > 86400:
            from chainup_agent.core.errors import AppError

            raise AppError(
                code="VALIDATION_ERROR",
                message="cooldownPreferenceSec 超出允许范围",
                status_code=422,
                details={"field": "cooldownPreferenceSec", "max": 86400},
            )
        merged["cooldownPreferenceSec"] = sec
    if "symbolPreference" in merged and merged["symbolPreference"] is not None:
        sp = merged["symbolPreference"]
        if not isinstance(sp, list) or not all(isinstance(x, str) for x in sp):
            from chainup_agent.core.errors import AppError

            raise AppError(
                code="VALIDATION_ERROR",
                message="symbolPreference 须为字符串数组",
                status_code=422,
                details={"field": "symbolPreference"},
            )
    return merged


def dumps_instance_overrides(data: dict[str, Any]) -> str:
    import json

    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
