"""Runtime Phase 1 DTOs (access / intent / routing / execution) aligned with OpenAPI fragments."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

# --- Intent pipeline (NLU draft + policy plan) ---


class IntentScenarioCandidateDraft(BaseModel):
    """Structured NLU: one scenarioId hypothesis with score."""

    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(alias="scenarioId")
    confidence: float = Field(ge=0.0, le=1.0)


class IntentNluDraft(BaseModel):
    """Understanding-layer output (keyword MVP; replaceable by LLM structured JSON)."""

    model_config = ConfigDict(populate_by_name=True)

    source: Literal["keyword_v1", "llm_structured_v1"] = Field(
        description="NLU backend: keyword_v1 | llm_structured_v1 (LLM JSON with keyword merge).",
    )
    primary_intent_family: str = Field(
        alias="primaryIntentFamily",
        description="Coarse bucket: trade_write | portfolio_read | wealth_read | chat | unknown",
    )
    scenario_id_candidates: list[IntentScenarioCandidateDraft] = Field(
        default_factory=list,
        alias="scenarioIdCandidates",
    )
    slots: dict[str, str] = Field(default_factory=dict)
    order_type_hint: Literal["market", "limit", "unknown"] = Field(
        default="unknown",
        alias="orderTypeHint",
    )
    clarify_hints: list[str] = Field(default_factory=list, alias="clarifyHints")


class IntentPolicyPlan(BaseModel):
    """Deterministic router output — feeds execution / Telegram orchestration."""

    model_config = ConfigDict(populate_by_name=True)

    next_step: Literal[
        "CLARIFY",
        "ROUTE_READ_SKILL",
        "ROUTE_CHAT_FAQ",
        "CONFIRM_TYPE_A",
        "RESOLVE_FLASH_NOTIONAL",
        "RESOLVE_TRADE_NOTIONAL",
        "EXECUTE_SPOT_CANCEL",
        "EXECUTE_FUTURES_CANCEL",
        "BLOCKED_FEATURE",
        "STUB_NOT_EXECUTABLE",
        "UNKNOWN",
    ] = Field(alias="nextStep")
    resolved_scenario_id: str | None = Field(default=None, alias="resolvedScenarioId")
    clarify: list[str] = Field(default_factory=list)
    policy_codes: list[str] = Field(default_factory=list, alias="policyCodes")
    note: str | None = None


# --- Access (access-control EvaluateEligibility + EligibilityEnvelope) ---


class EvaluateEligibilityRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str | None = Field(
        default=None,
        alias="userId",
        description=(
            "Telegram user id (tg_id) as numeric string — NOT the exchange sub-account id. "
            "Omit if subAccountId is provided."
        ),
    )
    sub_account_id: str | None = Field(
        default=None,
        alias="subAccountId",
        description=(
            "Exchange sub-account id from binding confirm; server resolves Telegram tg_id via agent_instance."
        ),
    )
    channel: str | None = Field(
        default=None,
        description="e.g. telegram; default treated as telegram in Coobit",
    )
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    telegram_chat_id: int | None = Field(
        default=None,
        alias="telegramChatId",
        description=(
            "Optional Telegram chat.id from webhook envelope; "
            "allowlist (CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST) may match chat id"
        ),
    )

    @model_validator(mode="after")
    def _user_or_subaccount(self) -> Self:
        u = (self.user_id or "").strip()
        s = (self.sub_account_id or "").strip()
        if not u and not s:
            raise ValueError("须提供 userId（Telegram tg_id）或 subAccountId（子账户 ID）至少一项。")
        return self


class EligibilityEnvelope(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    allowed: bool
    code: str | None = None
    reason: str | None = None
    locale: str | None = None
    capabilities: dict[str, Any] | None = None
    requires_main_site: bool | None = Field(
        default=None,
        alias="requiresMainSite",
        description=(
            "conservative hint: true when UX should route to Deeplink/H5/main-site binding "
            "or onboarding (e.g. subaccount/bind required); false when Telegram-only session is sufficient."
        ),
    )
    evaluated_at: datetime | None = Field(default=None, alias="evaluatedAt")
    eligibility_decision_id: str | None = Field(default=None, alias="eligibilityDecisionId")


class AccessReasonItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str
    summary: str


class AccessReasonsResponse(BaseModel):
    reasons: list[AccessReasonItem]


# --- Intent ---


class IntentRecognizeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    text: str = Field(description="User-visible utterance channel text")
    user_id: str | None = Field(default=None, alias="userId")
    channel: str | None = None
    session_id: str | None = Field(
        default=None,
        alias="sessionId",
        description="Channel session key for replay / observability (optional Phase1).",
    )
    execution_id: str | None = Field(
        default=None,
        alias="executionId",
        description="Active execution anchor if any (optional).",
    )
    locale: str | None = Field(default=None, description="BCP-47 / product locale hint")
    previous_scenario_id: str | None = Field(
        default=None,
        alias="previousScenarioId",
        description="Last committed scenarioId in the session (follow-up disambiguation).",
    )


class IntentCandidate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(alias="scenarioId")
    score: float = Field(ge=0.0, le=1.0)


class IntentRecognizeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str | None = Field(default=None, alias="scenarioId")
    confidence: float = Field(ge=0.0, le=1.0)
    candidates: list[IntentCandidate] = Field(default_factory=list)
    nlu: IntentNluDraft | None = None
    plan: IntentPolicyPlan | None = None
    orchestration_version: str | None = Field(
        default=None,
        alias="orchestrationVersion",
        description="Server intent-router version string (observability / replay).",
    )
    nlu_source: str | None = Field(
        default=None,
        alias="nluSource",
        description="Same as nlu.source when present.",
    )
    effective_locale: str | None = Field(
        default=None,
        alias="effectiveLocale",
        description="Normalized locale bucket: zh-Hans | zh-Hant | en (from request locale hint).",
    )
    effective_intent_nlu_use_llm: bool | None = Field(
        default=None,
        alias="effectiveIntentNluUseLlm",
        description=(
            "Whether this request entered the LLM NLU attempt branch "
            "(env override or gateway_defaults.intentNluUseLlm)."
        ),
    )


# --- Routing (noop body) ---


class RoutingExecuteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(alias="scenarioId")
    user_id: str = Field(alias="userId")
    channel: str | None = None
    utterance_snapshot: str | None = Field(
        default=None,
        alias="utteranceSnapshot",
        description="Optional echo of triggering text for audits",
    )
    symbol: str | None = Field(
        default=None,
        description=(
            "read.market.* public market: trading pair (e.g. BTC-USDT), "
            "normalized server-side for /sapi/v2/ticker|depth|trades"
        ),
    )
    market_data_limit: int | None = Field(
        default=None,
        alias="marketDataLimit",
        ge=1,
        le=100,
        description=(
            "read.market.depth (per-side rows) and read.market.trades (trade count); "
            "default 20 when omitted."
        ),
    )


class RoutingExecuteResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    routed: bool
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    note: str | None = None
    exchange_read_preview: dict[str, Any] | None = Field(
        default=None,
        alias="exchangeReadPreview",
        description="read.* exchange JSON snapshot (filtered); no secrets.",
    )
    execution_id: str | None = Field(
        default=None,
        alias="executionId",
        description=(
            "Set when POST /routing/execute runs the HTTP execution lifecycle "
            "(accept → exchange → finalize); use for Admin timeline correlation."
        ),
    )


# --- Scenarios catalogue ---


class ExecutionFlowStepOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    step_key: str = Field(alias="stepKey")
    label_zh: str = Field(alias="labelZh")
    order: int


class ScenarioListItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(alias="scenarioId")
    summary: str
    flow_summary: str | None = Field(
        default=None,
        alias="flowSummary",
        description="Human-readable 执行流程（与 summary 同窗，Phase2 优先展示本字段）。",
    )
    readiness: Literal["stub", "ready"]
    title: str | None = Field(
        default=None,
        description="Short zh title — aligned with Admin 运行场景 registry.",
    )
    category: str | None = Field(
        default=None,
        description="read | trade | margin | wealth | automation | chat",
    )
    risk_level: str | None = Field(
        default=None,
        alias="riskLevel",
        description="low | medium | high (product risk hint for ops UI).",
    )
    closure_status: str | None = Field(
        default=None,
        alias="closureStatus",
        description="FROZEN | TBD | PLACEHOLDER — ops runtime status hint.",
    )
    execution_steps: list[ExecutionFlowStepOut] = Field(
        default_factory=list,
        alias="executionSteps",
        description="Registered orchestration step sequence (FR-AO01).",
    )


class ScenarioDetailOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(alias="scenarioId")
    title: str | None = None
    category: str | None = None
    risk_level: str | None = Field(default=None, alias="riskLevel")
    readiness: Literal["stub", "ready"]
    closure_status: str | None = Field(default=None, alias="closureStatus")
    flow_summary: str = Field(alias="flowSummary")
    summary: str
    flow_anchor: str | None = Field(default=None, alias="flowAnchor")
    spec_refs: list[str] = Field(default_factory=list, alias="specRefs")
    prompt_binding_hint: str | None = Field(default=None, alias="promptBindingHint")
    execution_steps: list[ExecutionFlowStepOut] = Field(
        default_factory=list,
        alias="executionSteps",
    )
    orchestration_registry_version: str | None = Field(
        default=None,
        alias="orchestrationRegistryVersion",
    )


class ScenarioListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenarios: list[ScenarioListItem]
    orchestration_registry_version: str | None = Field(
        default=None,
        alias="orchestrationRegistryVersion",
        description="Registry bundle id — same spirit as Admin ORCHESTRATION_VERSION_DISPLAY.",
    )


# --- Execution (persisted ``agent_execution``; billing / audit anchor) ---


class ExecutionAcceptRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId")
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    channel: str | None = None
    idempotency_key: str | None = Field(default=None, alias="idempotencyKey")
    prompt_pack_version: str | None = Field(
        default=None,
        alias="promptPackVersion",
        description="Optional; when omitted, server fills from published pack for scenarioId if any.",
    )
    resolved_prompt_binding: dict[str, Any] | None = Field(
        default=None,
        alias="resolvedPromptBinding",
        description="Optional resolved prompt binding snapshot (observability).",
    )


class ExecutionAcceptResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    execution_id: str = Field(alias="executionId")
    state: Literal["ACCEPTED"] = "ACCEPTED"
    created_at: datetime = Field(alias="createdAt")


class ExecutionStatusResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    execution_id: str = Field(alias="executionId")
    user_id: str = Field(alias="userId")
    scenario_id: str | None = Field(default=None, alias="scenarioId")
    state: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
    prompt_pack_version: str | None = Field(
        default=None,
        alias="promptPackVersion",
        description="Published prompt pack version when scenario had an effective pack.",
    )
    resolved_prompt_binding: dict[str, Any] | None = Field(
        default=None,
        alias="resolvedPromptBinding",
    )


class ExecutionFinalizeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    execution_id: str = Field(alias="executionId")
    outcome: Literal["SUCCESS", "FAILED", "CANCELLED", "UNKNOWN"]
    note: str | None = None


class ExecutionFinalizeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    execution_id: str = Field(alias="executionId")
    state: str
    finalized_at: datetime = Field(alias="finalizedAt")


def utc_now() -> datetime:
    return datetime.now(UTC)
