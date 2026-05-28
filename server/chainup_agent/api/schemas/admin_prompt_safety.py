"""Pydantic DTOs — Admin prompt safety (ai.prompt-safety)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from chainup_agent.api.schemas.prompt_management import PromptPackSummaryOut

SafetyInterceptCategory = Literal["runtime", "prompt", "tool", "session"]
ToolEnforcementMode = Literal["default_deny", "allowlist_only", "approve_then_allow"]
ToolPolicyKind = Literal["deny", "allowlist", "shadow"]
RuntimeGovernanceHrefKind = Literal["confirmation", "policy", "routing"]


class SafetyBlocklistRuleOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rule_id: str = Field(alias="ruleId")
    phrase: str
    match_mode: str = Field(alias="matchMode")


class SafetyBlocklistOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    safety_phrase_blocklist_revision: str = Field(alias="safetyPhraseBlocklistRevision")
    safety_phrase_scan_scope_default: str = Field(alias="safetyPhraseScanScopeDefault")
    rules: list[SafetyBlocklistRuleOut]


class SafetyOverviewOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    safety_phrase_blocklist_revision: str = Field(alias="safetyPhraseBlocklistRevision")
    safety_phrase_scan_scope_default: str = Field(alias="safetyPhraseScanScopeDefault")
    platform_safety_pack: PromptPackSummaryOut | None = Field(
        default=None, alias="platformSafetyPack"
    )
    safety_prompt_pack_count: int = Field(alias="safetyPromptPackCount")
    published_safety_pack_count: int = Field(alias="publishedSafetyPackCount")
    enabled_confirmation_rules_count: int = Field(alias="enabledConfirmationRulesCount")
    global_agent_switch_on: bool = Field(alias="globalAgentSwitchOn")
    ops_suspended: bool = Field(alias="opsSuspended")


class SafetyInterceptItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    ts: datetime
    category: SafetyInterceptCategory
    scenario_label: str = Field(alias="scenarioLabel")
    kind_label: str = Field(alias="kindLabel")
    reason: str
    subject: str | None = None
    execution_id: str | None = Field(default=None, alias="executionId")
    matched_rule_id: str | None = Field(default=None, alias="matchedRuleId")


class SafetyInterceptListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[SafetyInterceptItem]
    total: int


class RuntimeSafetyGovernanceRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str
    name: str
    risk_level_label: str = Field(alias="riskLevelLabel")
    auto_exec_summary: str = Field(alias="autoExecSummary")
    confirm_summary: str = Field(alias="confirmSummary")
    breaker_summary: str = Field(alias="breakerSummary")
    href_kind: RuntimeGovernanceHrefKind = Field(alias="hrefKind")


class RuntimeSafetyGovernanceResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[RuntimeSafetyGovernanceRow]


class ToolSafetyPolicyRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str
    tool_pattern: str = Field(alias="toolPattern")
    policy: ToolPolicyKind
    enforcement_mode: ToolEnforcementMode = Field(alias="enforcementMode")
    note: str


class ToolSafetyPolicyResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ToolSafetyPolicyRow]


class SessionSafetyPolicyItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str
    label: str
    summary: str
    status: Literal["enabled", "warning", "info"]


class SessionSafetyPolicyResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[SessionSafetyPolicyItem]
