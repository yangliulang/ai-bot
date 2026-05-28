"""Admin Agent Management — Runtime (R01–R06) + G01 read model (agent-management OpenAPI 同窗)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


RuntimeAction = Literal["start", "pause", "resume", "stop"]


class GlobalAgentGateResponse(BaseModel):
    """FR-AM-G01 · 只读横幅数据源（不改 `GLOBAL_AGENT_SWITCH` 本体；映射运维 env）。"""

    model_config = ConfigDict(populate_by_name=True)

    global_agent_switch_on: bool = Field(
        alias="globalAgentSwitchOn",
        description="与 `GLOBAL_AGENT_SWITCH` 语义对齐：false 时须展示 G01 横幅",
    )
    ops_suspended: bool = Field(
        alias="opsSuspended",
        description="`CHAINUP_AGENT_AGENT_RUNTIME_OPS_SUSPENDED`",
    )
    banner_message: str | None = Field(
        default=None,
        alias="bannerMessage",
        description="OFF / 暂停时的短文案（前端可直接展示或作 fallback）",
    )
    reason_codes: list[str] = Field(
        default_factory=list,
        alias="reasonCodes",
        description="如 AGENT_GLOBAL_OFF / AGENT_OPS_SUSPENDED",
    )


class AgentBatchFailureItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    instance_id: str = Field(alias="instanceId")
    code: str
    message: str = ""


class AgentBatchRuntimeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str | None = Field(
        default=None,
        description="部分失败时 AGENT_BATCH_PARTIAL（OpenAPI AgentBatchRuntimeResult）",
    )
    message: str | None = None
    succeeded: list[str] = Field(default_factory=list)
    failures: list[AgentBatchFailureItem] = Field(default_factory=list)


class AgentRuntimeBatchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    instance_ids: list[str] = Field(alias="instanceIds", min_length=1)
    action: RuntimeAction
