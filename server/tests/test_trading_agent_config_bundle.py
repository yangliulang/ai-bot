"""GlobalConfigBundle — memory/STM + SESSION PATCH."""

from __future__ import annotations

import pytest

from chainup_agent.application.admin_trading_agent_config import (
    DOC_TRADING_AGENT_CONFIG_BUNDLE,
    patch_trading_agent_config_bundle,
    read_trading_agent_config_bundle,
)
from chainup_agent.application.memory_runtime_settings import (
    get_effective_settings,
    reset_memory_runtime_bundle_for_tests,
)
from chainup_agent.core.config import Settings, reset_settings_cache
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.base import get_session_factory
from chainup_agent.infrastructure.persistence.models.admin_ai_settings import AdminAiDocument


@pytest.fixture(autouse=True)
def _reset_bundle() -> None:
    reset_memory_runtime_bundle_for_tests()
    reset_settings_cache()


@pytest.mark.asyncio
async def test_patch_bundle_applies_hot_settings() -> None:
    factory = get_session_factory()
    async with factory() as session:
        row = AdminAiDocument(
            doc_key=DOC_TRADING_AGENT_CONFIG_BUNDLE,
            payload_json='{"values": {}}',
            row_version=1,
        )
        session.add(row)
        await session.flush()

        data, keys = await patch_trading_agent_config_bundle(
            session,
            values={
                "STM_L0_MAX_TURNS": 12,
                "SESSION_INBOUND_QUEUE_POLICY": "coalesce_latest",
            },
            if_match="1",
            expected_config_version=None,
        )
        assert "STM_L0_MAX_TURNS" in keys
        assert data["configVersion"] == 2
    eff = get_effective_settings(Settings())
    assert eff.stm_l0_max_turns == 12
    assert eff.session_inbound_queue_policy == "coalesce_latest"


@pytest.mark.asyncio
async def test_patch_bundle_version_conflict() -> None:
    factory = get_session_factory()
    async with factory() as session:
        row = AdminAiDocument(
            doc_key=DOC_TRADING_AGENT_CONFIG_BUNDLE,
            payload_json='{"values": {}}',
            row_version=3,
        )
        session.add(row)
        await session.flush()

        with pytest.raises(AppError) as exc:
            await patch_trading_agent_config_bundle(
                session,
                values={"STM_L0_MAX_TURNS": 8},
                if_match="1",
                expected_config_version=None,
            )
        assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_read_bundle_merges_defaults() -> None:
    factory = get_session_factory()
    async with factory() as session:
        view, ver = await read_trading_agent_config_bundle(session)
    assert ver >= 1
    assert view["values"]["STM_L0_MAX_TURNS"] == Settings().stm_l0_max_turns
