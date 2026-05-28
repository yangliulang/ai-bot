"""Regression: ORM/table drift (migration not applied) — readable errors instead of raw 500."""

from __future__ import annotations

import sqlite3

import pytest
from chainup_agent.infrastructure.db_schema_drift import is_missing_admin_ai_model_api_model_column
from httpx import AsyncClient
from sqlalchemy.exc import OperationalError


def test_detector_sqlite_missing_api_model_column() -> None:
    orig = sqlite3.OperationalError("no such column: admin_ai_model.api_model")
    exc = OperationalError("SELECT ... FROM admin_ai_model", {}, orig)
    assert is_missing_admin_ai_model_api_model_column(exc)


def test_detector_postgresql_missing_api_model_column() -> None:
    exc = OperationalError("", {}, RuntimeError("column admin_ai_model.api_model does not exist"))
    assert is_missing_admin_ai_model_api_model_column(exc)


@pytest.mark.parametrize(
    "msg",
    [
        "ProgrammingError: column api_model doesn't exist",
        "Unknown column 'api_model'",
    ],
)
def test_detector_variants_mysqlish(msg: str) -> None:
    exc = OperationalError("", {}, RuntimeError(msg))
    assert is_missing_admin_ai_model_api_model_column(exc)


def test_detector_false_for_unrelated_sqlite_error() -> None:
    orig = sqlite3.OperationalError("no such table: imaginary")
    exc = OperationalError("SELECT", {}, orig)
    assert not is_missing_admin_ai_model_api_model_column(exc)


@pytest.mark.asyncio
async def test_admin_ai_models_503_when_query_reports_missing_api_model_column(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Simulates deployed code ahead of alembic 0017; handler maps to structured 503."""

    async def list_models_reports_schema_drift(_session: object, _provider_id: str | None):
        raise OperationalError(
            "SELECT admin_ai_model.api_model FROM admin_ai_model",
            {},
            sqlite3.OperationalError("sqlite3: no such column: admin_ai_model.api_model"),
        )

    monkeypatch.setattr(
        "chainup_agent.api.routers.admin_ai_settings.list_models",
        list_models_reports_schema_drift,
    )
    r = await http_client.get("/api/v1/admin/ai/models")
    assert r.status_code == 503
    j = r.json()
    assert j["code"] == "AGENT_DB_SCHEMA_OUT_OF_DATE"
    assert "0017" in (j["message"] or "")
    assert j.get("details", {}).get("migrationHint") == "0017_admin_ai_model_api_model"
