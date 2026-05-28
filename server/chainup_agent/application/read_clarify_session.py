"""Read-path clarify — ReadClarifySessionSnapshot + rc:* (read-clarify-session v1.0)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from chainup_agent.api.schemas.agent_runtime import utc_now
from chainup_agent.application.clarify_user_visible import human_summary_resolved_slots
from chainup_agent.application.memory_session_store import merge_clarify_slot_dict
from chainup_agent.core.config import Settings

READ_CALLBACK_SLOT_MAP: dict[str, dict[str, str]] = {
    "rc:sym:BTC": {"primarySymbol": "BTCUSDT"},
    "rc:sym:ETH": {"primarySymbol": "ETHUSDT"},
    "rc:scope:market": {"scope": "market"},
    "rc:scope:portfolio": {"scope": "portfolio"},
    "rc:mon:spot": {"monitoringAssetClass": "spot"},
    "rc:mon:fut": {"monitoringAssetClass": "futures"},
    "rc:cancel": {},
}

READ_CALLBACK_USER_PHRASE: dict[str, str] = {
    "rc:sym:BTC": "BTC",
    "rc:sym:ETH": "ETH",
    "rc:scope:market": "看行情",
    "rc:scope:portfolio": "看我的持仓",
    "rc:mon:spot": "现货提醒",
    "rc:mon:fut": "合约提醒",
    "rc:cancel": "不问了",
}


@dataclass
class ReadClarifySessionSnapshot:
    session_id: str
    read_clarify_turn: int = 1
    resolved_read_slots_so_far: dict[str, str] = field(default_factory=dict)
    pending_read_clarify_kind: str | None = None
    execution_id: str | None = None
    intent_family: str | None = None
    abandoned: bool = False
    expires_at: Any = None

    def memory_summary(self) -> dict[str, str]:
        return {
            "resolvedReadSlotsHumanSummary": human_summary_resolved_slots(
                self.resolved_read_slots_so_far
            ),
            "pendingReadMissing": self.pending_read_clarify_kind or "",
        }


_read_sessions: dict[str, ReadClarifySessionSnapshot] = {}


def reset_read_clarify_session_store_for_tests() -> None:
    _read_sessions.clear()


def is_read_clarify_callback_data(data: str) -> bool:
    return data.strip().startswith("rc:") and data.strip() in READ_CALLBACK_SLOT_MAP


def get_read_clarify_session(session_id: str) -> ReadClarifySessionSnapshot | None:
    snap = _read_sessions.get(session_id.strip())
    if snap is None or snap.abandoned:
        return None
    if snap.expires_at and utc_now() >= snap.expires_at:
        snap.abandoned = True
        return None
    return snap


def abandon_read_clarify(session_id: str) -> None:
    snap = _read_sessions.get(session_id.strip())
    if snap:
        snap.abandoned = True


def apply_read_clarify_callback(
    session_id: str,
    callback_data: str,
) -> tuple[ReadClarifySessionSnapshot | None, str | None, str | None]:
    cd = callback_data.strip()
    if cd not in READ_CALLBACK_SLOT_MAP:
        return None, None, "该选项已过期。"
    snap = _read_sessions.get(session_id.strip())
    if snap is None or snap.abandoned:
        return None, None, "当前没有进行中的查询澄清。"
    if cd == "rc:cancel":
        snap.abandoned = True
        return None, None, "好的，有需要再说。"
    snap.resolved_read_slots_so_far = merge_clarify_slot_dict(
        snap.resolved_read_slots_so_far, READ_CALLBACK_SLOT_MAP[cd]
    )
    snap.read_clarify_turn += 1
    return snap, READ_CALLBACK_USER_PHRASE.get(cd, "继续"), None


def upsert_read_clarify_session(
    *,
    session_id: str,
    slots: dict[str, str] | None,
    pending_kind: str | None,
    settings: Settings,
    execution_id: str | None = None,
    intent_family: str | None = None,
) -> ReadClarifySessionSnapshot:
    sid = session_id.strip()
    now = utc_now()
    existing = _read_sessions.get(sid)
    if existing and not existing.abandoned:
        existing.resolved_read_slots_so_far = merge_clarify_slot_dict(
            existing.resolved_read_slots_so_far, slots
        )
        if pending_kind:
            existing.pending_read_clarify_kind = pending_kind
        existing.read_clarify_turn += 1
        return existing
    snap = ReadClarifySessionSnapshot(
        session_id=sid,
        resolved_read_slots_so_far=dict(slots or {}),
        pending_read_clarify_kind=pending_kind,
        execution_id=execution_id,
        intent_family=intent_family,
        expires_at=now + timedelta(seconds=settings.read_clarify_session_ttl_sec),
    )
    _read_sessions[sid] = snap
    return snap
