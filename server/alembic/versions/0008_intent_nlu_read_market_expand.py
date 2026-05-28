"""Extend intent NLU seed pack with read.market.depth / read.market.trades.

Revision ID: 0008_intent_nlu_read_market_expand
Revises: 0007_exec_event
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008_intent_nlu_read_market_expand"
down_revision: str | Sequence[str] | None = "0007_exec_event"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_INTENT_NLU_DEFAULT_SYSTEM = """\
你是交易所 Telegram 机器人的「意图解析」模块。仅输出 **一个 JSON 对象**
（不要 Markdown、不要代码围栏、不要解释文字）。
JSON 字段（camelCase）：
- primaryScenarioId: string，必须从下列 id 中选一个作为主意图：
  read.market.ticker, read.market.depth, read.market.trades, read.account.balance,
  trade.spot.flash_convert,
  trade.spot.limit_order, trade.futures.market_order, chat.faq
- scenarioIdCandidates: 数组，元素为 { "scenarioId": string, "confidence": number 0到1 }，
  最多 5 条，按置信度降序
- slots: 对象，可含 symbol（如 BTC-USDT）、side（BUY 或 SELL）、quantity（十进制字符串）
- orderTypeHint: "market" | "limit" | "unknown"

规则：不得编造未列出的 scenarioId；不确定时降低 confidence 或选 chat.faq。"""


def upgrade() -> None:
    messages = json.dumps(
        [{"role": "system", "content": _INTENT_NLU_DEFAULT_SYSTEM.strip()}],
        ensure_ascii=False,
    )
    bind = op.get_bind()
    res = bind.execute(
        sa.text(
            """
            UPDATE admin_prompt_pack
            SET messages_json = :messages,
                etag = :etag,
                updated_at = CURRENT_TIMESTAMP
            WHERE prompt_pack_id = :pid
            """
        ),
        {
            "messages": messages,
            "etag": 'W/"seed-intent-nlu-read-market-expand-1"',
            "pid": "pack_system_intent_nlu_v1",
        },
    )
    if getattr(res, "rowcount", None) == 0:
        bind.execute(
            sa.text(
                """
                INSERT INTO admin_prompt_pack (
                    prompt_pack_id, prompt_pack_type, scenario_id, lifecycle,
                    prompt_pack_version, etag, messages_json,
                    placeholder_denylist_revision, safety_phrase_blocklist_revision
                ) VALUES (
                    :pid, 'SYSTEM', :sid, 'PUBLISHED',
                    '1', :etag, :messages,
                    'rev0', 'rev0'
                )
                """
            ),
            {
                "pid": "pack_system_intent_nlu_v1",
                "sid": "agent.runtime.intent_nlu",
                "etag": 'W/"seed-intent-nlu-read-market-expand-1"',
                "messages": messages,
            },
        )


def downgrade() -> None:
    """Restore original 0006 intent NLU seed text (without depth/trades)."""
    old = """\
你是交易所 Telegram 机器人的「意图解析」模块。仅输出 **一个 JSON 对象**
（不要 Markdown、不要代码围栏、不要解释文字）。
JSON 字段（camelCase）：
- primaryScenarioId: string，必须从下列 id 中选一个作为主意图：
  read.market.ticker, read.account.balance, trade.spot.flash_convert,
  trade.spot.limit_order, trade.futures.market_order, chat.faq
- scenarioIdCandidates: 数组，元素为 { "scenarioId": string, "confidence": number 0到1 }，
  最多 5 条，按置信度降序
- slots: 对象，可含 symbol（如 BTC-USDT）、side（BUY 或 SELL）、quantity（十进制字符串）
- orderTypeHint: "market" | "limit" | "unknown"

规则：不得编造未列出的 scenarioId；不确定时降低 confidence 或选 chat.faq。"""
    messages = json.dumps([{"role": "system", "content": old.strip()}], ensure_ascii=False)
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            UPDATE admin_prompt_pack
            SET messages_json = :messages,
                etag = :etag,
                updated_at = CURRENT_TIMESTAMP
            WHERE prompt_pack_id = :pid
            """
        ),
        {
            "messages": messages,
            "etag": 'W/"seed-intent-nlu-1"',
            "pid": "pack_system_intent_nlu_v1",
        },
    )
