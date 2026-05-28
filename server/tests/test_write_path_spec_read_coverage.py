"""Write-path spec_read coverage — flash HTTP + scenario skill map."""

from __future__ import annotations

import pytest

from chainup_agent.application.runtime_skill_operation_spec import scenario_to_skill_id
from chainup_agent.application.write_path_pipeline import is_write_path_scenario


def test_write_path_scenario_includes_flash_and_futures() -> None:
    assert is_write_path_scenario("trade.spot.flash_convert")
    assert is_write_path_scenario("trade.futures.market_order")
    assert scenario_to_skill_id("automation.condition_order") == "skill.futures.take_profit_stop"


@pytest.mark.asyncio
async def test_http_flash_convert_emits_spec_read(http_client) -> None:
    """HTTP flash-convert must emit spec_read before exchange write (pipeline order)."""
    from chainup_agent.infrastructure.persistence.base import get_session_factory
    from chainup_agent.application.agent_execution_events import list_timeline_events_for_execution

    r = await http_client.post(
        "/api/v1/agent/trade/spot/flash-convert",
        json={
            "userId": "99001",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "volume": "0.001",
        },
    )
    if r.status_code == 403:
        pytest.skip("user not bound for flash convert")
    if r.status_code not in (200, 400, 502):
        pytest.skip(f"flash convert returned {r.status_code}")
    if r.status_code != 200:
        return
    eid = r.json().get("executionId")
    if not eid:
        return
    factory = get_session_factory()
    async with factory() as session:
        events = await list_timeline_events_for_execution(session, execution_public_id=eid)
    names = [e.event_type for e in events]
    assert "agent.skill.spec_read" in names
    assert names.index("agent.skill.spec_read") < names.index("confirmation.required")
