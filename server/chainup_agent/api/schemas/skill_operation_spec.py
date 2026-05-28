"""Admin / internal skill operation spec schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SkillOperationSpecSummaryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    skill_id: str = Field(alias="skillId")
    skill_spec_version: str = Field(alias="skillSpecVersion")
    lifecycle: str
    scenario_ids: list[str] = Field(default_factory=list, alias="scenarioIds")
    contract_complete: bool = Field(alias="contractComplete")
    spec_digest: str | None = Field(default=None, alias="specDigest")
    published_at: str | None = Field(default=None, alias="publishedAt")


class SkillOperationSpecListOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[SkillOperationSpecSummaryOut]


class SkillOperationSpecBodyOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    skill_id: str = Field(alias="skillId")
    skill_spec_version: str = Field(alias="skillSpecVersion")
    body_markdown: str = Field(alias="bodyMarkdown")
    spec_digest: str | None = Field(default=None, alias="specDigest")
    source_git_ref: str | None = Field(default=None, alias="sourceGitRef")


class SkillSpecVersionEntryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    skill_spec_version: str = Field(alias="skillSpecVersion")
    lifecycle: str
    published_at: str | None = Field(default=None, alias="publishedAt")


class SkillSpecVersionHistoryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    skill_id: str = Field(alias="skillId")
    items: list[SkillSpecVersionEntryOut]


class SkillSpecPublishRequestIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    skill_spec_version: str = Field(alias="skillSpecVersion")
    body_markdown: str | None = Field(default=None, alias="bodyMarkdown")
    spec_digest: str | None = Field(default=None, alias="specDigest")
    source_git_ref: str | None = Field(default=None, alias="sourceGitRef")


class SkillSpecPublishResultOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    skill_id: str = Field(alias="skillId")
    skill_spec_version: str = Field(alias="skillSpecVersion")
    lifecycle: str
    spec_digest: str | None = Field(default=None, alias="specDigest")


class EffectiveSkillBodyOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    skill_id: str = Field(alias="skillId")
    skill_spec_version: str = Field(alias="skillSpecVersion")
    body_markdown: str = Field(alias="bodyMarkdown")
    spec_digest: str | None = Field(default=None, alias="specDigest")
    etag: str | None = None
