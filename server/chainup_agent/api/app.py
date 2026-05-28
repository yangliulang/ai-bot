import logging
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, ProgrammingError
from starlette.exceptions import HTTPException as StarletteHTTPException

from chainup_agent.api.routers.admin_access_control import router as admin_access_control_router
from chainup_agent.api.routers.admin_confirmation_rules import router as admin_confirmation_rules_router
from chainup_agent.api.routers.admin_agent_control import router as admin_agent_control_router
from chainup_agent.api.routers.admin_agent_instances import router as admin_agent_instances_router
from chainup_agent.api.routers.admin_ai_settings import router as admin_ai_settings_router
from chainup_agent.api.routers.admin_observability import router as admin_observability_router
from chainup_agent.api.routers.admin_orchestration import router as admin_orchestration_router
from chainup_agent.api.routers.admin_prompt_safety import router as admin_prompt_safety_router
from chainup_agent.api.routers.admin_prompt_packs import router as admin_prompt_packs_router
from chainup_agent.api.routers.admin_skill_specs import router as admin_skill_specs_router
from chainup_agent.api.routers.admin_tool_registry import router as admin_tool_registry_router
from chainup_agent.api.routers.admin_telegram import router as admin_telegram_router
from chainup_agent.api.routers.admin_trading_bindings import router as admin_trading_bindings_router
from chainup_agent.api.routers.admin_trading_agent_config import (
    router as admin_trading_agent_config_router,
)
from chainup_agent.api.routers.auth import router as auth_router
from chainup_agent.api.routers.health import router as health_router
from chainup_agent.api.routers.internal_confirmation_rules import (
    router as internal_confirmation_rules_router,
)
from chainup_agent.api.routers.internal_prompts import router as internal_prompts_router
from chainup_agent.api.routers.internal_skills import router as internal_skills_router
from chainup_agent.api.routers.me_agent import router as me_agent_router
from chainup_agent.api.routers.v1.agent import router as agent_v1_router
from chainup_agent.api.routers.v1.agent_trade_spot import router as agent_trade_spot_router
from chainup_agent.api.routers.v1.agent_trade_futures import router as agent_trade_futures_router
from chainup_agent.api.routers.v1.agent_trade_margin import router as agent_trade_margin_router
from chainup_agent.api.routers.v1.agent_trading_reconcile import (
    router as agent_trading_reconcile_router,
)
from chainup_agent.api.routers.v1.runtime_memory import router as runtime_memory_router
from chainup_agent.api.routers.v1.runtime_skill import router as runtime_skill_router
from chainup_agent.api.routers.webhook import router as webhook_router
from chainup_agent.api.schemas.common import ErrorBody
from chainup_agent.core.config import get_settings
from chainup_agent.core.errors import AppError
from chainup_agent.core.logging import setup_logging
from chainup_agent.infrastructure.db_schema_drift import is_missing_admin_ai_model_api_model_column
from chainup_agent.infrastructure.persistence.base import dispose_engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    try:
        from chainup_agent.application.admin_trading_agent_config import (
            read_trading_agent_config_bundle,
        )
        from chainup_agent.infrastructure.persistence.base import get_session_factory

        factory = get_session_factory()
        async with factory() as session:
            await read_trading_agent_config_bundle(session)
    except Exception:
        logger.warning("trading_agent_config_bundle preload skipped", exc_info=True)
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()
    app = FastAPI(
        title="ChainUp AI Agent API",
        description=(
            "Coobit Agent runtime — HTTP surface for Telegram, onboarding, "
            "routing, access, execution. "
            "Date-time fields in JSON are UTC unless a field description states otherwise; "
            "see server/docs/BACKEND_SPEC.md §2.1."
        ),
        version="0.1.0",
        lifespan=lifespan,
        debug=settings.debug,
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["x-request-id"] = rid
        return response

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        rid = getattr(request.state, "request_id", "unknown")
        body = ErrorBody(
            code=exc.code,
            message=exc.message,
            request_id=rid,
            details=exc.details or None,
        )
        return JSONResponse(status_code=exc.status_code, content=body.model_dump(exclude_none=True))

    @app.exception_handler(StarletteHTTPException)
    async def http_exc_handler(request: Request, exc: StarletteHTTPException):
        rid = getattr(request.state, "request_id", "unknown")
        detail = exc.detail
        message = detail if isinstance(detail, str) else str(detail)
        body = ErrorBody(code=f"HTTP_{exc.status_code}", message=message, request_id=rid)
        return JSONResponse(status_code=exc.status_code, content=body.model_dump(exclude_none=True))

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        rid = getattr(request.state, "request_id", "unknown")
        body = ErrorBody(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            request_id=rid,
            details={"errors": exc.errors()},
        )
        return JSONResponse(status_code=422, content=body.model_dump(exclude_none=True))

    async def _sqlalchemy_db_api_handler(
        request: Request,
        exc: OperationalError | ProgrammingError,
    ):
        """Map common «code deployed ahead of migrations» faults to readable JSON."""
        rid = getattr(request.state, "request_id", "unknown")
        if is_missing_admin_ai_model_api_model_column(exc):
            body = ErrorBody(
                code="AGENT_DB_SCHEMA_OUT_OF_DATE",
                message=(
                    "数据库结构与当前服务端版本不匹配：请先执行 alembic 迁移升级"
                    "（须包含迁移 0017_admin_ai_model_api_model，"
                    "为 admin_ai_model 增加 api_model 列）。"
                ),
                request_id=rid,
                details={
                    "run": "cd server && uv run alembic upgrade head",
                    "migrationHint": "0017_admin_ai_model_api_model",
                },
            )
            return JSONResponse(status_code=503, content=body.model_dump(exclude_none=True))
        logger.error(
            "Unhandled SQLAlchemy DBAPI error rid=%s",
            rid,
            exc_info=exc,
        )
        body = ErrorBody(
            code="DATABASE_ERROR",
            message="Database error（详见服务端日志；勿向客户端暴露明细）",
            request_id=rid,
        )
        return JSONResponse(status_code=500, content=body.model_dump(exclude_none=True))

    app.add_exception_handler(OperationalError, _sqlalchemy_db_api_handler)
    app.add_exception_handler(ProgrammingError, _sqlalchemy_db_api_handler)

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(internal_prompts_router)
    app.include_router(internal_skills_router)
    app.include_router(internal_confirmation_rules_router)
    app.include_router(webhook_router)
    app.include_router(agent_v1_router)
    app.include_router(agent_trade_spot_router)
    app.include_router(agent_trade_futures_router)
    app.include_router(agent_trade_margin_router)
    app.include_router(agent_trading_reconcile_router)
    app.include_router(runtime_skill_router)
    app.include_router(runtime_memory_router)
    app.include_router(me_agent_router)
    app.include_router(admin_telegram_router)
    app.include_router(admin_ai_settings_router)
    app.include_router(admin_prompt_packs_router)
    app.include_router(admin_skill_specs_router)
    app.include_router(admin_tool_registry_router)
    app.include_router(admin_prompt_safety_router)
    app.include_router(admin_agent_control_router)
    app.include_router(admin_agent_instances_router)
    app.include_router(admin_observability_router)
    app.include_router(admin_orchestration_router)
    app.include_router(admin_trading_bindings_router)
    app.include_router(admin_access_control_router)
    app.include_router(admin_confirmation_rules_router)
    app.include_router(admin_trading_agent_config_router)
    return app
