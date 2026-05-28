"""Read-only scenario ↔ skill scope for execution governance panels (SC-PM-21 / FR-MC801)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_prompt_effective import get_published_pack_for_scenario
from chainup_agent.application.resolved_prompt_binding import (
    build_resolved_prompt_binding,
    primary_prompt_pack_version_for_binding,
)
from chainup_agent.application.skill_operation_spec_ref import (
    is_write_scenario,
    parse_skill_spec_ref_for_publish,
    resolve_skill_id_for_scenario,
    skill_spec_ref_from_variable_schema,
)
from chainup_agent.application.skill_operation_spec_store import get_effective_from_db
from chainup_agent.core.errors import AppError


def _variable_schema_from_row(row: Any) -> dict[str, Any] | None:
    raw = row.variable_schema_json
    if raw is None or not str(raw).strip():
        return None
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def _scenario_category(scenario_id: str) -> str:
    sid = scenario_id.strip()
    if sid.startswith("read.") or sid.startswith("research."):
        return "read"
    if sid.startswith("wealth."):
        return "wealth"
    if sid.startswith("monitoring.") or sid.startswith("automation."):
        return "monitoring"
    if is_write_scenario(sid):
        return "write"
    return "read"


async def resolve_scenario_skill_scope_view(
    session: AsyncSession,
    *,
    scenario_id: str,
) -> dict[str, Any]:
    sid = scenario_id.strip()
    category = _scenario_category(sid)
    binding = await build_resolved_prompt_binding(session, scenario_id=sid)
    pack_ver = await primary_prompt_pack_version_for_binding(binding)

    row_pack = await get_published_pack_for_scenario(session, scenario_id=sid)
    pack_id = row_pack.prompt_pack_id if row_pack else (binding or {}).get("tradingPromptPackId")
    if pack_id is not None:
        pack_id = str(pack_id).strip() or None

    schema = _variable_schema_from_row(row_pack) if row_pack else None
    skill_ref_raw = skill_spec_ref_from_variable_schema(schema)
    parsed_ref = parse_skill_spec_ref_for_publish(skill_spec_ref=skill_ref_raw, scenario_id=sid)
    prompt_skill_scope_ref: str | None = None
    if parsed_ref:
        prompt_skill_scope_ref = f"{parsed_ref.skill_id}@{parsed_ref.skill_spec_version}"
    elif skill_ref_raw:
        prompt_skill_scope_ref = skill_ref_raw.strip()

    primary_skill_id = resolve_skill_id_for_scenario(sid)
    skill_spec_version: str | None = None
    contract_complete: bool | None = None
    spec_digest: str | None = None

    if primary_skill_id:
        try:
            spec = await get_effective_from_db(session, skill_id=primary_skill_id, scenario_id=sid)
            skill_spec_version = spec.skill_spec_version
            spec_digest = spec.spec_digest
            contract_complete = bool(spec.sections)
        except AppError:
            skill_spec_version = None

    if category == "read" or (not primary_skill_id and category not in ("write", "wealth")):
        mode = "read_only"
        narrative = (
            "读侧场景：Runtime 走 B/C 类 Tool 链，无单一 A 类 write Skill；"
            "写路径须切换至交易类 scenarioId。"
        )
    elif not primary_skill_id:
        mode = "unmapped_write"
        narrative = (
            "写路径场景键尚未在 SCENARIO_PRIMARY_SKILL 登记主 Skill；"
            "须在 routing-engine 与 skill-specs 同窗补齐后再开放对话写操作。"
        )
    else:
        mode = "write_skill"
        narrative = (
            "写路径：Runtime 在类型 A 前 read_skill_operation_spec；"
            "Skill 正文在 skill-specs，Prompt 承载场景叙事与发布门禁指针。"
            if is_write_scenario(sid)
            else "—"
        )

    skills: list[dict[str, Any]] = []
    if primary_skill_id and mode == "write_skill":
        skills.append(
            {
                "skillId": primary_skill_id,
                "skillSpecVersion": skill_spec_version,
                "specDigest": spec_digest,
                "contractComplete": contract_complete,
                "role": "primary_write",
            }
        )

    return {
        "scenarioId": sid,
        "category": category,
        "mode": mode,
        "skills": skills,
        "promptStrategyPackId": pack_id,
        "promptStrategyVersion": pack_ver,
        "promptSkillScopeRef": prompt_skill_scope_ref,
        "narrative": narrative,
    }
