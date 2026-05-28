"""Runtime evaluation of admin confirmation rules against trade context."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.admin_confirmation_rules import load_merged_enabled_rules
from chainup_agent.domain.confirmation_rules_catalog import (
    SCENARIO_ID_TO_KEY,
    ConfirmationRuleDefinition,
    ScenarioKey,
    TriggerConditionRow,
)


@dataclass
class ConfirmationEvalContext:
    scenario_key: ScenarioKey
    scenario_id: str | None = None
    nominal_usdt: Decimal | None = None
    leverage: Decimal | None = None
    operation_scope: str | None = None


@dataclass
class MatchedConfirmationRule:
    rule_id: str
    title: str
    action: str


@dataclass
class ConfirmationEvalResult:
    matched_rules: list[MatchedConfirmationRule] = field(default_factory=list)
    requires_second_confirm: bool = False
    requires_otp_confirm: bool = False
    block_auto_execute: bool = False
    force_confirm_disabled_for_write: bool = False

    def to_timeline_summary(self) -> dict:
        return {
            "matchedRuleIds": [m.rule_id for m in self.matched_rules],
            "requiresSecondConfirm": self.requires_second_confirm,
            "requiresOtpConfirm": self.requires_otp_confirm,
            "blockAutoExecute": self.block_auto_execute,
            "forceConfirmDisabledForWrite": self.force_confirm_disabled_for_write,
        }


_NUMERIC_CLEAN_RE = re.compile(r"[,\s]")


def _parse_threshold(raw: str) -> Decimal | None:
    cleaned = _NUMERIC_CLEAN_RE.sub("", raw.strip())
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _compare_numeric(op: str, actual: Decimal, threshold: Decimal) -> bool:
    if op == "gt":
        return actual > threshold
    if op == "gte":
        return actual >= threshold
    if op == "lt":
        return actual < threshold
    if op == "lte":
        return actual <= threshold
    if op == "eq":
        return actual == threshold
    return False


def _compare_text(op: str, actual: str, expected: str) -> bool:
    if op == "contains":
        return expected in actual
    if op == "eq":
        return actual == expected
    return False


def _condition_matches(row: TriggerConditionRow, ctx: ConfirmationEvalContext) -> bool:
    fk = row["fieldKey"]
    op = row["operator"]
    val = row["value"]

    if fk == "nominal_usdt":
        if ctx.nominal_usdt is None:
            return False
        threshold = _parse_threshold(val)
        if threshold is None:
            return False
        return _compare_numeric(op, ctx.nominal_usdt, threshold)

    if fk == "leverage":
        if ctx.leverage is None:
            return False
        threshold = _parse_threshold(val.replace("x", "").replace("X", ""))
        if threshold is None:
            return False
        return _compare_numeric(op, ctx.leverage, threshold)

    if fk in ("operation_scope", "custom"):
        scope = (ctx.operation_scope or "").strip()
        if not scope:
            return False
        return _compare_text(op, scope, val.strip())

    return False


def _rule_matches(rule: ConfirmationRuleDefinition, ctx: ConfirmationEvalContext) -> bool:
    if ctx.scenario_key not in rule["scenarios"]:
        return False
    conditions = rule["triggerConditions"]
    if not conditions:
        return False
    return all(_condition_matches(c, ctx) for c in conditions)


def scenario_key_for_scenario_id(scenario_id: str) -> ScenarioKey | None:
    return SCENARIO_ID_TO_KEY.get(scenario_id)


def build_write_operation_scope(scenario_id: str) -> str:
    """Canonical tag for builtin operation_scope triggers on write paths."""
    if scenario_id.startswith("trade.spot."):
        return "改变持仓、委托或余额 · 现货写路径"
    if scenario_id.startswith("trade.futures."):
        return "改变持仓、委托或余额 · 合约写路径"
    return "改变持仓、委托或余额"


def evaluate_confirmation_rules_sync(
    rules: list[tuple[ConfirmationRuleDefinition, bool]],
    ctx: ConfirmationEvalContext,
) -> ConfirmationEvalResult:
    result = ConfirmationEvalResult()
    write_scope = ctx.operation_scope or ""

    for rule, enabled in rules:
        rid = rule["id"]
        action = rule["action"]

        if action == "force_confirm" and not enabled:
            if ctx.scenario_key in rule["scenarios"] and "改变持仓、委托或余额" in write_scope:
                result.force_confirm_disabled_for_write = True

        if not enabled:
            continue

        if not _rule_matches(rule, ctx):
            continue

        result.matched_rules.append(
            MatchedConfirmationRule(rule_id=rid, title=rule["title"], action=action)
        )
        if action == "second_confirm":
            result.requires_second_confirm = True
        elif action == "otp_confirm":
            result.requires_otp_confirm = True
        elif action == "block_auto_execute":
            result.block_auto_execute = True

    return result


async def evaluate_confirmation_for_trade(
    session: AsyncSession,
    *,
    scenario_id: str,
    nominal_usdt: Decimal | None = None,
    leverage: Decimal | None = None,
    operation_scope: str | None = None,
) -> ConfirmationEvalResult:
    scenario_key = scenario_key_for_scenario_id(scenario_id)
    if scenario_key is None:
        return ConfirmationEvalResult()

    scope = operation_scope or build_write_operation_scope(scenario_id)
    ctx = ConfirmationEvalContext(
        scenario_key=scenario_key,
        scenario_id=scenario_id,
        nominal_usdt=nominal_usdt,
        leverage=leverage,
        operation_scope=scope,
    )
    rules = await load_merged_enabled_rules(session)
    return evaluate_confirmation_rules_sync(rules, ctx)


def format_second_confirm_preamble() -> str:
    return "⚠️ 人工确认规则：此为二次确认环节，请再次核对以下参数与风险。\n\n"


def format_otp_confirm_note() -> str:
    return "（OTP 第二因素确认：Phase1 仅提示，完整 OTP 校验待后续迭代。）\n\n"


def format_block_auto_execute_message() -> str:
    return (
        "根据运营配置的人工确认规则，当前操作命中「禁止自动执行」策略，"
        "暂无法通过助手自动落单。请在运营后台调整规则或联系人工处理。"
    )
