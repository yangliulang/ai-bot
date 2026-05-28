"""
Layered intent recognition: NLU draft (keyword MVP) + deterministic policy / router.

Aligns with product agent-orchestration (FR-AO02 single primary scenario, registry checks,
trade-track mutex). LLM structured NLU can replace ``build_nlu_draft`` later without
changing the policy surface.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.agent_runtime import (
    IntentCandidate,
    IntentNluDraft,
    IntentPolicyPlan,
    IntentRecognizeResponse,
    IntentScenarioCandidateDraft,
)
from chainup_agent.application.agent_access_evaluate import recognize_intent_keyword
from chainup_agent.application.orchestration_steps import (
    ORCHESTRATION_VERSION_INTENT,
    append_intent_orchestration_step,
)
from chainup_agent.application.agent_scenario_catalog import scenario_readiness_map
from chainup_agent.application.effective_locale import normalize_effective_locale
from chainup_agent.application.telegram_symbol_extract import extract_symbol_for_ticker
from chainup_agent.application.memory_session_store import (
    get_pending_clarify_slots,
    merge_clarify_slot_dict,
    remember_pending_clarify,
)
from chainup_agent.application.trade_slot_clarify import (
    enrich_trade_slots_from_text,
    evaluate_trade_write_clarify,
)
from chainup_agent.core.config import Settings

logger = logging.getLogger(__name__)


def resolve_effective_intent_nlu_use_llm(
    settings: Settings,
    merged_defaults: dict[str, Any] | None = None,
) -> bool:
    """
    Effective intent NLU LLM policy: env ``CHAINUP_AGENT_INTENT_NLU_USE_LLM=true`` wins;
    else ``gateway_defaults.intentNluUseLlm`` (default false when unset).
    """
    if settings.intent_nlu_use_llm:
        return True
    if merged_defaults and merged_defaults.get("intentNluUseLlm") is True:
        return True
    return False


def enrich_draft_slots_from_text(text: str, draft: IntentNluDraft) -> IntentNluDraft:
    """Fill missing symbol/side/quantity/price from deterministic extractors (merge with NLU)."""
    slots = dict(draft.slots)
    if "symbol" not in slots:
        s = extract_symbol_for_ticker(text)
        if s:
            slots["symbol"] = s
    if "side" not in slots:
        s2 = _extract_side(text) or _extract_margin_side(text)
        if s2:
            slots["side"] = s2
    if "price" not in slots:
        ap = _extract_amend_new_price(text)
        if ap:
            slots["price"] = ap
        elif draft.order_type_hint == "limit":
            p = _extract_limit_price_raw(text)
            if p:
                slots["price"] = p
    if "timeInForce" not in slots and draft.order_type_hint == "limit":
        tif = _extract_time_in_force_slot(text)
        if tif:
            slots["timeInForce"] = tif
    if "quantity" not in slots:
        q = _extract_quantity_from_labeled(text) or _extract_quantity_preferred(text)
        if q:
            slots["quantity"] = q
    slots = enrich_trade_slots_from_text(text, slots)
    if "orderId" not in slots:
        oid = _extract_order_id_from_text(text)
        if oid:
            slots["orderId"] = oid
    if "openClose" not in slots:
        oc = _extract_open_close(text)
        if oc:
            slots["openClose"] = oc
    if "triggerPrice" not in slots:
        tp = _extract_trigger_price_raw(text)
        if tp:
            slots["triggerPrice"] = tp
    if "triggerType" not in slots:
        tt = _extract_trigger_type(text)
        if tt:
            slots["triggerType"] = tt
    return draft.model_copy(update={"slots": slots})


def prune_llm_slots_without_text_evidence(text: str, draft: IntentNluDraft) -> IntentNluDraft:
    """Drop LLM-invented trade slots not grounded in utterance extractors (禁止猜价猜量)."""
    if draft.source != "llm_structured_v1":
        return draft
    empty = IntentNluDraft(
        source="keyword_v1",
        primary_intent_family=draft.primary_intent_family,
        scenario_id_candidates=[],
        slots={},
        order_type_hint=draft.order_type_hint,
        clarify_hints=[],
    )
    grounded = enrich_draft_slots_from_text(text, empty)
    grounded_keys = set(grounded.slots.keys())
    slots = dict(draft.slots)
    for key in list(slots.keys()):
        if key in (
            "symbol",
            "side",
            "quantity",
            "quoteQty",
            "price",
            "orderId",
            "triggerPrice",
            "triggerType",
            "notionalMode",
            "balancePercent",
            "quoteNotionalFrozen",
        ):
            if key not in grounded_keys:
                slots.pop(key, None)
    if slots == draft.slots:
        return draft
    return draft.model_copy(update={"slots": slots})


_TRADE_SPOT_EXEC = frozenset(
    {
        "trade.spot.flash_convert",
        "trade.spot.limit_order",
        "trade.spot.cancel_order",
        "trade.spot.amend_limit_order",
    }
)


def _intent_family(scenario_id: str | None) -> str:
    if scenario_id is None:
        return "unknown"
    if scenario_id == "chat.faq":
        return "chat"
    if scenario_id.startswith("read."):
        return "portfolio_read"
    if scenario_id.startswith("wealth."):
        return "wealth_read"
    if scenario_id.startswith("trade."):
        return "trade_write"
    if scenario_id.startswith("margin."):
        return "margin_trade"
    if scenario_id.startswith("automation."):
        return "automation"
    return "unknown"


def _order_type_hint(text: str, scenario_id: str | None) -> Literal["market", "limit", "unknown"]:
    s = text.lower()
    if "限价" in text or "挂单" in text or "委托" in text or "limit" in s:
        return "limit"
    if "闪兑" in text or "市价" in text or "市价单" in text:
        return "market"
    if scenario_id == "trade.spot.flash_convert":
        return "market"
    if scenario_id == "trade.spot.limit_order":
        return "limit"
    if scenario_id == "trade.spot.amend_limit_order":
        return "limit"
    if scenario_id == "trade.futures.market_order":
        return "market"
    if scenario_id == "trade.futures.limit_order":
        return "limit"
    if scenario_id == "margin.cross.market_order":
        return "market"
    if scenario_id == "margin.cross.limit_order":
        return "limit"
    if scenario_id == "automation.condition_order":
        if re.search(r"触发后限价|限价触发|触发.{0,6}限价", text):
            return "limit"
        return "market"
    return "unknown"


def _extract_side(text: str) -> str | None:
    if re.search(r"买|买入|做多|\bbuy\b|\blong\b", text, re.IGNORECASE):
        return "BUY"
    if re.search(r"卖|卖出|做空|\bsell\b|\bshort\b", text, re.IGNORECASE):
        return "SELL"
    return None


def _extract_margin_side(text: str) -> str | None:
    if re.search(r"借钱|借款|借币买|借币买入", text):
        return "BUY"
    if re.search(r"卖出还款|还款卖|卖币还款", text):
        return "SELL"
    return None


def _extract_open_close(text: str) -> str | None:
    if re.search(r"平仓|平多|平空|减仓|\bclose\b", text, re.IGNORECASE):
        return "CLOSE"
    if re.search(r"开仓|开多|开空|\bopen\b", text, re.IGNORECASE):
        return "OPEN"
    return None


def _extract_quantity_raw(text: str) -> str | None:
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*([kKkMm million]?(?:枚|个|币)?)?", text)
    if not m:
        return None
    num = m.group(1)
    suf = (m.group(2) or "").strip().lower()
    if suf in ("k", "千"):
        return str(float(num) * 1000)
    if suf in ("m", "million", "百万"):
        return str(float(num) * 1_000_000)
    return num


def _extract_quantity_from_labeled(text: str) -> str | None:
    m = re.search(r"(?:数量|qty)\s*[:：]?\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def _extract_quantity_preferred(text: str) -> str | None:
    m = re.search(r"(?:买|卖)(?:入|出)?\s*(\d+(?:\.\d+)?)", text)
    if m:
        return m.group(1)
    return _extract_quantity_raw(text)


def _extract_limit_price_raw(text: str) -> str | None:
    m = re.search(r"触发价\s*[:：]?\s*(\d+(?:\.\d+)?)", text)
    if m:
        return None
    m = re.search(r"(?:限价|挂单|委托)\s*[:：]?\s*(\d+(?:\.\d+)?)", text)
    if m:
        return m.group(1)
    m = re.search(r"(?:价格|price)\s*[:：]?\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"@\s*(\d+(?:\.\d+)?)", text)
    if m:
        return m.group(1)
    return None


def _extract_time_in_force_slot(text: str) -> str | None:
    u = text.upper()
    for label in ("IOC", "FOK", "GTC"):
        if label in u:
            return label
    return None


def _extract_trigger_price_raw(text: str) -> str | None:
    m = re.search(r"触发价\s*[:：]?\s*(\d+(?:\.\d+)?)", text)
    if m:
        return m.group(1)
    m = re.search(r"触发\s*[:：]?\s*(\d+(?:\.\d+)?)", text)
    if m:
        return m.group(1)
    return None


def _extract_trigger_type(text: str) -> str | None:
    if re.search(r"上涨|涨到|突破|≥|>=|向上|3UP", text, re.IGNORECASE):
        return "3UP"
    if re.search(r"下跌|跌到|跌破|≤|<=|向下|4DOWN", text, re.IGNORECASE):
        return "4DOWN"
    return None


def _extract_amend_new_price(text: str) -> str | None:
    for pat in (
        r"新价\s*[:：]?\s*(\d+(?:\.\d+)?)",
        r"改价\s*[:：]?\s*(\d+(?:\.\d+)?)",
        r"改成\s*(\d+(?:\.\d+)?)",
        r"改为\s*(\d+(?:\.\d+)?)",
    ):
        m = re.search(pat, text)
        if m:
            return m.group(1)
    return None


def _extract_order_id_from_text(text: str) -> str | None:
    """Snowflake-style order id or labeled ``orderId`` / 订单号."""
    m = re.search(
        r"(?:订单号|订单\s*id|order\s*id|orderid)\s*[:：#]?\s*(\d{8,30})",
        text,
        re.IGNORECASE,
    )
    if m:
        return m.group(1)
    m = re.search(r"\border\s*#?\s*(\d{8,30})\b", text, re.IGNORECASE)
    if m:
        return m.group(1)
    if re.search(r"撤单|撤销|取消(?:订单|委托)", text):
        m = re.search(r"\b(\d{12,30})\b", text)
        if m:
            return m.group(1)
    if re.search(r"改单|改价|修改挂单|修改限价|修改委托", text):
        m = re.search(r"\b(\d{12,30})\b", text)
        if m:
            return m.group(1)
    return None


def _trade_track_conflict_text(text: str) -> bool:
    open_ord = any(
        k in text for k in ("当前委托", "未完成订单", "挂单列表", "我的挂单", "未成交订单")
    )
    cancel_ctx = "撤单" in text or "撤销" in text
    has_limit = ("限价" in text or "挂单" in text or "委托" in text) and not open_ord and not cancel_ctx
    has_market = "闪兑" in text or "市价" in text or "市价单" in text
    return has_limit and has_market


def _prefer_spot_flash_on_market_language(
    text: str,
    best: str | None,
    ranked: list[tuple[str, float]],
) -> tuple[str | None, list[tuple[str, float]]]:
    """
    When the user explicitly asks for spot *market* (市价/闪兑) but NLU (e.g. LLM)
    returns ``trade.spot.limit_order``, prefer ``trade.spot.flash_convert`` so Telegram
    can reach CONFIRM_TYPE_A instead of a trade stub.

    Skips coercion if limit-style words (限价/挂单/委托) appear — FR-AO02 / clarify paths
    handle mixed phrasing elsewhere.
    """
    if best != "trade.spot.limit_order":
        return best, ranked
    has_market = "闪兑" in text or "市价" in text or "市价单" in text
    has_limit = "限价" in text or "挂单" in text or "委托" in text
    if not has_market or has_limit:
        return best, ranked

    merged: dict[str, float] = {sid: float(sc) for sid, sc in ranked}
    lim = merged.get("trade.spot.limit_order", 0.0)
    flash = merged.get("trade.spot.flash_convert", 0.0)
    merged["trade.spot.flash_convert"] = max(flash, lim + 0.05, 0.56)
    merged["trade.spot.limit_order"] = min(lim, 0.34)
    new_ranked = sorted(merged.items(), key=lambda kv: kv[1], reverse=True)
    return new_ranked[0][0], new_ranked


def _prefer_read_balance_on_explicit_phrase(
    text: str,
    best: str | None,
    ranked: list[tuple[str, float]],
) -> tuple[str | None, list[tuple[str, float]]]:
    """
    When the user clearly asks for account balance but NLU (e.g. LLM) favors ``chat.faq``,
    promote ``read.account.balance`` ahead of FAQ.
    """
    raw = text.strip()
    if not raw or "理财" in raw or "固收" in raw:
        return best, ranked

    balance_phrases = (
        "账户余额",
        "帐户余额",
        "查余额",
        "查看余额",
        "查下余额",
        "看下余额",
        "我的余额",
        "余额多少",
        "还有多少币",
        "余额查询",
        "资产查询",
        "查询资产",
        "查看资产",
        "资产多少",
        "有多少资产",
        "账户里有多少",
        "帐户里有多少",
        "资金余额",
        "可用余额",
        "账户资金",
        "帐户资金",
    )
    explicit = any(p in raw for p in balance_phrases)
    fuzzy = False
    if not explicit:
        if "余额" in raw and any(
            x in raw for x in ("查", "查看", "查询", "想", "看", "告诉", "显示", "了解")
        ):
            fuzzy = True
        if ("资产" in raw or "仓" in raw) and any(
            x in raw for x in ("多少", "查询", "查看", "看下", "查下", "想", "钱", "余额")
        ):
            fuzzy = True

    if not (explicit or fuzzy):
        return best, ranked

    merged: dict[str, float] = {sid: float(sc) for sid, sc in ranked}
    bal = merged.get("read.account.balance", 0.0)
    chat = merged.get("chat.faq", 0.0)
    top_other = max(
        (sc for sid, sc in merged.items() if sid not in {"read.account.balance", "chat.faq"}),
        default=0.0,
    )

    merged["read.account.balance"] = max(0.93, bal, chat + 0.2, top_other + 0.12)
    if best == "chat.faq" or chat >= 0.82:
        merged["chat.faq"] = min(chat, 0.28)

    new_ranked = sorted(merged.items(), key=lambda kv: kv[1], reverse=True)
    return new_ranked[0][0], new_ranked


def _is_non_spot_trade_track_context(text: str) -> bool:
    """合约 / 杠杆 / 条件单等须走各自 scenario，不得被现货槽位补齐覆盖。"""
    raw = text.strip()
    return bool(
        re.search(
            r"永续|合约|期货|交割|开空|开多|币本位|全仓杠杆|逐仓杠杆|条件单|"
            r"止盈止损|计划委托|触发价",
            raw,
            re.IGNORECASE,
        )
        or re.search(r"(?i)u本位", raw)
    )


def _prefer_trade_on_complete_spot_slots(
    text: str,
    best: str | None,
    ranked: list[tuple[str, float]],
    slots: dict[str, str],
) -> tuple[str | None, list[tuple[str, float]]]:
    """「买入 1 eth」等：槽位已齐但 keyword 误落 chat.faq 时拉回写路径。"""
    if _is_non_spot_trade_track_context(text):
        return best, ranked
    sym = (slots.get("symbol") or "").strip()
    side = (slots.get("side") or "").strip()
    qty = (slots.get("quantity") or slots.get("quoteQty") or "").strip()
    if not sym or not side or not qty:
        return best, ranked
    if not re.search(r"买|卖|买入|卖出|buy|sell", text, re.IGNORECASE):
        return best, ranked

    hint = _order_type_hint(text, best)
    target = (
        "trade.spot.limit_order"
        if hint == "limit"
        else "trade.spot.flash_convert"
    )
    merged: dict[str, float] = {sid: float(sc) for sid, sc in ranked}
    merged[target] = max(merged.get(target, 0.0), 0.88)
    merged["chat.faq"] = min(merged.get("chat.faq", 0.0), 0.25)
    new_ranked = sorted(merged.items(), key=lambda kv: kv[1], reverse=True)
    return new_ranked[0][0], new_ranked


def _prefer_pending_trade_clarify_context(
    text: str,
    best: str | None,
    ranked: list[tuple[str, float]],
    *,
    pending_scenario_id: str | None,
    pending_slots: dict[str, str],
) -> tuple[str | None, list[tuple[str, float]]]:
    """澄清续轮：「闪兑」「当前市价」等须延续 pending 写单，不得落 read.market.ticker。"""
    from chainup_agent.application.clarify_phrase_slots import (
        merge_clarify_phrase_slots,
        resolve_spot_trade_scenario_from_slots,
    )

    pend = (pending_scenario_id or "").strip()
    if not pend.startswith("trade."):
        return best, ranked
    merged_slots = merge_clarify_phrase_slots(text, pending_slots)
    if not (merged_slots.get("symbol") or "").strip():
        return best, ranked

    target = resolve_spot_trade_scenario_from_slots(merged_slots) or pend
    if target not in ("trade.spot.flash_convert", "trade.spot.limit_order"):
        if pend in ("trade.spot.flash_convert", "trade.spot.limit_order"):
            target = pend

    ranked_map: dict[str, float] = {sid: float(sc) for sid, sc in ranked}
    ranked_map[target] = max(ranked_map.get(target, 0.0), 0.93)
    if "市价" in text or merge_clarify_phrase_slots(text, {}).get("tradeMode"):
        ranked_map["read.market.ticker"] = min(ranked_map.get("read.market.ticker", 0.0), 0.15)
        ranked_map["chat.faq"] = min(ranked_map.get("chat.faq", 0.0), 0.2)
    new_ranked = sorted(ranked_map.items(), key=lambda kv: kv[1], reverse=True)
    return new_ranked[0][0], new_ranked


def _prefer_read_followup_with_pending_symbol(
    text: str,
    best: str | None,
    ranked: list[tuple[str, float]],
    *,
    pending_scenario_id: str | None,
    pending_slots: dict[str, str],
) -> tuple[str | None, list[tuple[str, float]]]:
    """Follow-up read turns without re-stating symbol (e.g. 盘面分析 after ticker)."""
    if not pending_slots.get("symbol"):
        return best, ranked
    prev = (pending_scenario_id or "").strip()
    if not prev.startswith("read."):
        return best, ranked
    raw = text.strip()
    if not raw or extract_symbol_for_ticker(raw):
        return best, ranked

    target = prev
    if any(k in raw for k in ("深度", "盘口", "订单簿", "盘面", "挂单")):
        target = "read.market.depth"
    elif any(k in raw for k in ("成交", "明细", "逐笔")):
        target = "read.market.trades"
    elif any(k in raw for k in ("价格", "行情", "多少钱", "涨跌", "报价")):
        target = "read.market.ticker"
    elif any(k in raw for k in ("分析", "继续", "再看", "接着")):
        target = (
            "read.market.depth"
            if any(k in raw for k in ("深度", "盘面", "盘口"))
            else prev
        )

    merged: dict[str, float] = {sid: float(sc) for sid, sc in ranked}
    boost = min(1.0, max(0.9, merged.get(prev, 0.0) + 0.15))
    merged[target] = max(merged.get(target, 0.0), boost)
    new_ranked = sorted(merged.items(), key=lambda kv: kv[1], reverse=True)
    return new_ranked[0][0], new_ranked


def _clamp_ranked_scores(ranked: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """IntentCandidate.score must be in [0, 1]; boosts must not raise ValidationError."""
    return [(sid, min(1.0, max(0.0, float(sc)))) for sid, sc in ranked]


def _fr_ao02_score_ambiguous(ranked: list[tuple[str, float]]) -> bool:
    if len(ranked) < 2:
        return False
    top, second = ranked[0][1], ranked[1][1]
    if top < 0.34:
        return False
    return (top - second) < 0.11


def _fr_ao02_trade_pair_ambiguous(ranked: list[tuple[str, float]]) -> bool:
    if len(ranked) < 2:
        return False
    a, b = ranked[0][0], ranked[1][0]
    return a in _TRADE_SPOT_EXEC and b in _TRADE_SPOT_EXEC and ranked[1][1] >= 0.38


def build_nlu_draft_keyword_v1(
    text: str,
    *,
    best_sid: str | None,
    ranked: list[tuple[str, float]],
    previous_scenario_id: str | None = None,
) -> IntentNluDraft:
    """Understanding layer MVP: keyword router + light slots (regex / symbol extract)."""
    cands = [
        IntentScenarioCandidateDraft(scenario_id=sid, confidence=float(score))
        for sid, score in ranked
    ]
    eff_best = best_sid

    slots: dict[str, str | None] = {}
    sym = extract_symbol_for_ticker(text)
    if sym:
        slots["symbol"] = sym
    side = _extract_side(text)
    if side:
        slots["side"] = side
    qty = _extract_quantity_from_labeled(text) or _extract_quantity_preferred(text)
    if qty:
        slots["quantity"] = qty

    clarify: list[str] = []
    if previous_scenario_id and eff_best and previous_scenario_id != eff_best:
        clarify.append("previousScenarioId_differs_from_keyword_best")

    return IntentNluDraft(
        source="keyword_v1",
        primary_intent_family=_intent_family(eff_best),
        scenario_id_candidates=cands,
        slots={k: v for k, v in slots.items() if v},
        order_type_hint=_order_type_hint(text, eff_best),
        clarify_hints=clarify,
    )


def _amend_slots_complete(slots: dict[str, str]) -> bool:
    if not slots.get("symbol") or not slots.get("orderId"):
        return False
    return bool(slots.get("price") or slots.get("quantity"))


def apply_intent_policy(
    *,
    settings: Settings,
    text: str,
    draft: IntentNluDraft,
    ranked: list[tuple[str, float]],
    best_sid: str | None,
) -> tuple[IntentPolicyPlan, list[IntentCandidate], str | None, float]:
    """
    Deterministic router: registry, feature knobs, FR-AO02, slot checks.
    Returns (plan, candidates for API, resolved scenario_id, confidence).
    """
    registry = scenario_readiness_map()
    policy_codes: list[str] = []

    ranked = list(ranked)
    if not ranked and best_sid:
        ranked = [(best_sid, 1.0)]

    if best_sid is None:
        best_sid = ranked[0][0] if ranked else None

    def _candidates_from_ranked() -> list[IntentCandidate]:
        return [IntentCandidate(scenario_id=s, score=float(x)) for s, x in ranked[:8]]

    # --- Unregistered (forward-defence if NLU ever emits unknown ids) ---
    if best_sid and best_sid not in registry:
        plan = IntentPolicyPlan(
            next_step="UNKNOWN",
            resolved_scenario_id=None,
            clarify=["scenarioId_not_in_registry"],
            policy_codes=["REGISTRY_UNKNOWN_SCENARIO"],
            note="scenarioId 未在 寄存器登记，拒绝自动前进。",
        )
        return plan, [], None, 0.0

    ambiguous = _fr_ao02_score_ambiguous(ranked) or _fr_ao02_trade_pair_ambiguous(ranked)
    if ambiguous or _trade_track_conflict_text(text):
        policy_codes.append("FR_AO02_AMBIGUOUS")
        plan = IntentPolicyPlan(
            next_step="CLARIFY",
            resolved_scenario_id=None,
            clarify=[
                "请用一句说明：只做现货市价（闪兑）还是限价挂单？不要混用两种说法。",
            ],
            policy_codes=policy_codes,
            note="多主场景或成交方式冲突，须澄清后再路由。",
        )
        # Still echo candidates for observability
        return plan, _candidates_from_ranked(), None, min(1.0, ranked[0][1] if ranked else 0.0)

    assert best_sid is not None
    readiness = registry.get(best_sid, "stub")

    # --- Feature switches (product FEATURE_TRADING / FEATURE_AGENT_SPOT) ---
    if best_sid.startswith("trade.") and not settings.feature_trading:
        policy_codes.append("FEATURE_TRADING_OFF")
        plan = IntentPolicyPlan(
            next_step="BLOCKED_FEATURE",
            resolved_scenario_id=best_sid,
            clarify=[],
            policy_codes=policy_codes,
            note="FEATURE_TRADING 关闭，交易类意图不前进到写路径。",
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if (
        best_sid
        in (
            "trade.spot.flash_convert",
            "trade.spot.limit_order",
            "trade.spot.cancel_order",
            "trade.spot.amend_limit_order",
            "trade.spot.open_orders",
        )
        and not settings.feature_agent_spot
    ):
        policy_codes.append("FEATURE_AGENT_SPOT_OFF")
        plan = IntentPolicyPlan(
            next_step="BLOCKED_FEATURE",
            resolved_scenario_id=best_sid,
            clarify=[],
            policy_codes=policy_codes,
            note="现货 Agent 开关关闭。",
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid.startswith("trade.futures.") and not settings.feature_agent_futures:
        policy_codes.append("FEATURE_AGENT_FUTURES_OFF")
        plan = IntentPolicyPlan(
            next_step="BLOCKED_FEATURE",
            resolved_scenario_id=best_sid,
            clarify=[],
            policy_codes=policy_codes,
            note="合约 Agent 开关关闭。",
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid.startswith("automation.") and not settings.feature_agent_futures:
        policy_codes.append("FEATURE_AGENT_FUTURES_OFF")
        plan = IntentPolicyPlan(
            next_step="BLOCKED_FEATURE",
            resolved_scenario_id=best_sid,
            clarify=[],
            policy_codes=policy_codes,
            note="条件单依赖合约网关，合约 Agent 开关关闭。",
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid.startswith("margin.") and not settings.feature_agent_margin:
        policy_codes.append("FEATURE_AGENT_MARGIN_OFF")
        plan = IntentPolicyPlan(
            next_step="BLOCKED_FEATURE",
            resolved_scenario_id=best_sid,
            clarify=[],
            policy_codes=policy_codes,
            note="全仓杠杆 Agent 开关关闭。",
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    # --- Stub scenarios (FR-T05 style: not executable on this server yet) ---
    if readiness == "stub" and best_sid.startswith("trade."):
        policy_codes.append("FR_T05_SCENARIO_STUB")
        plan = IntentPolicyPlan(
            next_step="STUB_NOT_EXECUTABLE",
            resolved_scenario_id=best_sid,
            clarify=[
                f"场景 `{best_sid}` 在运行时为占位，须产品契约冻结后再接写接口。",
            ],
            policy_codes=policy_codes,
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if readiness == "stub":
        policy_codes.append("FR_T05_SCENARIO_STUB")
        plan = IntentPolicyPlan(
            next_step="STUB_NOT_EXECUTABLE",
            resolved_scenario_id=best_sid,
            clarify=[
                f"场景 `{best_sid}` 尚未在本服务接入完整交易所路径；见 GET /api/v1/agent/scenarios。",
            ],
            policy_codes=policy_codes,
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    # --- Ready paths ---
    if best_sid == "read.market.ticker":
        sym = draft.slots.get("symbol")
        if not sym:
            plan = IntentPolicyPlan(
                next_step="CLARIFY",
                resolved_scenario_id=best_sid,
                clarify=["请带上要查询的交易对，例如 BTC-USDT 或 ETH。"],
                policy_codes=policy_codes or ["SLOT_SYMBOL_REQUIRED"],
            )
            return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0
        plan = IntentPolicyPlan(
            next_step="ROUTE_READ_SKILL",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
            note=(
                "可调用 POST /api/v1/agent/routing/execute"
                "（read.market.ticker，symbol 已由 NLU 槽位提供）。"
            ),
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid == "read.market.depth":
        sym = draft.slots.get("symbol")
        if not sym:
            plan = IntentPolicyPlan(
                next_step="CLARIFY",
                resolved_scenario_id=best_sid,
                clarify=["请带上要查询盘口深度的交易对，例如 BTC-USDT 或 ETH。"],
                policy_codes=policy_codes or ["SLOT_SYMBOL_REQUIRED"],
            )
            return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0
        plan = IntentPolicyPlan(
            next_step="ROUTE_READ_SKILL",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
            note=(
                "可调用 POST /api/v1/agent/routing/execute"
                "（read.market.depth，symbol 已由 NLU 槽位提供）。"
            ),
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid == "read.market.trades":
        sym = draft.slots.get("symbol")
        if not sym:
            plan = IntentPolicyPlan(
                next_step="CLARIFY",
                resolved_scenario_id=best_sid,
                clarify=["请带上要查询近期成交的交易对，例如 BTC-USDT 或 ETH。"],
                policy_codes=policy_codes or ["SLOT_SYMBOL_REQUIRED"],
            )
            return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0
        plan = IntentPolicyPlan(
            next_step="ROUTE_READ_SKILL",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
            note=(
                "可调用 POST /api/v1/agent/routing/execute"
                "（read.market.trades，symbol 已由 NLU 槽位提供）。"
            ),
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid == "read.account.balance":
        plan = IntentPolicyPlan(
            next_step="ROUTE_READ_SKILL",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
            note="可调用 POST /api/v1/agent/routing/execute（read.account.balance）。",
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid == "wealth.holdings_read":
        plan = IntentPolicyPlan(
            next_step="ROUTE_READ_SKILL",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
            note="可调用 POST /api/v1/agent/routing/execute（wealth.holdings_read）。",
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid == "chat.faq":
        plan = IntentPolicyPlan(
            next_step="ROUTE_CHAT_FAQ",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid == "trade.spot.open_orders":
        plan = IntentPolicyPlan(
            next_step="ROUTE_READ_SKILL",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
            note=(
                "可调用 POST /api/v1/agent/routing/execute（trade.spot.open_orders）；"
                "可选 symbol、limit；Telegram 绑定用户将直接拉取 GET /sapi/v2/openOrders。"
            ),
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid == "trade.spot.cancel_order":
        slots = draft.slots
        missing: list[str] = []
        if not slots.get("symbol"):
            missing.append("缺交易对（如 BTC-USDT）")
        if not slots.get("orderId") and not slots.get("newClientOrderId"):
            missing.append("缺订单号（可在消息中写长数字或「订单号 xxx」）")
        if missing:
            plan = IntentPolicyPlan(
                next_step="CLARIFY",
                resolved_scenario_id=best_sid,
                clarify=missing,
                policy_codes=policy_codes or ["SLOT_CANCEL_INCOMPLETE"],
                note="撤单禁止猜测 orderId；信息不足仅澄清。",
            )
            return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0
        plan = IntentPolicyPlan(
            next_step="EXECUTE_SPOT_CANCEL",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
            note="槽位齐全：Telegram/HTTP 可直接调用 POST …/trade/spot/cancel。",
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid in (
        "trade.spot.flash_convert",
        "trade.spot.limit_order",
        "margin.cross.market_order",
        "margin.cross.limit_order",
        "trade.futures.market_order",
        "trade.futures.limit_order",
    ):
        dec = evaluate_trade_write_clarify(
            best_sid,
            text,
            {k: str(v) for k, v in draft.slots.items()},
            base_policy_codes=policy_codes,
        )
        plan = IntentPolicyPlan(
            next_step=dec.next_step,
            resolved_scenario_id=best_sid,
            clarify=list(dec.clarify),
            policy_codes=list(dec.policy_codes),
            note=dec.note,
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid == "trade.spot.amend_limit_order":
        slots = draft.slots
        missing: list[str] = []
        if not slots.get("symbol"):
            missing.append("缺交易对（如 BTC-USDT）")
        if not slots.get("orderId"):
            missing.append("缺订单号（可在消息中写长数字或「订单号 xxx」）")
        if not slots.get("price") and not slots.get("quantity"):
            missing.append("缺新限价或新数量（至少改一项）")
        if missing or not _amend_slots_complete({k: str(v) for k, v in slots.items()}):
            plan = IntentPolicyPlan(
                next_step="CLARIFY",
                resolved_scenario_id=best_sid,
                clarify=missing
                or [
                    "改单请先补齐：交易对、订单号、新限价或新数量；"
                    "类型 A 确认后将先撤原单再挂新单。"
                ],
                policy_codes=policy_codes or ["SLOT_AMEND_INCOMPLETE"],
                note="逻辑改单禁止猜测 orderId/新参数；信息不足仅澄清。",
            )
            return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0
        plan = IntentPolicyPlan(
            next_step="CONFIRM_TYPE_A",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
            note=(
                "槽位齐全：逻辑改单须类型 A 确认后再调用 "
                "POST …/trade/spot/amend-limit-order（cancel→order）。"
            ),
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid == "trade.futures.cancel_order":
        slots = draft.slots
        missing: list[str] = []
        if not slots.get("symbol"):
            missing.append("缺合约标的（如 BTC-USDT）")
        if not slots.get("orderId"):
            missing.append("缺订单号（可在消息中写长数字或「订单号 xxx」）")
        if missing:
            plan = IntentPolicyPlan(
                next_step="CLARIFY",
                resolved_scenario_id=best_sid,
                clarify=missing,
                policy_codes=policy_codes or ["SLOT_CANCEL_INCOMPLETE"],
                note="合约撤单禁止猜测 orderId；信息不足仅澄清。",
            )
            return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0
        plan = IntentPolicyPlan(
            next_step="EXECUTE_FUTURES_CANCEL",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
            note="槽位齐全：Telegram/HTTP 可直接调用 POST …/trade/futures/cancel。",
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid == "automation.condition_orders_read":
        plan = IntentPolicyPlan(
            next_step="ROUTE_READ_SKILL",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
            note=(
                "可调用 GET /api/v1/agent/trade/futures/condition-orders；"
                "或 POST /api/v1/agent/routing/execute（automation.condition_orders_read）。"
            ),
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid == "automation.condition_order_cancel":
        slots = draft.slots
        missing: list[str] = []
        if not slots.get("symbol"):
            missing.append("缺合约标的（如 BTC-USDT）")
        if not slots.get("orderId"):
            missing.append("缺条件单订单号")
        if missing:
            plan = IntentPolicyPlan(
                next_step="CLARIFY",
                resolved_scenario_id=best_sid,
                clarify=missing,
                policy_codes=policy_codes or ["SLOT_CANCEL_INCOMPLETE"],
                note="条件单撤销禁止猜测 orderId。",
            )
            return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0
        plan = IntentPolicyPlan(
            next_step="CONFIRM_TYPE_A",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
            note=(
                "槽位齐全：条件单撤销须类型 A 确认后再调用 "
                "POST …/trade/futures/cancel-condition。"
            ),
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    if best_sid == "automation.condition_order":
        slots = draft.slots
        missing: list[str] = []
        if not slots.get("symbol"):
            missing.append("缺合约标的（如 BTC-USDT）")
        if not slots.get("side"):
            missing.append("缺方向（买/卖或开多/开空）")
        if not slots.get("quantity"):
            missing.append("缺数量（张数或币量）")
        if not slots.get("triggerPrice"):
            missing.append("缺触发价（例如：触发价 91000）")
        if not slots.get("triggerType"):
            missing.append("缺触发方向（上涨触发 3UP / 下跌触发 4DOWN）")
        triggered_limit = draft.order_type_hint == "limit"
        if triggered_limit and not slots.get("price"):
            missing.append("触发后限价单须提供委托价（price）")
        if missing:
            plan = IntentPolicyPlan(
                next_step="CLARIFY",
                resolved_scenario_id=best_sid,
                clarify=missing,
                policy_codes=policy_codes or ["SLOT_TRADE_INCOMPLETE"],
                note="条件单写路径禁止猜测缺失字段。",
            )
            return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0
        plan = IntentPolicyPlan(
            next_step="CONFIRM_TYPE_A",
            resolved_scenario_id=best_sid,
            policy_codes=policy_codes,
            note=(
                "槽位齐全：条件单须类型 A 确认后再调用 "
                "POST …/trade/futures/condition-order。"
            ),
        )
        return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0

    plan = IntentPolicyPlan(
        next_step="UNKNOWN",
        resolved_scenario_id=best_sid,
        clarify=[],
        policy_codes=["UNHANDLED_READY_SCENARIO"],
        note="寄存器就绪但该 scenario 尚无策略分支（应补.policy）。",
    )
    return plan, _candidates_from_ranked(), best_sid, ranked[0][1] if ranked else 0.0


async def recognize_intent_full(
    *,
    settings: Settings,
    text: str,
    session_id: str | None = None,
    execution_id: str | None = None,
    user_id: str | None = None,
    locale: str | None = None,
    previous_scenario_id: str | None = None,
    session: AsyncSession | None = None,
) -> IntentRecognizeResponse:
    """End-to-end intent API: NLU draft + policy plan + visible scenario/confidence."""
    trimmed = text.strip()
    if not trimmed:
        draft = IntentNluDraft(
            source="keyword_v1",
            primary_intent_family="unknown",
            scenario_id_candidates=[],
            slots={},
            order_type_hint="unknown",
            clarify_hints=[],
        )
        plan = IntentPolicyPlan(
            next_step="CLARIFY",
            resolved_scenario_id=None,
            clarify=["请输入要处理的内容。"],
            policy_codes=["EMPTY_INPUT"],
            note="空 utterance，不猜测场景。",
        )
        logger.info(
            (
                "intent_pipeline_done session=%s execution=%s locale=%s "
                "next=%s scenario=- codes=EMPTY_INPUT"
            ),
            session_id or "-",
            execution_id or "-",
            locale or "-",
            plan.next_step,
        )
        return IntentRecognizeResponse(
            scenario_id=None,
            confidence=0.0,
            candidates=[],
            nlu=draft,
            plan=plan,
            orchestration_version=ORCHESTRATION_VERSION_INTENT,
            nlu_source=draft.source,
            effective_locale=normalize_effective_locale(locale),
            effective_intent_nlu_use_llm=False,
        )

    best, conf, ranked = recognize_intent_keyword(trimmed)
    draft = build_nlu_draft_keyword_v1(
        trimmed,
        best_sid=best,
        ranked=ranked,
        previous_scenario_id=previous_scenario_id,
    )

    effective_llm = False
    if session is not None:
        merged_defaults: dict[str, Any] | None = None
        if not settings.intent_nlu_use_llm:
            from chainup_agent.application.admin_ai_settings import read_gateway_defaults_merged

            merged_defaults, _ver = await read_gateway_defaults_merged(session)
        effective_llm = resolve_effective_intent_nlu_use_llm(settings, merged_defaults)

    if effective_llm and session is not None:
        from chainup_agent.application.agent_llm_intent_nlu import try_llm_intent_nlu_draft

        llm_out = await try_llm_intent_nlu_draft(
            session,
            settings,
            trimmed,
            effective_locale=normalize_effective_locale(locale),
            previous_scenario_id=previous_scenario_id,
            execution_id=execution_id,
            session_id=session_id,
        )
        if llm_out is not None:
            llm_draft, llm_ranked = llm_out
            draft = prune_llm_slots_without_text_evidence(
                trimmed, enrich_draft_slots_from_text(trimmed, llm_draft)
            )
            ranked = list(llm_ranked)
            best = ranked[0][0] if ranked else llm_draft.scenario_id_candidates[0].scenario_id
            conf = float(ranked[0][1]) if ranked else conf
        else:
            draft = enrich_draft_slots_from_text(trimmed, draft)

    else:
        draft = enrich_draft_slots_from_text(trimmed, draft)

    from chainup_agent.application.clarify_phrase_slots import merge_clarify_phrase_slots
    from chainup_agent.application.memory_session_store import (
        get_trade_write_context,
        remember_trade_write_context,
    )

    ctx_sid, ctx_slots = (
        get_trade_write_context(session_id) if session_id and session_id.strip() else (None, {})
    )
    phrase_slots = merge_clarify_phrase_slots(trimmed, dict(draft.slots))
    pend_sid: str | None = None
    pend_slots: dict[str, str] = {}
    if session_id and session_id.strip():
        pend_sid, pend_slots = get_pending_clarify_slots(session_id)

    read_carry = bool(
        pend_sid
        and pend_sid.startswith("read.")
        and (pend_slots.get("symbol") or "").strip()
    )
    if read_carry:
        draft_slots = merge_clarify_slot_dict(pend_slots, phrase_slots)
    elif ctx_slots:
        draft_slots = merge_clarify_slot_dict(ctx_slots, phrase_slots)
        if pend_slots:
            draft_slots = merge_clarify_slot_dict(pend_slots, draft_slots)
    elif pend_slots:
        draft_slots = merge_clarify_slot_dict(pend_slots, phrase_slots)
    else:
        draft_slots = phrase_slots
    draft = draft.model_copy(update={"slots": draft_slots})

    if session_id and session_id.strip():
        if not pend_slots and ctx_slots:
            pend_sid, pend_slots = ctx_sid, ctx_slots
        if pend_slots:
            merged_slots = dict(draft.slots)
            if pend_sid and pend_sid.strip():
                if not previous_scenario_id:
                    previous_scenario_id = pend_sid
                if pend_sid.startswith(("trade.", "margin.")):
                    best, ranked = _prefer_pending_trade_clarify_context(
                        trimmed,
                        best,
                        ranked,
                        pending_scenario_id=pend_sid,
                        pending_slots=merged_slots,
                    )
                elif pend_sid.startswith("read.") and pend_slots.get("symbol"):
                    best, ranked = _prefer_read_followup_with_pending_symbol(
                        trimmed,
                        best,
                        ranked,
                        pending_scenario_id=pend_sid,
                        pending_slots=merged_slots,
                    )

    best, ranked = _prefer_trade_on_complete_spot_slots(
        trimmed, best, ranked, dict(draft.slots)
    )
    best, ranked = _prefer_spot_flash_on_market_language(trimmed, best, ranked)
    best, ranked = _prefer_read_balance_on_explicit_phrase(trimmed, best, ranked)
    ranked = _clamp_ranked_scores(ranked)
    if ranked:
        best = ranked[0][0]

    plan, cand_list, resolved, conf_out = apply_intent_policy(
        settings=settings,
        text=trimmed,
        draft=draft,
        ranked=ranked,
        best_sid=best,
    )

    if session_id and session_id.strip() and plan.next_step in (
        "CLARIFY",
        "RESOLVE_FLASH_NOTIONAL",
        "RESOLVE_TRADE_NOTIONAL",
        "CONFIRM_TYPE_A",
    ):
        remember_trade_write_context(
            session_id,
            scenario_id=plan.resolved_scenario_id or resolved,
            slots={k: str(v) for k, v in (draft.slots or {}).items()},
        )
    if session_id and session_id.strip() and plan.next_step in (
        "CLARIFY",
        "RESOLVE_FLASH_NOTIONAL",
        "RESOLVE_TRADE_NOTIONAL",
    ):
        remember_pending_clarify(
            session_id,
            scenario_id=plan.resolved_scenario_id or resolved,
            slots=draft.slots,
        )
    elif session_id and session_id.strip() and plan.next_step == "ROUTE_READ_SKILL":
        sym = (draft.slots or {}).get("symbol")
        if sym:
            remember_pending_clarify(
                session_id,
                scenario_id=plan.resolved_scenario_id or resolved,
                slots={"symbol": str(sym).strip()},
            )
    elif session_id and session_id.strip() and plan.next_step == "CONFIRM_TYPE_A":
        from chainup_agent.application.memory_session_store import clear_pending_clarify

        clear_pending_clarify(session_id)

    # Top-level scenarioId: only when policy names a single executable primary
    show_id = resolved
    if plan.next_step in ("CLARIFY", "UNKNOWN") and plan.resolved_scenario_id is None:
        show_id = None

    out_conf = float(conf_out if conf_out is not None else conf)
    if plan.next_step == "CLARIFY" and not show_id:
        out_conf = min(out_conf, 0.45)

    logger.info(
        (
            "intent_pipeline_done session=%s execution=%s locale=%s next=%s "
            "scenario=%s codes=%s effective_intent_nlu_use_llm=%s"
        ),
        session_id or "-",
        execution_id or "-",
        locale or "-",
        plan.next_step,
        show_id or "-",
        ",".join(plan.policy_codes) if plan.policy_codes else "-",
        effective_llm,
    )

    if session is not None and execution_id and show_id:
        uid = (user_id or session_id or "anonymous").strip() or "anonymous"
        await append_intent_orchestration_step(
            session,
            execution_id=execution_id,
            user_id=uid,
            scenario_id=show_id,
        )

    return IntentRecognizeResponse(
        scenario_id=show_id,
        confidence=out_conf,
        candidates=cand_list,
        nlu=draft,
        plan=plan,
        orchestration_version=ORCHESTRATION_VERSION_INTENT,
        nlu_source=draft.source,
        effective_locale=normalize_effective_locale(locale),
        effective_intent_nlu_use_llm=effective_llm,
    )
