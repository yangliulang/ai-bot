"""Parse skillSpecRef for Prompt Publish gate (SC-PM-21)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

_SKILL_ID_RE = re.compile(r"^skill\.[a-z0-9_.]+$")

SCENARIO_PRIMARY_SKILL: dict[str, str] = {
    "trade.spot.flash_convert": "skill.spot.flash_convert",
    "trade.spot.limit_order": "skill.spot.limit_order",
    "trade.spot.amend_limit_order": "skill.spot.amend_limit_order",
    "trade.futures.market_order": "skill.futures.market_order",
    "trade.futures.limit_order": "skill.futures.limit_order",
    "trade.futures.amend_limit_order": "skill.futures.amend_limit_order",
    "trade.futures.take_profit_stop": "skill.futures.take_profit_stop",
    "futures.condition.order_create": "skill.futures.take_profit_stop",
    "margin.cross.market_order": "skill.margin.cross_market_order",
    "margin.cross.limit_order": "skill.margin.cross_limit_order",
    "wealth.subscribe": "skill.wealth.subscribe",
    "wealth.redeem": "skill.wealth.redeem",
}


@dataclass(frozen=True)
class ParsedSkillSpecRef:
    skill_id: str
    skill_spec_version: str


def resolve_skill_id_for_scenario(scenario_id: str) -> str | None:
    return SCENARIO_PRIMARY_SKILL.get(scenario_id.strip())


def is_write_scenario(scenario_id: str) -> bool:
    return resolve_skill_id_for_scenario(scenario_id) is not None


def _parse_explicit_ref(raw: str) -> ParsedSkillSpecRef | None:
    t = raw.strip()
    if not t:
        return None
    try:
        j = json.loads(t)
        if isinstance(j, dict):
            sid = str(j.get("skillId") or "").strip()
            ver = str(j.get("skillSpecVersion") or "").strip()
            if sid and ver and _SKILL_ID_RE.match(sid):
                return ParsedSkillSpecRef(skill_id=sid, skill_spec_version=ver)
    except json.JSONDecodeError:
        pass
    at = re.match(r"^(skill\.[a-z0-9_.]+)@([^\s]+)$", t)
    if at:
        return ParsedSkillSpecRef(skill_id=at.group(1), skill_spec_version=at.group(2))
    colon = re.match(r"^(skill\.[a-z0-9_.]+):([^\s]+)$", t)
    if colon:
        return ParsedSkillSpecRef(skill_id=colon.group(1), skill_spec_version=colon.group(2))
    return None


def skill_spec_ref_from_variable_schema(variable_schema: dict[str, Any] | None) -> str | None:
    if not variable_schema:
        return None
    raw = variable_schema.get("skillSpecRef")
    if raw is None:
        return None
    s = str(raw).strip()
    return s or None


def parse_skill_spec_ref_for_publish(
    *,
    skill_spec_ref: str | None,
    scenario_id: str | None,
) -> ParsedSkillSpecRef | None:
    explicit = _parse_explicit_ref(skill_spec_ref or "")
    if explicit:
        return explicit
    scenario = (scenario_id or "").strip()
    if scenario:
        skill_id = resolve_skill_id_for_scenario(scenario)
        if skill_id:
            return None
    return None


def parse_skill_spec_ref_with_pointer_fallback(
    *,
    skill_spec_ref: str | None,
    scenario_id: str | None,
    pointer_version: str | None,
) -> ParsedSkillSpecRef | None:
    """Explicit ref wins; else scenario write-path may use effective pointer version."""
    explicit = _parse_explicit_ref(skill_spec_ref or "")
    if explicit:
        return explicit
    scenario = (scenario_id or "").strip()
    skill_id = resolve_skill_id_for_scenario(scenario) if scenario else None
    if skill_id and pointer_version:
        return ParsedSkillSpecRef(skill_id=skill_id, skill_spec_version=pointer_version)
    return None
