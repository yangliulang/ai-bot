"""Prompt pack publish — skillSpecRef must resolve to PUBLISHED spec (SC-PM-21)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.skill_operation_spec_ref import (
    is_write_scenario,
    parse_skill_spec_ref_with_pointer_fallback,
    resolve_skill_id_for_scenario,
    skill_spec_ref_from_variable_schema,
)
from chainup_agent.application.skill_operation_spec_store import get_published_version_row
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.models.admin_prompt_pack import AdminPromptPack
from chainup_agent.infrastructure.persistence.models.skill_operation_spec import (
    SkillOperationSpecPointer,
)


async def assert_skill_spec_ref_publishable(session: AsyncSession, row: AdminPromptPack) -> None:
    ptype = (row.prompt_pack_type or "").upper()
    if ptype not in ("TRADING", "ANALYSIS"):
        return

    schema = None
    if row.variable_schema_json:
        import json

        try:
            obj = json.loads(row.variable_schema_json)
            schema = obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            schema = None

    ref_raw = skill_spec_ref_from_variable_schema(schema)
    scenario = (row.scenario_id or "").strip()

    needs_ref = ptype == "TRADING" or (ptype == "ANALYSIS" and bool(ref_raw))
    if not needs_ref:
        return

    if ptype == "TRADING" and not ref_raw and scenario and not is_write_scenario(scenario):
        return

    pointer_ver: str | None = None
    skill_for_scenario = resolve_skill_id_for_scenario(scenario) if scenario else None
    if skill_for_scenario:
        ptr = await session.get(SkillOperationSpecPointer, skill_for_scenario)
        if ptr:
            pointer_ver = ptr.skill_spec_version

    parsed = parse_skill_spec_ref_with_pointer_fallback(
        skill_spec_ref=ref_raw,
        scenario_id=scenario or None,
        pointer_version=pointer_ver,
    )
    if parsed is None:
        raise AppError(
            "PROMPT_SKILL_REF_INVALID",
            "交易类提示词须绑定已发布的技能规范（skillSpecRef 或写路径 scenario）",
            status_code=422,
        )

    published = await get_published_version_row(
        session, parsed.skill_id, parsed.skill_spec_version
    )
    if published is None:
        raise AppError(
            "PROMPT_SKILL_REF_INVALID",
            f"技能规范未在 Runtime 生效：{parsed.skill_id}@{parsed.skill_spec_version}",
            status_code=422,
            details={
                "skillId": parsed.skill_id,
                "skillSpecVersion": parsed.skill_spec_version,
            },
        )
