"""Telegram channel ``runtimeParams`` store (FR-TG-ADMIN-02) — singleton JSON document."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.admin_ai_settings import _check_version
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.models.admin_ai_settings import AdminAiDocument

DOC_TELEGRAM_CHANNEL_RUNTIME = "telegram_channel_runtime"

# keys.md §4.2 + admin ``telegram-runtime-params.ts`` §3 capability keys
ALLOWED_RUNTIME_KEYS: frozenset[str] = frozenset(
    {
        "TELEGRAM_DEFAULT_LOCALE",
        "TELEGRAM_HELP_H5_URL_TEMPLATE",
        "TELEGRAM_LINK_PREVIEW_DEFAULT",
        "TELEGRAM_TYPING_INDICATOR_MODE",
        "TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT",
        "TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_CN",
        "TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_TW",
        "TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_EN",
        "TELEGRAM_CHANNEL_TRADE_OK",
        "TELEGRAM_CHANNEL_AUTO_EXEC_OK",
        "TELEGRAM_CHANNEL_VOICE_OK",
        "TELEGRAM_CHANNEL_FILE_OK",
    }
)

MAX_WELCOME_TEXT_LEN = 4096


async def _ensure_row(session: AsyncSession) -> AdminAiDocument:
    row = await session.get(AdminAiDocument, DOC_TELEGRAM_CHANNEL_RUNTIME)
    if row is None:
        row = AdminAiDocument(
            doc_key=DOC_TELEGRAM_CHANNEL_RUNTIME,
            payload_json=json.dumps({}, ensure_ascii=False),
            row_version=1,
        )
        session.add(row)
        await session.flush()
    return row


def _coerce_param_value(key: str, value: Any) -> Any:
    if key.endswith("_OK") or key == "TELEGRAM_LINK_PREVIEW_DEFAULT":
        if isinstance(value, bool):
            return value
        if value in ("true", "True", "1", 1):
            return True
        if value in ("false", "False", "0", 0):
            return False
        raise AppError(
            code="ADMIN_TELEGRAM_RUNTIME_PARAM_INVALID",
            message=f"{key} 须为布尔值",
            status_code=400,
            details={"key": key},
        )
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    text = value.strip() if key != "TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT" else value
    if key.startswith("TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT") and len(text) > MAX_WELCOME_TEXT_LEN:
        raise AppError(
            code="ADMIN_TELEGRAM_WELCOME_TEXT_TOO_LONG",
            message=f"{key} 超过 Telegram 单条消息上限（{MAX_WELCOME_TEXT_LEN} 字符）",
            status_code=400,
            details={"key": key, "maxLength": MAX_WELCOME_TEXT_LEN},
        )
    return text


def validate_runtime_params_patch(patch: dict[str, Any]) -> dict[str, Any]:
    if not patch:
        raise AppError(
            code="ADMIN_TELEGRAM_RUNTIME_PARAMS_REQUIRED",
            message="runtimeParams 不能为空",
            status_code=400,
        )
    out: dict[str, Any] = {}
    for key, value in patch.items():
        if not isinstance(key, str) or not key.startswith("TELEGRAM_"):
            raise AppError(
                code="ADMIN_TELEGRAM_RUNTIME_PARAM_INVALID",
                message="runtimeParams 键须以 TELEGRAM_ 开头",
                status_code=400,
                details={"key": key},
            )
        if key not in ALLOWED_RUNTIME_KEYS:
            raise AppError(
                code="ADMIN_TELEGRAM_RUNTIME_PARAM_UNKNOWN",
                message=f"未登记的 runtimeParams 键：{key}",
                status_code=400,
                details={"key": key},
            )
        out[key] = _coerce_param_value(key, value)
    return out


async def load_runtime_params(session: AsyncSession) -> tuple[dict[str, Any], int]:
    row = await _ensure_row(session)
    data = json.loads(row.payload_json)
    if not isinstance(data, dict):
        return {}, int(row.row_version)
    return data, int(row.row_version)


async def merge_runtime_params(
    session: AsyncSession,
    patch: dict[str, Any],
    if_match: str | None,
) -> tuple[dict[str, Any], int]:
    normalized = validate_runtime_params_patch(patch)
    row = await _ensure_row(session)
    _check_version(int(row.row_version), if_match)
    cur = json.loads(row.payload_json)
    if not isinstance(cur, dict):
        cur = {}
    cur.update(normalized)
    row.payload_json = json.dumps(cur, ensure_ascii=False)
    row.row_version = int(row.row_version) + 1
    await session.flush()
    return cur, int(row.row_version)
