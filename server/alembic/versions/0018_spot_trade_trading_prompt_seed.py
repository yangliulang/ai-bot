"""Seed TRADING prompt packs for spot flash / limit (Phase1 assembly allow-list).

Revision ID: 0018_spot_trade_trading_prompt_seed
Revises: 0017_admin_ai_model_api_model
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0018_spot_trade_trading_prompt_seed"
down_revision: str | Sequence[str] | None = "0017_admin_ai_model_api_model"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_FLASH_TRADING = (
    "你是 **现货闪兑（市价）** 助手：帮助用户理解即将提交的 **Type-A 确认** 参数。"
    "\n**仅依据**运行时 **`RUNTIME_CONTEXT_JSON`**（若有）与用户原文；"
    "**禁止**编造订单号或未确认的成交价；**禁止**投资建议。"
    "**不得**代替用户点击确认；说明风险与核对要点即可。**简短** **2～6 句**。"
)
_LIMIT_TRADING = (
    "你是 **现货限价单** 助手：帮助用户理解 **限价、数量、方向、时效（GTC/IOC/FOK）**。"
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

    flash_msgs = json.dumps(
        [
            {"role": "system", "content": _FLASH_TRADING.strip()},
            {"role": "user", "content": "示例：市价买入 0.01 BTC 会有什么风险？"},
            {
                "role": "assistant",
                "content": (
                    "说明市价单按盘口成交、可能与展示价有滑点；提醒用户在 Type-A 弹窗核对"
                    "交易对/方向/数量后再确认，不代替下单。"
                ),
            },
        ],
        ensure_ascii=False,
    )
    limit_msgs = json.dumps(
        [
            {"role": "system", "content": _LIMIT_TRADING.strip()},
            {"role": "user", "content": "示例：限价 65000 买 0.01 BTC，GTC 是什么意思？"},
            {
                "role": "assistant",
                "content": (
                    "解释 GTC 为挂单直至成交或撤单；提醒核对限价与 base 数量，"
                    "确认前勿承诺一定成交。"
                ),
            },
        ],
        ensure_ascii=False,
    )
    _upsert(
        "pack_trading_spot_flash_convert_v1",
        "TRADING",
        "trade.spot.flash_convert",
        'W/"flash-v1"',
        flash_msgs,
    )
    _upsert(
        "pack_trading_spot_limit_order_v1",
        "TRADING",
        "trade.spot.limit_order",
        'W/"limit-v1"',
        limit_msgs,
    )


def downgrade() -> None:
    bind = op.get_bind()
    for pid in (
        "pack_trading_spot_flash_convert_v1",
        "pack_trading_spot_limit_order_v1",
    ):
        bind.execute(
            sa.text("DELETE FROM admin_prompt_pack WHERE prompt_pack_id = :pid"),
            {"pid": pid},
        )
