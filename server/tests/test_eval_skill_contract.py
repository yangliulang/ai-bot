"""Eval runner tests — 2026-05-28--skill-contract-eval-staging."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from chainup_agent.application.eval_skill_contract import (
    EVAL_SKILL_P0_FIXTURES,
    EVAL_SKILL_P0_SET_IDS,
    EVAL_VERSION,
    SkillEvalFixture,
    assert_eval_skill_amend_cancel_before_order,
    assert_eval_skill_flash_no_limit_price,
    assert_eval_skill_margin_double_confirm,
    assert_eval_skill_missing_qty_no_confirm,
    run_eval_skill_p0_fixture,
)
from chainup_agent.application.skill_contract_gates import (
    is_valid_amend_write_sequence,
    margin_cross_write_allowed,
)
from tests.skill_spec_helpers import seed_skill_operation_specs_from_bundle


@pytest.fixture(autouse=True)
async def _seed_skill_specs_db() -> None:
    await seed_skill_operation_specs_from_bundle()


def test_eval_skill_p0_constants() -> None:
    assert EVAL_VERSION == "0.1.0"
    assert EVAL_SKILL_P0_SET_IDS == (
        "eval.skill.missing_qty_no_confirm",
        "eval.skill.flash_no_limit_price",
        "eval.skill.margin_double_confirm",
        "eval.skill.amend_cancel_before_order",
    )
    assert len(EVAL_SKILL_P0_FIXTURES) == 4
    assert {f.eval_set_id for f in EVAL_SKILL_P0_FIXTURES} == set(EVAL_SKILL_P0_SET_IDS)


def test_missing_qty_no_confirm() -> None:
    slots = {"symbol": "BTCUSDT", "side": "BUY", "price": "95000"}
    assert_eval_skill_missing_qty_no_confirm("skill.spot.limit_order", slots)


def test_flash_no_limit_price() -> None:
    slots = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": "0.01",
        "price": "95000",
    }
    assert_eval_skill_flash_no_limit_price("skill.spot.flash_convert", slots)


def test_margin_double_confirm() -> None:
    assert assert_eval_skill_margin_double_confirm(1) is False
    assert assert_eval_skill_margin_double_confirm(2) is True


def test_amend_cancel_before_order_valid() -> None:
    assert_eval_skill_amend_cancel_before_order(["cancel", "order"])


def test_amend_cancel_before_order_invalid() -> None:
    with pytest.raises(AssertionError, match="cancel must precede order"):
        assert_eval_skill_amend_cancel_before_order(["order", "cancel"])


@pytest.mark.parametrize("fixture", EVAL_SKILL_P0_FIXTURES, ids=lambda f: f.eval_set_id)
def test_run_eval_skill_p0_fixture(fixture: SkillEvalFixture) -> None:
    run_eval_skill_p0_fixture(fixture)


def test_margin_cross_write_allowed_zero_p1() -> None:
    assert margin_cross_write_allowed(0) is False


def test_amend_sequence_missing_cancel_p1() -> None:
    assert not is_valid_amend_write_sequence(["order"])


@pytest.mark.asyncio
async def test_runtime_effective_given_skill_spot_limit_order(
    http_client: AsyncClient,
) -> None:
    r = await http_client.get(
        "/api/v1/runtime/skill-operation-spec/effective",
        params={"skillId": "skill.spot.limit_order"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["skillId"] == "skill.spot.limit_order"
    assert body["lifecycle"] == "PUBLISHED"
    assert body["skillSpecVersion"]
    assert body["specDigest"]
    sections = body.get("sections") or []
    assert sections, "effective spec must expose section bodyMarkdown"
    combined = "".join(s.get("bodyMarkdown") or "" for s in sections)
    assert len(combined) > 0


@pytest.mark.asyncio
async def test_agent_scenario_p0_fixture_ids(http_client: AsyncClient) -> None:
    for fixture in EVAL_SKILL_P0_FIXTURES:
        r = await http_client.get(
            f"/api/v1/agent/scenarios/{fixture.scenario_id}",
        )
        assert r.status_code == 200, fixture.scenario_id
        assert r.json()["scenarioId"] == fixture.scenario_id
