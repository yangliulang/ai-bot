"""HTTP Agent trade routes — execution finalize when exchange write ends UNKNOWN."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.agent_runtime import ExecutionFinalizeRequest
from chainup_agent.application.agent_execution_memory import execution_finalize
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.exchange.coobit_openapi import app_error_indicates_exchange_unknown


async def finalize_trade_http_on_error(
    session: AsyncSession,
    execution_id: str,
    exc: AppError,
    *,
    note_prefix: str,
) -> None:
    outcome = "UNKNOWN" if app_error_indicates_exchange_unknown(exc) else "FAILED"
    suffix = "unknown" if outcome == "UNKNOWN" else "rejected"
    await execution_finalize(
        session,
        ExecutionFinalizeRequest(
            execution_id=execution_id,
            outcome=outcome,
            note=f"{note_prefix}_{suffix}",
        ),
    )
