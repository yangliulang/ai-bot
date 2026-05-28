"""CLI: bootstrap `admin_console_user` for database-backed console login."""

from __future__ import annotations

import argparse
import asyncio
import sys

from sqlalchemy.exc import IntegrityError

from chainup_agent.core.config import get_settings
from chainup_agent.infrastructure.persistence.admin_user_password import hash_password
from chainup_agent.infrastructure.persistence.base import (
    dispose_engine,
    get_engine,
    get_session_factory,
)
from chainup_agent.infrastructure.persistence.models import AdminConsoleUser, Base


def _parse() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Insert one row into admin_console_user. "
            "Apply schema first: `alembic upgrade head` (or --ensure-schema for local dev)."
        ),
    )
    p.add_argument("--username", required=True, help="Login name (unique, stored verbatim)")
    p.add_argument("--password", required=True)
    p.add_argument(
        "--ensure-schema",
        action="store_true",
        help="create_all (dev only; production must use Alembic migrations)",
    )
    return p.parse_args()


async def _run(args: argparse.Namespace) -> int:
    settings = get_settings()
    if settings.admin_console_auth_mode != "database":
        print(
            "warning: set CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE=database for DB-backed login",
            file=sys.stderr,
        )

    engine = get_engine()
    if args.ensure_schema:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    password_hash = hash_password(args.password)
    factory = get_session_factory()
    async with factory() as session:
        session.add(
            AdminConsoleUser(
                username=args.username,
                password_hash=password_hash,
                is_active=True,
            ),
        )
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            print(f"error: username {args.username!r} already exists", file=sys.stderr)
            return 1
    print(f"ok: created admin_console_user {args.username!r}")
    return 0


def main() -> None:
    args = _parse()

    async def _inner() -> int:
        try:
            return await _run(args)
        finally:
            await dispose_engine()

    raise SystemExit(asyncio.run(_inner()))
