"""Seed TRADING prompt packs for futures market / limit (Phase 2.3c).

Revision ID: 0023_futures_trading_prompt_seed
Revises: 0022_admin_prompt_pack_version_event
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0023_futures_trading_prompt_seed"
down_revision: str | Sequence[str] | None = "0022_admin_prompt_pack_version_event"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_FUTURES_MARKET_TRADING = (
    "你是 **合约/U本位市价单** 助手：帮助用户理解即将提交的 **Type-A 确认** 参数。"
    "\n**仅依据**运行时 **`RUNTIME_CONTEXT_JSON`**（若有）与用户原文；"
    "**禁止**编造订单号、杠杆、强平价或未确认的成交价；**禁止**投资建议。"
    "**不得**代替用户点击确认；说明合约风险（杠杆、滑点、资金费率）与核对要点即可。"
    "**简短** **2～6 句**。"
)
_FUTURES_LIMIT_TRADING = (
    "你是 **合约/U本位限价单** 助手：帮助用户理解 **限价、数量、方向、开平仓**。"
    "\n**仅依据**运行时上下文与用户原文；**禁止**编造订单或成交价；**禁止**投资建议。"
    "**不得**代替用户确认下单。**简短** **2～6 句**。"
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

    market_msgs = json.dumps(
        [
            {"role": "system", "content": _FUTURES_MARKET_TRADING.strip()},
            {"role": "user", "content": "示例：U本位市价开多 0.01 BTC 有什么风险？"},
            {
                "role": "assistant",
                "content": (
                    "说明市价单按盘口成交、可能与展示价有滑点；提醒核对合约/方向/数量/开平仓，"
                    "杠杆与保证金风险需在官方界面确认，不代替下单。"
                ),
            },
        ],
        ensure_ascii=False,
    )
    limit_msgs = json.dumps(
        [
            {"role": "system", "content": _FUTURES_LIMIT_TRADING.strip()},
            {"role": "user", "content": "示例：合约限价 65000 开空 0.01 BTC 是什么意思？"},
            {
                "role": "assistant",
                "content": (
                    "解释限价为指定价格挂单直至成交或撤单；提醒核对限价与数量及开平仓意图，"
                    "确认前勿承诺一定成交。"
                ),
            },
        ],
        ensure_ascii=False,
    )
    _upsert(
        "pack_trading_futures_market_order_v1",
        "TRADING",
        "trade.futures.market_order",
        'W/"futures-market-v1"',
        market_msgs,
    )
    _upsert(
        "pack_trading_futures_limit_order_v1",
        "TRADING",
        "trade.futures.limit_order",
        'W/"futures-limit-v1"',
        limit_msgs,
    )


def downgrade() -> None:
    bind = op.get_bind()
    for pid in (
        "pack_trading_futures_market_order_v1",
        "pack_trading_futures_limit_order_v1",
    ):
        bind.execute(
            sa.text("DELETE FROM admin_prompt_pack WHERE prompt_pack_id = :pid"),
            {"pid": pid},
        )
