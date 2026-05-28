"""Admin Tool Registry mirror schemas — CC-P1-03."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ToolRegistryMirrorEntryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    stable_id: str = Field(alias="stableId")
    entry_class: str = Field(alias="entryClass")
    matrix_status: str = Field(alias="matrixStatus")
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    summary: str | None = None


class ToolRegistryMirrorListOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    registry_version: str = Field(alias="registryVersion")
    items: list[ToolRegistryMirrorEntryOut]


class RegistryMismatchOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    missing_in_mirror: list[str] = Field(default_factory=list, alias="missingInMirror")
    extra_in_mirror: list[str] = Field(default_factory=list, alias="extraInMirror")


class RegistryIdempotencyAuditOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ok: bool
    audit_version: str = Field(alias="auditVersion")
    skill_mismatches: RegistryMismatchOut = Field(alias="skillMismatches")
    tool_mismatches: RegistryMismatchOut = Field(alias="toolMismatches")
