"""Admin prompt safety — overview, intercepts, governance summaries (ai.prompt-safety)."""

from __future__ import annotations

import json
import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.admin_prompt_safety import (
    RuntimeSafetyGovernanceRow,
    SafetyBlocklistOut,
    SafetyBlocklistRuleOut,
    SafetyInterceptItem,
    SafetyInterceptListResponse,
    SafetyOverviewOut,
    SessionSafetyPolicyItem,
    SessionSafetyPolicyResponse,
    ToolSafetyPolicyRow,
    ToolSafetyPolicyResponse,
)
from chainup_agent.api.schemas.prompt_management import PromptPackSummaryOut
from chainup_agent.application.admin_confirmation_rules import list_confirmation_rules
from chainup_agent.application.admin_prompt_packs import list_prompt_packs, pack_to_summary_dict
from chainup_agent.application.agent_prompt_assembly import PLATFORM_SAFETY_SCENARIO_ID
from chainup_agent.application.prompt_safety_phrase_validation import (
    DEFAULT_SAFETY_PHRASE_SCAN_SCOPE,
    SAFETY_PHRASE_BLOCKLIST_REVISION,
    blocklist_rules_for_api,
)
from chainup_agent.core.config import get_settings
from chainup_agent.infrastructure.persistence.models.admin_safety_intercept_log import (
    AdminSafetyInterceptLog,
)
from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution
from chainup_agent.infrastructure.persistence.models.agent_execution_event import (
    AgentExecutionEvent,
)


async def log_prompt_publish_blocked(
    session: AsyncSession,
    *,
    prompt_pack_id: str,
    matched_rule_id: str | None,
    reason: str,
) -> None:
    row = AdminSafetyInterceptLog(
        intercept_id=f"int_{uuid.uuid4().hex[:22]}",
        category="prompt",
        scenario_label=f"Prompt 包 · {prompt_pack_id}",
        kind_label="Publish 阻断",
        reason=reason[:2000],
        subject=prompt_pack_id[:256],
        matched_rule_id=matched_rule_id,
        execution_id=None,
    )
    session.add(row)
    await session.flush()


async def get_safety_blocklist() -> SafetyBlocklistOut:
    return SafetyBlocklistOut(
        safetyPhraseBlocklistRevision=SAFETY_PHRASE_BLOCKLIST_REVISION,
        safetyPhraseScanScopeDefault=DEFAULT_SAFETY_PHRASE_SCAN_SCOPE,
        rules=[SafetyBlocklistRuleOut.model_validate(r) for r in blocklist_rules_for_api()],
    )


async def get_safety_overview(session: AsyncSession) -> SafetyOverviewOut:
    settings = get_settings()
    safety_rows = await list_prompt_packs(session, prompt_pack_type="SAFETY")
    published = [r for r in safety_rows if (r.lifecycle or "").upper() == "PUBLISHED"]
    platform = next(
        (
            r
            for r in published
            if (r.scenario_id or "").strip() == PLATFORM_SAFETY_SCENARIO_ID
        ),
        published[0] if published else None,
    )
    platform_out = (
        PromptPackSummaryOut.model_validate(pack_to_summary_dict(platform))
        if platform
        else None
    )
    rules = await list_confirmation_rules(session)
    enabled_rules = sum(1 for i in rules.items if i.enabled)
    return SafetyOverviewOut(
        safetyPhraseBlocklistRevision=SAFETY_PHRASE_BLOCKLIST_REVISION,
        safetyPhraseScanScopeDefault=DEFAULT_SAFETY_PHRASE_SCAN_SCOPE,
        platformSafetyPack=platform_out,
        safetyPromptPackCount=len(safety_rows),
        publishedSafetyPackCount=len(published),
        enabledConfirmationRulesCount=enabled_rules,
        globalAgentSwitchOn=not settings.agent_runtime_global_disabled,
        opsSuspended=settings.agent_runtime_ops_suspended,
    )


def _payload_dict(raw: str) -> dict:
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        return {}


