"""Seed TRADING prompt packs for balance / wealth Telegram LLM narration.

Revision ID: 0016_read_account_balance_wealth_trading_prompt_seed
Revises: 0015_read_market_depth_trades_trading_prompt_seed
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0016_read_account_balance_wealth_trading_prompt_seed"
down_revision: str | Sequence[str] | None = "0015_read_market_depth_trades_trading_prompt_seed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_READ_ACCOUNT_BALANCE_TRADING = (
    "你是 **账户余额只读摘要**助手：**仅依据**运行时注入的 "
    "**`RUNTIME_CONTEXT_JSON`** 中的 **`exchangeReadPreview`**"
    "（绑定用户 GET /sapi/v1/account 摘要，已脱敏）与用户问题作答。"
    "\n**严禁**编造未出现在快照中的资产或数量；"
    "**禁止**索要 API Secret、投资建议或代收验证码。"
    "**简短** **2～8 句**。"
)
_WEALTH_HOLDINGS_TRADING = (
    "你是 **理财/OTC 持仓只读摘要**助手：**仅依据**运行时注入的 "
    "**`RUNTIME_CONTEXT_JSON`** 中的 **`exchangeReadPreview`**"
    "（绑定用户 account/by_type 摘要）作答。"
    "\n严禁编造快照中不存在的条目或金额。**禁止**投资建议。**简短** **2～8 句**。"
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

    bal_msgs = json.dumps(
        [
            {"role": "system", "content": _READ_ACCOUNT_BALANCE_TRADING.strip()},
            {"role": "user", "content": "示例：我 USDT 可用大概多少？"},
            {
                "role": "assistant",
                "content": (
                    "请仅根据 exchangeReadPreview 中的余额条目回答；"
                    "若没有 USDT 或字段缺失则说明快照未包含。"
                ),
            },
        ],
        ensure_ascii=False,
    )
    wh_msgs = json.dumps(
        [
            {"role": "system", "content": _WEALTH_HOLDINGS_TRADING.strip()},
            {"role": "user", "content": "示例：理财侧有哪些币种有余额？"},
            {
                "role": "assistant",
                "content": "请仅列出快照中出现的资产概要；为空则说明接口未返回持券。",
            },
        ],
        ensure_ascii=False,
    )
    _upsert(
        "pack_trading_read_account_balance_v1",
        "TRADING",
        "read.account.balance",
        'W/"read-account-balance-trading-seed-1"',
        bal_msgs,
    )
    _upsert(
        "pack_trading_wealth_holdings_read_v1",
        "TRADING",
        "wealth.holdings_read",
        'W/"wealth-holdings-read-trading-seed-1"',
        wh_msgs,
    )


def downgrade() -> None:
    bind = op.get_bind()
    for pid in (
        "pack_trading_read_account_balance_v1",
        "pack_trading_wealth_holdings_read_v1",
    ):
        bind.execute(
            sa.text("DELETE FROM admin_prompt_pack WHERE prompt_pack_id = :pid"),
            {"pid": pid},
        )
