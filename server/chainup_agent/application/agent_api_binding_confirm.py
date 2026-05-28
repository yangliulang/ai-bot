"""Apply trading API binding after successful validate (exchange probe)."""

from __future__ import annotations

from datetime import UTC, datetime

from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_api_binding import validate_agent_trading_api_keys_or_raise
from chainup_agent.application.agent_instance import upsert_agent_instance_for_telegram_binding
from chainup_agent.application.telegram_activation_welcome import (
    ActivationWelcomeOutcome,
    dispatch_activation_welcome,
)
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.exchange.coobit_openapi import normalize_openapi_base_url
from chainup_agent.infrastructure.persistence.models.agent_instance import AgentInstance
from chainup_agent.infrastructure.persistence.models.telegram_agent_trading_binding import (
    TelegramAgentTradingBinding,
)
from chainup_agent.infrastructure.security.field_encryption import (
    decrypt_json_plaintext,
    encrypt_json_plaintext,
)


def _fernet_key_bytes(settings: Settings) -> bytes:
    raw = settings.binding_secrets_fernet_key.strip()
    if not raw:
        raise AppError(
            code="AGENT_BINDING_STORAGE_UNAVAILABLE",
            message="服务未配置 CHAINUP_AGENT_BINDING_SECRETS_FERNET_KEY，无法托管 API 密钥",
            status_code=503,
        )
    key = raw.encode("utf-8")
    try:
        Fernet(key)
    except ValueError as e:
        raise AppError(
            code="AGENT_BINDING_FERNET_KEY_INVALID",
            message="CHAINUP_AGENT_BINDING_SECRETS_FERNET_KEY 不是合法的 Fernet 密钥",
            status_code=503,
            details={"hint": "使用 cryptography.fernet.Fernet.generate_key().decode() 生成"},
        ) from e
    return key


def decrypt_binding_trade_credentials_for_row(
    settings: Settings,
    row: TelegramAgentTradingBinding,
) -> tuple[str, str, str]:
    """Unseal credentials for outbound exchange reads (same baseUrl + keys as probe)."""
    key_bytes = _fernet_key_bytes(settings)
    try:
        bag = decrypt_json_plaintext(key_bytes, row.trading_credentials_sealed)
    except ValueError as e:
        raise AppError(
            code="AGENT_BINDING_CREDENTIALS_UNAVAILABLE",
            message="绑定凭据不可用或与当前密钥不匹配，请用户重新绑定。",
            status_code=503,
            details={"bindingId": row.id},
        ) from e
    ak = (bag.get("api_key") or "").strip()
    sk = (bag.get("secret_key") or "").strip()
    if not ak or not sk:
        raise AppError(
            code="AGENT_BINDING_CREDENTIALS_UNAVAILABLE",
            message="托管凭据不完整，请用户重新完成绑定流程。",
            status_code=503,
            details={"bindingId": row.id},
        )
    openapi = normalize_openapi_base_url(row.openapi_base_url)
    return openapi, ak, sk


def _parse_telegram_user_id(telegram: dict[str, str] | None) -> int:
    if not telegram:
        raise AppError(
            code="AGENT_TELEGRAM_CONTEXT_REQUIRED",
            message="保存绑定须携带 telegram 上下文（含 tg_id）",
            status_code=400,
        )
    tid = telegram.get("tg_id", "").strip()
    if not tid:
        raise AppError(
            code="AGENT_TELEGRAM_CONTEXT_REQUIRED",
            message="telegram.tg_id 不可为空",
            status_code=400,
        )
    try:
        return int(tid)
    except ValueError as e:
        raise AppError(
            code="AGENT_TELEGRAM_CONTEXT_INVALID",
            message="telegram.tg_id 须为数值字符串",
            status_code=400,
            details={"tg_id": tid[:32]},
        ) from e


def _tg_optional(telegram: dict[str, str] | None, key: str, max_len: int) -> str | None:
    if not telegram:
        return None
    v = telegram.get(key)
    if v is None or not str(v).strip():
        return None
    return str(v).strip()[:max_len]


