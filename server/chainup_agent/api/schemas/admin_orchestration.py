"""Admin orchestration API schemas — 运行场景 · 执行策略."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FailureStopPolicy = Literal["stop_notify", "stop_silent", "escalate_manual"]


class OrchestrationExecutionPolicyOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    orchestration_registry_version: str = Field(alias="orchestrationRegistryVersion")
    auto_execution_allowed: bool = Field(alias="autoExecutionAllowed")
    block_auto_high_risk_write: bool = Field(alias="blockAutoHighRiskWrite")
    query_auto_default: bool = Field(alias="queryAutoDefault")
    confirmation_required_for_writes: bool = Field(alias="confirmationRequiredForWrites")
    second_confirm_large_notional: bool = Field(alias="secondConfirmLargeNotional")
    high_leverage_confirm: bool = Field(alias="highLeverageConfirm")
    max_notional_usdt: int = Field(alias="maxNotionalUsdt")
    max_leverage: int = Field(alias="maxLeverage")
    max_daily_write_operations: int = Field(alias="maxDailyWriteOperations")
    rate_limit_note: str = Field(alias="rateLimitNote")
    max_retries: int = Field(alias="maxRetries")
    execution_timeout_seconds: int = Field(alias="executionTimeoutSeconds")
    failure_stop_policy: FailureStopPolicy = Field(alias="failureStopPolicy")
    max_tool_calls: int = Field(alias="maxToolCalls")
    max_orchestration_steps: int = Field(alias="maxOrchestrationSteps")
    max_model_rounds: int = Field(alias="maxModelRounds")
    model_rounds_limit_enabled: bool = Field(alias="modelRoundsLimitEnabled")
    budget_exceeded_stable_code: str = Field(alias="budgetExceededStableCode")
    c_class_pool_note: str = Field(alias="cClassPoolNote")
    retry_summary: str = Field(alias="retrySummary")
    unknown_handling_summary: str = Field(alias="unknownHandlingSummary")
    engineering_spec_refs: list[str] = Field(default_factory=list, alias="engineeringSpecRefs")
