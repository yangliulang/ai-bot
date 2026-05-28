"""Eval runner for ``eval.skill.*`` P0 bundle (OP-SKILL B · SK-B03)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from chainup_agent.application.skill_contract_gates import (
    GateResult,
    can_proceed_to_type_a,
    is_valid_amend_write_sequence,
    margin_cross_write_allowed,
)

EVAL_VERSION = "0.1.0"

EVAL_SKILL_P0_SET_IDS: tuple[str, ...] = (
    "eval.skill.missing_qty_no_confirm",
    "eval.skill.flash_no_limit_price",
    "eval.skill.margin_double_confirm",
    "eval.skill.amend_cancel_before_order",
)


@dataclass(frozen=True)
class SkillEvalFixture:
    eval_set_id: str
    skill_id: str
    scenario_id: str
    slots: dict[str, Any]
    expect_type_a: bool
    expect_write: bool
    amend_sequence: tuple[str, ...] | None = None
    margin_confirm_count: int | None = None


# Mirrors product-doc/src/admin/src/skillContract/fixtures.ts
EVAL_SKILL_P0_FIXTURES: tuple[SkillEvalFixture, ...] = (
    SkillEvalFixture(
        eval_set_id="eval.skill.missing_qty_no_confirm",
        skill_id="skill.spot.limit_order",
        scenario_id="trade.spot.limit_order",
        slots={"symbol": "BTCUSDT", "side": "BUY", "type": "LIMIT", "price": "95000"},
        expect_type_a=False,
        expect_write=False,
    ),
    SkillEvalFixture(
        eval_set_id="eval.skill.flash_no_limit_price",
        skill_id="skill.spot.flash_convert",
        scenario_id="trade.spot.flash_convert",
        slots={
            "symbol": "BTCUSDT",
            "side": "BUY",
            "quantity": "0.01",
            "price": "95000",
        },
        expect_type_a=False,
        expect_write=False,
    ),
    SkillEvalFixture(
        eval_set_id="eval.skill.margin_double_confirm",
        skill_id="skill.margin.cross_market_order",
        scenario_id="margin.cross.market_order",
        slots={"symbol": "BTC_USDT", "side": "BUY", "quoteQty": "1000"},
        expect_type_a=True,
        expect_write=False,
        margin_confirm_count=1,
    ),
    SkillEvalFixture(
        eval_set_id="eval.skill.amend_cancel_before_order",
        skill_id="skill.spot.amend_limit_order",
        scenario_id="trade.spot.amend_limit_order",
        slots={
            "originalOrderId": "ord-1",
            "symbol": "BTCUSDT",
            "side": "BUY",
            "price": "96000",
            "quantity": "0.01",
        },
        expect_type_a=True,
        expect_write=True,
        amend_sequence=("cancel", "order"),
    ),
)


def _write_allowed_for_fixture(
    fixture: SkillEvalFixture,
    gate: GateResult,
) -> bool:
    if fixture.margin_confirm_count is not None:
        return margin_cross_write_allowed(fixture.margin_confirm_count)
    if fixture.amend_sequence is not None:
        return is_valid_amend_write_sequence(fixture.amend_sequence)
    return gate.ok


def assert_eval_skill_missing_qty_no_confirm(skill_id: str, slots: dict[str, Any]) -> None:
    """eval.skill.missing_qty_no_confirm — missing qty must block Type A and write."""
    gate = can_proceed_to_type_a(skill_id, slots)
    if gate.ok:
        raise AssertionError("missing qty must not allow Type A")
    if _write_allowed_for_fixture(
        SkillEvalFixture(
            eval_set_id="eval.skill.missing_qty_no_confirm",
            skill_id=skill_id,
            scenario_id="trade.spot.limit_order",
            slots=slots,
            expect_type_a=False,
            expect_write=False,
        ),
        gate,
    ):
        raise AssertionError("missing qty must not allow write")


def assert_eval_skill_flash_no_limit_price(skill_id: str, slots: dict[str, Any]) -> None:
    """eval.skill.flash_no_limit_price — flash_convert must reject limit price."""
    gate = can_proceed_to_type_a(skill_id, slots)
    if gate.ok:
        raise AssertionError("flash_convert with price must not allow Type A")
    if gate.reason != "flash_convert_must_not_carry_limit_price":
        raise AssertionError(
            f"expected flash_convert_must_not_carry_limit_price, got {gate.reason!r}"
        )


def assert_eval_skill_margin_double_confirm(confirm_count: int) -> bool:
    """eval.skill.margin_double_confirm — SC-CH-TG-MARGIN-01 direction."""
    return margin_cross_write_allowed(confirm_count)


def assert_eval_skill_amend_cancel_before_order(actions: list[str] | tuple[str, ...]) -> None:
    """eval.skill.amend_cancel_before_order — cancel must precede order."""
    if not is_valid_amend_write_sequence(actions):
        raise AssertionError(
            "amend write sequence violated: cancel must precede order"
        )


def run_eval_skill_p0_fixture(fixture: SkillEvalFixture) -> None:
    """Run one P0 fixture; raises if gates disagree with expectTypeA / expectWrite."""
    gate = can_proceed_to_type_a(fixture.skill_id, fixture.slots)

    if fixture.eval_set_id == "eval.skill.missing_qty_no_confirm":
        assert_eval_skill_missing_qty_no_confirm(fixture.skill_id, fixture.slots)
        return

    if fixture.eval_set_id == "eval.skill.flash_no_limit_price":
        assert_eval_skill_flash_no_limit_price(fixture.skill_id, fixture.slots)
        return

    if fixture.eval_set_id == "eval.skill.margin_double_confirm":
        if gate.ok != fixture.expect_type_a:
            raise AssertionError(
                f"Type A gate mismatch: expected {fixture.expect_type_a}, got {gate.ok}"
            )
        count = fixture.margin_confirm_count if fixture.margin_confirm_count is not None else 0
        write_ok = assert_eval_skill_margin_double_confirm(count)
        if write_ok != fixture.expect_write:
            raise AssertionError(
                f"write gate mismatch: expected {fixture.expect_write}, got {write_ok}"
            )
        return

    if fixture.eval_set_id == "eval.skill.amend_cancel_before_order":
        if gate.ok != fixture.expect_type_a:
            raise AssertionError(
                f"Type A gate mismatch: expected {fixture.expect_type_a}, got {gate.ok}"
            )
        seq = fixture.amend_sequence or ()
        if fixture.expect_write:
            assert_eval_skill_amend_cancel_before_order(seq)
        elif is_valid_amend_write_sequence(seq):
            raise AssertionError("expected invalid amend sequence for negative write")
        return

    raise AssertionError(f"unknown evalSetId: {fixture.eval_set_id}")
