"""exchange-facing tool declarations as **JSON Schema only** (runtime-injection §4 · AC-09b).

No parallel handwritten parameter tables — callers inject this document verbatim into the
**Tool Spec** assembly block before the user turn.
"""

from __future__ import annotations

import copy
from typing import Any

_EXCHANGE_READ_TOOLS: list[dict[str, Any]] = [
    {
        "toolId": "read.market.ticker",
        "description": "Fetch latest public ticker / last price for a spot symbol.",
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Trading pair such as BTC-USDT.",
                }
            },
            "required": ["symbol"],
        },
    },
    {
        "toolId": "read.market.depth",
        "description": "Fetch order-book depth snapshot for a spot symbol.",
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "symbol": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "required": ["symbol"],
        },
    },
    {
        "toolId": "read.account.balance",
        "description": "Summarize spot balances for the bound trading sub-account.",
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {},
        },
    },
]


def exchange_read_tools_bundle() -> dict[str, Any]:
    """Serializable SSOT bundle for Tool Spec injection."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "exchange_read_tools",
        "description": (
            "SSOT registry slice for read-oriented exchange scenarios. "
            "Inject as structured JSON — **do not** duplicate parameters as prose tables."
        ),
        "tools": copy.deepcopy(_EXCHANGE_READ_TOOLS),
    }


INTENT_NLU_OUTPUT_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "intent_nlu_structured_payload",
    "description": (
        "Structured intent NLU JSON (camelCase). SSOT for model output shape "
        "(agent_llm_intent_nlu)."
    ),
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "primaryScenarioId": {"type": "string"},
        "scenarioIdCandidates": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "scenarioId": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                },
                "required": ["scenarioId", "confidence"],
            },
        },
        "slots": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
        "orderTypeHint": {"type": "string", "enum": ["market", "limit", "unknown"]},
    },
    "required": ["primaryScenarioId", "scenarioIdCandidates", "slots", "orderTypeHint"],
}
