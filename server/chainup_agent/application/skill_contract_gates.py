"""Write-path slot gates — Python port of product-doc skillContract/gates.ts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SlotBag = dict[str, Any]


@dataclass(frozen=True)
class GateResult:
    ok: bool
    missing: tuple[str, ...]
    reason: str | None = None


def _has(value: Any) -> bool:
    return value is not None and value != ""


def _has_qty_or_quote(slots: SlotBag) -> bool:
    return _has(slots.get("quantity")) or _has(slots.get("quoteQty"))


def can_proceed_to_type_a(skill_id: str, slots: SlotBag) -> GateResult:
    """Whether Type A confirmation may proceed (step 3 gate)."""
    missing: list[str] = []

    if skill_id == "skill.spot.limit_order":
        if not _has(slots.get("symbol")):
            missing.append("symbol")
        if not _has(slots.get("side")):
            missing.append("side")
        if not _has(slots.get("price")):
            missing.append("price")
        if not _has_qty_or_quote(slots):
            missing.append("quantity|quoteQty")
    elif skill_id == "skill.spot.flash_convert":
        if not _has(slots.get("symbol")):
            missing.append("symbol")
        if not _has(slots.get("side")):
            missing.append("side")
        if not _has_qty_or_quote(slots):
            missing.append("quantity|quoteQty")
        if _has(slots.get("price")):
            return GateResult(
                ok=False,
                missing=("price",),
                reason="flash_convert_must_not_carry_limit_price",
            )
    elif skill_id == "skill.spot.amend_limit_order":
        if not _has(slots.get("originalOrderId")) and not _has(
            slots.get("originalClientOrderId")
        ):
            missing.append("originalOrderId|originalClientOrderId")
        if not _has(slots.get("symbol")):
            missing.append("symbol")
        if not _has(slots.get("side")):
            missing.append("side")
        if not _has(slots.get("price")):
            missing.append("price")
        if not _has(slots.get("quantity")):
            missing.append("quantity")
    elif skill_id == "skill.futures.limit_order":
        if not _has(slots.get("symbol")):
            missing.append("symbol")
        if not _has(slots.get("positionSide")):
            missing.append("positionSide")
        if not _has(slots.get("price")):
            missing.append("price")
        if not _has(slots.get("quantity")):
            missing.append("quantity")
    elif skill_id == "skill.margin.cross_market_order":
        if not _has(slots.get("symbol")):
            missing.append("symbol")
        if not _has(slots.get("side")):
            missing.append("side")
        if not _has_qty_or_quote(slots):
            missing.append("quantity|quoteQty")
        if _has(slots.get("price")):
            return GateResult(
                ok=False,
                missing=("price",),
                reason="cross_market_must_not_carry_limit_price",
            )
    else:
        return GateResult(ok=True, missing=())

    return GateResult(ok=len(missing) == 0, missing=tuple(missing))


def is_valid_amend_write_sequence(actions: list[str] | tuple[str, ...]) -> bool:
    """Logical amend: cancel must precede order."""
    try:
        cancel_idx = list(actions).index("cancel")
        order_idx = list(actions).index("order")
    except ValueError:
        return False
    return cancel_idx < order_idx


def margin_cross_write_allowed(confirm_count: int) -> bool:
    """Full cross margin: two user confirmations required before write."""
    return confirm_count >= 2
