"""Memory/STM + SESSION config — env Settings with optional GlobalConfigBundle overrides."""

from __future__ import annotations

from typing import Any, Literal

from chainup_agent.core.config import Settings, get_settings

# SSOT keys: product-doc/.../trading-agent-config/keys.md §2.1～§2.3 (MR-MEM subset).
MEMORY_RUNTIME_CONFIG_KEYS: frozenset[str] = frozenset(
    {
        "STM_L0_MAX_TURNS",
        "STM_IDLE_RESUME_PROMPT_SEC",
        "STM_IDLE_DEFAULT_POLICY",
        "STM_CLARIFY_SESSION_TTL_SEC",
        "RESUME_CLASSIFIER_MODE",
        "RESUME_CLASSIFIER_MIN_CONFIDENCE",
        "WARM_EXECUTION_INDEX_TTL_SEC",
        "STM_SESSION_CLEAR_MODE",
        "STM_HOT_RECYCLE_SESSION_IDLE_SEC",
        "STM_HOT_RECYCLE_EXECUTION_AFTER_TERMINAL_SEC",
        "SESSION_INBOUND_QUEUE_POLICY",
        "SESSION_INBOUND_QUEUE_MAX_DEPTH",
        "SESSION_INBOUND_COALESCE_WINDOW_MS",
        "SESSION_BUSY_ACK_WITHIN_MS",
        "SESSION_MAX_ACTIVE_WRITE_EXECUTIONS",
        "SESSION_BLOCK_NEW_WRITE_ON_UNKNOWN",
        "READ_CLARIFY_SESSION_TTL_SEC",
        "READ_CLARIFY_MAX_TURNS",
    }
)

_KEY_TO_ATTR: dict[str, str] = {
    "STM_L0_MAX_TURNS": "stm_l0_max_turns",
    "STM_IDLE_RESUME_PROMPT_SEC": "stm_idle_resume_prompt_sec",
    "STM_IDLE_DEFAULT_POLICY": "stm_idle_default_policy",
    "STM_CLARIFY_SESSION_TTL_SEC": "stm_clarify_session_ttl_sec",
    "RESUME_CLASSIFIER_MODE": "resume_classifier_mode",
    "RESUME_CLASSIFIER_MIN_CONFIDENCE": "resume_classifier_min_confidence",
    "WARM_EXECUTION_INDEX_TTL_SEC": "warm_execution_index_ttl_sec",
    "STM_SESSION_CLEAR_MODE": "stm_session_clear_mode",
    "STM_HOT_RECYCLE_SESSION_IDLE_SEC": "stm_hot_recycle_session_idle_sec",
    "STM_HOT_RECYCLE_EXECUTION_AFTER_TERMINAL_SEC": "stm_hot_recycle_execution_after_terminal_sec",
    "SESSION_INBOUND_QUEUE_POLICY": "session_inbound_queue_policy",
    "SESSION_INBOUND_QUEUE_MAX_DEPTH": "session_inbound_queue_max_depth",
    "SESSION_INBOUND_COALESCE_WINDOW_MS": "session_inbound_coalesce_window_ms",
    "SESSION_BUSY_ACK_WITHIN_MS": "session_busy_ack_within_ms",
    "SESSION_MAX_ACTIVE_WRITE_EXECUTIONS": "session_max_active_write_executions",
    "SESSION_BLOCK_NEW_WRITE_ON_UNKNOWN": "session_block_new_write_on_unknown",
    "READ_CLARIFY_SESSION_TTL_SEC": "read_clarify_session_ttl_sec",
    "READ_CLARIFY_MAX_TURNS": "read_clarify_max_turns",
}

_bundle_values: dict[str, Any] = {}


def reset_memory_runtime_bundle_for_tests() -> None:
    _bundle_values.clear()


def set_memory_runtime_bundle_values(values: dict[str, Any] | None) -> None:
    """Replace in-process bundle overrides (from Admin PATCH or tests)."""
    global _bundle_values
    if not values:
        _bundle_values = {}
        return
    normalized: dict[str, Any] = {}
    for key, raw in values.items():
        k = str(key).strip()
        if k not in MEMORY_RUNTIME_CONFIG_KEYS:
            continue
        normalized[k] = _coerce_key(k, raw)
    _bundle_values = normalized


def get_memory_runtime_bundle_values() -> dict[str, Any]:
    return dict(_bundle_values)


def defaults_from_settings(settings: Settings | None = None) -> dict[str, Any]:
    s = settings or get_settings()
    out: dict[str, Any] = {}
    for key, attr in _KEY_TO_ATTR.items():
        out[key] = getattr(s, attr)
    return out


def merged_bundle_view(settings: Settings | None = None) -> dict[str, Any]:
    base = defaults_from_settings(settings)
    base.update(_bundle_values)
    return base


