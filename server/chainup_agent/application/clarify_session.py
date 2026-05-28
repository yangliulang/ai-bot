"""Write-path ClarifySessionSnapshot — slots, lifecycle, cl:* callbacks (clarify-session v1.6)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from chainup_agent.api.schemas.agent_runtime import utc_now
from chainup_agent.application.clarify_user_visible import human_summary_resolved_slots
from chainup_agent.application.memory_session_store import (
    clear_pending_clarify,
    merge_clarify_slot_dict,
    remember_pending_clarify,
)
from chainup_agent.core.config import Settings

LifecycleState = Literal["active", "stale", "abandoned"]

CLARIFY_CALLBACK_SLOT_MAP: dict[str, dict[str, str]] = {
    "cl:fc": {"tradeMode": "flash_convert", "type": "MARKET"},
    "cl:lo": {"tradeMode": "limit_order", "type": "LIMIT"},
    "cl:buy": {"side": "BUY"},
    "cl:sell": {"side": "SELL"},
    "cl:sym:ok": {},
    "cl:sym:no": {},
    "cl:qty:base": {"qtyKind": "base"},
    "cl:qty:quote": {"qtyKind": "quote"},
    "cl:resume": {},
    "cl:new": {},
}

CLARIFY_CALLBACK_USER_PHRASE: dict[str, str] = {
    "cl:fc": "闪兑",
    "cl:lo": "限价",
    "cl:buy": "买入",
    "cl:sell": "卖出",
    "cl:sym:ok": "确认交易对",
    "cl:sym:no": "换一个交易对",
    "cl:qty:base": "按币的数量",
    "cl:qty:quote": "按 USDT 金额",
    "cl:resume": "继续上一笔",
    "cl:new": "新话题",
}


def _utc_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


@dataclass
class ClarifySessionSnapshot:
    session_id: str
    execution_id: str
    clarify_turn: int = 1
    resolved_slots_so_far: dict[str, str] = field(default_factory=dict)
    pending_clarify_kind: str | None = None
    effective_locale: str = "zh-Hans"
    last_clarify_message_id: int | None = None
    expires_at: datetime | None = None
    lifecycle_state: LifecycleState = "active"
    stale_at: datetime | None = None
    abandoned: bool = False
    last_user_message_at: datetime | None = None
    last_outbound_normalized: str | None = None
    last_inbound_text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "sessionId": self.session_id,
            "executionId": self.execution_id,
            "clarifyTurn": self.clarify_turn,
            "resolvedSlotsSoFar": dict(self.resolved_slots_so_far),
            "pendingClarifyKind": self.pending_clarify_kind,
            "effectiveLocale": self.effective_locale,
            "lastClarifyMessageId": self.last_clarify_message_id,
            "expiresAt": _utc_iso(self.expires_at) if self.expires_at else None,
            "lifecycleState": self.lifecycle_state,
            "staleAt": _utc_iso(self.stale_at) if self.stale_at else None,
            "abandoned": self.abandoned,
        }

    def memory_summary(self) -> dict[str, str]:
        return {
            "resolvedSlotsHumanSummary": human_summary_resolved_slots(self.resolved_slots_so_far),
            "pendingMissingHumanSummary": self.pending_clarify_kind or "",
            "clarifyTurn": str(self.clarify_turn),
            "abandoned": "true" if self.abandoned else "false",
        }


_clarify_sessions: dict[str, ClarifySessionSnapshot] = {}


def reset_clarify_session_store_for_tests() -> None:
    _clarify_sessions.clear()


def get_clarify_session(session_id: str) -> ClarifySessionSnapshot | None:
    snap = _clarify_sessions.get(session_id.strip())
    if snap is None or snap.abandoned:
        return None if snap and snap.abandoned else snap
    return snap


def get_clarify_session_raw(session_id: str) -> ClarifySessionSnapshot | None:
    return _clarify_sessions.get(session_id.strip())


def is_clarify_callback_data(data: str) -> bool:
    cd = data.strip()
    return cd.startswith("cl:") and cd in CLARIFY_CALLBACK_SLOT_MAP


def abandon_clarify_session(
    session_id: str,
    *,
    reason: str = "user_abandon",
) -> ClarifySessionSnapshot | None:
    snap = _clarify_sessions.get(session_id.strip())
    if snap is None:
        clear_pending_clarify(session_id)
        return None
    snap.abandoned = True
    snap.lifecycle_state = "abandoned"
    snap.pending_clarify_kind = None
    clear_pending_clarify(session_id)
    return snap


def mark_clarify_stale(session_id: str, settings: Settings) -> ClarifySessionSnapshot | None:
    snap = _clarify_sessions.get(session_id.strip())
    if snap is None or snap.abandoned:
        return None
    now = utc_now()
    snap.lifecycle_state = "stale"
    snap.stale_at = now
    from chainup_agent.application.memory_stale_resume import upsert_warm_execution_episode

    upsert_warm_execution_episode(
        session_id=snap.session_id,
        execution_id=snap.execution_id,
        resolved_slots=snap.resolved_slots_so_far,
        human_summary=human_summary_resolved_slots(snap.resolved_slots_so_far),
        stale_at=now,
        settings=settings,
    )
    return snap


def touch_clarify_user_message(session_id: str, text: str) -> None:
    snap = _clarify_sessions.get(session_id.strip())
    if snap is None:
        return
    snap._prev_inbound_for_dedupe = snap.last_inbound_text  # noqa: SLF001
    snap.last_user_message_at = utc_now()
    snap.last_inbound_text = text.strip()[:2000] or None


def record_clarify_outbound(session_id: str, outbound: str) -> None:
    from chainup_agent.application.clarify_user_visible import normalize_outbound_for_dedupe

    snap = _clarify_sessions.get(session_id.strip())
    if snap is None:
        return
    snap.last_outbound_normalized = normalize_outbound_for_dedupe(outbound)


def apply_clarify_callback(
    session_id: str,
    callback_data: str,
    *,
    settings: Settings,
) -> tuple[ClarifySessionSnapshot | None, str | None, str | None]:
    """
    Returns (snapshot, synthetic_user_phrase, error_user_message).
    ``cl:new`` abandons; ``cl:resume`` reactivates stale session.
    """
    cd = callback_data.strip()
    if cd not in CLARIFY_CALLBACK_SLOT_MAP:
        return None, None, "该选项已过期，请重新说明你的需求。"

    snap = _clarify_sessions.get(session_id.strip())
    if snap is None or snap.abandoned:
        return None, None, "当前没有进行中的下单澄清，请直接说你想做什么。"

    if snap.expires_at and utc_now() >= snap.expires_at:
        abandon_clarify_session(session_id, reason="ttl_expired")
        return None, None, "上一笔澄清已过期，请重新说明。"

    if cd == "cl:new":
        abandon_clarify_session(session_id, reason="cl_new")
        return None, None, "好的，我们聊点别的。你想查行情还是交易？"

    if snap.lifecycle_state == "stale" and cd not in ("cl:resume", "cl:new"):
        return None, None, "上一笔已暂停较久，请点「继续上一笔」或重新说明。"

    if cd == "cl:resume":
        if snap.lifecycle_state != "stale":
            return snap, CLARIFY_CALLBACK_USER_PHRASE[cd], None
        snap.lifecycle_state = "active"
        snap.stale_at = None
        snap.clarify_turn += 1
        remember_pending_clarify(
            session_id,
            scenario_id=None,
            slots=snap.resolved_slots_so_far,
        )
        return snap, CLARIFY_CALLBACK_USER_PHRASE[cd], None

    extra = dict(CLARIFY_CALLBACK_SLOT_MAP[cd])
    if cd == "cl:sym:no":
        merged = dict(snap.resolved_slots_so_far)
        merged.pop("symbol", None)
        snap.resolved_slots_so_far = merged
        snap.pending_clarify_kind = "symbol"
    else:
        snap.resolved_slots_so_far = merge_clarify_slot_dict(snap.resolved_slots_so_far, extra)
    snap.clarify_turn += 1
    snap.lifecycle_state = "active"
    remember_pending_clarify(session_id, scenario_id=None, slots=snap.resolved_slots_so_far)
    phrase = CLARIFY_CALLBACK_USER_PHRASE.get(cd, "继续")
    return snap, phrase, None


def upsert_clarify_session(
    *,
    session_id: str,
    execution_id: str,
    slots: dict[str, str] | None,
    pending_kind: str | None = None,
    settings: Settings,
    effective_locale: str = "zh-Hans",
) -> ClarifySessionSnapshot:
    sid = session_id.strip()
    now = utc_now()
    existing = _clarify_sessions.get(sid)
    ttl_sec = settings.stm_clarify_session_ttl_sec
    if existing and not existing.abandoned and existing.execution_id == execution_id:
        existing.resolved_slots_so_far = merge_clarify_slot_dict(
            existing.resolved_slots_so_far, slots
        )
        if pending_kind:
            existing.pending_clarify_kind = pending_kind
        existing.clarify_turn += 1
        existing.last_user_message_at = now
        existing.lifecycle_state = "active"
        existing.stale_at = None
        remember_pending_clarify(sid, scenario_id=None, slots=existing.resolved_slots_so_far)
        return existing

    snap = ClarifySessionSnapshot(
        session_id=sid,
        execution_id=execution_id.strip(),
        clarify_turn=1,
        resolved_slots_so_far=dict(slots or {}),
        pending_clarify_kind=pending_kind,
        effective_locale=effective_locale,
        expires_at=now + timedelta(seconds=ttl_sec),
        lifecycle_state="active",
        last_user_message_at=now,
    )
    _clarify_sessions[sid] = snap
    remember_pending_clarify(sid, scenario_id=None, slots=snap.resolved_slots_so_far)
    return snap


def evaluate_idle_or_ttl_stale(session_id: str, settings: Settings) -> bool:
    """Return True if session was transitioned to stale."""
    snap = _clarify_sessions.get(session_id.strip())
    if snap is None or snap.abandoned or snap.lifecycle_state == "stale":
        return snap.lifecycle_state == "stale" if snap else False
    now = utc_now()
    idle = False
    if snap.last_user_message_at:
        idle = (now - snap.last_user_message_at).total_seconds() >= settings.stm_idle_resume_prompt_sec
    ttl = snap.expires_at is not None and now >= snap.expires_at
    if idle or ttl:
        mark_clarify_stale(session_id, settings)
        return True
    return False
