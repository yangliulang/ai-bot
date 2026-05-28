"""Builtin confirmation rules catalog — mirrors product-doc prototype (ai.confirmation-rules)."""

from __future__ import annotations

from typing import Literal, TypedDict

RiskLevel = Literal["low", "medium", "high"]
RuleAction = Literal["force_confirm", "second_confirm", "otp_confirm", "block_auto_execute"]
ScenarioKey = Literal[
    "spot",
    "futures",
    "convert",
    "wealth",
    "leverage",
    "transfer",
    "conditional_order",
]
TriggerFieldKey = Literal["nominal_usdt", "leverage", "operation_scope", "custom"]
TriggerOpKey = Literal["gt", "gte", "lt", "lte", "eq", "contains"]


class TriggerConditionRow(TypedDict):
    fieldKey: TriggerFieldKey
    operator: TriggerOpKey
    value: str


class ConfirmationRuleDefinition(TypedDict):
    id: str
    title: str
    summary: str
    riskLevel: RiskLevel
    triggerConditions: list[TriggerConditionRow]
    scenarios: list[ScenarioKey]
    action: RuleAction
    defaultEnabled: bool


BUILTIN_CONFIRMATION_RULES: list[ConfirmationRuleDefinition] = [
    {
        "id": "hitl-trade-fund-write",
        "title": "交易与资金侧操作 · 强制确认",
        "summary": "会改变持仓、委托或账户余额的请求，须先经用户完成摘单确认后再落单，覆盖现货/合约/划转等主要场景。",
        "riskLevel": "high",
        "triggerConditions": [
            {"fieldKey": "operation_scope", "operator": "contains", "value": "改变持仓、委托或余额"},
        ],
        "scenarios": ["spot", "futures", "transfer", "conditional_order", "leverage"],
        "action": "force_confirm",
        "defaultEnabled": True,
    },
    {
        "id": "hitl-large-notional",
        "title": "大额名义本金 · 二次确认",
        "summary": "单笔名义本金超过平台大额阈值时，除常规确认外须再次核对关键参数与风险。",
        "riskLevel": "high",
        "triggerConditions": [{"fieldKey": "nominal_usdt", "operator": "gt", "value": "50,000"}],
        "scenarios": ["spot", "futures"],
        "action": "second_confirm",
        "defaultEnabled": True,
    },
    {
        "id": "hitl-high-leverage",
        "title": "高杠杆 · 二次确认",
        "summary": "杠杆超过配置上限或处于高倍档时，须再次确认强平与资金占用风险。",
        "riskLevel": "high",
        "triggerConditions": [{"fieldKey": "leverage", "operator": "gt", "value": "20"}],
        "scenarios": ["futures", "leverage"],
        "action": "second_confirm",
        "defaultEnabled": True,
    },
    {
        "id": "hitl-conditional-auto",
        "title": "条件单与自动化任务",
        "summary": "新建或撤销条件单、计划委托及会落单的自动化任务时，须先完成用户侧确认。",
        "riskLevel": "medium",
        "triggerConditions": [
            {"fieldKey": "operation_scope", "operator": "contains", "value": "条件单/自动化任务创建或撤销"},
        ],
        "scenarios": ["conditional_order", "futures", "spot"],
        "action": "force_confirm",
        "defaultEnabled": True,
    },
    {
        "id": "hitl-wealth",
        "title": "理财申购赎回",
        "summary": "须通过官网或理财 H5 完成的申赎，助手仅可引导官方入口，不得越过用户确认代为提交。",
        "riskLevel": "medium",
        "triggerConditions": [
            {"fieldKey": "operation_scope", "operator": "contains", "value": "理财申赎且需 H5/官网"},
        ],
        "scenarios": ["wealth"],
        "action": "force_confirm",
        "defaultEnabled": True,
    },
    {
        "id": "hitl-close-all",
        "title": "一键平仓与清仓类指令",
        "summary": "一键平仓、全仓 reduce-only 等强语义动作，须在确认流程中显式收口，避免误触大资金变动。",
        "riskLevel": "high",
        "triggerConditions": [
            {"fieldKey": "operation_scope", "operator": "contains", "value": "一键平仓或全仓清仓类"},
        ],
        "scenarios": ["futures"],
        "action": "second_confirm",
        "defaultEnabled": True,
    },
]

DEMO_CUSTOM_CONFIRMATION_RULES: list[ConfirmationRuleDefinition] = [
    {
        "id": "custom-demo-flash-convert",
        "title": "闪兑 · 大额二次确认",
        "summary": "闪兑单笔名义超过运营阈值时，除常规确认外须再次核对币种与到账信息。",
        "riskLevel": "medium",
        "triggerConditions": [{"fieldKey": "nominal_usdt", "operator": "gt", "value": "10,000"}],
        "scenarios": ["convert"],
        "action": "second_confirm",
        "defaultEnabled": True,
    },
    {
        "id": "custom-demo-transfer-otp",
        "title": "资金划出 · OTP 验证",
        "summary": "划出类操作超过一定名义时，须通过 OTP 等第二因素校验后再继续。",
        "riskLevel": "high",
        "triggerConditions": [{"fieldKey": "nominal_usdt", "operator": "gte", "value": "5,000"}],
        "scenarios": ["transfer"],
        "action": "otp_confirm",
        "defaultEnabled": True,
    },
    {
        "id": "custom-demo-block-auto-order",
        "title": "条件单机器人模板 · 禁止自动执行",
        "summary": "命中特定高频/网格模板时禁止静默自动落单，须显式确认或人工介入后再执行。",
        "riskLevel": "high",
        "triggerConditions": [
            {"fieldKey": "operation_scope", "operator": "contains", "value": "高频或网格类自动化模板"},
        ],
        "scenarios": ["futures", "conditional_order"],
        "action": "block_auto_execute",
        "defaultEnabled": False,
    },
]

BUILTIN_RULE_IDS: frozenset[str] = frozenset(r["id"] for r in BUILTIN_CONFIRMATION_RULES)

VALID_RISK_LEVELS: frozenset[str] = frozenset({"low", "medium", "high"})
VALID_ACTIONS: frozenset[str] = frozenset(
    {"force_confirm", "second_confirm", "otp_confirm", "block_auto_execute"}
)
VALID_SCENARIOS: frozenset[str] = frozenset(
    {"spot", "futures", "convert", "wealth", "leverage", "transfer", "conditional_order"}
)
VALID_TRIGGER_FIELDS: frozenset[str] = frozenset(
    {"nominal_usdt", "leverage", "operation_scope", "custom"}
)
VALID_TRIGGER_OPS: frozenset[str] = frozenset({"gt", "gte", "lt", "lte", "eq", "contains"})

SCENARIO_ID_TO_KEY: dict[str, ScenarioKey] = {
    "trade.spot.flash_convert": "convert",
    "trade.spot.limit_order": "spot",
    "trade.spot.amend_limit_order": "spot",
    "trade.spot.cancel_order": "spot",
    "trade.spot.open_orders": "spot",
    "trade.futures.limit_order": "futures",
    "trade.futures.market_order": "futures",
    "margin.cross.market_order": "leverage",
    "margin.cross.limit_order": "leverage",
    "wealth.holdings_read": "wealth",
}


def is_builtin_rule_id(rule_id: str) -> bool:
    return rule_id in BUILTIN_RULE_IDS


def builtin_rule_by_id(rule_id: str) -> ConfirmationRuleDefinition | None:
    for r in BUILTIN_CONFIRMATION_RULES:
        if r["id"] == rule_id:
            return r
    return None
