"""§6 — trading reconcile HTTP models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TradingReconcileRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId", description="Telegram tg_id decimal string")
    execution_id: str | None = Field(
        default=None,
        alias="executionId",
        description="Recommended — infer case and query targets from timeline",
    )
    venue: Literal["spot", "futures"] | None = Field(
        default=None,
        description="Override venue when executionId omitted",
    )
    symbol: str | None = Field(default=None, description="Trading pair / contract symbol")
    order_id: str | None = Field(default=None, alias="orderId")
    client_order_id: str | None = Field(default=None, alias="clientOrderId")
    case_kind: str | None = Field(
        default=None,
        alias="caseKind",
        description="Optional override: CANCEL_SUCCEEDED_REPLACE_FAILED, SUBMIT_UNKNOWN, …",
    )


class TradingReconcileResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    reconcile_id: str = Field(alias="reconcileId")
    execution_id: str | None = Field(default=None, alias="executionId")
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    case_kind: str = Field(alias="caseKind")
    resolution_status: str = Field(alias="resolutionStatus")
    still_unknown: bool = Field(alias="stillUnknown")
    neutral_hint: str = Field(alias="neutralHint")
    user_message: str = Field(alias="userMessage")
    order_lookups: list[dict[str, Any]] = Field(default_factory=list, alias="orderLookups")
    partial_failure_code: str | None = Field(default=None, alias="partialFailureCode")


class TradingReconcileStatusResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    execution_id: str = Field(alias="executionId")
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    state: str | None = None
    case_kind: str = Field(alias="caseKind")
    resolution_status: str = Field(alias="resolutionStatus")
    still_unknown: bool = Field(alias="stillUnknown")
    last_reconcile_at_seq: int | None = Field(default=None, alias="lastReconcileAtSeq")
    reconcile_id: str = Field(alias="reconcileId")
    user_message: str | None = Field(default=None, alias="userMessage")
    hints: dict[str, Any] = Field(default_factory=dict)
