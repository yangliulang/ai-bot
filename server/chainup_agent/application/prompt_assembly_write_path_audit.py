"""Write-path TRADING prompt assembly audit (runtime-injection §1 · OP-PR · AC-09a～f)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_execution_events import (
    append_execution_timeline_event,
    list_timeline_events_for_execution,
)
from chainup_agent.application.agent_prompt_assembly import _scenario_strategy_marker_slug
from chainup_agent.application.agent_prompt_effective import effective_prompt_snapshot_for_scenario

WRITE_PATH_TRADING_SCENARIO_IDS: frozenset[str] = frozenset(
    {
        "trade.spot.limit_order",
        "trade.spot.flash_convert",
        "trade.spot.amend_limit_order",
    }
)

PROMPT_ASSEMBLY_CONTRACT = "runtime-injection§1.v1"


def assert_trading_write_assembly_order(
    messages: list[dict[str, str]],
    meta: dict[str, Any],
    *,
    scenario_id: str,
) -> None:
    """AC-1 / AC-2: §1 block order markers + assembly contract meta."""
    if scenario_id not in WRITE_PATH_TRADING_SCENARIO_IDS:
        raise AssertionError(f"unsupported write-path scenario: {scenario_id}")
    if not messages:
        raise AssertionError("empty messages")
    merged = messages[0].get("content") or ""
    if messages[0].get("role") != "system":
        raise AssertionError("first message must be merged system block")
    if "### PLATFORM_SYSTEM" not in merged:
        raise AssertionError("missing PLATFORM_SYSTEM marker")
    if "### PLATFORM_SAFETY" not in merged:
        raise AssertionError("missing PLATFORM_SAFETY marker")
    marker = f"### SCENARIO_STRATEGY_{_scenario_strategy_marker_slug(scenario_id)}"
    if marker not in merged:
        raise AssertionError(f"missing scenario strategy marker {marker}")
    if meta.get("promptAssemblyContract") != PROMPT_ASSEMBLY_CONTRACT:
        raise AssertionError("promptAssemblyContract mismatch")
    assert_trading_write_tool_schema_ssot(messages)


def assert_trading_write_tool_schema_ssot(messages: list[dict[str, str]]) -> None:
    """AC-2: Tool Spec block is JSON Schema SSOT, not prose parameter tables."""
    tool_block = ""
    for m in messages:
        if m.get("role") == "system" and "TOOL_SPEC_JSON_SCHEMA_SSOT" in (m.get("content") or ""):
            tool_block = m.get("content") or ""
            break
    if not tool_block.strip():
        raise AssertionError("missing TOOL_SPEC_JSON_SCHEMA_SSOT block")
    if "JSON Schema SSOT" not in tool_block and "$schema" not in tool_block:
        raise AssertionError("tool block must reference JSON Schema SSOT")
    if "read.market.ticker" not in tool_block and '"tools"' not in tool_block:
        raise AssertionError("tool registry slice missing from Tool Spec block")
    marker = "### TOOL_SPEC_JSON_SCHEMA_SSOT\n"
    if marker not in tool_block:
        raise AssertionError("Tool Spec block missing SSOT marker")
    rest = tool_block.split(marker, 1)[1]
    end = rest.find("\n\n说明")
    blob = (rest[:end] if end >= 0 else rest).strip()
    try:
        parsed = json.loads(blob)
    except json.JSONDecodeError as exc:
        raise AssertionError("Tool Spec block must embed parseable JSON") from exc
    if not isinstance(parsed, dict):
        raise AssertionError("Tool Spec JSON must be an object")
    if "$schema" not in parsed and "tools" not in parsed:
        raise AssertionError("Tool Spec JSON missing $schema or tools")


def assert_few_shot_before_context_tools_user(messages: list[dict[str, str]]) -> None:
    """AC-3: few-shot user/assistant pairs precede Runtime Context / Tool / User."""
    tool_idx = next(
        (
            i
            for i, m in enumerate(messages)
            if m.get("role") == "system"
            and "TOOL_SPEC_JSON_SCHEMA_SSOT" in (m.get("content") or "")
        ),
        -1,
    )
    if tool_idx < 0:
        raise AssertionError("missing tool/context system block")
    if messages[-1].get("role") != "user":
        raise AssertionError("last message must be user turn")
    for i, m in enumerate(messages[1:tool_idx], start=1):
        if m.get("role") not in ("user", "assistant"):
            raise AssertionError("few-shot region must only contain user/assistant messages")
    if tool_idx >= len(messages) - 1:
        raise AssertionError("Tool Spec block must precede final user message")
    has_few_shot = any(m.get("role") == "assistant" for m in messages[1:tool_idx])
    if not has_few_shot:
        raise AssertionError("expected seeded few-shot assistant before Tool Spec block")


async def append_trading_write_prompt_snapshot_if_missing(
    session: AsyncSession,
    *,
    execution_id: str,
    user_id: str,
    scenario_id: str,
) -> bool:
    """AC-5: emit ``prompt.snapshot`` / ``trading_write`` once per execution (idempotent)."""
    sid = scenario_id.strip()
    if sid not in WRITE_PATH_TRADING_SCENARIO_IDS:
        return False
    eid = execution_id.strip()
    existing = await list_timeline_events_for_execution(session, execution_public_id=eid)
    for row in existing:
        if row.event_type == "prompt.snapshot" and (row.step_kind or "") == "trading_write":
            return False
    ver, bind = await effective_prompt_snapshot_for_scenario(session, scenario_id=sid)
    if not ver or not bind:
        return False
    await append_execution_timeline_event(
        session,
        execution_id=eid,
        user_id=user_id.strip(),
        event_name="prompt.snapshot",
        step_kind="trading_write",
        outcome="info",
        payload={
            "scenarioId": sid,
            "promptPackVersion": ver,
            "resolvedPromptBinding": bind,
            "promptAssemblyContract": PROMPT_ASSEMBLY_CONTRACT,
            "transitionTrigger": "prompt.snapshot.trading_write",
        },
    )
    return True
