"""Shared helpers for skill operation spec tests."""

from __future__ import annotations

import pytest

from chainup_agent.application.skill_operation_spec_store import import_runtime_bundle
from chainup_agent.infrastructure.persistence.base import get_session_factory


async def seed_skill_operation_specs_from_bundle() -> None:
    factory = get_session_factory()
    async with factory() as session:
        await import_runtime_bundle(session)
        await session.commit()


async def init_binding_sqlite_with_skill_specs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    fernet_key: str,
) -> None:
    """Fresh binding DB + published skill pointers (write-path tests swap DATABASE_URL)."""
    from tests.test_api import _init_binding_sqlite

    await _init_binding_sqlite(monkeypatch, tmp_path, fernet_key)
    await seed_skill_operation_specs_from_bundle()
