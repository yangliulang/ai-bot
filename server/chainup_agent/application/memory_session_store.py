"""In-memory STM session store (L0/L1 · clear · prompt preview)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from chainup_agent.api.schemas.agent_runtime import utc_now

_L0_PREVIEW_MAX = 8
_CONTENT_PREVIEW_LEN = 120


def _utc_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _content_preview(content: str) -> str:
    text = content.strip()
    if len(text) <= _CONTENT_PREVIEW_LEN:
        return text
    return f"{text[: _CONTENT_PREVIEW_LEN - 1]}…"


@dataclass
class L0Message:
    role: str
    content: str


@dataclass
class SessionRecord:
    user_id: str | None = None
    l0_messages: list[L0Message] = field(default_factory=list)
    l1_drafts: list[dict[str, Any]] = field(default_factory=list)
    pending_type_a_valid: bool = False
    session_cleared_at: datetime | None = None
    last_resolved_scenario_id: str | None = None
    pending_clarify_scenario_id: str | None = None
    pending_clarify_slots: dict[str, str] = field(default_factory=dict)
    last_trade_scenario_id: str | None = None
    last_trade_slots: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SemanticNarrativeFixture:
    summary: str
    proposition_types: tuple[str, ...]
    as_of: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "propositionTypes": list(self.proposition_types),
            "asOf": self.as_of,
        }


DEFAULT_SEMANTIC_FIXTURE = SemanticNarrativeFixture(
    summary="用户偏好：默认关注 BTC；回复尽量简短。",
    proposition_types=("preferred_symbols", "interaction_preference"),
    as_of="2026-05-25T10:00:00Z",
)

_sessions: dict[str, SessionRecord] = {}
_semantic_fixtures: dict[str, SemanticNarrativeFixture] = {}


def reset_memory_session_store_for_tests() -> None:
    """Clear all in-memory STM state (pytest isolation)."""
    _sessions.clear()
    _semantic_fixtures.clear()


def _get_or_create_session(session_id: str) -> SessionRecord:
    sid = session_id.strip()
    if sid not in _sessions:
        _sessions[sid] = SessionRecord()
    return _sessions[sid]


def bind_session_user(session_id: str, user_id: str) -> None:
    rec = _get_or_create_session(session_id)
    rec.user_id = user_id.strip()


def append_l0_message(session_id: str, *, role: str, content: str) -> None:
    rec = _get_or_create_session(session_id)
    rec.l0_messages.append(L0Message(role=role.strip(), content=content))


def register_l1_draft(session_id: str, draft: dict[str, Any]) -> None:
    rec = _get_or_create_session(session_id)
    rec.l1_drafts.append(dict(draft))


def register_pending_type_a(session_id: str, *, waiting: bool = True) -> None:
    rec = _get_or_create_session(session_id)
    rec.pending_type_a_valid = waiting


def set_last_resolved_scenario(session_id: str, scenario_id: str) -> None:
    rec = _get_or_create_session(session_id)
    rec.last_resolved_scenario_id = scenario_id.strip()


def get_last_resolved_scenario(session_id: str) -> str | None:
    rec = _sessions.get(session_id.strip())
    if rec is None:
        return None
    return rec.last_resolved_scenario_id


def set_semantic_fixture(user_id: str, fixture: SemanticNarrativeFixture | None) -> None:
    uid = user_id.strip()
    if fixture is None:
        _semantic_fixtures.pop(uid, None)
    else:
        _semantic_fixtures[uid] = fixture


def get_semantic_fixture(user_id: str) -> SemanticNarrativeFixture | None:
    return _semantic_fixtures.get(user_id.strip())


def get_l0_for_prompt(session_id: str) -> list[dict[str, str]]:
    rec = _sessions.get(session_id.strip())
    if rec is None:
        return []
    return [{"role": m.role, "content": m.content} for m in rec.l0_messages]


def invalidate_pending_type_a_on_stm_clear(session_id: str) -> bool:
    """FR-STM03 — return True if a pending Type A card was invalidated."""
    rec = _sessions.get(session_id.strip())
    if rec is None or not rec.pending_type_a_valid:
        return False
    rec.pending_type_a_valid = False
    return True


def clear_session_stm(
    session_id: str,
    user_id: str,
    *,
    invalidate_pending_type_a: bool = True,
) -> tuple[datetime, bool]:
    """FR-STM01 — clear L0 window and active L1 for session; preserve LTM/Semantic."""
    sid = session_id.strip()
    uid = user_id.strip()
    rec = _get_or_create_session(sid)
    rec.user_id = uid
    pending_invalidated = False
    if invalidate_pending_type_a and rec.pending_type_a_valid:
        rec.pending_type_a_valid = False
        pending_invalidated = True
    now = utc_now()
    rec.l0_messages.clear()
    rec.l1_drafts.clear()
    rec.pending_clarify_slots.clear()
    rec.pending_clarify_scenario_id = None
    rec.last_trade_slots.clear()
    rec.last_trade_scenario_id = None
    rec.session_cleared_at = now
    return now, pending_invalidated


def merge_clarify_slot_dict(
    base: dict[str, str] | None,
    incoming: dict[str, str] | None,
) -> dict[str, str]:
    """Multi-turn clarify: later non-empty values override earlier partial slots."""
    out: dict[str, str] = dict(base or {})
    for key, val in (incoming or {}).items():
        s = str(val).strip() if val is not None else ""
        if s:
            out[key] = s
    return out


def get_pending_clarify_slots(session_id: str) -> tuple[str | None, dict[str, str]]:
    rec = _sessions.get(session_id.strip())
    if rec is None:
        return None, {}
    if not rec.pending_clarify_slots:
        return rec.pending_clarify_scenario_id, {}
    return rec.pending_clarify_scenario_id, dict(rec.pending_clarify_slots)


def remember_pending_clarify(
    session_id: str,
    *,
    scenario_id: str | None,
    slots: dict[str, str] | None,
) -> dict[str, str]:
    """Persist partial slots after CLARIFY / notional-pending for next user turn."""
    sid = session_id.strip()
    rec = _get_or_create_session(sid)
    if scenario_id and scenario_id.strip():
        rec.pending_clarify_scenario_id = scenario_id.strip()
    merged = merge_clarify_slot_dict(rec.pending_clarify_slots, slots)
    rec.pending_clarify_slots = merged
    return dict(merged)


def clear_pending_clarify(session_id: str) -> None:
    rec = _sessions.get(session_id.strip())
    if rec is None:
        return
    rec.pending_clarify_slots.clear()
    rec.pending_clarify_scenario_id = None


def remember_trade_write_context(
    session_id: str,
    *,
    scenario_id: str | None,
    slots: dict[str, str] | None,
) -> None:
    """Retain last spot/margin trade slots across clarify turns (survives CONFIRM clear)."""
    if not slots or not (slots.get("symbol") or "").strip():
        return
    rec = _get_or_create_session(session_id)
    if scenario_id and scenario_id.strip():
        rec.last_trade_scenario_id = scenario_id.strip()
    rec.last_trade_slots = merge_clarify_slot_dict(rec.last_trade_slots, slots)


def get_trade_write_context(session_id: str) -> tuple[str | None, dict[str, str]]:
    rec = _sessions.get(session_id.strip())
    if rec is None or not rec.last_trade_slots:
        return None, {}
    return rec.last_trade_scenario_id, dict(rec.last_trade_slots)


def clear_trade_write_context(session_id: str) -> None:
    rec = _sessions.get(session_id.strip())
    if rec is None:
        return
    rec.last_trade_scenario_id = None
    rec.last_trade_slots.clear()


def build_memory_context_preview(
    *,
    user_id: str,
    semantic_narrative_enabled: bool,
    session_cleared_at: datetime | None,
) -> dict[str, Any]:
    semantic_block: dict[str, Any] | None = None
    if semantic_narrative_enabled:
        fixture = get_semantic_fixture(user_id) or DEFAULT_SEMANTIC_FIXTURE
        semantic_block = fixture.to_dict()
    return {
        "semanticNarrativeEnabled": semantic_narrative_enabled,
        "semanticNarrativeBlock": semantic_block,
        "userMemoryRevokedAt": None,
        "sessionClearedAt": _utc_iso(session_cleared_at) if session_cleared_at else None,
    }


def get_session_context_preview(
    session_id: str,
    user_id: str,
    *,
    semantic_narrative_enabled: bool = False,
) -> dict[str, Any]:
    sid = session_id.strip()
    uid = user_id.strip()
    rec = _sessions.get(sid)
    if rec is None:
        rec = SessionRecord()
    l0 = rec.l0_messages
    preview = [
        {"role": m.role, "contentPreview": _content_preview(m.content)}
        for m in l0[-_L0_PREVIEW_MAX:]
    ]
    return {
        "sessionId": sid,
        "userId": uid,
        "l0MessageCount": len(l0),
        "l0MessagesPreview": preview,
        "pendingTypeAValid": rec.pending_type_a_valid,
        "memoryContext": build_memory_context_preview(
            user_id=uid,
            semantic_narrative_enabled=semantic_narrative_enabled,
            session_cleared_at=rec.session_cleared_at,
        ),
    }


def snapshot_session_state(
    session_id: str,
    user_id: str,
    *,
    semantic_narrative_enabled: bool = False,
) -> dict[str, Any]:
    """Eval helper — full state dict before/after clear."""
    ctx = get_session_context_preview(
        session_id,
        user_id,
        semantic_narrative_enabled=semantic_narrative_enabled,
    )
    return {
        "l0Messages": get_l0_for_prompt(session_id),
        "l0MessageCount": ctx["l0MessageCount"],
        "pendingTypeAValid": ctx["pendingTypeAValid"],
        "memoryContext": ctx["memoryContext"],
    }
