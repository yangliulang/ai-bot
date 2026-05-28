"""Phase 1 agent onboarding / binding / subaccount status DTOs (camelCase JSON)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from chainup_agent.api.schemas.agent_api_binding import TelegramInboundPayload


class ApiBindingStatusResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    telegram_user_id: int = Field(alias="telegramUserId")
    agent_trading_api_binding_status: Literal["NONE", "BOUND"] = Field(
        alias="agentTradingApiBindingStatus",
    )
    openapi_base_url: str | None = Field(default=None, alias="openapiBaseUrl")
    binding_id: int | None = Field(default=None, alias="bindingId")
    tg_username: str | None = Field(default=None, alias="tgUsername")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")


class SubaccountStatusResponse(BaseModel):
    """子账户与 Key 由用户在所内自备；本列以「已托管交易 API 绑定」近似 ready。"""

    model_config = ConfigDict(populate_by_name=True)

    telegram_user_id: int = Field(alias="telegramUserId")
    subaccount_ready: bool = Field(alias="subaccountReady")
    agent_sub_account_id: str | None = Field(
        default=None,
        alias="agentSubAccountId",
        description="未单独落库；恒为 null，待与所内子账户主键对签后填充。",
    )
    trading_api_binding_status: Literal["NONE", "BOUND"] = Field(
        alias="tradingApiBindingStatus",
    )


class OnboardingInitiateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    telegram: TelegramInboundPayload | None = None


class OnboardingInitiateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    onboarding_id: str = Field(alias="onboardingId")
    telegram_user_id: int = Field(alias="telegramUserId")
    next_step: Literal["bind_trading_api", "complete"] = Field(alias="nextStep")
    agent_trading_api_binding_status: Literal["NONE", "BOUND"] = Field(
        alias="agentTradingApiBindingStatus",
    )


class SubaccountCreateDeferredResponse(BaseModel):
    """不代开立子账户；契约占位。用户 Deeplink 前已在所内自建子账户与 API Key。"""

    model_config = ConfigDict(populate_by_name=True)

    accepted: bool = False
    status: Literal["DEFERRED_EXCHANGE_CONSOLE"] = "DEFERRED_EXCHANGE_CONSOLE"
    code: str = "AGENT_SUBACCOUNT_CREATE_PHASE1_NOT_AUTOMATED"
    message: str = Field(
        default=(
            "本服务不提供自动开立子账户或代开 API Key。"
            "请先在主站/所内自行创建 Agent 专用子账户与交易 API Key，"
            "再进入 Deeplink 完成校验与托管绑定。"
        ),
    )