def _event_to_intercept(
    ev: AgentExecutionEvent,
    *,
    exec_row: AgentExecution | None,
) -> SafetyInterceptItem | None:
    payload = _payload_dict(ev.payload_json)
    sid = payload.get("scenarioId") or (exec_row.scenario_id if exec_row else None) or "—"
    sk = (ev.step_kind or "").strip()
    outcome = (ev.outcome or "").strip().lower()
    trigger = str(payload.get("transitionTrigger") or "")

    if sk == "confirm_gate" and outcome == "failure":
        rules = payload.get("confirmationRules") if isinstance(payload.get("confirmationRules"), dict) else {}
        rule_ids = rules.get("matchedRuleIds") if isinstance(rules.get("matchedRuleIds"), list) else []
        return SafetyInterceptItem(
            id=ev.id,
            ts=ev.created_at,
            category="runtime",
            scenarioLabel=str(sid),
            kindLabel="人工确认规则",
            reason="命中「禁止自动执行」或同类运行时护栏",
            subject=ev.user_id,
            executionId=ev.execution_id,
            matchedRuleId=str(rule_ids[0]) if rule_ids else None,
        )

    if sk == "band_check" and outcome == "failure":
        return SafetyInterceptItem(
            id=ev.id,
            ts=ev.created_at,
            category="runtime",
            scenarioLabel=str(sid),
            kindLabel="限价偏离",
            reason=str(payload.get("appErrorCode") or "价格偏离带校验未通过"),
            subject=ev.user_id,
            executionId=ev.execution_id,
        )

    if sk == "routing.read.failed" or trigger.endswith(".failed"):
        return SafetyInterceptItem(
            id=ev.id,
            ts=ev.created_at,
            category="tool",
            scenarioLabel=str(sid),
            kindLabel="只读路由失败",
            reason=str(payload.get("appErrorCode") or payload.get("note") or "exchange read blocked"),
            subject=ev.user_id,
            executionId=ev.execution_id,
        )

    if "routing.read.failed" in trigger or payload.get("appErrorCode"):
        return SafetyInterceptItem(
            id=ev.id,
            ts=ev.created_at,
            category="tool",
            scenarioLabel=str(sid),
            kindLabel="工具/路由",
            reason=str(payload.get("appErrorCode") or trigger or "intercepted"),
            subject=ev.user_id,
            executionId=ev.execution_id,
        )

    return None


async def list_safety_intercepts(
    session: AsyncSession,
    *,
    category: str | None,
    limit: int,
    offset: int,
) -> SafetyInterceptListResponse:
    cat = category.strip().lower() if category and category.strip() else None
    if cat and cat not in ("runtime", "prompt", "tool", "session"):
        cat = None

    items: list[SafetyInterceptItem] = []

    log_stmt = select(AdminSafetyInterceptLog).order_by(AdminSafetyInterceptLog.created_at.desc())
    if cat:
        log_stmt = log_stmt.where(AdminSafetyInterceptLog.category == cat)
    log_rows = list((await session.scalars(log_stmt.limit(limit + offset))).all())

    for row in log_rows:
        items.append(
            SafetyInterceptItem(
                id=row.intercept_id,
                ts=row.created_at,
                category=row.category,  # type: ignore[arg-type]
                scenarioLabel=row.scenario_label,
                kindLabel=row.kind_label,
                reason=row.reason,
                subject=row.subject,
                executionId=row.execution_id,
                matchedRuleId=row.matched_rule_id,
            )
        )

    if not cat or cat in ("runtime", "tool"):
        ev_stmt = (
            select(AgentExecutionEvent, AgentExecution)
            .join(
                AgentExecution,
                AgentExecution.execution_id == AgentExecutionEvent.execution_id,
                isouter=True,
            )
            .where(
                or_(
                    (AgentExecutionEvent.step_kind == "confirm_gate")
                    & (AgentExecutionEvent.outcome == "failure"),
                    (AgentExecutionEvent.step_kind == "band_check")
                    & (AgentExecutionEvent.outcome == "failure"),
                    AgentExecutionEvent.step_kind == "routing.read.failed",
                    AgentExecutionEvent.event_type.like("%routing.read.failed%"),
                )
            )
            .order_by(AgentExecutionEvent.created_at.desc())
            .limit(max(limit + offset, 50))
        )
        ev_res = await session.execute(ev_stmt)
        for ev, ex in ev_res.all():
            mapped = _event_to_intercept(ev, exec_row=ex)
            if mapped is None:
                continue
            if cat and mapped.category != cat:
                continue
            items.append(mapped)

    items.sort(key=lambda x: x.ts, reverse=True)
    total = len(items)
    page = items[offset : offset + limit]
    return SafetyInterceptListResponse(items=page, total=total)


