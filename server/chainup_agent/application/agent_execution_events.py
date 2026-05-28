"""Persist timeline rows for Admin FR-MC801 (aligned with product observability §2.1)."""

from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.orchestration_budget import assert_execution_budget_allows_append
from chainup_agent.api.schemas.agent_runtime import utc_now
from chainup_agent.infrastructure.persistence.models.agent_execution_event import (
    AgentExecutionEvent,
)

_MAX_PAYLOAD_JSON = 12_000


def _json_dumps_slim(obj: dict[str, Any]) -> str:
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    if len(s) > _MAX_PAYLOAD_JSON:
        return json.dumps(
            {"_truncated": True, "preview": s[:8000]},
            ensure_ascii=False,
            separators=(",", ":"),
        )
    return s


async def append_execution_timeline_event(
    session: AsyncSession,
    *,
    execution_id: str,
    user_id: str,
    event_name: str,
    step_kind: str | None = None,
    outcome: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    """Append one timeline row; ``seq`` monotonic per ``execution_id``."""
    eid = execution_id.strip()
    uid = user_id.strip()
    en = event_name.strip()
    sk = step_kind.strip() if step_kind and step_kind.strip() else None

    await assert_execution_budget_allows_append(
        session,
        execution_id=eid,
        step_kind=sk,
        event_name=en,
    )

    stmt = select(func.coalesce(func.max(AgentExecutionEvent.seq), 0)).where(
        AgentExecutionEvent.execution_id == eid
    )
    res = await session.execute(stmt)
    next_seq = int(res.scalar_one()) + 1
    row = AgentExecutionEvent(
        id=f"exec_ev_{uuid.uuid4().hex[:20]}",
        execution_id=eid,
        user_id=uid,
        seq=next_seq,
        event_type=en,
        step_kind=sk,
        outcome=outcome.strip() if outcome and outcome.strip() else None,
        payload_json=_json_dumps_slim(dict(payload or {})),
        created_at=utc_now(),
    )
    session.add(row)
    await session.flush()


async def list_timeline_events_for_execution(
    session: AsyncSession, *, execution_public_id: str
) -> list[AgentExecutionEvent]:
    eid = execution_public_id.strip()
    stmt = (
        select(AgentExecutionEvent)
        .where(AgentExecutionEvent.execution_id == eid)
        .order_by(AgentExecutionEvent.seq.asc())
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())
