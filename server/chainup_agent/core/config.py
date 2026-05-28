from functools import lru_cache
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CHAINUP_AGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = Field(default="development", description="environment name")
    debug: bool = Field(default=False)

    api_host: str = "0.0.0.0"
    api_port: int = 8080

    log_json: bool = Field(
        default=False,
        description="If true, emit structured JSON logs; otherwise plain text",
    )

    database_url: str = Field(
        default="sqlite+aiosqlite:///./db/chainup_agent.sqlite3",
        description="SQLAlchemy async URL (dev default: SQLite under ./db; run API from server/)",
    )

    public_base_url: str = Field(
        default="http://localhost:8080",
        description="External base URL for webhook registration helpers",
    )

    telegram_bot_token: str = Field(
        default="",
        description=(
            "Telegram Bot API token — local/dev only via .env; never log or expose to SPA; "
            "rotate via BotFather if leaked"
        ),
    )

    telegram_bind_page_url: str = Field(
        default="",
        description=(
            "Deeplink/H5 landing where the user completes Telegram ↔ account binding; "
            "inbound webhook echoes this URL in plaintext and as InlineKeyboard when chat is "
            "not treated as bound. Use http(s) URL; empty disables link/button."
        ),
    )

    telegram_bound_chat_allowlist: str = Field(
        default="",
        description=(
            "联调专用: comma-separated Telegram chat_id values treated as already bound "
            "(no persistence). Empty means every chat gets the bind deeplink until real binding "
            "storage ships (roadmap §1.1 APIs). "
            "Legacy env: CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST."
        ),
    )

    @model_validator(mode="before")
    @classmethod
    def _inherit_legacy_telegram_bound_chat_allowlist(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        if str(data.get("telegram_bound_chat_allowlist") or "").strip():
            return data
        legacy = data.get("telegram_phase1_bound_chat_ids")
        if legacy is None:
            import os

            legacy = os.environ.get("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST")
        if legacy is not None and str(legacy).strip():
            merged = dict(data)
            merged["telegram_bound_chat_allowlist"] = str(legacy).strip()
            return merged
        return data

    telegram_webhook_inline_processing: bool = Field(
        default=False,
        description=(
            "When true, handle Telegram webhook updates inline before returning HTTP 200 "
            "(no FastAPI BackgroundTasks). Use when the host freezes/stops work after the "
            "response (e.g. some serverless) so sendMessage still runs. Trade-off: slower ACK "
            "to Telegram if LLM/routing is slow."
        ),
    )

    telegram_bot_api_transport_retries: int = Field(
        default=2,
        ge=0,
        le=8,
        description=(
            "On transient Telegram Bot API transport failures (ConnectError, timeouts, proxy), "
            "retry up to this many **additional** attempts after the first (exponential backoff). "
            "Does not fix blocked egress; set HTTPS_PROXY / firewall as needed."
        ),
    )
    telegram_activation_welcome_timeout_sec: float = Field(
        default=10.0,
        ge=1.0,
        le=60.0,
        description="HTTP timeout for post-binding activation welcome sendMessage (seconds).",
    )

    telegram_error_llm_rewrite: bool = Field(
        default=True,
        description=(
            "When true, selected trading-related AppError replies on Telegram use Admin AI "
            "LLM to rewrite messages to friendly Chinese (with fallback to plain text)."
        ),
    )
    telegram_error_llm_timeout_sec: float = Field(
        default=15.0,
        ge=3.0,
        le=60.0,
        description="HTTP timeout for Telegram error-message LLM rewrite (seconds).",
    )

    telegram_intent_preview_in_reply: bool = Field(
        default=False,
        description=(
            "When true, Telegram bound replies append the "
            "'(编排预览) 粗略意图…' debugging line "
            "from _format_faq_hint. Default false for production UX."
        ),
    )

    telegram_llm_narrate_read_market_ticker: bool = Field(
        default=False,
        description=(
            "When true, after a successful Telegram read.market.ticker routing, "
            "invoke the LLM once "
            "with exchange snapshot in runtime_context (ASSEMBLY narration). "
            "Falls back to deterministic lines if LLM unavailable."
        ),
    )

    telegram_llm_narrate_read_market_depth: bool = Field(
        default=False,
        description=(
            "When true, after a successful Telegram read.market.depth routing, "
            "invoke the LLM once "
            "with snapshot in runtime_context (ASSEMBLY). Falls back if LLM unavailable."
        ),
    )

    telegram_llm_narrate_read_market_trades: bool = Field(
        default=False,
        description=(
            "When true, after a successful Telegram read.market.trades routing, "
            "invoke one LLM turn with snapshot in runtime_context "
            "(ASSEMBLY). Falls back if LLM unavailable."
        ),
    )

    telegram_llm_narrate_read_account_balance: bool = Field(
        default=False,
        description=(
            "When true, after a successful Telegram read.account.balance routing, "
            "invoke one LLM turn with exchangeReadPreview in runtime_context "
            "(ASSEMBLY). Falls back if LLM unavailable."
        ),
    )

    telegram_llm_narrate_wealth_holdings_read: bool = Field(
        default=False,
        description=(
            "When true, after a successful Telegram wealth.holdings_read routing, "
            "invoke one LLM turn with snapshot in runtime_context "
            "(ASSEMBLY). Falls back if LLM unavailable."
        ),
    )

    telegram_llm_narrate_spot_flash_confirm: bool = Field(
        default=False,
        description=(
            "When true, before flash Type-A inline keyboard, prepend optional LLM "
            "risk/summary lines (trade.spot.flash_convert TRADING pack); "
            "deterministic confirmation block always follows."
        ),
    )

    telegram_llm_narrate_spot_limit_confirm: bool = Field(
        default=False,
        description=(
            "When true, before limit Type-A inline keyboard, optional LLM preamble "
            "(trade.spot.limit_order); deterministic confirmation always follows."
        ),
    )

    telegram_llm_narrate_futures_market_confirm: bool = Field(
        default=False,
        description=(
            "When true, before futures market Type-A inline keyboard, optional LLM "
            "preamble (trade.futures.market_order TRADING pack); deterministic "
            "confirmation block always follows."
        ),
    )

    telegram_llm_narrate_futures_limit_confirm: bool = Field(
        default=False,
        description=(
            "When true, before futures limit Type-A inline keyboard, optional LLM "
            "preamble (trade.futures.limit_order); deterministic confirmation always "
            "follows."
        ),
    )

    binding_secrets_fernet_key: str = Field(
        default="",
        description=(
            "Fernet key (UTF-8 string from `cryptography.fernet.Fernet.generate_key().decode()`) "
            "used to seal trading API secrets in `telegram_agent_trading_binding`. "
            "Empty disables POST .../api-binding/confirm persistence (503)."
        ),
    )

    default_agent_template_id: str = Field(
        default="tmpl_agent_default",
        description=(
            "PM Agent template id pinned on instance create (single-template default)"
        ),
    )
    default_agent_template_version: str = Field(
        default="1",
        description="Template version copied onto agent_instance at binding confirm",
    )

    agent_runtime_global_disabled: bool = Field(
        default=False,
        description=(
            "When true, `/api/v1/agent/access/evaluate` denies with AGENT_GLOBAL_OFF "
            "(feature kill-switch)."
        ),
    )

    agent_runtime_ops_suspended: bool = Field(
        default=False,
        description=(
            "When true, eligibility evaluates to AGENT_OPS_SUSPENDED (ops pause without redeploy)."
        ),
    )

    feature_trading: bool = Field(
        default=True,
        description=(
            "Product FEATURE_TRADING: when false, trade.* intents are blocked in "
            "intent policy (POST /intent/recognize plan.nextStep=BLOCKED_FEATURE)."
        ),
    )
    feature_agent_spot: bool = Field(
        default=True,
        description=(
            "Product FEATURE_AGENT_SPOT: when false, trade.spot.flash_convert / "
            "trade.spot.limit_order are blocked at intent policy layer."
        ),
    )

    feature_agent_futures: bool = Field(
        default=True,
        description=(
            "Product FEATURE_AGENT_FUTURES: when false, trade.futures.* writes "
            "are blocked at intent policy and HTTP router."
        ),
    )

    feature_agent_margin: bool = Field(
        default=True,
        description=(
            "Product FEATURE_AGENT_MARGIN: when false, margin.cross.* writes "
            "are blocked at intent policy and HTTP router."
        ),
    )

    trade_spot_limit_price_band_enabled: bool = Field(
        default=False,
        description=(
            "When true, spot LIMIT orders may reject locally if limit price deviates from "
            "public lastPrice by more than trade_spot_limit_price_band_max_pct (FR-T12-style)."
        ),
    )
    trade_spot_limit_price_band_max_pct: float = Field(
        default=5.0,
        ge=0.01,
        le=50.0,
        description="Max percent deviation from lastPrice for LIMIT band guard (when enabled).",
    )

    intent_nlu_use_llm: bool = Field(
        default=False,
        description=(
            "When true (CHAINUP_AGENT_INTENT_NLU_USE_LLM), forces LLM intent NLU before "
            "keyword_v1 even if gateway_defaults.intentNluUseLlm is false. When false, "
            "Admin gateway_defaults.intentNluUseLlm applies (POST /intent/recognize + TG)."
        ),
    )
    intent_nlu_llm_timeout_sec: float = Field(
        default=25.0,
        ge=5.0,
        le=120.0,
        description="HTTP timeout for intent NLU LLM call (seconds).",
    )
    intent_clarify_use_llm: bool = Field(
        default=False,
        description=(
            "When true (CHAINUP_AGENT_INTENT_CLARIFY_USE_LLM), Telegram CLARIFY may "
            "polish rule-based lines via agent.runtime.runtime_clarify; else "
            "gateway_defaults.intentClarifyUseLlm applies."
        ),
    )
    intent_clarify_llm_timeout_sec: float = Field(
        default=20.0,
        ge=5.0,
        le=60.0,
        description="HTTP timeout for clarify LLM polish (seconds).",
    )

    stm_l0_max_turns: int = Field(
        default=10,
        ge=2,
        le=50,
        description="L0 recent turn cap (STM_L0_MAX_TURNS).",
    )
    stm_idle_resume_prompt_sec: int = Field(
        default=1800,
        ge=60,
        le=86400,
        description="Idle seconds before clarify/write L1 goes stale (STM_IDLE_RESUME_PROMPT_SEC).",
    )
    stm_idle_default_policy: Literal["stale_prior_write", "prompt_resume_or_new"] = Field(
        default="stale_prior_write",
        description="STM_IDLE_DEFAULT_POLICY — stale vs blocking resume/new keyboard.",
    )
    stm_clarify_session_ttl_sec: int = Field(
        default=900,
        ge=60,
        le=7200,
        description="ClarifySessionSnapshot.expiresAt default TTL.",
    )
    resume_classifier_mode: Literal["rules_only", "rules_then_llm"] = Field(
        default="rules_then_llm",
        description="RESUME_CLASSIFIER_MODE.",
    )
    resume_classifier_min_confidence: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="RESUME_CLASSIFIER_MIN_CONFIDENCE for resume_prior_write.",
    )
    warm_execution_index_ttl_sec: int = Field(
        default=86400,
        ge=300,
        le=604800,
        description="WARM_EXECUTION_INDEX_TTL_SEC.",
    )
    stm_session_clear_mode: Literal["in_place", "rotate_session_id"] = Field(
        default="in_place",
        description="STM_SESSION_CLEAR_MODE (FR-STM01).",
    )
    stm_hot_recycle_session_idle_sec: int = Field(
        default=86400,
        ge=300,
        le=604800,
        description="STM_HOT_RECYCLE_SESSION_IDLE_SEC.",
    )
    stm_hot_recycle_execution_after_terminal_sec: int = Field(
        default=7200,
        ge=60,
        le=86400,
        description="STM_HOT_RECYCLE_EXECUTION_AFTER_TERMINAL_SEC.",
    )
    read_clarify_session_ttl_sec: int = Field(
        default=600,
        ge=60,
        le=3600,
        description="ReadClarifySessionSnapshot TTL (READ_CLARIFY_SESSION_TTL_SEC).",
    )
    read_clarify_max_turns: int = Field(
        default=2,
        ge=1,
        le=5,
        description="READ_CLARIFY_MAX_TURNS budget.",
    )
    session_inbound_queue_policy: Literal[
        "serial_per_session", "coalesce_latest", "reject_while_busy"
    ] = Field(
        default="serial_per_session",
        description="SESSION_INBOUND_QUEUE_POLICY.",
    )
    session_inbound_queue_max_depth: int = Field(
        default=3,
        ge=1,
        le=20,
        description="SESSION_INBOUND_QUEUE_MAX_DEPTH.",
    )
    session_inbound_coalesce_window_ms: int = Field(
        default=800,
        ge=100,
        le=5000,
        description="SESSION_INBOUND_COALESCE_WINDOW_MS (coalesce_latest only).",
    )
    session_busy_ack_within_ms: int = Field(
        default=800,
        ge=100,
        le=5000,
        description="SESSION_BUSY_ACK_WITHIN_MS typing/progress ack budget.",
    )
    session_max_active_write_executions: int = Field(
        default=1,
        ge=1,
        le=3,
        description="SESSION_MAX_ACTIVE_WRITE_EXECUTIONS.",
    )
    session_block_new_write_on_unknown: bool = Field(
        default=True,
        description="Block new writes while unknown_pending (SESSION_BLOCK_NEW_WRITE_ON_UNKNOWN).",
    )

    admin_panel_username: str = Field(
        default="",
        description="SPA admin login; empty disables /api/auth/login (503)",
    )
    admin_panel_password: str = Field(
        default="",
        description="SPA admin password; pair with admin_panel_username (env mode only)",
    )

    admin_console_auth_mode: Literal["env", "database"] = Field(
        default="env",
        description=(
            "env: single operator from ADMIN_PANEL_USERNAME/PASSWORD; "
            "database: operators in admin_console_user (bcrypt), seed via chainup-agent-seed-admin"
        ),
    )

    admin_console_open_registration: bool = Field(
        default=False,
        description=(
            "database mode only: allow POST /api/auth/register after the first operator exists. "
            "When false (default), only bootstrap registration is permitted "
            "(admin_console_user empty)."
        ),
    )

    admin_console_jwt_secret: str = Field(
        default="",
        description=(
            "When non-empty: POST /api/auth/login returns HS256 JWT access_token and "
            "all /api/v1/admin/* routes require Authorization: Bearer <token>. "
            "When empty (default): legacy opaque token from login — not verifiable server-side."
        ),
    )

    admin_console_access_token_ttl_seconds: int = Field(
        default=43_200,
        ge=60,
        le=86400 * 30,
        description="JWT exp TTL for admin console access_token when JWT secret is set",
    )

    admin_ai_catalog_seed_demo_if_empty: bool = Field(
        default=False,
        description=(
            "When true, empty AI provider catalog triggers demo provider+models seed on "
            "GET /admin/ai endpoints (ORM-only SQLite convenience). "
            "Default false: deletes persist; "
            "use Alembic migration `0004_aisettings` for initial demo data."
        ),
    )

    llm_fallback_api_key: str = Field(
        default="",
        description=(
            "Bearer token used for OpenAI-compatible LLM calls when Admin Provider.secret_ref "
            "is empty, or as fallback after resolving secret_ref. "
            "Prefer secret_ref→env per provider."
        ),
    )

    @field_validator(
        "database_url",
        "telegram_bot_token",
        "telegram_bind_page_url",
        "telegram_bound_chat_allowlist",
        "binding_secrets_fernet_key",
        "default_agent_template_id",
        "default_agent_template_version",
        "llm_fallback_api_key",
        "admin_console_jwt_secret",
    )
    @classmethod
    def _strip_optional_str(cls, v: str) -> str:
        return v.strip()

    @field_validator("admin_console_jwt_secret")
    @classmethod
    def _jwt_secret_min_length_when_set(cls, v: str) -> str:
        s = v.strip()
        if s and len(s) < 16:
            raise ValueError(
                "ADMIN_CONSOLE_JWT_SECRET must be at least 16 characters when non-empty"
            )
        return s

    @field_validator("telegram_bind_page_url")
    @classmethod
    def _bind_page_url_shape(cls, v: str) -> str:
        if not v:
            return v
        if not (v.startswith("https://") or v.startswith("http://")):
            msg = "TELEGRAM_BIND_PAGE_URL must be empty or an http(s) URL"
            raise ValueError(msg)
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def get_effective_settings(base: Settings | None = None) -> Settings:
    """Env Settings + Admin GlobalConfigBundle overrides (hot reload on PATCH)."""
    from chainup_agent.application.memory_runtime_settings import overlay_settings

    return overlay_settings(base)


def reset_settings_cache() -> None:
    get_settings.cache_clear()
