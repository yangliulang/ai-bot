"""Admin scenario skill scope — execution governance read model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScenarioSkillScopeSkillItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    skill_id: str = Field(alias="skillId")
    skill_spec_version: str | None = Field(default=None, alias="skillSpecVersion")
    spec_digest: str | None = Field(default=None, alias="specDigest")
    contract_complete: bool | None = Field(default=None, alias="contractComplete")
    role: str = "primary_write"


class ScenarioSkillScopeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(alias="scenarioId")
    category: str
    mode: str
    skills: list[ScenarioSkillScopeSkillItem] = Field(default_factory=list)
    prompt_strategy_pack_id: str | None = Field(default=None, alias="promptStrategyPackId")
    prompt_strategy_version: str | None = Field(default=None, alias="promptStrategyVersion")
    prompt_skill_scope_ref: str | None = Field(default=None, alias="promptSkillScopeRef")
    narrative: str

    @classmethod
    def from_view(cls, doc: dict[str, Any]) -> ScenarioSkillScopeResponse:
        skills_raw = doc.get("skills") if isinstance(doc.get("skills"), list) else []
        skills = [ScenarioSkillScopeSkillItem.model_validate(s) for s in skills_raw if isinstance(s, dict)]
        return cls(
            scenarioId=str(doc.get("scenarioId") or ""),
            category=str(doc.get("category") or "read"),
            mode=str(doc.get("mode") or "read_only"),
            skills=skills,
            promptStrategyPackId=doc.get("promptStrategyPackId"),
            promptStrategyVersion=doc.get("promptStrategyVersion"),
            promptSkillScopeRef=doc.get("promptSkillScopeRef"),
            narrative=str(doc.get("narrative") or ""),
        )
