"""Governance ``pp-*`` catalog + DB resolution."""

from __future__ import annotations

import pytest

from chainup_agent.application.prompt_governance_resolve import (
    get_published_governance_pack_for_scenario,
)
from chainup_agent.application.resolved_prompt_binding import build_resolved_prompt_binding
from chainup_agent.data.prompt_governance_catalog import (
    all_governance_pack_seeds,
    governance_pack_id_for_scenario,
)
from chainup_agent.infrastructure.persistence.base import get_session_factory
from tests.test_api import _init_schema_sqlite


@pytest.mark.asyncio
async def test_governance_catalog_has_16_packs() -> None:
    seeds = all_governance_pack_seeds()
    ids = {s.prompt_pack_id for s in seeds}
    assert len(ids) == 16
    assert "pp-system-core" in ids
    assert "pp-analysis-core" in ids
    assert "pp-trading-spot-limit" in ids


@pytest.mark.asyncio
async def test_scenario_maps_to_governance_pack_id() -> None:
    assert governance_pack_id_for_scenario("trade.spot.limit_order") == "pp-trading-spot-limit"
    assert governance_pack_id_for_scenario("read.market.ticker") == "pp-analysis-core"
    assert governance_pack_id_for_scenario("chat.faq") is None


@pytest.mark.asyncio
async def test_db_seed_resolves_governance_packs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from chainup_agent.application.prompt_governance_db_seed import seed_governance_prompt_packs

    await _init_schema_sqlite(monkeypatch, tmp_path)
    factory = get_session_factory()
    async with factory() as session:
        await seed_governance_prompt_packs(session)
        await session.commit()

    factory = get_session_factory()
    async with factory() as session:
        row = await get_published_governance_pack_for_scenario(
            session, scenario_id="trade.spot.limit_order"
        )
        assert row is not None
        assert row.prompt_pack_id == "pp-trading-spot-limit"
        bind = await build_resolved_prompt_binding(session, scenario_id="trade.spot.limit_order")
        assert bind is not None
        assert bind["systemPromptPackId"] == "pp-system-core"
        assert bind["safetyPromptPackId"] == "pp-safety-global"
        assert bind["runtimeClarifyPromptPackId"] == "pp-runtime-clarify"
        assert bind["tradingPromptPackId"] == "pp-trading-spot-limit"

        read_row = await get_published_governance_pack_for_scenario(
            session, scenario_id="read.market.ticker"
        )
        assert read_row is not None
        assert read_row.prompt_pack_id == "pp-analysis-core"
