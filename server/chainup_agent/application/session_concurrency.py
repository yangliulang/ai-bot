"""Per-session inbound queue + update_id idempotency (session-concurrency-policy v1.0)."""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, TypeVar

from chainup_agent.core.config import Settings

logger = logging.getLogger(__name__)

T = TypeVar("T")

_seen_update_ids: dict[str, set[int]] = {}
_session_locks: dict[str, asyncio.Lock] = {}
_inbound_queues: dict[str, deque[str]] = {}
_coalesce_pending: dict[str, Callable[[], Awaitable[Any]] | None] = {}
_coalesce_last_result: dict[str, Any] = {}
_active_write_execution: dict[str, str] = {}
_parse_chain_count: dict[str, int] = {}


def reset_session_concurrency_for_tests() -> None:
    _seen_update_ids.clear()
    _session_locks.clear()
    _inbound_queues.clear()
    _coalesce_pending.clear()
    _coalesce_last_result.clear()
    _active_write_execution.clear()
    _parse_chain_count.clear()


def remember_telegram_update_id(bot_token: str, update_id: int | None) -> bool:
    """Return False if duplicate update_id (idempotent no-op)."""
    if update_id is None:
        return True
    key = bot_token[-8:]
    seen = _seen_update_ids.setdefault(key, set())
    if update_id in seen:
        logger.info("telegram_update_idempotent_duplicate update_id=%s", update_id)
        return False
    seen.add(update_id)
    if len(seen) > 5000:
        _seen_update_ids[key] = set(list(seen)[-2000:])
    return True


def _lock_for_session(session_id: str) -> asyncio.Lock:
    sid = session_id.strip()
    if sid not in _session_locks:
        _session_locks[sid] = asyncio.Lock()
    return _session_locks[sid]


@dataclass
class InboundQueueMeta:
    queue_depth: int = 0
    coalesced_count: int = 1
    concurrency_decision: str = "served_execution"
    blocked_reason: str | None = None


async def run_serial_per_session(
    session_id: str,
    *,
    settings: Settings,
    coro_factory: Callable[[], Awaitable[T]],
) -> T:
    """Per-session queue: serial_per_session (default) or coalesce_latest."""
    sid = session_id.strip()
    lock = _lock_for_session(sid)
    policy = settings.session_inbound_queue_policy

    if policy == "reject_while_busy" and lock.locked():
        depth = len(_inbound_queues.get(sid, []))
        if depth >= settings.session_inbound_queue_max_depth:
            raise RuntimeError("session_inbound_rejected_busy")

    if policy == "coalesce_latest" and lock.locked():
        _coalesce_pending[sid] = coro_factory
        _inbound_queues.setdefault(sid, deque()).append("coalesced")
        async with lock:
            if sid in _coalesce_last_result:
                return _coalesce_last_result.pop(sid)
        return await coro_factory()

    async with lock:
        _parse_chain_count[sid] = _parse_chain_count.get(sid, 0) + 1
        result = await coro_factory()
        if policy == "coalesce_latest":
            while True:
                pending = _coalesce_pending.pop(sid, None)
                if pending is None:
                    break
                result = await pending()
            _coalesce_last_result[sid] = result
        return result


def release_session_write_gates(session_id: str) -> None:
    """Type-A cancel / abandon — clear in-memory write gates."""
    from chainup_agent.application.memory_session_store import (
        clear_trade_write_context,
        register_pending_type_a,
    )

    sid = session_id.strip()
    register_pending_type_a(sid, waiting=False)
    clear_active_write_execution(sid)
    clear_trade_write_context(sid)


def register_active_write_execution(session_id: str, execution_id: str) -> None:
    _active_write_execution[session_id.strip()] = execution_id.strip()


def clear_active_write_execution(session_id: str) -> None:
    _active_write_execution.pop(session_id.strip(), None)


def get_active_write_execution(session_id: str) -> str | None:
    return _active_write_execution.get(session_id.strip())


def block_second_write_message(
    *,
    session_id: str,
    user_text: str,
    settings: Settings,
    pending_type_a: bool,
    unknown_pending: bool,
) -> str | None:
    """SC-AO-10a/10b — user-visible block when new write while confirm/unknown."""
    active = get_active_write_execution(session_id)
    if settings.session_max_active_write_executions < 1:
        return None
    if unknown_pending and settings.session_block_new_write_on_unknown:
        if any(w in user_text for w in ("买", "卖", "下单", "闪兑", "开仓")):
            return (
                "上一笔结果还在确认中，我可以先帮你看订单状态。"
                "请稍后再发起新的下单。"
            )
    if pending_type_a and active:
        if any(w in user_text for w in ("买", "卖", "改", "另外", "ETH", "BTC")):
            return "你还有一笔待确认订单，请先点确认或取消，再发起新的交易。"
    return None


def observability_snapshot(session_id: str, settings: Settings) -> dict[str, Any]:
    return {
        "sessionQueueDepth": len(_inbound_queues.get(session_id, [])),
        "sessionInboundPolicy": settings.session_inbound_queue_policy,
        "activeWriteExecutionId": get_active_write_execution(session_id),
        "parseChainCount": _parse_chain_count.get(session_id, 0),
    }
