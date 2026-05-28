"""skill_operation_spec tables + runtime-bundle seed.

Revision ID: 0029_skill_operation_spec_publish
Revises: 0028_agent_instance_activation_welcome
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import sqlalchemy as sa
from alembic import op

revision: str = "0029_skill_operation_spec_publish"
down_revision: str | Sequence[str] | None = "0028_agent_instance_activation_welcome"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_BUNDLE = (
    Path(__file__).resolve().parents[2]
    / "chainup_agent"
    / "data"
    / "skill_specs"
    / "runtime-bundle.json"
)


def upgrade() -> None:
    op.create_table(
        "skill_operation_spec_version",
        sa.Column("skill_id", sa.String(128), primary_key=True),
        sa.Column("skill_spec_version", sa.String(64), primary_key=True),
        sa.Column("lifecycle", sa.String(16), nullable=False, server_default="PUBLISHED"),
        sa.Column("body_markdown", sa.Text(), nullable=False),
        sa.Column("spec_digest", sa.String(64), nullable=False),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("source_git_ref", sa.String(256), nullable=True),
        sa.Column("contract_complete", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index(
        "idx_skill_operation_spec_version_published",
        "skill_operation_spec_version",
        ["skill_id", "published_at"],
    )
    op.create_table(
        "skill_operation_spec_pointer",
        sa.Column("skill_id", sa.String(128), primary_key=True),
        sa.Column("skill_spec_version", sa.String(64), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    if not _BUNDLE.is_file():
        return
    raw = json.loads(_BUNDLE.read_text(encoding="utf-8"))
    items = raw.get("items") if isinstance(raw, dict) else []
    bind = op.get_bind()
    for it in items:
        if not isinstance(it, dict):
            continue
        skill_id = str(it.get("skillId") or "").strip()
        version = str(it.get("skillSpecVersion") or "").strip()
        body = str(it.get("bodyMarkdown") or "")
        if not skill_id or not version or not body.strip():
            continue
        digest = str(it.get("specDigest") or "").strip()
        if not digest:
            import hashlib

            digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        bind.execute(
            sa.text(
                """
                INSERT INTO skill_operation_spec_version (
                    skill_id, skill_spec_version, lifecycle, body_markdown,
                    spec_digest, contract_complete
                ) VALUES (
                    :skill_id, :version, 'PUBLISHED', :body, :digest, 1
                )
                ON CONFLICT(skill_id, skill_spec_version) DO NOTHING
                """
            ),
            {
                "skill_id": skill_id,
                "version": version,
                "body": body,
                "digest": digest,
            },
        )
        bind.execute(
            sa.text(
                """
                INSERT INTO skill_operation_spec_pointer (skill_id, skill_spec_version)
                VALUES (:skill_id, :version)
                ON CONFLICT(skill_id) DO UPDATE SET
                    skill_spec_version = excluded.skill_spec_version,
                    updated_at = CURRENT_TIMESTAMP
                """
            ),
            {"skill_id": skill_id, "version": version},
        )


def downgrade() -> None:
    op.drop_table("skill_operation_spec_pointer")
    op.drop_table("skill_operation_spec_version")
