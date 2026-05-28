"""Inbound preprocess while clarify active — §2.3 full sequence before intent NLU."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from chainup_agent.application.clarify_session import (
    abandon_clarify_session,
    evaluate_idle_or_ttl_stale,
    get_clarify_session,
    get_clarify_session_raw,
    touch_clarify_user_message,
    upsert_clarify_session,
)
from chainup_agent.application.clarify_user_visible import (
    classify_clarify_inbound,
    strip_internal_jargon_from_outbound,
)
from chainup_agent.application.memory_session_store import register_pending_type_a
from chainup_agent.application.memory_stale_resume import (
    apply_resume_to_clarify_session,
    classify_resume,
    stale_idle_hint_message,
)
from chainup_agent.application.read_clarify_session import (
    abandon_read_clarify,
    upsert_read_clarify_session,
)
from chainup_agent.core.config import Settings

logger = logging.getLogger(__name__)

_ABANDON_REPLY = "好的，已取消这笔下单。有需要再说。"
_READ_INTERRUPT_REPLY = "好的，我先帮你看行情/账户信息。"
_GREETING_REPLY = "你好，我是交易助手。可以说查行情、看余额，或买入/卖出某币种。"


@dataclass
class ClarifyInboundPreprocess:
    proceed_to_intent: bool = True
    early_reply: str | None = None
    resume_observability: dict[str, Any] | None = None
    concurrency_meta: dict[str, Any] | None = None


def preprocess_clarify_inbound(
    *,
    session_id: str,
    user_text: str,
    settings: Settings,
    execution_id: str | None = None,
    pending_type_a: bool = False,
) -> ClarifyInboundPreprocess:
    """
    clarify-session §2.3 + §2.4 + §1.1 (type A freezes clarify when pending).
    """
    sid = session_id.strip()
    text = user_text.strip()
    touch_clarify_user_message(sid, text)

    if pending_type_a:
        return ClarifyInboundPreprocess(proceed_to_intent=True)

    was_stale = evaluate_idle_or_ttl_stale(sid, settings)
    snap = get_clarify_session_raw(sid)

    if was_stale and snap and snap.lifecycle_state == "stale":
        if text:
            resume = classify_resume(session_id=sid, inbound_text=text, settings=settings)
            if resume.decision == "resume_prior_write":
                apply_resume_to_clarify_session(
                    sid, resume, settings=settings, inbound_text=text
                )
                return ClarifyInboundPreprocess(
                    proceed_to_intent=True,
                    resume_observability=resume.to_observability(),
                )
            if resume.decision == "need_one_clarify":
                hint = (
                    "你之前有一笔买入相关的下单还没说完。"
                    "请说一下标的和数量，例如「BNB 闪兑 100U」。"
                )
                return ClarifyInboundPreprocess(
                    proceed_to_intent=False,
                    early_reply=hint,
                    resume_observability=resume.to_observability(),
                )
            kind = classify_clarify_inbound(text)
            if kind in ("greeting", "chitchat"):
                abandon_clarify_session(sid, reason="stale_greeting")
                return ClarifyInboundPreprocess(
                    proceed_to_intent=True,
                    early_reply=_GREETING_REPLY,
                )
            if kind == "abandon":
                abandon_clarify_session(sid, reason="stale_abandon")
                return ClarifyInboundPreprocess(
                    proceed_to_intent=False,
                    early_reply=_ABANDON_REPLY,
                )
        idle_hint = stale_idle_hint_message()
        return ClarifyInboundPreprocess(
            proceed_to_intent=True,
            early_reply=idle_hint if settings.stm_idle_default_policy == "stale_prior_write" else None,
        )

    active = get_clarify_session(sid)
    if active is None:
        return ClarifyInboundPreprocess(proceed_to_intent=True)

    from chainup_agent.application.clarify_phrase_slots import merge_clarify_phrase_slots
    from chainup_agent.application.memory_session_store import remember_pending_clarify

    phrase_slots = merge_clarify_phrase_slots(text, active.resolved_slots_so_far)
    if phrase_slots != active.resolved_slots_so_far:
        active.resolved_slots_so_far = phrase_slots
        remember_pending_clarify(sid, scenario_id=None, slots=phrase_slots)

    kind = classify_clarify_inbound(text)
    if kind == "abandon":
        abandon_clarify_session(sid, reason="inbound_abandon")
        return ClarifyInboundPreprocess(
            proceed_to_intent=False,
            early_reply=_ABANDON_REPLY,
        )
    if kind in ("read_interrupt", "greeting"):
        abandon_clarify_session(sid, reason=kind)
        abandon_read_clarify(sid)
        reply = _READ_INTERRUPT_REPLY if kind == "read_interrupt" else _GREETING_REPLY
        return ClarifyInboundPreprocess(
            proceed_to_intent=True,
            early_reply=reply,
        )

    if execution_id:
        upsert_clarify_session(
            session_id=sid,
            execution_id=execution_id,
            slots=None,
            pending_kind=active.pending_clarify_kind,
            settings=settings,
            effective_locale=active.effective_locale,
        )

    return ClarifyInboundPreprocess(proceed_to_intent=True)


def _maybe_dedupe_outbound(session_id: str, body: str, inbound_text: str) -> str:
    from chainup_agent.application.clarify_session import get_clarify_session_raw
    from chainup_agent.application.clarify_user_visible import (
        normalize_outbound_for_dedupe,
        outbound_would_repeat,
    )

    snap = get_clarify_session_raw(session_id)
    if snap is None or not snap.last_outbound_normalized:
        return body
    prev_in = getattr(snap, "_prev_inbound_for_dedupe", None)
    inbound_changed = bool(inbound_text.strip()) and inbound_text.strip() != (prev_in or "")
    if outbound_would_repeat(
        previous_outbound=snap.last_outbound_normalized,
        candidate_outbound=body,
        inbound_changed=inbound_changed,
    ):
        return f"收到，{body}" if not body.startswith("收到") else body
    _ = normalize_outbound_for_dedupe
    return body


def after_clarify_plan(
    *,
    session_id: str,
    execution_id: str,
    slots: dict[str, str] | None,
    next_step: str,
    pending_kind: str | None,
    settings: Settings,
    outbound_text: str,
    inbound_text: str = "",
) -> str:
    """Post-process outbound — jargon strip + dedupe progress suffix."""
    body = strip_internal_jargon_from_outbound(outbound_text)
    body = _maybe_dedupe_outbound(session_id, body, inbound_text)
    if next_step in ("CLARIFY", "RESOLVE_FLASH_NOTIONAL", "RESOLVE_TRADE_NOTIONAL"):
        upsert_clarify_session(
            session_id=session_id,
            execution_id=execution_id,
            slots=slots,
            pending_kind=pending_kind,
            settings=settings,
        )
    elif next_step == "CONFIRM_TYPE_A":
        register_pending_type_a(session_id, waiting=True)
    from chainup_agent.application.clarify_session import record_clarify_outbound

    record_clarify_outbound(session_id, body)
    return body


def maybe_start_read_clarify(
    *,
    session_id: str,
    scenario_id: str | None,
    slots: dict[str, str] | None,
    settings: Settings,
    user_text: str = "",
) -> None:
    """Light read clarify when scope ambiguous."""
    text = user_text.strip()
    slot_map = dict(slots or {})
    if scenario_id and "read" in scenario_id:
        if slot_map and not slot_map.get("symbol") and not slot_map.get("scope"):
            if "盈亏" in text or "盈亏" in str(slot_map):
                upsert_read_clarify_session(
                    session_id=session_id,
                    slots=slot_map,
                    pending_kind="scope_portfolio_vs_market",
                    settings=settings,
                    intent_family="portfolio_read",
                )
                return
            if "BTC" in text.upper() and "ETH" in text.upper():
                upsert_read_clarify_session(
                    session_id=session_id,
                    slots=slot_map,
                    pending_kind="multi_symbol_compare",
                    settings=settings,
                    intent_family="market_read",
                )
                return
        if "提醒" in text or "涨到" in text or "跌到" in text:
            if not slot_map.get("monitoringAssetClass"):
                upsert_read_clarify_session(
                    session_id=session_id,
                    slots=slot_map,
                    pending_kind="monitoring_asset_class",
                    settings=settings,
                    intent_family="monitoring_draft",
                )


def read_clarify_reply_after_intent(
    *,
    session_id: str,
    effective_locale: str | None,
) -> tuple[str, dict[str, Any] | None] | None:
    from chainup_agent.application.telegram_clarify_outbound import try_read_clarify_telegram_reply

    return try_read_clarify_telegram_reply(
        session_id=session_id,
        effective_locale=effective_locale,
    )
