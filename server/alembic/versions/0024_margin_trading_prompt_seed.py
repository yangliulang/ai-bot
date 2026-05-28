"""Seed TRADING prompt packs for cross margin market / limit (Phase 2.4).

Revision ID: 0024_margin_trading_prompt_seed
Revises: 0023_futures_trading_prompt_seed
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0024_margin_trading_prompt_seed"
down_revision: str | Sequence[str] | None = "0023_futures_trading_prompt_seed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_MARGIN_MARKET_TRADING = (
    "你是 **全仓杠杆（cross）市价单** 助手：帮助用户理解 **双次 Type-A 确认** 前的参数。"
    "\n**仅依据**运行时上下文与用户原文；**禁止**编造借入额、利率或成交价；**禁止**投资建议。"
    "**须**说明自动借入计息风险；**不得**代替用户完成两次确认。**简短** **2～6 句**。"
)
_MARGIN_LIMIT_TRADING = (
    "你是 **全仓杠杆限价单** 助手：帮助用户理解 **限价、数量、方向、借还语义**。"
    "\n**仅依据**运行时上下文；**禁止**编造订单；**须**提示双次确认流程。**简短** **2～6 句**。"
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
            {"role": "system", "content": _MARGIN_MARKET_TRADING.strip()},
            {"role": "user", "content": "示例：全仓杠杆市价借钱买入 0.01 BTC 要注意什么？"},
            {
                "role": "assistant",
                "content": (
                    "说明全仓 cross 与自动借入计息；提醒用户须完成两次确认卡，"
                    "核对交易对/方向/数量后再提交，不代替下单。"
                ),
            },
        ],
        ensure_ascii=False,
    )
    limit_msgs = json.dumps(
        [
            {"role": "system", "content": _MARGIN_LIMIT_TRADING.strip()},
            {"role": "user", "content": "示例：全仓杠杆限价 65000 卖出还款 0.01 BTC？"},
            {
                "role": "assistant",
                "content": (
                    "解释限价挂单与借还方向；提醒双次确认与计息披露，确认前勿承诺一定成交。"
                ),
            },
        ],
        ensure_ascii=False,
    )
    _upsert(
        "pack_trading_margin_cross_market_order_v1",
        "TRADING",
        "margin.cross.market_order",
        'W/"margin-market-v1"',
        market_msgs,
    )
    _upsert(
        "pack_trading_margin_cross_limit_order_v1",
        "TRADING",
        "margin.cross.limit_order",
        'W/"margin-limit-v1"',
        limit_msgs,
    )


def downgrade() -> None:
    bind = op.get_bind()
    for pid in (
        "pack_trading_margin_cross_market_order_v1",
        "pack_trading_margin_cross_limit_order_v1",
    ):
        bind.execute(
            sa.text("DELETE FROM admin_prompt_pack WHERE prompt_pack_id = :pid"),
            {"pid": pid},
        )
