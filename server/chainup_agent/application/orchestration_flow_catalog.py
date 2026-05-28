"""Orchestration execution-flow catalog — FR-AO01 registry slice (Phase 2).

Human-readable **执行流程** for Admin ``/ai/runtime-orchestration`` and runtime step
templates aligned with ``agent-orchestration/confirmation-flow.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Readiness = Literal["ready", "stub"]
ClosureStatus = Literal["FROZEN", "TBD", "PLACEHOLDER"]

ORCHESTRATION_FLOW_VERSION = "2026.05-orc-v1"


@dataclass(frozen=True, slots=True)
class OrchestrationFlowStep:
    step_key: str
    label_zh: str
    order: int


@dataclass(frozen=True, slots=True)
class ScenarioOrchestrationFlow:
    scenario_id: str
    title: str
    category: str
    risk_level: str
    readiness: Readiness
    flow_summary: str
    execution_steps: tuple[OrchestrationFlowStep, ...]
    flow_anchor: str | None = None
    spec_refs: tuple[str, ...] = ()
    prompt_binding_hint: str | None = None

    @property
    def closure_status(self) -> ClosureStatus:
        if self.readiness == "ready":
            return "FROZEN"
        if self.category in ("margin", "automation") and self.readiness == "stub":
            return "TBD"
        if self.scenario_id == "wealth.holdings_read":
            return "FROZEN"
        return "TBD"


def _steps(*pairs: tuple[str, str]) -> tuple[OrchestrationFlowStep, ...]:
    return tuple(
        OrchestrationFlowStep(step_key=k, label_zh=label, order=i + 1)
        for i, (k, label) in enumerate(pairs)
    )


_READ_INTENT = ("intent.route", "意图识别")
_ACCESS = ("access.evaluate", "门禁评估")
_READ_MARKET = ("read.market", "读行情")
_READ_DEPTH = ("read.depth", "读取盘口")
_READ_TRADES = ("read.trades", "读成交")
_READ_BALANCE = ("read.balance", "读余额")
_READ_WEALTH = ("read.wealth", "读理财持仓")
_READ_ORDERS = ("read.orders", "私域读单")
_SUMMARIZE = ("summarize.return", "返回结果")

_WRITE_RISK = ("risk.check", "风险检查")
_VALIDATE = ("validate.slots", "参数校验")
_CONFIRM = ("confirm.type_a", "类型 A 确认")
_CONFIRM_STRONG = ("confirm.type_a", "二次确认")
_EXCHANGE_WRITE = ("exchange.write", "下单")
_EXCHANGE_CANCEL = ("exchange.cancel", "撤单")
_CHAT_LLM = ("llm.chat", "对话生成")


ORCHESTRATION_FLOW_CATALOG: tuple[ScenarioOrchestrationFlow, ...] = (
    ScenarioOrchestrationFlow(
        scenario_id="read.market.ticker",
        title="行情查询",
        category="read",
        risk_level="low",
        readiness="ready",
        flow_summary="分析 → 读行情 → 返回结果",
        execution_steps=_steps(_READ_INTENT, _ACCESS, _READ_MARKET, _SUMMARIZE),
        flow_anchor="read-analyze-and-search-via-agent · read.market.ticker",
        spec_refs=("flows/read-analyze-and-search-via-agent.md",),
        prompt_binding_hint="TRADING 包 · read.market.ticker",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="read.market.depth",
        title="盘口深度",
        category="read",
        risk_level="low",
        readiness="ready",
        flow_summary="读取盘口 → 汇总展示",
        execution_steps=_steps(_READ_INTENT, _ACCESS, _READ_DEPTH, _SUMMARIZE),
        flow_anchor="read-analyze · GET /sapi/v2/depth",
        spec_refs=("domains/agent/exchange-agent/trade-assistance.md §8.3",),
    ),
    ScenarioOrchestrationFlow(
        scenario_id="read.market.trades",
        title="近期成交",
        category="read",
        risk_level="low",
        readiness="ready",
        flow_summary="分析 → 解读 → 返回",
        execution_steps=_steps(_READ_INTENT, _ACCESS, _READ_TRADES, _SUMMARIZE),
        flow_anchor="read-analyze · GET /sapi/v2/trades",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="read.account.balance",
        title="账户余额查询",
        category="read",
        risk_level="low",
        readiness="ready",
        flow_summary="鉴权子账户 → 读余额 → 返回",
        execution_steps=_steps(_READ_INTENT, _ACCESS, _READ_BALANCE, _SUMMARIZE),
        flow_anchor="portfolio-insight · FR-T02",
        spec_refs=("domains/agent/exchange-agent/portfolio-insight.md",),
    ),
    ScenarioOrchestrationFlow(
        scenario_id="wealth.holdings_read",
        title="理财持仓查询",
        category="wealth",
        risk_level="low",
        readiness="ready",
        flow_summary="读持仓 → 返回",
        execution_steps=_steps(_READ_INTENT, _ACCESS, _READ_WEALTH, _SUMMARIZE),
        flow_anchor="wealth-via-agent",
        spec_refs=("flows/wealth-via-agent.md",),
        prompt_binding_hint="FEATURE_AGENT_WEALTH 闸",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="trade.spot.open_orders",
        title="现货当前委托",
        category="read",
        risk_level="low",
        readiness="ready",
        flow_summary="私域读单 → 结构化返回",
        execution_steps=_steps(_READ_INTENT, _ACCESS, _READ_ORDERS, _SUMMARIZE),
        flow_anchor="trade-assistance · openOrders",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="trade.spot.flash_convert",
        title="现货闪兑",
        category="trade",
        risk_level="high",
        readiness="ready",
        flow_summary="风险检查 → 确认 → 成交",
        execution_steps=_steps(
            _READ_INTENT,
            ("read.skill", "读技能规范"),
            _VALIDATE,
            _WRITE_RISK,
            _CONFIRM,
            _EXCHANGE_WRITE,
            _SUMMARIZE,
        ),
        flow_anchor="trade-via-agent · ADR-001 · 类型 A",
        spec_refs=(
            "flows/trade-via-agent.md",
            "domains/agent/agent-orchestration/confirmation-flow.md",
        ),
        prompt_binding_hint="须 FR-AO01～04 步骤序",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="trade.spot.limit_order",
        title="现货限价单",
        category="trade",
        risk_level="high",
        readiness="ready",
        flow_summary="风险检查 → 确认 → 下单",
        execution_steps=_steps(
            _READ_INTENT,
            ("read.skill", "读技能规范"),
            _VALIDATE,
            _WRITE_RISK,
            _CONFIRM,
            _EXCHANGE_WRITE,
            _SUMMARIZE,
        ),
        flow_anchor="confirmation-flow · FR-AO01",
        spec_refs=("flows/trade-via-agent.md",),
        prompt_binding_hint="read_skill_operation_spec 先于类型 A",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="trade.spot.cancel_order",
        title="现货撤单",
        category="trade",
        risk_level="high",
        readiness="ready",
        flow_summary="校验订单 → 确认 → 撤单",
        execution_steps=_steps(
            _READ_INTENT,
            _VALIDATE,
            _WRITE_RISK,
            _CONFIRM,
            _EXCHANGE_CANCEL,
            _SUMMARIZE,
        ),
        flow_anchor="trade-via-agent · cancel",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="trade.spot.amend_limit_order",
        title="现货逻辑改单",
        category="trade",
        risk_level="high",
        readiness="ready",
        flow_summary="读在途单 → 类型 A → cancel → replace",
        execution_steps=_steps(
            _READ_INTENT,
            ("read.skill", "读技能规范"),
            _VALIDATE,
            _WRITE_RISK,
            _CONFIRM,
            _EXCHANGE_CANCEL,
            _EXCHANGE_WRITE,
            _SUMMARIZE,
        ),
        flow_anchor="trade-via-agent · CC-P0-02 · 逻辑改单",
        spec_refs=("flows/trade-via-agent.md",),
        prompt_binding_hint="read_skill_operation_spec · amend_limit_order",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="trade.spot.oco",
        title="现货 OCO",
        category="trade",
        risk_level="high",
        readiness="stub",
        flow_summary="矩阵 PATH 未冻结 · FR-T05",
        execution_steps=_steps(_READ_INTENT, _ACCESS, _SUMMARIZE),
        flow_anchor="design/api · CC-P1-01 书面延期",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="trade.spot.bracket",
        title="现货 Bracket",
        category="trade",
        risk_level="high",
        readiness="stub",
        flow_summary="矩阵 PATH 未冻结 · FR-T05",
        execution_steps=_steps(_READ_INTENT, _ACCESS, _SUMMARIZE),
        flow_anchor="design/api · CC-P1-01 书面延期",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="trade.futures.market_order",
        title="合约市价",
        category="trade",
        risk_level="high",
        readiness="ready",
        flow_summary="风险检查 → 二次确认 → 下单",
        execution_steps=_steps(
            _READ_INTENT,
            _VALIDATE,
            _WRITE_RISK,
            _CONFIRM_STRONG,
            _EXCHANGE_WRITE,
            _SUMMARIZE,
        ),
        flow_anchor="trade-via-agent · Phase 2.3 · HTTP + TG Type-A（Step 2.3b）",
        prompt_binding_hint="TRADING 包 · trade.futures.market_order（Step 2.3c）",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="trade.futures.limit_order",
        title="合约限价",
        category="trade",
        risk_level="high",
        readiness="ready",
        flow_summary="风险检查 → 确认 → 下单",
        execution_steps=_steps(
            _READ_INTENT,
            _VALIDATE,
            _WRITE_RISK,
            _CONFIRM,
            _EXCHANGE_WRITE,
            _SUMMARIZE,
        ),
        flow_anchor="trade-via-agent · Phase2",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="trade.futures.cancel_order",
        title="合约撤单",
        category="trade",
        risk_level="medium",
        readiness="ready",
        flow_summary="识别委托 → 撤单",
        execution_steps=_steps(
            _READ_INTENT,
            _VALIDATE,
            _EXCHANGE_CANCEL,
            _SUMMARIZE,
        ),
        flow_anchor="trade-via-agent · Phase 2.3 · cancel",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="margin.cross.market_order",
        title="全仓杠杆市价",
        category="margin",
        risk_level="high",
        readiness="ready",
        flow_summary="风险检查 → 双次确认 → 下单",
        execution_steps=_steps(
            _READ_INTENT,
            _VALIDATE,
            _WRITE_RISK,
            ("confirm.type_a", "双次强确认"),
            _EXCHANGE_WRITE,
            _SUMMARIZE,
        ),
        flow_anchor="trade-via-agent · Phase 2.4 · HTTP + TG 双确认",
        prompt_binding_hint="TRADING 包 · margin.cross.market_order（0024）",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="margin.cross.limit_order",
        title="全仓杠杆限价",
        category="margin",
        risk_level="high",
        readiness="ready",
        flow_summary="风险检查 → 双次确认 → 挂单",
        execution_steps=_steps(
            _READ_INTENT,
            _VALIDATE,
            _WRITE_RISK,
            ("confirm.type_a", "双次确认"),
            _EXCHANGE_WRITE,
            _SUMMARIZE,
        ),
        flow_anchor="trade-via-agent · Phase 2.4",
        prompt_binding_hint="TRADING 包 · margin.cross.limit_order（0024）",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="automation.condition_order",
        title="条件单创建",
        category="automation",
        risk_level="medium",
        readiness="ready",
        flow_summary="触发条件 → 确认 → 创建条件单",
        execution_steps=_steps(
            _READ_INTENT,
            _VALIDATE,
            _WRITE_RISK,
            _CONFIRM,
            _EXCHANGE_WRITE,
            _SUMMARIZE,
        ),
        flow_anchor="automation-alerts · Phase 2.5",
        prompt_binding_hint="TRADING 包 · automation.condition_order（0025）",
        spec_refs=("flows/automation-alerts.md",),
    ),
    ScenarioOrchestrationFlow(
        scenario_id="automation.condition_orders_read",
        title="条件单查询",
        category="automation",
        risk_level="low",
        readiness="ready",
        flow_summary="拉取开放委托并筛选条件单",
        execution_steps=_steps(_READ_INTENT, _VALIDATE, _READ_ORDERS, _SUMMARIZE),
        flow_anchor="automation-alerts · Phase 2.5 · read",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="automation.condition_order_cancel",
        title="条件单撤销",
        category="automation",
        risk_level="medium",
        readiness="ready",
        flow_summary="触发条件确认 → 撤单",
        execution_steps=_steps(
            _READ_INTENT,
            _VALIDATE,
            _WRITE_RISK,
            _CONFIRM,
            _EXCHANGE_CANCEL,
            _SUMMARIZE,
        ),
        flow_anchor="automation-alerts · Phase 2.5 · cancel",
    ),
    ScenarioOrchestrationFlow(
        scenario_id="chat.faq",
        title="纯对话问答",
        category="chat",
        risk_level="low",
        readiness="ready",
        flow_summary="意图识别 → 拼装 Prompt → 对话返回",
        execution_steps=_steps(_READ_INTENT, _ACCESS, _CHAT_LLM, _SUMMARIZE),
        flow_anchor="Prompt Assembly · 无交易所写",
        prompt_binding_hint="chat.faq TRADING 层 + LLM",
    ),
)


def flow_by_scenario_id(scenario_id: str) -> ScenarioOrchestrationFlow | None:
    sid = scenario_id.strip()
    for row in ORCHESTRATION_FLOW_CATALOG:
        if row.scenario_id == sid:
            return row
    return None


def flow_catalog_index() -> dict[str, ScenarioOrchestrationFlow]:
    return {row.scenario_id: row for row in ORCHESTRATION_FLOW_CATALOG}
