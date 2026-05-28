"""Seed TRADING prompt pack for read.market.ticker LLM narration (facts in runtime_context).

Revision ID: 0014_read_market_ticker_trading_prompt_seed
Revises: 0013_phase1_prompt_assembly_seed
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0014_read_market_ticker_trading_prompt_seed"
down_revision: str | Sequence[str] | None = "0013_phase1_prompt_assembly_seed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_READ_MARKET_TICKER_TRADING = """\
你是 **现货 ticker 行情摘要**助手：**仅依据**运行时注入的 **`RUNTIME_CONTEXT_JSON`** 中的 **`exchangeReadPreview`**（Coobit 只读公共快照）与 **用户具体问题**作答。
严禁编造快照中不存在的价格、涨跌幅或成交量。**禁止**给出投资建议或承诺收益。
使用与用户语种接近的中文或英文，**简短** **2～8 句**；不确定处请让用户在交易所官方界面核对。
"""


def upgrade() -> None:
    bind = op.get_bind()

    def _upsert(pid: str, ptype: str, sid: str, etag: str, messages: str) -> None:
        res = bind.execute(
            sa.text(
                """
                UPDATE admin_prompt_pack
                SET messages_json = :messages,
                    etag = :etag,
                    prompt_pack_type = :ptype,
                    scenario_id = :sid,
                    lifecycle = 'PUBLISHED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE prompt_pack_id = :pid
                """
            ),
            {"pid": pid, "ptype": ptype, "sid": sid, "etag": etag, "messages": messages},
        )
        if getattr(res, "rowcount", None) == 0:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO admin_prompt_pack (
                        prompt_pack_id, prompt_pack_type, scenario_id, lifecycle,
                        prompt_pack_version, etag, messages_json,
                        placeholder_denylist_revision, safety_phrase_blocklist_revision,
                        variable_schema_json
                    ) VALUES (
                        :pid, :ptype, :sid, 'PUBLISHED',
                        '1', :etag, :messages,
                        'rev0', 'rev0',
                        NULL
                    )
                    """
                ),
                {"pid": pid, "ptype": ptype, "sid": sid, "etag": etag, "messages": messages},
            )

    m_ticker = json.dumps(
        [
            {"role": "system", "content": _READ_MARKET_TICKER_TRADING.strip()},
            {
                "role": "user",
                "content": "示例：BTC-USDT 最新价大概是多少？",
            },
            {
                "role": "assistant",
                "content": (
                    "请仅根据当前注入的 ticker 快照中的最新价字段回答用户；若没有该字段则说明数据未就绪。"
                ),
            },
        ],
        ensure_ascii=False,
    )
    _upsert(
        "pack_trading_read_market_ticker_v1",
        "TRADING",
        "read.market.ticker",
        'W/"read-market-ticker-trading-seed-1"',
        m_ticker,
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text("DELETE FROM admin_prompt_pack WHERE prompt_pack_id = :pid"),
        {"pid": "pack_trading_read_market_ticker_v1"},
    )
