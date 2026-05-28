"""Admin confirmation rules tables + demo custom seed.

Revision ID: 0020_admin_confirmation_rules
Revises: 0019_remove_phase1_prompt_identifiers
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0020_admin_confirmation_rules"
down_revision: str | Sequence[str] | None = "0019_remove_phase1_prompt_identifiers"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_DEMO_CUSTOM = [
    {
        "rule_id": "custom-demo-flash-convert",
        "title": "闪兑 · 大额二次确认",
        "summary": "闪兑单笔名义超过运营阈值时，除常规确认外须再次核对币种与到账信息。",
        "risk_level": "medium",
        "action": "second_confirm",
        "scenarios_json": json.dumps(["convert"], ensure_ascii=False),
        "trigger_conditions_json": json.dumps(
            [{"fieldKey": "nominal_usdt", "operator": "gt", "value": "10,000"}],
            ensure_ascii=False,
        ),
        "default_enabled": True,
    },
    {
        "rule_id": "custom-demo-transfer-otp",
        "title": "资金划出 · OTP 验证",
        "summary": "划出类操作超过一定名义时，须通过 OTP 等第二因素校验后再继续。",
        "risk_level": "high",
        "action": "otp_confirm",
        "scenarios_json": json.dumps(["transfer"], ensure_ascii=False),
        "trigger_conditions_json": json.dumps(
            [{"fieldKey": "nominal_usdt", "operator": "gte", "value": "5,000"}],
            ensure_ascii=False,
        ),
        "default_enabled": True,
    },
    {
        "rule_id": "custom-demo-block-auto-order",
        "title": "条件单机器人模板 · 禁止自动执行",
        "summary": "命中特定高频/网格模板时禁止静默自动落单，须显式确认或人工介入后再执行。",
        "risk_level": "high",
        "action": "block_auto_execute",
        "scenarios_json": json.dumps(["futures", "conditional_order"], ensure_ascii=False),
        "trigger_conditions_json": json.dumps(
            [{"fieldKey": "operation_scope", "operator": "contains", "value": "高频或网格类自动化模板"}],
            ensure_ascii=False,
        ),
        "default_enabled": False,
    },
]


def upgrade() -> None:
    op.create_table(
        "admin_confirmation_rule_custom",
        sa.Column("rule_id", sa.String(length=80), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("scenarios_json", sa.Text(), nullable=False),
        sa.Column("trigger_conditions_json", sa.Text(), nullable=False),
        sa.Column("default_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=True),
    )
    op.create_table(
        "admin_confirmation_rule_enabled",
        sa.Column("rule_id", sa.String(length=80), primary_key=True, nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    t = sa.table(
        "admin_confirmation_rule_custom",
        sa.column("rule_id", sa.String),
        sa.column("title", sa.String),
        sa.column("summary", sa.Text),
        sa.column("risk_level", sa.String),
        sa.column("action", sa.String),
        sa.column("scenarios_json", sa.Text),
        sa.column("trigger_conditions_json", sa.Text),
        sa.column("default_enabled", sa.Boolean),
        sa.column("created_by", sa.String),
    )
    op.bulk_insert(
        t,
        [{**row, "created_by": "seed"} for row in _DEMO_CUSTOM],
    )


def downgrade() -> None:
    op.drop_table("admin_confirmation_rule_enabled")
    op.drop_table("admin_confirmation_rule_custom")
