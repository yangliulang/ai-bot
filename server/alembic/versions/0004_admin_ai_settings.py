"""Admin AI Settings — providers, models, gateway/health JSON documents.

Revision ID: 0004_aisettings
Revises: 0003_ai
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_aisettings"
down_revision: str | Sequence[str] | None = "0003_ai"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admin_ai_provider",
        sa.Column("provider_id", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("base_url", sa.String(length=512), nullable=False),
        sa.Column("secret_ref", sa.String(length=512), nullable=True),
        sa.Column("row_version", sa.BigInteger(), server_default="1", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("provider_id"),
    )
    op.create_table(
        "admin_ai_model",
        sa.Column("model_id", sa.String(length=128), nullable=False),
        sa.Column("provider_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="enabled", nullable=False),
        sa.Column("context_window_tokens", sa.BigInteger(), nullable=True),
        sa.Column("row_version", sa.BigInteger(), server_default="1", nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["admin_ai_provider.provider_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("model_id"),
    )
    op.create_index(op.f("ix_admin_ai_model_provider_id"), "admin_ai_model", ["provider_id"], unique=False)
    op.create_table(
        "admin_ai_document",
        sa.Column("doc_key", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.String(length=65536), nullable=False),
        sa.Column("row_version", sa.BigInteger(), server_default="1", nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("doc_key"),
    )

    bind = op.get_bind()
    _gateway_seed = {
        "defaultProviderId": "demo",
        "defaultModelId": "gpt-4.1-mini",
        "orchestrationExecutionBudget": {
            "maxToolCallsPerExecution": 32,
            "maxOrchestrationStepsPerExecution": 32,
            "maxModelTurnsPerExecution": None,
        },
        "defaultInferenceModel": "gpt-4.1",
        "scenarioChatModel": "gpt-4.1-mini",
        "scenarioTradingModel": "gpt-4.1",
        "scenarioRiskModel": "gpt-4.1",
        "maxContextTokens": 128000,
        "maxOutputTokens": 4096,
        "timeoutSec": 120,
        "fallbackOnPrimaryFailure": True,
        "fallbackOnTimeout": True,
        "downgradePeakTraffic": False,
        "fallbackModel": "gpt-4.1-mini",
        "maxTokensPerRequest": 32000,
        "dailyTokenBudgetM": 50,
        "rateLimitRpm": 600,
    }
    bind.execute(
        sa.text(
            "INSERT INTO admin_ai_document (doc_key, payload_json, row_version) "
            "VALUES (:k, :p, 1)"
        ),
        {"k": "gateway_defaults", "p": json.dumps(_gateway_seed, ensure_ascii=False)},
    )
    bind.execute(
        sa.text(
            "INSERT INTO admin_ai_document (doc_key, payload_json, row_version) "
            "VALUES (:k, :p, 1)"
        ),
        {"k": "health_policy", "p": "{}"},
    )
    bind.execute(
        sa.text(
            "INSERT INTO admin_ai_provider "
            "(provider_id, display_name, base_url, secret_ref, row_version) "
            "VALUES (:id, :dn, :bu, NULL, 1)"
        ),
        {
            "id": "demo",
            "dn": "Demo OpenAI-compatible",
            "bu": "https://api.openai.com/v1",
        },
    )
    for mid, ctx in (
        ("gpt-4.1", 1_000_000),
        ("gpt-4.1-mini", 128_000),
        ("claude-3.5-sonnet", 200_000),
        ("gemini-1.5-pro", 1_000_000),
    ):
        bind.execute(
            sa.text(
                "INSERT INTO admin_ai_model "
                "(model_id, provider_id, status, context_window_tokens, row_version) "
                "VALUES (:mid, 'demo', 'enabled', :ctx, 1)"
            ),
            {"mid": mid, "ctx": ctx},
        )


def downgrade() -> None:
    op.drop_table("admin_ai_document")
    op.drop_index(op.f("ix_admin_ai_model_provider_id"), table_name="admin_ai_model")
    op.drop_table("admin_ai_model")
    op.drop_table("admin_ai_provider")
