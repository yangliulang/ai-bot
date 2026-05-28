"""Admin GlobalConfigBundle — memory/STM + SESSION keys (trading-agent-config flow)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.admin_ai_settings import _check_version, _normalize_if_match
from chainup_agent.application.memory_runtime_settings import (
    defaults_from_settings,
    merged_bundle_view,
    set_memory_runtime_bundle_values,
    validate_bundle_patch_values,
)
from chainup_agent.core.config import get_settings
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.models.admin_ai_settings import AdminAiDocument

DOC_TRADING_AGENT_CONFIG_BUNDLE = "trading_agent_config_bundle"


async def _load_bundle_row(session: AsyncSession) -> AdminAiDocument | None:
    return await session.get(AdminAiDocument, DOC_TRADING_AGENT_CONFIG_BUNDLE)


async def ensure_trading_agent_config_bundle(session: AsyncSession) -> AdminAiDocument:
    row = await _load_bundle_row(session)
    if row is None:
        row = AdminAiDocument(
            doc_key=DOC_TRADING_AGENT_CONFIG_BUNDLE,
            payload_json=json.dumps({"values": {}}, ensure_ascii=False),
            row_version=1,
        )
        session.add(row)
        await session.flush()
    return row


def _parse_stored_values(row: AdminAiDocument) -> dict[str, Any]:
    raw = json.loads(row.payload_json)
    if not isinstance(raw, dict):
        return {}
    values = raw.get("values")
    if not isinstance(values, dict):
        return {}
    return dict(values)


async def read_trading_agent_config_bundle(
    session: AsyncSession,
) -> tuple[dict[str, Any], int]:
    row = await ensure_trading_agent_config_bundle(session)
    stored = _parse_stored_values(row)
    set_memory_runtime_bundle_values(stored)
    base = get_settings()
    return {
        "configVersion": int(row.row_version),
        "values": merged_bundle_view(base),
        "defaults": defaults_from_settings(base),
        "appliedKeys": sorted(stored.keys()),
    }, int(row.row_version)


async def patch_trading_agent_config_bundle(
    session: AsyncSession,
    *,
    values: dict[str, Any],
    if_match: str | None,
    expected_config_version: int | None,
) -> tuple[dict[str, Any], list[str]]:
    row = await ensure_trading_agent_config_bundle(session)
    expect = _normalize_if_match(if_match)
    if expect is None and expected_config_version is not None:
        expect = str(int(expected_config_version))
    _check_version(int(row.row_version), expect)

    validated = validate_bundle_patch_values(values)
    cur = _parse_stored_values(row)
    cur.update(validated)
    row.payload_json = json.dumps({"values": cur}, ensure_ascii=False)
    row.row_version = int(row.row_version) + 1
    await session.flush()
    set_memory_runtime_bundle_values(cur)
    view = merged_bundle_view(get_settings())
    return (
        {
            "configVersion": int(row.row_version),
            "values": view,
            "appliedKeys": sorted(validated.keys()),
        },
        sorted(validated.keys()),
    )