async def get_runtime_governance_summary(session: AsyncSession) -> list[RuntimeSafetyGovernanceRow]:
    rules = await list_confirmation_rules(session)
    enabled_high = sum(
        1 for i in rules.items if i.enabled and i.risk_level == "high"
    )
    block_auto = sum(
        1 for i in rules.items if i.enabled and i.action == "block_auto_execute"
    )
    settings = get_settings()
    return [
        RuntimeSafetyGovernanceRow(
            key="r1",
            name="高风险交易与资金动作",
            riskLevelLabel="高",
            autoExecSummary="高风险写路径默认关闭自动落单",
            confirmSummary=f"已启用人工确认规则 {sum(1 for i in rules.items if i.enabled)} 条（高 {enabled_high}）",
            breakerSummary="连续失败则停编并排障提示",
            hrefKind="confirmation",
        ),
        RuntimeSafetyGovernanceRow(
            key="r2",
            name="越权与非法委托",
            riskLevelLabel="高",
            autoExecSummary="命中即拒答，不进入下单链路",
            confirmSummary="不适用（已拦截）",
            breakerSummary="同意图短窗重复请求合并告警",
            hrefKind="routing",
        ),
        RuntimeSafetyGovernanceRow(
            key="r3",
            name="杠杆与名义限额",
            riskLevelLabel="高",
            autoExecSummary="超限前须人工确认或拆分委托",
            confirmSummary="超额/高杠杆走二次确认（见确认规则）",
            breakerSummary="超阈自动驳回并记拦截流水",
            hrefKind="policy",
        ),
        RuntimeSafetyGovernanceRow(
            key="r4",
            name="自动执行熔断",
            riskLevelLabel="中",
            autoExecSummary=f"禁止自动执行规则 {block_auto} 条已启用",
            confirmSummary="与上行规则联动",
            breakerSummary=(
                "运维暂停已开"
                if settings.agent_runtime_ops_suspended
                else "全局闸 "
                + ("关闭" if settings.agent_runtime_global_disabled else "开启")
            ),
            hrefKind="policy",
        ),
    ]


def get_tool_safety_policies() -> ToolSafetyPolicyResponse:
    return ToolSafetyPolicyResponse(
        items=[
            ToolSafetyPolicyRow(
                key="t1",
                toolPattern="exchange.withdraw* · 提现类",
                policy="deny",
                enforcementMode="default_deny",
                note="Phase1 未登记提现写工具；禁止智能体直连提现写操作",
            ),
            ToolSafetyPolicyRow(
                key="t2",
                toolPattern="read.* · 交易所只读",
                policy="allowlist",
                enforcementMode="allowlist_only",
                note="仅 exchange_tool_schema_registry 内 read.* 工具可注入 LLM 上下文",
            ),
            ToolSafetyPolicyRow(
                key="t3",
                toolPattern="trade.spot.* · 现货写",
                policy="shadow",
                enforcementMode="approve_then_allow",
                note="写路径须 Type-A 确认 + 人工确认规则评估；不经 LLM tool call 直写",
            ),
        ]
    )


def get_session_safety_policy() -> SessionSafetyPolicyResponse:
    return SessionSafetyPolicyResponse(
        items=[
            SessionSafetyPolicyItem(
                key="s1",
                label="高频意图限速",
                summary="同会话短窗口内重复高风险意图合并提示（Telegram 轮次级）",
                status="enabled",
            ),
            SessionSafetyPolicyItem(
                key="s2",
                label="异常行为检测",
                summary="短时多品种扫单、异常撤单比 — 标记并降级自动执行（Phase1 部分）",
                status="warning",
            ),
            SessionSafetyPolicyItem(
                key="s3",
                label="会话维度熔断",
                summary="连续拒答或工具失败率异常 — 临时收紧工具白名单（规划中）",
                status="info",
            ),
        ]
    )


async def load_full_pack_scan_extra_text(session: AsyncSession) -> str:
    """FULL_PACK scope: include published platform SYSTEM + SAFETY bodies."""
    parts: list[str] = []
    for ptype in ("SYSTEM", "SAFETY"):
        rows = await list_prompt_packs(session, prompt_pack_type=ptype, lifecycle="PUBLISHED")
        if not rows and ptype == "SYSTEM":
            rows = await list_prompt_packs(session, prompt_pack_type=ptype, lifecycle="LOCKED")
        for row in rows[:3]:
            try:
                msgs = json.loads(row.messages_json or "[]")
            except json.JSONDecodeError:
                continue
            if isinstance(msgs, list):
                for m in msgs:
                    if isinstance(m, dict) and isinstance(m.get("content"), str):
                        parts.append(m["content"])
    return "\n".join(parts)
