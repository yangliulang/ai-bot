"""Rename prompt pack / platform scenario ids — drop ``phase1`` stage markers.

Revision ID: 0019_remove_phase1_prompt_identifiers
Revises: 0018_spot_trade_trading_prompt_seed
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0019_remove_phase1_prompt_identifiers"
down_revision: str | Sequence[str] | None = "0018_spot_trade_trading_prompt_seed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_PACK_ID_RENAMES: tuple[tuple[str, str], ...] = (
    ("pack_phase1_platform_system_v1", "pack_platform_system_v1"),
    ("pack_phase1_platform_safety_v1", "pack_platform_safety_v1"),
    ("pack_trading_chat_faq_phase1_v1", "pack_trading_chat_faq_v1"),
    ("pack_trading_read_market_ticker_phase1_v1", "pack_trading_read_market_ticker_v1"),
    ("pack_trading_read_market_depth_phase1_v1", "pack_trading_read_market_depth_v1"),
    ("pack_trading_read_market_trades_phase1_v1", "pack_trading_read_market_trades_v1"),
    ("pack_trading_read_account_balance_phase1_v1", "pack_trading_read_account_balance_v1"),
    ("pack_trading_wealth_holdings_read_phase1_v1", "pack_trading_wealth_holdings_read_v1"),
    ("pack_trading_spot_flash_convert_phase1_v1", "pack_trading_spot_flash_convert_v1"),
    ("pack_trading_spot_limit_order_phase1_v1", "pack_trading_spot_limit_order_v1"),
)

_SCENARIO_ID_RENAMES: tuple[tuple[str, str], ...] = (
    ("agent.runtime.phase1_platform_system", "agent.runtime.platform_system"),
    ("agent.runtime.phase1_platform_safety", "agent.runtime.platform_safety"),
)


def _rename_pack_ids(bind: sa.Connection, pairs: tuple[tuple[str, str], ...]) -> None:
    for old_id, new_id in pairs:
        exists_new = bind.execute(
            sa.text("SELECT 1 FROM admin_prompt_pack WHERE prompt_pack_id = :nid LIMIT 1"),
            {"nid": new_id},
        ).fetchone()
        exists_old = bind.execute(
            sa.text("SELECT 1 FROM admin_prompt_pack WHERE prompt_pack_id = :oid LIMIT 1"),
            {"oid": old_id},
        ).fetchone()
        if exists_old and not exists_new:
            bind.execute(
                sa.text(
                    "UPDATE admin_prompt_pack SET prompt_pack_id = :nid WHERE prompt_pack_id = :oid"
                ),
                {"nid": new_id, "oid": old_id},
            )
        elif exists_old and exists_new:
            bind.execute(
                sa.text("DELETE FROM admin_prompt_pack WHERE prompt_pack_id = :oid"),
                {"oid": old_id},
            )


def _rename_scenario_ids(bind: sa.Connection, pairs: tuple[tuple[str, str], ...]) -> None:
    for old_sid, new_sid in pairs:
        bind.execute(
            sa.text(
                """
                UPDATE admin_prompt_pack
                SET scenario_id = :nsid
                WHERE scenario_id = :osid
                """
            ),
            {"nsid": new_sid, "osid": old_sid},
        )


def _scrub_messages_json(bind: sa.Connection) -> None:
    bind.execute(
        sa.text(
            """
            UPDATE admin_prompt_pack
            SET messages_json = REPLACE(
                REPLACE(
                    REPLACE(messages_json, 'PHASE1_RUNTIME_CONTEXT_JSON', 'RUNTIME_CONTEXT_JSON'),
                    '（Phase1）', ''
                ),
                'Phase1 ', ''
            )
            WHERE messages_json LIKE '%Phase1%' OR messages_json LIKE '%PHASE1_%'
            """
        )
    )


def upgrade() -> None:
    bind = op.get_bind()
    _rename_pack_ids(bind, _PACK_ID_RENAMES)
    _rename_scenario_ids(bind, _SCENARIO_ID_RENAMES)
    _scrub_messages_json(bind)
    bind.execute(
        sa.text(
            """
            UPDATE agent_instance
            SET template_id = 'tmpl_agent_default'
            WHERE template_id = 'tmpl_phase1_default'
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            UPDATE agent_instance
            SET template_id = 'tmpl_phase1_default'
            WHERE template_id = 'tmpl_agent_default'
            """
        )
    )
    _rename_scenario_ids(bind, tuple((b, a) for a, b in _SCENARIO_ID_RENAMES))
    _rename_pack_ids(bind, tuple((b, a) for a, b in _PACK_ID_RENAMES))
