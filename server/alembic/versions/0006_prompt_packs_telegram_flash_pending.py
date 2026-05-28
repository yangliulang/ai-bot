"""Prompt packs (Phase1) + Telegram flash-convert pending confirmation sessions.

Revision ID: 0006_pm_tg
Revises: 0005_exec
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_pm_tg"
down_revision: str | Sequence[str] | None = "0005_exec"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_INTENT_NLU_DEFAULT_SYSTEM = """\
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


def upgrade() -> None:
    op.create_table(
        "admin_prompt_pack",
        sa.Column("prompt_pack_id", sa.String(length=128), nullable=False),
        sa.Column("prompt_pack_type", sa.String(length=32), nullable=False),
        sa.Column("scenario_id", sa.String(length=128), nullable=True),
        sa.Column("lifecycle", sa.String(length=32), nullable=False),
        sa.Column("prompt_pack_version", sa.String(length=64), nullable=False),
        sa.Column("etag", sa.String(length=128), nullable=False),
        sa.Column("messages_json", sa.Text(), nullable=False),
        sa.Column("placeholder_denylist_revision", sa.String(length=64), nullable=True),
        sa.Column("safety_phrase_blocklist_revision", sa.String(length=64), nullable=True),
        sa.Column("row_version", sa.BigInteger(), server_default="1", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("prompt_pack_id"),
    )
    op.create_index(
        op.f("ix_admin_prompt_pack_scenario_lifecycle"),
        "admin_prompt_pack",
        ["scenario_id", "lifecycle"],
        unique=False,
    )

    op.create_table(
        "agent_telegram_pending_confirm",
        sa.Column("id", sa.String(length=48), nullable=False),
        sa.Column("public_token", sa.String(length=24), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("kind", sa.String(length=48), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_agent_telegram_pending_confirm_token"),
        "agent_telegram_pending_confirm",
        ["public_token"],
        unique=True,
    )
    op.create_index(
        op.f("ix_agent_telegram_pending_confirm_user"),
        "agent_telegram_pending_confirm",
        ["telegram_user_id"],
        unique=False,
    )

    bind = op.get_bind()
    messages = json.dumps(
        [{"role": "system", "content": _INTENT_NLU_DEFAULT_SYSTEM.strip()}],
        ensure_ascii=False,
    )
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
            "etag": 'W/"seed-intent-nlu-1"',
            "messages": messages,
        },
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_agent_telegram_pending_confirm_user"), table_name="agent_telegram_pending_confirm"
    )
    op.drop_index(
        op.f("ix_agent_telegram_pending_confirm_token"), table_name="agent_telegram_pending_confirm"
    )
    op.drop_table("agent_telegram_pending_confirm")
    op.drop_index(op.f("ix_admin_prompt_pack_scenario_lifecycle"), table_name="admin_prompt_pack")
    op.drop_table("admin_prompt_pack")
