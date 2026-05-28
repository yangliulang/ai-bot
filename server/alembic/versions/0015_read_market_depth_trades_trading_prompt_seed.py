"""Seed TRADING prompt packs for read.market.depth / read.market.trades LLM narration.

Revision ID: 0015_read_market_depth_trades_trading_prompt_seed
Revises: 0014_read_market_ticker_trading_prompt_seed
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0015_read_market_depth_trades_trading_prompt_seed"
down_revision: str | Sequence[str] | None = "0014_read_market_ticker_trading_prompt_seed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_READ_MARKET_DEPTH_TRADING = (
    "你是 **现货盘口深度**助手：**仅依据**运行时注入的 "
    "**`RUNTIME_CONTEXT_JSON`** 中的 **`exchangeReadPreview`**"
    "（Coobit 只读深度快照摘要）与用户问题作答。"
    "\n严禁编造快照中不存在的挂单档位或量级。**禁止**投资建议。"
    "**简短** **2～8 句**，语种贴近用户。"
)
_READ_MARKET_TRADES_TRADING = (
    "你是 **现货近期成交**助手：**仅依据**运行时注入的 "
    "**`RUNTIME_CONTEXT_JSON`** 中的 **`exchangeReadPreview`**（公共成交快照摘要）作答。"
    "\n严禁编造未出现的成交价或笔数。**禁止**投资建议。"
    "**简短** **2～8 句**，语种贴近用户。"
)


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

    depth_msgs = json.dumps(
        [
            {"role": "system", "content": _READ_MARKET_DEPTH_TRADING.strip()},
            {
                "role": "user",
                "content": "示例：当前买盘最厚的大概在哪一档价位？",
            },
            {
                "role": "assistant",
                "content": (
                    "请仅依据注入的深度快照摘要中的 bids/asks 回答；"
                    "若没有有效档位则说明数据未就绪。"
                ),
            },
        ],
        ensure_ascii=False,
    )
    trades_msgs = json.dumps(
        [
            {"role": "system", "content": _READ_MARKET_TRADES_TRADING.strip()},
            {
                "role": "user",
                "content": "示例：最近几笔成交方向和大致价位？",
            },
            {
                "role": "assistant",
                "content": (
                    "请仅依据注入的成交快照中的最近条目回答；若列表为空则说明暂无返回数据。"
                ),
            },
        ],
        ensure_ascii=False,
    )
    _upsert(
        "pack_trading_read_market_depth_v1",
        "TRADING",
        "read.market.depth",
        'W/"read-market-depth-trading-seed-1"',
        depth_msgs,
    )
    _upsert(
        "pack_trading_read_market_trades_v1",
        "TRADING",
        "read.market.trades",
        'W/"read-market-trades-trading-seed-1"',
        trades_msgs,
    )


def downgrade() -> None:
    bind = op.get_bind()
    for pid in (
        "pack_trading_read_market_depth_v1",
        "pack_trading_read_market_trades_v1",
    ):
        bind.execute(
            sa.text("DELETE FROM admin_prompt_pack WHERE prompt_pack_id = :pid"),
            {"pid": pid},
        )
