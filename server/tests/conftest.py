from collections.abc import AsyncIterator
from pathlib import Path

import chainup_agent.infrastructure.persistence.models  # noqa: F401 — register models for create_all
import pytest
from chainup_agent.core.config import reset_settings_cache
from chainup_agent.infrastructure.persistence.base import dispose_engine
from chainup_agent.infrastructure.persistence.models.base import Base
from chainup_agent.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine


@pytest.fixture(autouse=True)
def _hermetic_sqlite_schema(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Isolate each test DB under ``tmp_path`` and create schema (avoids stale repo-root sqlite)."""
    db_file = (tmp_path / "pytest_chainup_agent.sqlite3").resolve()
    monkeypatch.setenv("CHAINUP_AGENT_DATABASE_URL", f"sqlite+aiosqlite:///{db_file.as_posix()}")
    reset_settings_cache()
    sync_engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()


@pytest.fixture(autouse=True)
async def _dispose_engine_between_tests() -> None:
    yield
    await dispose_engine()


@pytest.fixture(autouse=True)
def _reset_settings() -> None:
    reset_settings_cache()
    yield
    reset_settings_cache()


@pytest.fixture(autouse=True)
def _admin_console_jwt_secret_cleared_for_http_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """Most API tests expect Admin routes without Bearer; bearer-specific tests override this."""
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET", "")


@pytest.fixture(autouse=True)
def _intent_nlu_llm_off_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHAINUP_AGENT_INTENT_NLU_USE_LLM", "false")


@pytest.fixture
async def http_client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