async def confirm_agent_trading_api_binding(
    *,
    session: AsyncSession,
    settings: Settings,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    sub_account_id: str | None,
    telegram: dict[str, str] | None,
    idempotency_key: str | None = None,
    deeplink_token: str | None = None,
) -> tuple[TelegramAgentTradingBinding, bool, str, ActivationWelcomeOutcome]:
    await validate_agent_trading_api_keys_or_raise(
        openapi_base_url=openapi_base_url,
        api_key=api_key,
        secret_key=secret_key,
        sub_account_id=sub_account_id,
    )
    key_bytes = _fernet_key_bytes(settings)
    openapi_norm = normalize_openapi_base_url(openapi_base_url)
    ak = api_key.strip()
    sk = secret_key.strip()
    sealed = encrypt_json_plaintext(
        key_bytes,
        {"api_key": ak, "secret_key": sk},
    )
    tg_uid = _parse_telegram_user_id(telegram)
    now = datetime.now(UTC)

    stmt = select(TelegramAgentTradingBinding).where(
        TelegramAgentTradingBinding.telegram_user_id == tg_uid,
    )
    res = await session.execute(stmt)
    row = res.scalar_one_or_none()
    row_created = False
    if row is None:
        row = TelegramAgentTradingBinding(
            telegram_user_id=tg_uid,
            openapi_base_url=openapi_norm,
            trading_credentials_sealed=sealed,
            tg_username=_tg_optional(telegram, "tg_username", 128),
            tg_first_name=_tg_optional(telegram, "tg_first_name", 256),
            tg_last_name=_tg_optional(telegram, "tg_last_name", 256),
            tg_lang=_tg_optional(telegram, "tg_lang", 32),
            idempotency_key_last=(idempotency_key.strip()[:128] if idempotency_key else None),
            deeplink_token_last=(deeplink_token.strip()[:512] if deeplink_token else None),
            created_at=now,
            updated_at=now,
        )
        session.add(row)
        row_created = True
    else:
        row.openapi_base_url = openapi_norm
        row.trading_credentials_sealed = sealed
        row.tg_username = _tg_optional(telegram, "tg_username", 128)
        row.tg_first_name = _tg_optional(telegram, "tg_first_name", 256)
        row.tg_last_name = _tg_optional(telegram, "tg_last_name", 256)
        row.tg_lang = _tg_optional(telegram, "tg_lang", 32)
        row.idempotency_key_last = idempotency_key.strip()[:128] if idempotency_key else None
        row.deeplink_token_last = deeplink_token.strip()[:512] if deeplink_token else None
        row.updated_at = now

    sub_norm = (sub_account_id or "").strip()
    inst_row, _ = await upsert_agent_instance_for_telegram_binding(
        session,
        settings=settings,
        telegram_user_id=tg_uid,
        exchange_sub_account_user_id=sub_norm,
    )

    await session.commit()
    await session.refresh(row)
    welcome_outcome = await dispatch_activation_welcome(
        session,
        settings,
        telegram_user_id=tg_uid,
        telegram=telegram,
    )
    if welcome_outcome.sent:
        await session.commit()
    return row, row_created, inst_row.instance_id, welcome_outcome


async def has_telegram_trading_binding(session: AsyncSession, telegram_user_id: int) -> bool:
    stmt = (
        select(TelegramAgentTradingBinding.id)
        .where(
            TelegramAgentTradingBinding.telegram_user_id == telegram_user_id,
        )
        .limit(1)
    )
    r = await session.execute(stmt)
    return r.scalar_one_or_none() is not None


async def is_telegram_user_agent_hosted_bound(
    session: AsyncSession, telegram_user_id: int
) -> bool:
    """
    Telegram Bot treats the user as bound only when both trading API hosting
    and an ``agent_instance`` row exist (admin I06 delete clears both).
    """
    if not await has_telegram_trading_binding(session, telegram_user_id):
        return False
    stmt = (
        select(AgentInstance.id)
        .where(AgentInstance.telegram_user_id == telegram_user_id)
        .limit(1)
    )
    r = await session.execute(stmt)
    return r.scalar_one_or_none() is not None
