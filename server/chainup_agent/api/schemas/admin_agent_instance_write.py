"""Admin agent instance write paths — I02 / I04 / I05."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AdminCreateAgentInstanceRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    telegram_user_id: str = Field(alias="telegramUserId")
    template_id: str | None = Field(default=None, alias="templateId")
    template_version: str | None = Field(default=None, alias="templateVersion")
    exchange_sub_account_user_id: str | None = Field(
        default=None,
        alias="exchangeSubAccountUserId",
        description="子账户标识；未绑 API 时可先登记，用户再走 Deeplink 完成密钥绑定",
    )


class AdminAgentInstanceCreatedResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    instance_id: str = Field(alias="instanceId")
    user_id: str = Field(alias="userId")
    template_id: str = Field(alias="templateId")
    runtime_instance_state: str = Field(alias="runtimeInstanceState")
    agent_sub_account_id: str | None = Field(default=None, alias="agentSubAccountId")


class AdminPatchAgentInstanceRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    instance_overrides: dict[str, Any] | None = Field(
        default=None,
        alias="instanceOverrides",
        description="白名单键 patch；与存量 merge",
    )
    runtime_state: str | None = Field(
        default=None,
        alias="runtimeState",
        description="RUNNING|PAUSED|STOPPED|ERROR — 与 Runtime R01–R05 同窗，可选直写",
    )


class AdminBindInstanceSubaccountRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    exchange_sub_account_user_id: str | None = Field(
        default=None,
        alias="exchangeSubAccountUserId",
    )
    sub_account_id: str | None = Field(default=None, alias="subAccountId")
