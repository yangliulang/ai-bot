"""Stale + Resume gate — WarmExecutionEpisode, ResumeClassifier (memory-runtime §14.6)."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

from chainup_agent.api.schemas.agent_runtime import utc_now
from chainup_agent.application.clarify_session import (
    ClarifySessionSnapshot,
    abandon_clarify_session,
    get_clarify_session_raw,
    upsert_clarify_session,
)
from chainup_agent.application.clarify_user_visible import human_summary_resolved_slots
from chainup_agent.core.config import Settings

logger = logging.getLogger(__name__)

ResumeDecision = Literal[
    "resume_prior_write", "new_intent", "need_one_clarify", "rules_bypass"
]


@dataclass
class WarmExecutionEpisode:
    session_id: str
    execution_id: str
    resolved_slots: dict[str, str] = field(default_factory=dict)
    human_summary: str = ""
    stale_at: datetime | None = None
    episode_pick_reason: str = "most_recent"

    def to_dict(self) -> dict[str, Any]:
        stale_iso = None
        if self.stale_at:
            stale_iso = self.stale_at.astimezone(UTC).isoformat().replace("+00:00", "Z")
        return {
            "sessionId": self.session_id,
            "executionId": self.execution_id,
            "resolvedSlotsSoFar": dict(self.resolved_slots),
            "resolvedSlotsHumanSummary": self.human_summary,
            "staleAt": stale_iso,
            "episodePickReason": self.episode_pick_reason,
        }


@dataclass(frozen=True)
class ResumeClassifierResult:
    decision: ResumeDecision
    confidence: float
    execution_id: str | None = None
    episode_pick_reason: str | None = None
    merged_slots: dict[str, str] | None = None

    def to_observability(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "confidence": self.confidence,
            "executionId": self.execution_id,
            "episodePickReason": self.episode_pick_reason,
        }


_warm_episodes: dict[str, list[WarmExecutionEpisode]] = {}


def reset_warm_episode_store_for_tests() -> None:
    _warm_episodes.clear()


def upsert_warm_execution_episode(
    *,
    session_id: str,
    execution_id: str,
    resolved_slots: dict[str, str],
    human_summary: str,
    stale_at: datetime,
    settings: Settings,
) -> WarmExecutionEpisode:
    _ = settings
    sid = session_id.strip()
    ep = WarmExecutionEpisode(
        session_id=sid,
        execution_id=execution_id.strip(),
        resolved_slots=dict(resolved_slots),
        human_summary=human_summary,
        stale_at=stale_at,
        episode_pick_reason="most_recent",
    )
    lst = _warm_episodes.setdefault(sid, [])
    lst[:] = [e for e in lst if e.execution_id != ep.execution_id]
    lst.append(ep)
    lst.sort(key=lambda e: e.stale_at or datetime.min.replace(tzinfo=UTC), reverse=True)
    return ep


def pick_warm_episode(
    session_id: str,
    *,
    inbound_text: str | None = None,
) -> WarmExecutionEpisode | None:
    lst = _warm_episodes.get(session_id.strip())
    if not lst:
        return None
    text = (inbound_text or "").upper()
    if text:
        for ep in lst:
            sym = (ep.resolved_slots.get("symbol") or "").upper()
            base = (ep.resolved_slots.get("baseAsset") or "").upper()
            if sym and sym.replace("-", "") in text.replace("-", ""):
                ep.episode_pick_reason = "symbol_match"
                return ep
            if base and base in text:
                ep.episode_pick_reason = "symbol_match"
                return ep
    lst[0].episode_pick_reason = "most_recent"
    return lst[0]


_RESUME_EXPLICIT = re.compile(
    r"还是|继续|上一笔|刚才|照旧|再来一笔|100\s*[uU]|闪兑|限价",
    re.IGNORECASE,
)
_AMBIGUOUS_SHORT = re.compile(r"^(?:买|卖|嗯|好)$")


def classify_resume(
    *,
    session_id: str,
    inbound_text: str,
    settings: Settings,
) -> ResumeClassifierResult:
    """FR-STM13/14 — rules-first resume gate."""
    text = inbound_text.strip()
    ep = pick_warm_episode(session_id, inbound_text=text)
    if ep is None:
        return ResumeClassifierResult(decision="new_intent", confidence=0.0)

    if _AMBIGUOUS_SHORT.match(text):
        if "再来一笔" in text or "上一笔" in text:
            return ResumeClassifierResult(
                decision="need_one_clarify",
                confidence=0.85,
                execution_id=ep.execution_id,
                episode_pick_reason=ep.episode_pick_reason,
            )
        return ResumeClassifierResult(decision="new_intent", confidence=0.2)

    if _RESUME_EXPLICIT.search(text):
        merged = dict(ep.resolved_slots)
        qty = re.search(r"(\d+(?:\.\d+)?)\s*(?:U|USDT|u)", text, re.IGNORECASE)
        if qty:
            merged["quoteQty"] = qty.group(1)
        conf = 0.92 if qty or "闪兑" in text or "买" in text else 0.8
        if conf >= settings.resume_classifier_min_confidence:
            return ResumeClassifierResult(
                decision="resume_prior_write",
                confidence=conf,
                execution_id=ep.execution_id,
                episode_pick_reason=ep.episode_pick_reason,
                merged_slots=merged,
            )
        return ResumeClassifierResult(decision="new_intent", confidence=conf)

    if "再来一笔" in text:
        return ResumeClassifierResult(
            decision="need_one_clarify",
            confidence=0.88,
            execution_id=ep.execution_id,
            episode_pick_reason=ep.episode_pick_reason,
        )

    return ResumeClassifierResult(decision="new_intent", confidence=0.3)


def apply_resume_to_clarify_session(
    session_id: str,
    result: ResumeClassifierResult,
    *,
    settings: Settings,
    inbound_text: str,
) -> ClarifySessionSnapshot | None:
    if result.decision != "resume_prior_write" or not result.execution_id:
        return None
    merged = dict(result.merged_slots or {})
    snap = upsert_clarify_session(
        session_id=session_id,
        execution_id=result.execution_id,
        slots=merged,
        pending_kind=None,
        settings=settings,
    )
    snap.lifecycle_state = "active"
    snap.stale_at = None
    snap.last_user_message_at = utc_now()
    logger.info(
        "agent.memory.resume_classified session=%s execution=%s decision=%s conf=%.2f",
        session_id,
        result.execution_id,
        result.decision,
        result.confidence,
    )
    _ = inbound_text
    return snap


def stale_idle_hint_message() -> str:
    return "你有一段时间没说话了；若要继续上一笔下单，直接说数量或点「继续上一笔」。"
