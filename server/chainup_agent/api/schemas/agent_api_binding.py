from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ValidateAgentApiKeysRequest(BaseModel):
    """Deeplink / H5 校验用（与前端 ``agentApiBinding.ts`` 对齐）。"""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    openapi_base_url: str = Field(
        ...,
        description="交易所 OpenAPI baseurl（现货网关，例如 https://openapi.xxx.xx）",
    )
    api_key: str = Field(..., description="子账户交易 API Key")
    secret_key: str = Field(..., description="子账户交易 API Secret")
    sub_account_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("sub_account_id", "subAccountId"),
        description="用户填写的交易所子账户用户 ID；校验须非空，且在账户接口返回含 id 字段时须一致",
    )


class ValidateAgentApiKeysResponse(BaseModel):
    """成功体：前端接受 ``valid`` 或 ``ok`` 任一即可。"""

    valid: bool = True
    ok: bool = True


class TelegramInboundPayload(BaseModel):
    """与 Deeplink ``tg_*`` query / 前端 snake_case POST 对齐；非签名信任边界。"""

    model_config = ConfigDict(extra="ignore")

    tg_id: str | None = Field(None, description="Telegram 用户数值 id（字符串形态）")
    tg_username: str | None = None
    tg_first_name: str | None = None
    tg_last_name: str | None = None
    tg_lang: str | None = None


class ConfirmAgentApiBindingRequest(ValidateAgentApiKeysRequest):
    """校验通过后写入 ``telegram_agent_trading_binding``；须携带 ``telegram`` 与 ``tg_id``。"""

    telegram: TelegramInboundPayload | None = Field(None, description="入站会话上下文")


class ConfirmAgentApiBindingResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    saved: bool = True
    telegram_user_id: int = Field(..., serialization_alias="telegramUserId")
    instance_id: str = Field(..., serialization_alias="instanceId")
    exchange_sub_account_user_id: str = Field(
        ...,
        serialization_alias="agentSubAccountId",
        description="回显用户声明的子账户 ID（非 Secret）",
    )
    binding_row_created: bool = Field(
        ...,
        serialization_alias="bindingRowCreated",
    )
    activation_welcome_sent: bool = Field(
        ...,
        serialization_alias="activationWelcomeSent",
    )
    activation_welcome_skip_reason: str | None = Field(
        default=None,
        serialization_alias="activationWelcomeSkipReason",
    )


class MeAgentTradingApiBindingRequest(BaseModel):
    """产品与 ``deeplink/tradingApiBinding.ts`` camelCase Body 对齐的别名路径。"""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    openapi_base_url: str = Field(
        ...,
        validation_alias=AliasChoices("openapi_base_url", "openapiBaseUrl"),
        description="与 validate/confirm 同口径的根 URL",
    )
    api_key: str = Field(
        ...,
        validation_alias=AliasChoices("api_key", "apiKey"),
    )
    secret_key: str = Field(
        ...,
        validation_alias=AliasChoices("secret_key", "apiSecret"),
    )
    telegram: TelegramInboundPayload | None = None
    idempotency_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("idempotency_key", "idempotencyKey"),
    )
    deeplink_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("deeplink_token", "deeplinkToken"),
    )
    sub_account_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("sub_account_id", "subAccountId"),
        description="与校验步骤同一字段；确认绑定时必填；写入 agent_instance",
    )


class MeAgentTradingApiBindingResponse(BaseModel):
    """成功体兼容 PM Web 占位字段；密钥永不回显。"""

    model_config = ConfigDict(populate_by_name=True)

    saved: bool = True
    agent_trading_api_binding_status: str = "BOUND"
    binding_row_created: bool = Field(
        ...,
        description="新插入绑定行为 true；已存在行上的更新（重复提交绑定）为 false。",
        serialization_alias="bindingRowCreated",
    )
    instance_id: str = Field(..., serialization_alias="instanceId")
    exchange_sub_account_user_id: str = Field(
        ...,
        serialization_alias="agentSubAccountId",
    )
    activation_welcome_sent: bool = Field(
        default=False,
        serialization_alias="activationWelcomeSent",
    )
    activation_welcome_skip_reason: str | None = Field(
        default=None,
        serialization_alias="activationWelcomeSkipReason",
    )
