"""Detect common ORM-vs-DB mismatches after deploy without ``alembic upgrade``."""

from __future__ import annotations


def is_missing_admin_ai_model_api_model_column(exc: BaseException) -> bool:
    """
    True when the DB was not migrated past ``0017_admin_ai_model_api_model``.

    SQLAlchemy propagates dialect-specific DBAPI errors wrapped in `.orig`
    / `__cause__`; message shapes differ (SQLite vs PostgreSQL vs MySQL).
    """
    parts: list[str] = [str(exc)]
    cause = getattr(exc, "__cause__", None)
    if cause is not None:
        parts.append(str(cause))
    orig = getattr(exc, "orig", None)
    if orig is not None:
        parts.append(str(orig))
    t = " ".join(parts).lower()
    if "api_model" not in t:
        return False
    return (
        "no such column" in t
        or "does not exist" in t
        or "doesn't exist" in t
        or "unknown column" in t
        # MySQL-ish / generic SQLSTATE phrasing seen in adapters
        or ("column" in t and "api_model" in t and ("not exist" in t or "undefined" in t))
    )
