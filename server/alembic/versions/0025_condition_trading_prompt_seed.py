"""Seed TRADING prompt pack for futures condition order (Phase 2.5).

Revision ID: 0025_condition_trading_prompt_seed
Revises: 0024_margin_trading_prompt_seed
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0025_condition_trading_prompt_seed"
down_revision: str | Sequence[str] | None = "0024_margin_trading_prompt_seed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_CONDITION_TRADING = (
    "你是 **合约条件单 / 止盈止损** 助手：帮助用户理解 **触发价、触发方向（3UP/4DOWN）"
    "与触发后委托类型（市价/限价）**。"
    "\n**仅依据**运行时上下文与用户原文；**禁止**编造已挂单或成交价；**禁止**投资建议。"
    "**须**说明条件单与即时挂单不同、触发前不在盘口展示；**不得**代替用户完成 Type-A 确认。"
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
            {"role": "system", "content": _CONDITION_TRADING.strip()},
            {"role": "user", "content": "示例：BTC 触发价 91000 上涨触发后市价平多要注意什么？"},
            {
                "role": "assistant",
                "content": (
                    "说明触发条件区块须先核对；91000 上涨触发（3UP）后市价平仓与即时单不同，"
                    "触发前不会在盘口展示；请完成 Type-A 确认后再提交，不代替下单。"
                ),
            },
        ],
        ensure_ascii=False,
    )
    _upsert(
        "pack_trading_automation_condition_order_v1",
        "TRADING",
        "automation.condition_order",
        'W/"condition-order-v1"',
        msgs,
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "DELETE FROM admin_prompt_pack WHERE prompt_pack_id = :pid"
        ),
        {"pid": "pack_trading_automation_condition_order_v1"},
    )
