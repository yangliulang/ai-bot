"""Evaluate runtime eligibility vs trading binding DB + allowlist."""

from __future__ import annotations

import re
import uuid

from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.agent_runtime import (
    AccessReasonItem,
    AccessReasonsResponse,
    EligibilityEnvelope,
    EvaluateEligibilityRequest,
    utc_now,
)
from chainup_agent.application.admin_access_control import (
    ban_envelope_code,
    fetch_active_ban,
    rollout_whitelist_enforced,
    user_in_rollout_whitelist,
)
from chainup_agent.application.agent_api_binding_confirm import has_telegram_trading_binding
from chainup_agent.application.telegram_bound_chat_allowlist import parse_bound_chat_allowlist_ids
from chainup_agent.infrastructure.persistence.models.agent_instance import AgentInstance
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError

CHANNEL_TELEGRAM = "telegram"


def static_access_reasons() -> AccessReasonsResponse:
    """Stable catalogue for FE copy and ops; codes align AgentManagement enum."""
    pairs: list[tuple[str, str]] = [
        ("AGENT_GLOBAL_OFF", "运行时全局停用（FEATURE / 运维开关）。"),
        ("AGENT_OPS_SUSPENDED", "运营暂停；暂不提供 Agent 对话能力。"),
        ("AGENT_COMPLIANCE_RESTRICTED", "合规限制；暂不开放该区域或用户。"),
        ("AGENT_USER_BLOCKED", "用户被风控或服务侧拉黑。"),
        ("AGENT_REGION_BLOCKED", "地区或渠道策略拦截。"),
        ("AGENT_KYC_REQUIRED", "须完成更高等级 KYC 后才能继续使用。"),
        ("AGENT_KYC_INSUFFICIENT", "认证等级不满足当前能力前置条件。"),
        ("AGENT_ROLLOUT_BLOCKED", "分批发布未放行该用户群体。"),
        ("AGENT_BILLING_BLOCKED", "扣费被拒绝或余额不满足最小扣费。"),
        ("AGENT_MEMBERSHIP_BLOCKED", "会员 / 等级不满足。"),
        ("AGENT_SUBACCOUNT_REQUIRED", "尚未完成 Telegram 与交易账户 API 绑定或子账户未就绪。"),
    ]
    return AccessReasonsResponse(
        reasons=[AccessReasonItem(code=c, summary=s) for c, s in pairs],
    )


def _effective_channel(channel: str | None) -> str:
    c = (channel or "").strip().lower()
    return c if c else CHANNEL_TELEGRAM


async def telegram_user_id_from_exchange_subaccount(
    session: AsyncSession, sub_account_id: str
) -> int | None:
    """Map ``agent_instance.exchange_sub_account_user_id`` → ``telegram_user_id`` (first row)."""
    sub_norm = sub_account_id.strip()
    if not sub_norm:
        return None
    stmt = (
        select(AgentInstance.telegram_user_id)
        .where(AgentInstance.exchange_sub_account_user_id == sub_norm)
        .limit(1)
    )
    res = await session.execute(stmt)
    row = res.first()
    if row is None:
        return None
    return int(row[0])