def _coerce_key(key: str, raw: Any) -> Any:
    attr = _KEY_TO_ATTR[key]
    if attr == "session_block_new_write_on_unknown":
        if isinstance(raw, bool):
            return raw
        return str(raw).strip().lower() in ("1", "true", "yes", "on")
    if attr == "resume_classifier_min_confidence":
        return float(raw)
    if key in (
        "STM_IDLE_DEFAULT_POLICY",
        "RESUME_CLASSIFIER_MODE",
        "STM_SESSION_CLEAR_MODE",
        "SESSION_INBOUND_QUEUE_POLICY",
    ):
        return str(raw).strip()
    return int(raw)


def validate_bundle_patch_values(values: dict[str, Any]) -> dict[str, Any]:
    from chainup_agent.core.errors import AppError

    unknown = [k for k in values if str(k).strip() not in MEMORY_RUNTIME_CONFIG_KEYS]
    if unknown:
        raise AppError(
            code="VALIDATION_ERROR",
            message="GlobalConfigBundle 含未知 configKey",
            status_code=422,
            details={"unknownKeys": unknown[:20]},
        )
    out: dict[str, Any] = {}
    for key, raw in values.items():
        k = str(key).strip()
        try:
            v = _coerce_key(k, raw)
        except (TypeError, ValueError) as exc:
            raise AppError(
                code="VALIDATION_ERROR",
                message=f"configKey {k} 类型无效",
                status_code=422,
                details={"configKey": k},
            ) from exc
        _validate_bounds(k, v)
        out[k] = v
    return out


def _validate_bounds(key: str, value: Any) -> None:
    from chainup_agent.core.errors import AppError

    if key == "STM_L0_MAX_TURNS" and not (2 <= int(value) <= 50):
        raise AppError(
            code="VALIDATION_ERROR",
            message="STM_L0_MAX_TURNS 须在 2～50",
            status_code=422,
        )
    if key == "RESUME_CLASSIFIER_MIN_CONFIDENCE" and not (0.0 <= float(value) <= 1.0):
        raise AppError(
            code="VALIDATION_ERROR",
            message="RESUME_CLASSIFIER_MIN_CONFIDENCE 须在 0～1",
            status_code=422,
        )
    if key == "STM_IDLE_DEFAULT_POLICY" and value not in (
        "stale_prior_write",
        "prompt_resume_or_new",
    ):
        raise AppError(
            code="VALIDATION_ERROR",
            message="STM_IDLE_DEFAULT_POLICY 枚举无效",
            status_code=422,
        )
    if key == "RESUME_CLASSIFIER_MODE" and value not in ("rules_only", "rules_then_llm"):
        raise AppError(
            code="VALIDATION_ERROR",
            message="RESUME_CLASSIFIER_MODE 枚举无效",
            status_code=422,
        )
    if key == "SESSION_INBOUND_QUEUE_POLICY" and value not in (
        "serial_per_session",
        "coalesce_latest",
        "reject_while_busy",
    ):
        raise AppError(
            code="VALIDATION_ERROR",
            message="SESSION_INBOUND_QUEUE_POLICY 枚举无效",
            status_code=422,
        )


def overlay_settings(base: Settings | None = None) -> Settings:
    """Env Settings merged with Admin bundle overrides (hot, no process restart)."""
    s = base if base is not None else get_settings()
    if not _bundle_values:
        return s
    patch: dict[str, Any] = {}
    for key, val in _bundle_values.items():
        attr = _KEY_TO_ATTR.get(key)
        if attr:
            patch[attr] = val
    if not patch:
        return s
    return s.model_copy(update=patch)


def build_memory_runtime_config_snapshot(settings: Settings) -> dict[str, Any]:
    """OpenAPI MemoryRuntimeConfigSnapshot camelCase for Execution step 2."""
    return {
        "stmL0MaxTurns": settings.stm_l0_max_turns,
        "stmIdleResumePromptSec": settings.stm_idle_resume_prompt_sec,
        "stmIdleDefaultPolicy": settings.stm_idle_default_policy,
        "stmClarifySessionTtlSec": settings.stm_clarify_session_ttl_sec,
        "resumeClassifierMode": settings.resume_classifier_mode,
        "resumeClassifierMinConfidence": settings.resume_classifier_min_confidence,
        "warmExecutionIndexTtlSec": settings.warm_execution_index_ttl_sec,
        "stmSessionClearMode": settings.stm_session_clear_mode,
        "stmHotRecycleSessionIdleSec": settings.stm_hot_recycle_session_idle_sec,
        "stmHotRecycleExecutionAfterTerminalSec": settings.stm_hot_recycle_execution_after_terminal_sec,
    }


def get_effective_settings(base: Settings | None = None) -> Settings:
    return overlay_settings(base)
