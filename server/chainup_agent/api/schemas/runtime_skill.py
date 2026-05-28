"""Runtime skill operation spec HTTP schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SkillOperationSpecSectionOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    body_markdown: str = Field(alias="bodyMarkdown")


class SkillOperationSpecEffectiveOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    skill_id: str = Field(alias="skillId")
    skill_spec_version: str = Field(alias="skillSpecVersion")
    spec_digest: str = Field(alias="specDigest")
    lifecycle: str = "PUBLISHED"
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    sections: list[SkillOperationSpecSectionOut]
