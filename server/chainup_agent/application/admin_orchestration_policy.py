"""Admin orchestration execution policy — Phase 2 read model for 运行场景 · 执行策略."""

from __future__ import annotations

from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.admin_ai_settings import read_gateway_defaults_merged
from chainup_agent.application.agent_scenario_catalog import ORCHESTRATION_REGISTRY_VERSION

FailureStopPolicy = Literal["stop_notify", "stop_silent", "escalate_manual"]

_ENGINEERING_SPEC_REFS: tuple[str, ...] = (
    "domains/agent/agent-orchestration/runtime-freeze.md §3 · 写路径最小编排 DAG 下限",
    "domains/agent/agent-orchestration/execution-lifecycle.md §4 · FR-AO06",
    "domains/agent/agent-orchestration/retry-policy.md",
    "domains/admin/tool-management/runtime-contract.md §3",
    "design/api.md · 编排执行预算 / FR-MC408",
)


async def read_orchestration_execution_policy(session: AsyncSession) -> dict[str, Any]:
    """Merged ops policy + gateway budget (camelCase)."""
    merged, _ver = await read_gateway_defaults_merged(session)
    bud = merged.get("orchestrationExecutionBudget")
    if not isinstance(bud, dict):
        bud = {}

    max_tools = int(bud.get("maxToolCallsPerExecution") or 32)
    max_steps = int(bud.get("maxOrchestrationStepsPerExecution") or 32)
    max_model = bud.get("maxModelTurnsPerExecution")
    max_model_rounds = int(max_model) if isinstance(max_model, int) and max_model >= 1 else 16

    timeout_sec = merged.get("timeoutSec")
    execution_timeout = int(timeout_sec) if isinstance(timeout_sec, int) and timeout_sec >= 1 else 120

    return {
        "orchestrationRegistryVersion": ORCHESTRATION_REGISTRY_VERSION,
        "autoExecutionAllowed": True,
        "blockAutoHighRiskWrite": True,
        "queryAutoDefault": True,
        "confirmationRequiredForWrites": True,
        "secondConfirmLargeNotional": True,
        "highLeverageConfirm": True,
        "maxNotionalUsdt": 50_000,
        "maxLeverage": 20,
        "maxDailyWriteOperations": 200,
        "rateLimitNote": "同一用户 10 秒内同类写请求合并提示（演示）",
        "maxRetries": 3,
        "executionTimeoutSeconds": execution_timeout,
        "failureStopPolicy": "stop_notify",
        "maxToolCalls": max_tools,
        "maxOrchestrationSteps": max_steps,
        "maxModelRounds": max_model_rounds,
        "modelRoundsLimitEnabled": max_model is not None,
        "budgetExceededStableCode": "ORCHESTRATION_BUDGET_EXCEEDED",
        "cClassPoolNote": (
            "与 ADR-003 外网步预算叠加时以更严或 design 优先级为准（execution-lifecycle §4.1）"
        ),
        "retrySummary": "retry-policy：重试不得跳过确认门 / read_skill（SC-AO-06）",
        "unknownHandlingSummary": (
            "UNKNOWN / 504 路径：查单对账 + Runtime reconciliation；"
            "禁止写类无脑同参自动重试（runtime-contract）"
        ),
        "engineeringSpecRefs": list(_ENGINEERING_SPEC_REFS),
    }
