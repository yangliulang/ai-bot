"""Agent trading API binding — validate-only (no persistence of secrets)."""

from __future__ import annotations

from typing import Any

from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.exchange.coobit_openapi import (
    fetch_signed_spot_account_json,
    normalize_openapi_base_url,
)

_MIN_KEY_LEN = 8
_MAX_KEY_LEN = 512
_MAX_SUB_ACCOUNT_ID_LEN = 128

_ACCOUNT_ID_KEYS: tuple[str, ...] = (
    "userId",
    "user_id",
    "uid",
    "accountId",
    "account_id",
    "subUserId",
    "sub_user_id",
    "subUid",
    "sub_uid",
    "subaccountUserId",
    "sub_account_user_id",
    "subAccountId",
    "sub_account_id",
    "brokerUserId",
    "broker_user_id",
)


def _normalize_id_fragment(value: Any) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value)
    s = str(value).strip()
    return s if s else None


def _extract_account_identity_candidates(account: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for key in _ACCOUNT_ID_KEYS:
        frag = _normalize_id_fragment(account.get(key))
        if frag:
            out.add(frag)
    nested = account.get("user")
    if isinstance(nested, dict):
        for key in _ACCOUNT_ID_KEYS:
            frag = _normalize_id_fragment(nested.get(key))
            if frag:
                out.add(frag)
    return out


def _verify_declared_sub_account_id(*, account: dict[str, Any], declared: str) -> None:
    """If the exchange payload exposes id-like fields, they must match ``declared``."""
    exp = declared.strip()
    if not exp:
        raise AppError(
            code="AGENT_SUB_ACCOUNT_ID_REQUIRED",
            message="子账户 ID 不可为空",
            status_code=400,
        )
    candidates = _extract_account_identity_candidates(account)
    if not candidates:
        return
    if exp in candidates:
        return
    for c in candidates:
        try:
            if int(exp) == int(c):
                return
        except ValueError:
            continue
    raise AppError(
        code="AGENT_SUB_ACCOUNT_ID_MISMATCH",
        message="子账户 ID 与交易所账户接口返回不一致，请核对所填 ID 是否为当前 API Key 所属子账户",
        status_code=400,
        details={"declaredSubAccountId": exp[:64]},
    )


def _parse_required_sub_account_id(raw: str | None) -> str:
    if raw is None or not str(raw).strip():
        raise AppError(
            code="AGENT_SUB_ACCOUNT_ID_REQUIRED",
            message="须填写子账户 ID（交易所子账户用户标识）",
            status_code=400,
        )
    s = str(raw).strip()
    if len(s) > _MAX_SUB_ACCOUNT_ID_LEN:
        raise AppError(
            code="AGENT_SUB_ACCOUNT_ID_INVALID",
            message="子账户 ID 过长",
            status_code=400,
            details={"max_length": _MAX_SUB_ACCOUNT_ID_LEN},
        )
    return s


async def validate_agent_trading_api_keys_or_raise(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    sub_account_id: str | None,
) -> None:
    """
    Structural checks, signed **GET /sapi/v1/account**, optional cross-check of ``sub_account_id``.

    When the account JSON contains recognizable id fields, ``sub_account_id`` must match
    one of them.
    If no id fields are present (exchange-specific), only non-empty ``sub_account_id`` is required.
    """
    openapi_base_normalized = normalize_openapi_base_url(openapi_base_url)

    ak = api_key.strip()
    sk = secret_key.strip()
    if not ak or not sk:
        raise AppError(
            code="AGENT_API_KEYS_INCOMPLETE",
            message="API Key 与 Secret Key 均不可为空",
            status_code=400,
        )
    if len(ak) < _MIN_KEY_LEN or len(sk) < _MIN_KEY_LEN:
        raise AppError(
            code="AGENT_API_KEYS_INVALID",
            message="API Key 或 Secret Key 长度过短",
            status_code=400,
            details={"min_length": _MIN_KEY_LEN},
        )
    if len(ak) > _MAX_KEY_LEN or len(sk) > _MAX_KEY_LEN:
        raise AppError(
            code="AGENT_API_KEYS_INVALID",
            message="API Key 或 Secret Key 长度超过上限",
            status_code=400,
            details={"max_length": _MAX_KEY_LEN},
        )

    declared_sub = _parse_required_sub_account_id(sub_account_id)

    account = await fetch_signed_spot_account_json(
        openapi_base_url=openapi_base_normalized,
        api_key=ak,
        secret_key=sk,
    )
    _verify_declared_sub_account_id(account=account, declared=declared_sub)