async def evaluate_eligibility(
    *,
    session: AsyncSession | None,
    settings: Settings,
    body: EvaluateEligibilityRequest,
) -> EligibilityEnvelope:
    now = utc_now()
    decision_id = uuid.uuid4().hex[:24]

    if settings.agent_runtime_global_disabled:
        return EligibilityEnvelope(
            allowed=False,
            code="AGENT_GLOBAL_OFF",
            reason=("Agent 运行时全局停用 （CHAINUP_AGENT_AGENT_RUNTIME_GLOBAL_DISABLED=true）。"),
            evaluated_at=now,
            eligibility_decision_id=decision_id,
            requires_main_site=None,
        )

    if settings.agent_runtime_ops_suspended:
        return EligibilityEnvelope(
            allowed=False,
            code="AGENT_OPS_SUSPENDED",
            reason="运营暂停接入；请稍后重试或联系运维。",
            evaluated_at=now,
            eligibility_decision_id=decision_id,
            requires_main_site=None,
        )

    ch = _effective_channel(body.channel)
    if ch != CHANNEL_TELEGRAM:
        return EligibilityEnvelope(
            allowed=False,
            code="AGENT_ROLLOUT_BLOCKED",
            reason=f"暂不支持的渠道：{body.channel}",
            evaluated_at=now,
            eligibility_decision_id=decision_id,
            requires_main_site=None,
        )

    uid_raw = (body.user_id or "").strip()
    sub_raw = (body.sub_account_id or "").strip()

    telegram_user_id: int
    if sub_raw:
        if session is None:
            raise AppError(
                code="VALIDATION_ERROR",
                message="使用 subAccountId 须具备数据库绑定数据；当前请求无会话。",
                status_code=422,
                details={"field": "subAccountId"},
            )
        try:
            tid = await telegram_user_id_from_exchange_subaccount(session, sub_raw)
        except OperationalError:
            tid = None
        if tid is None:
            raise AppError(
                code="VALIDATION_ERROR",
                message=(
                    "未找到与该 subAccountId 对应的 Agent 绑定实例。请确认已在 H5 完成交易 API 绑定；"
                    "探测身份时请使用 Body 字段 subAccountId 传子账户号，userId 仅传 Telegram tg_id（二者不可混用）。"
                ),
                status_code=422,
                details={"field": "subAccountId", "subAccountId": sub_raw},
            )
        telegram_user_id = tid
        if uid_raw:
            if not uid_raw.isdigit():
                raise AppError(
                    code="VALIDATION_ERROR",
                    message="与 subAccountId 同时传入的 userId 须为 Telegram tg_id 数值串。",
                    status_code=422,
                    details={"field": "userId"},
                )
            if int(uid_raw) != telegram_user_id:
                raise AppError(
                    code="VALIDATION_ERROR",
                    message="subAccountId 对应的 Telegram 用户与 userId 不一致；请只传 subAccountId 或只传 userId。",
                    status_code=422,
                    details={
                        "userId": uid_raw,
                        "resolvedTelegramUserId": str(telegram_user_id),
                    },
                )
    else:
        if not uid_raw.isdigit():
            raise AppError(
                code="VALIDATION_ERROR",
                message="Telegram 渠道下 userId 必须为数值字符串（Telegram tg_id，非交易所子账户号）。",
                status_code=422,
                details={"field": "userId"},
            )
        telegram_user_id = int(uid_raw)

    ban_row = None
    if session is not None:
        try:
            ban_row = await fetch_active_ban(session, user_uid=str(telegram_user_id))
        except OperationalError:
            ban_row = None
    if ban_row is not None:
        code = ban_envelope_code(ban_row)
        summary_core = next(
            (r.summary for r in static_access_reasons().reasons if r.code == code),
            code,
        )
        return EligibilityEnvelope(
            allowed=False,
            code=code,
            reason=f"{summary_core}（reasonCode={ban_row.reason_code}）",
            evaluated_at=now,
            eligibility_decision_id=decision_id,
            requires_main_site=None,
        )

    allow = parse_bound_chat_allowlist_ids(settings.telegram_bound_chat_allowlist)
    if telegram_user_id in allow:
        caps = {
            "telegramUserId": str(telegram_user_id),
            "bindingVerified": False,
            "boundChatAllowlist": True,
        }
        return EligibilityEnvelope(
            allowed=True,
            locale="zh-Hans",
            capabilities=caps,
            evaluated_at=now,
            eligibility_decision_id=decision_id,
            requires_main_site=False,
        )

    tid_chat = body.telegram_chat_id
    if tid_chat is not None and tid_chat in allow:
        caps = {
            "telegramUserId": str(telegram_user_id),
            "telegramChatId": str(tid_chat),
            "bindingVerified": False,
            "boundChatAllowlist": True,
        }
        return EligibilityEnvelope(
            allowed=True,
            locale="zh-Hans",
            capabilities=caps,
            evaluated_at=now,
            eligibility_decision_id=decision_id,
            requires_main_site=False,
        )

    if session is not None:
        try:
            enforced = await rollout_whitelist_enforced(session)
            if enforced and not await user_in_rollout_whitelist(session, user_uid=str(telegram_user_id)):
                return EligibilityEnvelope(
                    allowed=False,
                    code="AGENT_ROLLOUT_BLOCKED",
                    reason="当前为灰度放行策略：仅白名单内用户可使用；请联系运营添加。",
                    evaluated_at=now,
                    eligibility_decision_id=decision_id,
                    requires_main_site=None,
                )
        except OperationalError:
            pass

    bound = False
    if session is not None:
        try:
            bound = await has_telegram_trading_binding(session, telegram_user_id)
        except OperationalError:
            bound = False

    if not bound:
        return EligibilityEnvelope(
            allowed=False,
            code="AGENT_SUBACCOUNT_REQUIRED",
            reason="请先完成 Deeplink/H5 上的交易 API 绑定，再使用需要账户身份的 Agent 能力。",
            evaluated_at=now,
            eligibility_decision_id=decision_id,
            requires_main_site=True,
        )

    caps = {
        "telegramUserId": str(telegram_user_id),
        "bindingVerified": True,
        "boundChatAllowlist": False,
        "scenarioContext": {"requestedScenarioId": body.scenario_id},
    }

    return EligibilityEnvelope(
        allowed=True,
        locale="zh-Hans",
        capabilities=caps,
        evaluated_at=now,
        eligibility_decision_id=decision_id,
        requires_main_site=False,
    )


