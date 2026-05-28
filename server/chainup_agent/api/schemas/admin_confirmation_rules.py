"""Pydantic DTOs — Admin confirmation rules (ai.confirmation-rules)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RiskLevel = Literal["low", "medium", "high"]
RuleAction = Literal["force_confirm", "second_confirm", "otp_confirm", "block_auto_execute"]
ScenarioKey = Literal[
    "spot",
    "futures",
    "convert",
    "wealth",
    "leverage",
    "transfer",
    "conditional_order",
]
TriggerFieldKey = Literal["nominal_usdt", "leverage", "operation_scope", "custom"]
TriggerOpKey = Literal["gt", "gte", "lt", "lte", "eq", "contains"]


class TriggerConditionRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    field_key: TriggerFieldKey = Field(alias="fieldKey")
    operator: TriggerOpKey
    value: str = Field(min_length=1, max_length=512)


class ConfirmationRuleItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    summary: str
    risk_level: RiskLevel = Field(alias="riskLevel")
    trigger_conditions: list[TriggerConditionRow] = Field(alias="triggerConditions")
    scenarios: list[ScenarioKey]
    action: RuleAction
    default_enabled: bool = Field(alias="defaultEnabled")
    enabled: bool
    is_builtin: bool = Field(alias="isBuiltin")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")


class ConfirmationRuleListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ConfirmationRuleItem]
    total: int
    enabled_count: int = Field(alias="enabledCount")


class ConfirmationRuleCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1, max_length=256)
    summary: str = Field(min_length=1, max_length=4096)
    risk_level: RiskLevel = Field(alias="riskLevel")
    trigger_conditions: list[TriggerConditionRow] = Field(alias="triggerConditions", min_length=1)
    scenarios: list[ScenarioKey] = Field(min_length=1)
    action: RuleAction
    default_enabled: bool = Field(default=True, alias="defaultEnabled")


class ConfirmationRuleUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1, max_length=256)
    summary: str = Field(min_length=1, max_length=4096)
    risk_level: RiskLevel = Field(alias="riskLevel")
    trigger_conditions: list[TriggerConditionRow] = Field(alias="triggerConditions", min_length=1)
    scenarios: list[ScenarioKey] = Field(min_length=1)
    action: RuleAction
    default_enabled: bool = Field(alias="defaultEnabled")


class ConfirmationRuleEnabledPatchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    enabled: bool


class ConfirmationRuleResetResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ConfirmationRuleItem]
    total: int
    enabled_count: int = Field(alias="enabledCount")
