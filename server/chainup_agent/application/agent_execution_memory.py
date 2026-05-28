"""Execution lifecycle persisted to ``agent_execution`` (billing / audit anchor).

Former in-memory registry is replaced by DB rows.
``execution/*`` HTTP routes use ``DbSession``.
Telegram bound turns call ``run_telegram_turn_execution`` (accept → work → finalize + commit).
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.agent_runtime import (
    ExecutionAcceptRequest,
    ExecutionAcceptResponse,
    ExecutionFinalizeRequest,
    ExecutionFinalizeResponse,
    ExecutionStatusResponse,
    utc_now,
)
from chainup_agent.application.agent_prompt_effective import effective_prompt_snapshot_for_scenario
from chainup_agent.application.resolved_prompt_binding import append_prompt_binding_resolved_if_missing
from chainup_agent.application.write_path_pipeline import append_execution_dispatched
from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution
from chainup_agent.infrastructure.persistence.models.agent_execution_event import (
    AgentExecutionEvent,
)

logger = logging.getLogger(__name__)

_FINAL_MAP = {"SUCCESS": "SUCCEEDED", "FAILED": "FAILED", "CANCELLED": "CANCELLED"}


def _new_execution_id() -> str:
    return f"exec-{uuid.uuid4().hex[:14]}"


async def execution_accept(
    session: AsyncSession,
    body: ExecutionAcceptRequest,
    *,
    source: str | None = None,
) -> ExecutionAcceptResponse:
    eid = _new_execution_id()
    now = utc_now()
    sid = body.scenario_id.strip() if body.scenario_id and body.scenario_id.strip() else None
    chan = body.channel.strip() if body.channel and body.channel.strip() else None
    idem = (
        body.idempotency_key.strip()
        if body.idempotency_key and body.idempotency_key.strip()
        else None
    )
    src = source.strip() if source and source.strip() else None
    ppv = (body.prompt_pack_version or "").strip() if body.prompt_pack_version else None
    rpb = body.resolved_prompt_binding
    if ppv is None and rpb is None and sid:
        ppv, rpb = await effective_prompt_snapshot_for_scenario(session, scenario_id=sid)
    row = AgentExecution(
        execution_id=eid,
        user_id=body.user_id.strip(),
        scenario_id=sid,
        channel=chan,
        state="ACCEPTED",
        source=src,
        idempotency_key=idem,
        note=None,
        prompt_pack_version=ppv,
        resolved_prompt_binding=rpb,
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    await session.flush()
    await append_execution_dispatched(
        session,
        execution_id=eid,
        user_id=row.user_id,
        scenario_id=sid,
        source=src,
        channel=chan,
    )
    if sid:
        await append_prompt_binding_resolved_if_missing(
            session,
            execution_id=eid,
            user_id=row.user_id,
            scenario_id=sid,
        )
    logger.info(
        "execution_accept id=%s user=%s scenario=%s source=%s",
        eid,
        row.user_id,
        row.scenario_id,
        src,
    )
    return ExecutionAcceptResponse(
        execution_id=eid,
        state="ACCEPTED",
        created_at=now,
    )


async def execution_get(session: AsyncSession, execution_id: str) -> ExecutionStatusResponse | None:
    row = await session.get(AgentExecution, execution_id)
    if row is None:
        return None
    return ExecutionStatusResponse(
        execution_id=row.execution_id,
        user_id=row.user_id,
        scenario_id=row.scenario_id,
        state=row.state,
        created_at=row.created_at,
        updated_at=row.updated_at,
        prompt_pack_version=row.prompt_pack_version,
        resolved_prompt_binding=row.resolved_prompt_binding,
    )


async def execution_finalize(
    session: AsyncSession,
    body: ExecutionFinalizeRequest,
) -> ExecutionFinalizeResponse | None:
    row = await session.get(AgentExecution, body.execution_id)
    if row is None:
        return None
    now = utc_now()
    new_state = _FINAL_MAP.get(body.outcome, body.outcome)
    row.state = new_state
    row.updated_at = now
    if body.note:
        row.note = body.note[:4000]
    await session.flush()
    logger.info("execution_finalize id=%s state=%s", body.execution_id, new_state)
    return ExecutionFinalizeResponse(
        execution_id=body.execution_id,
        state=new_state,
        finalized_at=now,
    )


async def run_telegram_turn_execution(
    session: AsyncSession,
    *,
    user_id: str,
    scenario_id: str | None,
    compute: Callable[[str], Awaitable[tuple[str, dict[str, Any] | None, bool]]],
) -> tuple[str, dict[str, Any] | None]:
    """accept → ``compute(turn_execution_id)`` → finalize (unless ``leave_accepted``).

    ``leave_accepted`` (**True**): row stays **ACCEPTED**
    (e.g. Telegram 闪兑 Type-A 已出确认按钮，待 **callback** 落单后再 **finalize**)。
    第三元组项为 **False** 时按原逻辑 **SUCCESS** 收口。
    """
    req = ExecutionAcceptRequest(user_id=user_id, scenario_id=scenario_id, channel="telegram")
    acc = await execution_accept(session, req, source="telegram_webhook")
    eid = acc.execution_id
    try:
        text, markup, leave_accepted = await compute(eid)
        if leave_accepted:
            await session.commit()
            return text, markup
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(execution_id=eid, outcome="SUCCESS"),
        )
        await session.commit()
        return text, markup
    except Exception:
        await execution_finalize(
            session,
            ExecutionFinalizeRequest(execution_id=eid, outcome="FAILED"),
        )
        await session.commit()
        raise


async def reset_execution_store_for_tests(session: AsyncSession) -> None:
    """Truncate executions for isolated tests sharing an engine."""
    await session.execute(delete(AgentExecutionEvent))
    await session.execute(delete(AgentExecution))
    await session.commit()