_RE_NUM = re.compile(r"[\d,，.]+")


def strip_amount_hint(text: str) -> str:
    """Cheap noise strip for deterministic keyword intents (Telegram snippets)."""
    t = text.lower().strip()
    t = _RE_NUM.sub(" ", t)
    return " ".join(t.split())


def recognize_intent_keyword(text: str) -> tuple[str | None, float, list[tuple[str, float]]]:
    """
    Minimal CN keyword router for Phase 1 demos (replace with LLM later).

    Returns (best_scenario_or_none, confidence, sorted_candidates descending).
    """
    raw = text.strip()
    if not raw:
        return None, 0.0, []

    s = strip_amount_hint(raw)
    scores: dict[str, float] = {}

    def bump(sid: str, w: float) -> None:
        scores[sid] = scores.get(sid, 0.0) + w

    # Wealth / OTC read (before generic 余额 to win on「理财余额」)
    if "理财" in raw or "固收" in raw or re.search(r"\botc\b", s):
        bump("wealth.holdings_read", 0.93)

    # Read paths
    if any(k in s for k in ("盘口", "买卖盘", "订单簿", "挂单盘", "orderbook")) or re.search(
        r"\bdepth\b", s
    ):
        bump("read.market.depth", 0.92)
    if any(
        k in s
        for k in (
            "近期成交",
            "最新成交",
            "逐笔成交",
            "最近成交",
            "public trades",
            "recent trades",
        )
    ):
        bump("read.market.trades", 0.91)
    if "理财" not in raw:
        balance_kw = (
            any(k in raw for k in ("余额", "资产", "钱"))
            or "balance" in s
            or (
                "仓" in raw
                and "全仓" not in raw
                and "逐仓" not in raw
                and "开仓" not in raw
                and "平仓" not in raw
            )
        )
        if balance_kw:
            bump("read.account.balance", 0.85)
        if any(
            p in raw
            for p in (
                "账户余额",
                "帐户余额",
                "我的余额",
                "查余额",
                "查看余额",
                "查下余额",
                "看下余额",
                "余额查询",
                "资产查询",
                "查询资产",
                "查看资产",
            )
        ):
            bump("read.account.balance", 0.08)

    cancel_kw = (
        any(k in raw for k in ("撤单", "撤销委托", "取消订单", "取消委托"))
        or "撤销" in raw
        or bool(re.search(r"\bcancel\s+(?:the\s+)?order\b", s))
    )
    open_ord_kw = any(
        k in raw
        for k in ("当前委托", "未完成订单", "挂单列表", "我的挂单", "未成交订单")
    ) or bool(re.search(r"\bopen\s+orders?\b", s))
    limit_ctx = any(k in raw for k in ("限价", "挂单")) or (
        "委托" in raw and not open_ord_kw and not cancel_kw
    )

    # 「价格」单独出现时更像查行情；限价上下文里「价格」是槽位而非 ticker。
    if any(k in s for k in ("行情", "价格", "涨跌幅", "k线", "ticker")) and not limit_ctx:
        bump("read.market.ticker", 0.9)

    fut_ctx = any(
        k in raw
        for k in ("合约", "永续", "期货", "交割", "开空", "开多", "平仓", "币本位")
    ) or bool(re.search(r"(?i)u本位", raw))
    spot_market = any(k in s for k in ("闪兑", "市价", "市价单"))
    cond_ctx = any(
        k in raw
        for k in ("条件单", "止盈止损", "止盈单", "止损单", "计划委托", "触发价")
    )

    cond_read_kw = open_ord_kw or any(
        k in raw for k in ("查询条件", "条件单列表", "我的条件单", "条件单列表")
    ) or ("查询" in raw and "条件" in raw)
    # Automation / conditional orders（路线图 §2.5）
    if cond_ctx and cond_read_kw and not cancel_kw:
        bump("automation.condition_orders_read", 0.62)
    if cond_ctx and cancel_kw and not fut_ctx:
        bump("automation.condition_order_cancel", 0.68)
    if cond_ctx and not cancel_kw and not cond_read_kw:
        bump("automation.condition_order", 0.58 if not fut_ctx else 0.68)

    # Margin cross（路线图 §2.4 — stub）
    margin_keyword_strong = any(k in raw for k in ("全仓杠杆", "逐仓杠杆", "杠杆市价"))
    margin_limit_kw = margin_keyword_strong and limit_ctx
    if margin_limit_kw:
        bump("margin.cross.limit_order", 0.62)
    elif margin_keyword_strong:
        bump("margin.cross.market_order", 0.6)

    # Spot vs futures trade paths（路线图 §2.1 vs §2.3）
    if fut_ctx:
        if cancel_kw:
            if cond_ctx:
                bump("automation.condition_order_cancel", 0.7)
            else:
                bump("trade.futures.cancel_order", 0.66)
        if cond_read_kw and cond_ctx and not cancel_kw:
            bump("automation.condition_orders_read", 0.66)
        if limit_ctx:
            bump("trade.futures.limit_order", 0.65)
        elif spot_market:
            bump("trade.futures.market_order", 0.62)
        else:
            bump("trade.futures.market_order", 0.45)
    else:
        if not margin_keyword_strong:
            if spot_market:
                bump("trade.spot.flash_convert", 0.55)
            if limit_ctx:
                bump("trade.spot.limit_order", 0.5)
        if cancel_kw:
            bump("trade.spot.cancel_order", 0.62)
        amend_kw = any(
            k in raw
            for k in ("改单", "改价", "修改挂单", "修改限价", "修改委托")
        ) and not cancel_kw
        if amend_kw:
            bump("trade.spot.amend_limit_order", 0.72)
        if re.search(r"(?i)\boco\b", raw) or "括号单" in raw:
            bump("trade.spot.oco", 0.64)
        if re.search(r"(?i)bracket", raw) or ("括号" in raw and "括号单" not in raw):
            bump("trade.spot.bracket", 0.6)
        if open_ord_kw and not cancel_kw:
            bump("trade.spot.open_orders", 0.56)
        if "杠杆" in raw and spot_market and not margin_keyword_strong:
            bump("margin.cross.market_order", 0.52)

    # Default FAQ fall-through
    if not scores:
        return "chat.faq", 0.35, [("chat.faq", 0.35)]

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best_sid, best = ranked[0]
    second = ranked[1][1] if len(ranked) > 1 else 0.0
    confidence = min(1.0, best / (best + second + 1e-6))

    cand = ranked[:5]
    return best_sid, float(confidence), cand
