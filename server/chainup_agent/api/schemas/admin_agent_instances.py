"""Admin read-only Agent instances (agent-management I01/I03; partial fields)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from chainup_agent.core.config import Settings, get_settings
from chainup_agent.domain.instance_overrides import parse_instance_overrides_json
from chainup_agent.infrastructure.persistence.models.agent_instance import AgentInstance
from chainup_agent.infrastructure.persistence.models.telegram_agent_trading_binding import (
    TelegramAgentTradingBinding,
)


class AdminAgentInstanceItem(BaseModel):
    """One Agent instance + optional Telegram trading binding row (no secrets)."""

    model_config = ConfigDict(populate_by_name=True)

    instance_id: str = Field(serialization_alias="instanceId")
    telegram_user_id: str = Field(
        serialization_alias="telegramUserId",
        description="Telegram 数值 user id（字符串化，便于前端 BigInt）",
    )
    exchange_sub_account_user_id: str = Field(serialization_alias="exchangeSubAccountUserId")
    template_id: str = Field(serialization_alias="templateId")
    template_version: str = Field(serialization_alias="templateVersion")
    channel: Literal["telegram"] = "telegram"
    trading_api_binding_status: Literal["BOUND", "NONE"] = Field(
        serialization_alias="tradingApiBindingStatus",
    )
    openapi_base_url: str | None = Field(default=None, serialization_alias="openapiBaseUrl")
    binding_id: int | None = Field(default=None, serialization_alias="bindingId")
    tg_username: str | None = Field(default=None, serialization_alias="tgUsername")
    tg_lang: str | None = Field(default=None, serialization_alias="tgLang")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    user_id: str = Field(
        default="",
        serialization_alias="userId",
        description="Coobit 主站 userId 未入库时为空串",
    )
    user_email_masked: str = Field(
        default="—",
        serialization_alias="userEmailMasked",
        description="占位",
    )
    template_display_name: str = Field(
        default="",
        serialization_alias="templateDisplayName",
        description="无模板服务时默认同 templateId",
    )
    agent_state: str = Field(default="NORMAL", serialization_alias="agentState")
    runtime_state: str = Field(default="RUNNING", serialization_alias="runtimeState")
    sub_account_status: Literal["LINKED", "NONE"] = Field(serialization_alias="subAccountStatus")
    last_product_block_reason: str = Field(default="", serialization_alias="lastProductBlockReason")
    last_active_at: datetime = Field(serialization_alias="lastActiveAt")
    appendix82: dict[str, object] = Field(default_factory=dict, serialization_alias="appendix82")
    instance_overrides: dict[str, object] = Field(
        default_factory=dict,
        serialization_alias="instanceOverrides",
    )


class AdminAgentInstanceListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[AdminAgentInstanceItem]
    total: int


def admin_agent_instance_item_from_rows(
    *,
    instance_row: AgentInstance,
    binding_row: TelegramAgentTradingBinding | None,
    settings: Settings | None = None,
) -> AdminAgentInstanceItem:
    st = settings or get_settings()
    ai = instance_row
    tb = binding_row
    tid_str = str(ai.telegram_user_id)
    bound = tb is not None
    disp = (ai.template_id or "").strip() or ai.template_id
    rt = (ai.runtime_state or "RUNNING").strip().upper()
    if rt not in ("RUNNING", "PAUSED", "STOPPED", "ERROR"):
        rt = "RUNNING"

    if st.agent_runtime_global_disabled:
        agent_st = "GLOBAL_OFF"
        block = "GLOBAL_AGENT_SWITCH=OFF（G01）：禁止 Start / Resume；Pause / Stop 仍可用。"
    elif st.agent_runtime_ops_suspended:
        agent_st = "OPS_SUSPENDED"
        block = "运维全局暂停：禁止 Start / Resume。"
    elif bound:
        agent_st = "NORMAL"
        block = "—"
    else:
        agent_st = "AGENT_SUBACCOUNT_BLOCKED"
        block = "交易 API 未绑定"

    overrides = parse_instance_overrides_json(getattr(ai, "instance_overrides_json", None))

    return AdminAgentInstanceItem(
        instance_id=ai.instance_id,
        telegram_user_id=tid_str,
        exchange_sub_account_user_id=ai.exchange_sub_account_user_id,
        template_id=ai.template_id,
        template_version=ai.template_version,
        trading_api_binding_status="BOUND" if bound else "NONE",
        openapi_base_url=tb.openapi_base_url if tb else None,
        binding_id=tb.id if tb else None,
        tg_username=tb.tg_username if tb else None,
        tg_lang=tb.tg_lang if tb else None,
        created_at=ai.created_at,
        updated_at=ai.updated_at,
        template_display_name=disp,
        sub_account_status="LINKED" if bound else "NONE",
        last_active_at=ai.updated_at,
        runtime_state=rt,
        agent_state=agent_st,
        last_product_block_reason=block,
        instance_overrides=overrides,
    )
