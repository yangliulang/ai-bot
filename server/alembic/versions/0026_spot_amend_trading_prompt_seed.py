"""Seed TRADING prompt pack for spot logical amend (Phase 2.x).

Revision ID: 0026_spot_amend_trading_prompt_seed
Revises: 0025_condition_trading_prompt_seed
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0026_spot_amend_trading_prompt_seed"
down_revision: str | Sequence[str] | None = "0025_condition_trading_prompt_seed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_AMEND_TRADING = (
    "你是 **现货逻辑改单** 助手：帮助用户理解 **在途限价委托改价/改量** 须 **一次 Type-A 确认后** "
    "**先撤原单再挂新单**（**非**交易所原生 amend）。"
    "\n**仅依据**运行时上下文与用户原文；**禁止**编造已改单成功或新单号；**禁止**投资建议。"
    "**须**说明新旧参数对比与「先撤销再挂单」语义；**不得**代替用户点击确认。"
    "**简短** **2～6 句**。"
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

    msgs = json.dumps(
        [
            {"role": "system", "content": _AMEND_TRADING.strip()},
            {
                "role": "user",
                "content": "示例：BTC-USDT 订单号 256609229205684228 改价 65000",
            },
            {
                "role": "assistant",
                "content": (
                    "逻辑改单须核对原单与新限价；确认后将先撤销原委托再提交新限价单，"
                    "并非交易所一键 amend；请完成 Type-A「确认修改」后再执行。"
                ),
            },
        ],
        ensure_ascii=False,
    )
    _upsert(
        "pack_trading_spot_amend_limit_order_v1",
        "TRADING",
        "trade.spot.amend_limit_order",
        "etag_trading_spot_amend_limit_order_v1",
        msgs,
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "DELETE FROM admin_prompt_pack WHERE prompt_pack_id = :pid"
        ),
        {"pid": "pack_trading_spot_amend_limit_order_v1"},
    )
