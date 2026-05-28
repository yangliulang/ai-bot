"""Runtime read path for PUBLISHED skill operation specs (FR-T11 · bundled snapshot)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from chainup_agent.core.errors import AppError

_BUNDLE_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "skill_specs" / "runtime-bundle.json"
)

_SECTION_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class SkillOperationSpecSection:
    id: str
    title: str
    body_markdown: str


@dataclass(frozen=True)
class EffectiveSkillOperationSpec:
    skill_id: str
    skill_spec_version: str
    spec_digest: str
    lifecycle: str
    scenario_id: str | None
    sections: tuple[SkillOperationSpecSection, ...]


@lru_cache(maxsize=1)
def _load_bundle_items() -> dict[str, dict[str, Any]]:
    if not _BUNDLE_PATH.is_file():
        return {}
    raw = json.loads(_BUNDLE_PATH.read_text(encoding="utf-8"))
    items = raw.get("items") if isinstance(raw, dict) else None
    if not isinstance(items, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for it in items:
        if not isinstance(it, dict):
            continue
        sid = str(it.get("skillId") or "").strip()
        if sid:
            out[sid] = it
    return out


def _sections_from_markdown(body: str) -> tuple[SkillOperationSpecSection, ...]:
    text = body.strip()
    if not text:
        return ()
    parts = _SECTION_RE.split(text)
    if len(parts) < 3:
        return (
            SkillOperationSpecSection(
                id="body",
                title="body",
                body_markdown=text[:4000],
            ),
        )
    sections: list[SkillOperationSpecSection] = []
    # parts[0] is preamble before first ##; then title, body, title, body, ...
    idx = 1
    while idx + 1 < len(parts):
        title = parts[idx].strip()
        chunk = parts[idx + 1].strip()
        sec_id = re.sub(r"[^\w]+", "_", title.lower())[:48] or "section"
        sections.append(
            SkillOperationSpecSection(
                id=sec_id,
                title=title,
                body_markdown=chunk[:8000],
            )
        )
        idx += 2
    return tuple(sections)


_SCENARIO_SKILL_ID: dict[str, str] = {
    "trade.spot.limit_order": "skill.spot.limit_order",
    "trade.spot.amend_limit_order": "skill.spot.amend_limit_order",
    "trade.spot.flash_convert": "skill.spot.flash_convert",
    "trade.futures.market_order": "skill.futures.market_order",
    "trade.futures.limit_order": "skill.futures.limit_order",
    "trade.futures.amend_limit_order": "skill.futures.amend_limit_order",
    "trade.futures.take_profit_stop": "skill.futures.take_profit_stop",
    "automation.condition_order": "skill.futures.take_profit_stop",
    "automation.condition_order_cancel": "skill.futures.take_profit_stop",
    "margin.cross.market_order": "skill.margin.cross_market_order",
    "margin.cross.limit_order": "skill.margin.cross_limit_order",
    "wealth.subscribe": "skill.wealth.subscribe",
    "wealth.redeem": "skill.wealth.redeem",
}


def scenario_to_skill_id(scenario_id: str) -> str | None:
    return _SCENARIO_SKILL_ID.get(scenario_id.strip())


def get_effective_skill_operation_spec(
    *,
    skill_id: str,
    scenario_id: str | None = None,
) -> EffectiveSkillOperationSpec:
    kid = skill_id.strip()
    if not kid:
        raise AppError(
            "VALIDATION_ERROR",
            "skillId 不能为空",
            status_code=422,
        )
    items = _load_bundle_items()
    row = items.get(kid)
    if row is None:
        raise AppError(
            "PROMPT_SKILL_REF_INVALID",
            f"未找到已发布的技能操作规范：{kid}",
            status_code=404,
        )
    lifecycle = str(row.get("lifecycle") or "").strip().upper()
    if lifecycle != "PUBLISHED":
        raise AppError(
            "PROMPT_SKILL_REF_INVALID",
            "技能操作规范未发布或版本无效",
            status_code=403,
        )
    if scenario_id:
        mapped = scenario_to_skill_id(scenario_id)
        if mapped and mapped != kid:
            raise AppError(
                "PROMPT_SKILL_REF_INVALID",
                f"scenarioId 与 skillId 不匹配（期望 {mapped}）",
                status_code=403,
            )
    body = str(row.get("bodyMarkdown") or "")
    return EffectiveSkillOperationSpec(
        skill_id=kid,
        skill_spec_version=str(row.get("skillSpecVersion") or "").strip() or "0.0.0",
        spec_digest=str(row.get("specDigest") or "").strip(),
        lifecycle="PUBLISHED",
        scenario_id=scenario_id.strip() if scenario_id and scenario_id.strip() else None,
        sections=_sections_from_markdown(body),
    )
