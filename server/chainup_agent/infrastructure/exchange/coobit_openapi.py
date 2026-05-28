"""Coobit / ChainUp OpenAPI — signed USER_DATA probes (no secret logging)."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, NoReturn
from urllib.parse import quote, urlparse, urlencode

import httpx

from chainup_agent.core.errors import AppError

_SPOT_ACCOUNT_PATH = "/sapi/v1/account"
_SPOT_ASSET_ACCOUNT_BY_TYPE_PATH = "/sapi/v1/asset/account/by_type"
_SPOT_TICKER_V2_PATH = "/sapi/v2/ticker"
_SPOT_DEPTH_V2_PATH = "/sapi/v2/depth"
_SPOT_TRADES_V2_PATH = "/sapi/v2/trades"
_SPOT_ORDER_V2_PATH = "/sapi/v2/order"
_SPOT_CANCEL_V2_PATH = "/sapi/v2/cancel"
_SPOT_OPEN_ORDERS_V2_PATH = "/sapi/v2/openOrders"
_MARGIN_ORDER_V2_PATH = "/sapi/v2/margin/order"
_FUTURES_ORDER_V1_PATH = "/fapi/v1/order"
_FUTURES_OPEN_ORDERS_V1_PATH = "/fapi/v1/openOrders"
_FUTURES_CANCEL_V1_PATH = "/fapi/v1/cancel"
_FUTURES_CONDITION_ORDER_V1_PATH = "/fapi/v1/conditionOrder"
_DEFAULT_TIMEOUT_S = 10.0

# Mirrors ``agent_spot_trade._ALLOWED_SPOT_ORDER_PREVIEW_KEYS`` for timeline payloads (no secrets).
_TIMELINE_SPOT_ORDER_RESPONSE_KEYS = frozenset(
    {
        "orderId",
        "orderIdString",
        "clientOrderId",
        "clientorderId",
        "status",
        "symbol",
        "symbolName",
        "side",
        "type",
        "price",
        "origQty",
        "executedQty",
        "avgPrice",
        "transactTime",
    }
)


def spot_order_response_body_timeline_preview(data: dict[str, Any]) -> dict[str, Any]:
    """
    Non-secret subset of Coobit ``POST /sapi/v2/order`` JSON for execution timeline.

    Includes business fields when present plus typical error ``code`` / ``msg``.
    """
    out: dict[str, Any] = {}
    for k in _TIMELINE_SPOT_ORDER_RESPONSE_KEYS:
        if k not in data:
            continue
        v = data[k]
        if v is None:
            continue
        if isinstance(v, bool):
            out[k] = v
        elif isinstance(v, (int, float)):
            out[k] = v
        else:
            s = str(v).strip()
            if s:
                out[k] = s[:128]
    for k in ("code", "msg"):
        if k not in data:
            continue
        v = data[k]
        if v is None:
            continue
        if isinstance(v, (int, float)):
            out[k] = v
        else:
            s = str(v).strip()
            if s:
                out[k] = s[:512] if k == "msg" else s[:128]
    return out


def normalize_coobit_spot_symbol_param(symbol: str) -> str:
    """
    Best-effort ticker symbol for ``GET /sapi/v2/ticker?symbol=``.

    Accepts ``BTC-USDT``, ``btc/usdt``, ``BTCUSDT`` → ``BTC-USDT`` style when a
    known quote suffix is present.
    """
    raw = symbol.strip().upper().replace("/", "-").replace("_", "-")
    if "-" in raw:
        return raw
    quotes = ("USDT", "USDC", "BTC", "ETH", "TRY", "EUR", "USD", "BUSD")
    for q in quotes:
        if raw.endswith(q) and len(raw) > len(q):
            return f"{raw[: -len(q)]}-{q}"
    return raw


def normalize_coobit_spot_order_symbol(symbol: str) -> str:
    """
    Compact trading pair id (e.g. ``BTCUSDT``) for ticker fallbacks and Agent
    ``symbolOrder`` field — **not** necessarily the ``POST /sapi/v2/order`` body format.

    Prefer :func:`normalize_coobit_spot_order_body_symbol` for signed order requests (v2
    doc: *Symbol Name E.g. BTC/USDT*).
    """
    n = normalize_coobit_spot_symbol_param(symbol.strip())
    return n.replace("-", "").upper()


def normalize_coobit_spot_order_body_symbol(symbol: str) -> str:
    """
    ``POST /sapi/v2/order`` JSON ``symbol`` per OpenAPI v2 Spot — **Request Body**:
    *Symbol Name E.g. BTC/USDT* (slash-separated).
    """
    n = normalize_coobit_spot_symbol_param(symbol.strip())
    if not n:
        return n
    return n.replace("-", "/")


def spot_ticker_symbol_candidates(sym_ticker: str, sym_order: str) -> list[str]:
    """
    ``GET /sapi/v2/ticker`` 的 ``symbol`` 在不同网关可能是 ``BTC-USDT``、``BTCUSDT``、``btcusdt``、``BTC/USDT`` 等；
    依序尝试以提高兼容性。
    """
    seen: set[str] = set()
    out: list[str] = []

    def add(raw: str) -> None:
        s = raw.strip()
        if not s or s in seen:
            return
        seen.add(s)
        out.append(s)

    st = (sym_ticker or "").strip()
    so = (sym_order or "").strip()
    add(st)
    add(so)
    if so:
        add(so.lower())
    if "-" in st:
        add(st.replace("-", "/"))
        compact = st.replace("-", "").upper()
        add(compact)
        add(compact.lower())
    return out


def normalize_openapi_base_url(raw: str) -> str:
    """
    Return base URL without trailing slash. Accepts ``http(s)`` with host.

    Raises ``AppError`` (400) when the value cannot be used as an OpenAPI origin.
    """
    s = raw.strip()
    if not s:
        raise AppError(
            code="AGENT_OPENAPI_BASE_URL_INVALID",
            message="OpenAPI base URL 不可为空",
            status_code=400,
        )
    parsed = urlparse(s)
    if parsed.scheme not in ("http", "https"):
        raise AppError(
            code="AGENT_OPENAPI_BASE_URL_INVALID",
            message="OpenAPI base URL 须为以 http:// 或 https:// 开头的完整地址",
            status_code=400,
        )
    if not parsed.netloc:
        raise AppError(
            code="AGENT_OPENAPI_BASE_URL_INVALID",
            message="OpenAPI base URL 缺少有效主机名",
            status_code=400,
        )
    return s.rstrip("/")


def build_coobit_signed_get_request_path(path: str, query_params: dict[str, Any]) -> str:
    """
    Build ``requestPath`` for Coobit signed GET calls: ``path`` plus optional **sorted**
    query string (GitBook: GET params go in query; signature uses ``timestamp + GET +
    requestPath + body`` with empty body — ``requestPath`` **must** include ``?…`` when
    querying).
    """
    items: list[tuple[str, str]] = []
    for key in sorted(query_params.keys()):
        val = query_params[key]
        if val is None:
            continue
        s = str(val).strip()
        if not s:
            continue
        items.append((key, s))
    if not items:
        return path
    qs = urlencode(items, quote_via=quote)
    return f"{path}?{qs}"


def _coobit_sign_hex(
    *, secret_key: str, timestamp_ms: str, method: str, request_path: str, body: str
) -> str:
    """HMAC-SHA256 over ``timestamp + method + requestPath + body`` (GitBook)."""
    payload = f"{timestamp_ms}{method.upper()}{request_path}{body}"
    digest = hmac.new(
        secret_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest


def _signed_headers_get(*, api_key: str, secret_key: str, request_path: str) -> dict[str, str]:
    ts = str(int(time.time() * 1000))
    sign = _coobit_sign_hex(
        secret_key=secret_key,
        timestamp_ms=ts,
        method="GET",
        request_path=request_path,
        body="",
    )
    return {
        "X-CH-APIKEY": api_key,
        "X-CH-SIGN": sign,
        "X-CH-TS": ts,
        "Content-Type": "application/json",
    }


def _signed_headers_post(
    *, api_key: str, secret_key: str, request_path: str, body: str
) -> dict[str, str]:
    ts = str(int(time.time() * 1000))
    sign = _coobit_sign_hex(
        secret_key=secret_key,
        timestamp_ms=ts,
        method="POST",
        request_path=request_path,
        body=body,
    )
    return {
        "X-CH-APIKEY": api_key,
        "X-CH-SIGN": sign,
        "X-CH-TS": ts,
        "Content-Type": "application/json",
    }


def _coobit_exchange_code_indicates_success(code: Any) -> bool:
    """HTTP 体 ``code`` 在部分网关为 ``0`` 或 ``200``（字符串或数字）均表示成功。"""
    if code is None or isinstance(code, bool):
        return False
    if isinstance(code, int):
        return code in (0, 200)
    s = str(code).strip()
    if not s:
        return False
    if s.lower() in ("0", "200", "ok", "success"):
        return True
    try:
        return int(float(s)) in (0, 200)
    except ValueError:
        return False


def _coobit_body_indicates_error(data: Any) -> bool:
    """True when JSON matches GitBook-style error objects ``{code, msg}``."""
    if not isinstance(data, dict):
        return False
    if "code" not in data or "msg" not in data:
        return False
    return not _coobit_exchange_code_indicates_success(data.get("code"))


def _coobit_spot_order_rejected_user_message(data: dict[str, Any]) -> str:
    raw = data.get("msg")
    if raw is not None:
        s = str(raw).strip()
        if s:
            return f"交易所拒绝现货委托：{s[:512]}"
    return "交易所拒绝现货委托"


_SPOT_REJECT_PERMISSION_HINT_ZH = (
    "【处理建议】多为 API Key 未勾选「现货 / 币币 / 下单」权限，或子账户不允许交易、READ-ONLY Key。"
    "请到交易所控制台为该 Key 开通交易权限（或换新 Key），确认子账户可交易；若启用 IP 白名单请放行 Agent 出口 IP，"
    "然后在 Deeplink 中重新完成绑定。"
)


def _spot_order_rejection_looks_like_permission_denied(msg: str) -> bool:
    s = msg.lower()
    needles_en = (
        "permission",
        "don't have permission",
        "do not have permission",
        "no permission",
        "access denied",
        "not authorized",
        "forbidden",
    )
    needles_zh = ("无权限", "没有权限", "权限不足", "未授权", "禁止访问")
    return any(n in s for n in needles_en) or any(n in msg for n in needles_zh)


def _coobit_spot_order_rejected_app_error(
    data: dict[str, Any],
    *,
    http_status: int | None = None,
) -> AppError:
    """Build ``AGENT_SPOT_ORDER_REJECTED`` with optional permission troubleshooting."""
    msg_raw = str(data.get("msg") or "").strip()
    message = _coobit_spot_order_rejected_user_message(data)
    details: dict[str, Any] = {
        "exchange_code": data.get("code"),
        "exchange_msg": data.get("msg"),
        "exchange_response_preview": spot_order_response_body_timeline_preview(data),
    }
    if http_status is not None:
        details["http_status"] = http_status
    if _spot_order_rejection_looks_like_permission_denied(msg_raw):
        details["reject_reason"] = "API_PERMISSION_OR_SUBACCOUNT"
        message = f"{message}\n\n{_SPOT_REJECT_PERMISSION_HINT_ZH}"
    return AppError(
        code="AGENT_SPOT_ORDER_REJECTED",
        message=message,
        status_code=400,
        details=details,
    )


async def probe_spot_account(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> None:
    """
    GET ``/sapi/v1/account`` on the spot gateway with Coobit signed headers.

    Raises ``AppError`` when the exchange rejects the key, returns an error payload,
    or the request cannot be completed.
    """
    await fetch_signed_spot_account_json(
        openapi_base_url=openapi_base_url,
        api_key=api_key,
        secret_key=secret_key,
        timeout_s=timeout_s,
    )


async def fetch_signed_spot_account_json(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """GET ``/sapi/v1/account``; return JSON object on success."""
    url = f"{openapi_base_url}{_SPOT_ACCOUNT_PATH}"
    headers = _signed_headers_get(
        api_key=api_key,
        secret_key=secret_key,
        request_path=_SPOT_ACCOUNT_PATH,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.get(url, headers=headers)
    except httpx.TimeoutException as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="连接交易所 OpenAPI 超时，请稍后重试",
            status_code=502,
            details={"reason": "timeout"},
        )
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所 OpenAPI，请检查 base URL 与网络",
            status_code=502,
            details={"reason": "request_error"},
        )

    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            raise AppError(
                code="AGENT_OPENAPI_PROBE_FAILED",
                message="交易所 OpenAPI 返回了非 JSON 响应",
                status_code=502,
                details={"reason": "invalid_json"},
            ) from None
        if not isinstance(data, dict):
            raise AppError(
                code="AGENT_OPENAPI_PROBE_FAILED",
                message="账户接口返回 JSON 非对象",
                status_code=502,
                details={"reason": "unexpected_shape"},
            )
        if _coobit_body_indicates_error(data):
            raise AppError(
                code="AGENT_API_KEYS_REJECTED",
                message="API Key 或 Secret Key 未通过交易所校验",
                status_code=400,
                details={
                    "exchange_code": data.get("code"),
                    "exchange_msg": data.get("msg"),
                },
            )
        return data

    if response.status_code in (401, 403):
        raise AppError(
            code="AGENT_API_KEYS_REJECTED",
            message="API Key 或 Secret Key 未通过交易所校验",
            status_code=400,
            details={"http_status": response.status_code},
        )

    payload: dict[str, Any] | None = None
    try:
        parsed = response.json()
        if isinstance(parsed, dict):
            payload = parsed
    except ValueError:
        payload = None

    if payload and _coobit_body_indicates_error(payload):
        raise AppError(
            code="AGENT_API_KEYS_REJECTED",
            message="API Key 或 Secret Key 未通过交易所校验",
            status_code=400,
            details={
                "exchange_code": payload.get("code"),
                "exchange_msg": payload.get("msg"),
                "http_status": response.status_code,
            },
        )

    raise AppError(
        code="AGENT_OPENAPI_PROBE_FAILED",
        message="校验请求未成功，请稍后重试或联系运维",
        status_code=502,
        details={
            "http_status": response.status_code,
            "reason": "unexpected_response",
        },
    )


async def fetch_signed_asset_account_by_type_json(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    account_type: int = 4,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """
    POST ``/sapi/v1/asset/account/by_type`` — wealth / multi-ledger slice (product ``accountType=4`` otc).

    Shape is exchange-defined; callers sanitize for previews. See ``product-doc/specs/design/api.md``.
    """
    base = normalize_openapi_base_url(openapi_base_url)
    url = f"{base}{_SPOT_ASSET_ACCOUNT_BY_TYPE_PATH}"
    body_obj: dict[str, Any] = {"accountType": int(account_type)}
    body_str = json.dumps(body_obj, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    headers = _signed_headers_post(
        api_key=api_key,
        secret_key=secret_key,
        request_path=_SPOT_ASSET_ACCOUNT_BY_TYPE_PATH,
        body=body_str,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.post(url, headers=headers, content=body_str.encode("utf-8"))
    except httpx.TimeoutException as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="理财账本接口请求超时，请稍后重试",
            status_code=502,
            details={"reason": "timeout", "path": _SPOT_ASSET_ACCOUNT_BY_TYPE_PATH},
        )
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所理财账本接口",
            status_code=502,
            details={"reason": "request_error", "path": _SPOT_ASSET_ACCOUNT_BY_TYPE_PATH},
        )

    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            raise AppError(
                code="AGENT_OPENAPI_PROBE_FAILED",
                message="理财账本接口返回非 JSON",
                status_code=502,
                details={"reason": "invalid_json"},
            ) from None
        if not isinstance(data, dict):
            raise AppError(
                code="AGENT_OPENAPI_PROBE_FAILED",
                message="理财账本接口返回 JSON 非对象",
                status_code=502,
                details={"reason": "unexpected_shape"},
            )
        if _coobit_body_indicates_error(data):
            raise AppError(
                code="AGENT_API_KEYS_REJECTED",
                message="API Key 或 Secret Key 未通过交易所校验",
                status_code=400,
                details={
                    "exchange_code": data.get("code"),
                    "exchange_msg": data.get("msg"),
                },
            )
        return data

    if response.status_code in (401, 403):
        raise AppError(
            code="AGENT_API_KEYS_REJECTED",
            message="API Key 或 Secret Key 未通过交易所校验",
            status_code=400,
            details={"http_status": response.status_code},
        )

    payload: dict[str, Any] | None = None
    try:
        parsed = response.json()
        if isinstance(parsed, dict):
            payload = parsed
    except ValueError:
        payload = None

    if payload and _coobit_body_indicates_error(payload):
        raise AppError(
            code="AGENT_API_KEYS_REJECTED",
            message="API Key 或 Secret Key 未通过交易所校验",
            status_code=400,
            details={
                "exchange_code": payload.get("code"),
                "exchange_msg": payload.get("msg"),
                "http_status": response.status_code,
            },
        )

    raise AppError(
        code="AGENT_OPENAPI_PROBE_FAILED",
        message="理财账本请求未成功，请稍后重试或联系运维",
        status_code=502,
        details={
            "http_status": response.status_code,
            "reason": "unexpected_response",
            "path": _SPOT_ASSET_ACCOUNT_BY_TYPE_PATH,
        },
    )


async def fetch_spot_public_ticker_json(
    *,
    openapi_base_url: str,
    symbol: str,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """
    GET ``/sapi/v2/ticker`` (public market); symbol must match exchange catalog.

    See ``product-doc/specs/openapi/exchange/coobit-public.yaml``.
    """
    base = normalize_openapi_base_url(openapi_base_url)
    url = f"{base}{_SPOT_TICKER_V2_PATH}"
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.get(url, params={"symbol": symbol})
    except httpx.TimeoutException as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="连接交易所 OpenAPI 超时，请稍后重试",
            status_code=502,
            details={"reason": "timeout", "path": _SPOT_TICKER_V2_PATH},
        )
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所 OpenAPI，请检查 base URL 与网络",
            status_code=502,
            details={"reason": "request_error", "path": _SPOT_TICKER_V2_PATH},
        )

    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            raise AppError(
                code="AGENT_OPENAPI_PROBE_FAILED",
                message="交易所 ticker 返回非 JSON",
                status_code=502,
                details={"reason": "invalid_json"},
            ) from None
        if not isinstance(data, dict):
            raise AppError(
                code="AGENT_OPENAPI_PROBE_FAILED",
                message="ticker 接口返回 JSON 非对象",
                status_code=502,
                details={"reason": "unexpected_shape"},
            )
        if _coobit_body_indicates_error(data):
            raise AppError(
                code="AGENT_OPENAPI_MARKET_REJECTED",
                message="行情接口返回错误，请核对交易对或服务状态",
                status_code=502,
                details={
                    "exchange_code": data.get("code"),
                    "exchange_msg": data.get("msg"),
                },
            )
        return data

    payload: dict[str, Any] | None = None
    try:
        parsed = response.json()
        if isinstance(parsed, dict):
            payload = parsed
    except ValueError:
        payload = None

    if payload and _coobit_body_indicates_error(payload):
        raise AppError(
            code="AGENT_OPENAPI_MARKET_REJECTED",
            message="行情接口返回错误，请核对交易对或服务状态",
            status_code=502,
            details={
                "exchange_code": payload.get("code"),
                "exchange_msg": payload.get("msg"),
                "http_status": response.status_code,
            },
        )

    raise AppError(
        code="AGENT_OPENAPI_PROBE_FAILED",
        message="行情请求未成功",
        status_code=502,
        details={
            "http_status": response.status_code,
            "path": _SPOT_TICKER_V2_PATH,
            "reason": "unexpected_response",
        },
    )


async def fetch_spot_public_ticker_json_with_fallbacks(
    *,
    openapi_base_url: str,
    symbol_candidates: list[str],
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """Try ``fetch_spot_public_ticker_json`` with each symbol string until one succeeds."""
    if not symbol_candidates:
        raise AppError(
            code="VALIDATION_ERROR",
            message="ticker symbol 候选为空",
            status_code=422,
            details={"reason": "no_symbol_candidates"},
        )
    last: AppError | None = None
    for sym in symbol_candidates:
        try:
            return await fetch_spot_public_ticker_json(
                openapi_base_url=openapi_base_url,
                symbol=sym,
                timeout_s=timeout_s,
            )
        except AppError as exc:
            last = exc
            if exc.code in ("AGENT_OPENAPI_MARKET_REJECTED", "AGENT_OPENAPI_PROBE_FAILED"):
                continue
            raise
    assert last is not None
    raise last


def _clamp_market_data_limit(raw: int | None, *, default: int = 20, hi: int = 100) -> int:
    if raw is None:
        return default
    return max(1, min(int(raw), hi))


async def fetch_spot_public_depth_json(
    *,
    openapi_base_url: str,
    symbol: str,
    limit: int,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """GET ``/sapi/v2/depth`` (public order book)."""
    base = normalize_openapi_base_url(openapi_base_url)
    lim = _clamp_market_data_limit(limit)
    url = f"{base}{_SPOT_DEPTH_V2_PATH}"
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.get(url, params={"symbol": symbol, "limit": lim})
    except httpx.TimeoutException as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="连接交易所 OpenAPI 超时，请稍后重试",
            status_code=502,
            details={"reason": "timeout", "path": _SPOT_DEPTH_V2_PATH},
        )
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所 OpenAPI，请检查 base URL 与网络",
            status_code=502,
            details={"reason": "request_error", "path": _SPOT_DEPTH_V2_PATH},
        )

    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            raise AppError(
                code="AGENT_OPENAPI_PROBE_FAILED",
                message="交易所 depth 返回非 JSON",
                status_code=502,
                details={"reason": "invalid_json"},
            ) from None
        if not isinstance(data, dict):
            raise AppError(
                code="AGENT_OPENAPI_PROBE_FAILED",
                message="depth 接口返回 JSON 非对象",
                status_code=502,
                details={"reason": "unexpected_shape"},
            )
        if _coobit_body_indicates_error(data):
            raise AppError(
                code="AGENT_OPENAPI_MARKET_REJECTED",
                message="深度接口返回错误，请核对交易对或服务状态",
                status_code=502,
                details={
                    "exchange_code": data.get("code"),
                    "exchange_msg": data.get("msg"),
                },
            )
        return data

    payload: dict[str, Any] | None = None
    try:
        parsed = response.json()
        if isinstance(parsed, dict):
            payload = parsed
    except ValueError:
        payload = None

    if payload and _coobit_body_indicates_error(payload):
        raise AppError(
            code="AGENT_OPENAPI_MARKET_REJECTED",
            message="深度接口返回错误，请核对交易对或服务状态",
            status_code=502,
            details={
                "exchange_code": payload.get("code"),
                "exchange_msg": payload.get("msg"),
                "http_status": response.status_code,
            },
        )

    raise AppError(
        code="AGENT_OPENAPI_PROBE_FAILED",
        message="深度请求未成功",
        status_code=502,
        details={
            "http_status": response.status_code,
            "path": _SPOT_DEPTH_V2_PATH,
            "reason": "unexpected_response",
        },
    )


async def fetch_spot_public_depth_json_with_fallbacks(
    *,
    openapi_base_url: str,
    symbol_candidates: list[str],
    limit: int,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """Try ``fetch_spot_public_depth_json`` with each symbol string until one succeeds."""
    if not symbol_candidates:
        raise AppError(
            code="VALIDATION_ERROR",
            message="depth symbol 候选为空",
            status_code=422,
            details={"reason": "no_symbol_candidates"},
        )
    last: AppError | None = None
    lim = _clamp_market_data_limit(limit)
    for sym in symbol_candidates:
        try:
            return await fetch_spot_public_depth_json(
                openapi_base_url=openapi_base_url,
                symbol=sym,
                limit=lim,
                timeout_s=timeout_s,
            )
        except AppError as exc:
            last = exc
            if exc.code in ("AGENT_OPENAPI_MARKET_REJECTED", "AGENT_OPENAPI_PROBE_FAILED"):
                continue
            raise
    assert last is not None
    raise last


async def fetch_spot_public_trades_json(
    *,
    openapi_base_url: str,
    symbol: str,
    limit: int,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> list[dict[str, Any]]:
    """
    GET ``/sapi/v2/trades`` (public recent trades).

    Returns a list of objects (normalized empty list if the exchange returns an empty array).
    """
    base = normalize_openapi_base_url(openapi_base_url)
    lim = _clamp_market_data_limit(limit)
    url = f"{base}{_SPOT_TRADES_V2_PATH}"
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.get(url, params={"symbol": symbol, "limit": lim})
    except httpx.TimeoutException as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="连接交易所 OpenAPI 超时，请稍后重试",
            status_code=502,
            details={"reason": "timeout", "path": _SPOT_TRADES_V2_PATH},
        )
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所 OpenAPI，请检查 base URL 与网络",
            status_code=502,
            details={"reason": "request_error", "path": _SPOT_TRADES_V2_PATH},
        )

    if response.status_code != 200:
        payload: dict[str, Any] | None = None
        try:
            parsed = response.json()
            if isinstance(parsed, dict):
                payload = parsed
        except ValueError:
            payload = None
        if payload and _coobit_body_indicates_error(payload):
            raise AppError(
                code="AGENT_OPENAPI_MARKET_REJECTED",
                message="成交接口返回错误，请核对交易对或服务状态",
                status_code=502,
                details={
                    "exchange_code": payload.get("code"),
                    "exchange_msg": payload.get("msg"),
                    "http_status": response.status_code,
                },
            )
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="近期成交请求未成功",
            status_code=502,
            details={
                "http_status": response.status_code,
                "path": _SPOT_TRADES_V2_PATH,
                "reason": "unexpected_response",
            },
        )

    try:
        data = response.json()
    except ValueError:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="交易所 trades 返回非 JSON",
            status_code=502,
            details={"reason": "invalid_json"},
        ) from None

    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        for key in ("data", "trades", "items"):
            inner = data.get(key)
            if isinstance(inner, list):
                return [x for x in inner if isinstance(x, dict)]
        if _coobit_body_indicates_error(data):
            raise AppError(
                code="AGENT_OPENAPI_MARKET_REJECTED",
                message="成交接口返回错误，请核对交易对或服务状态",
                status_code=502,
                details={
                    "exchange_code": data.get("code"),
                    "exchange_msg": data.get("msg"),
                },
            )
    raise AppError(
        code="AGENT_OPENAPI_PROBE_FAILED",
        message="trades 接口返回格式异常",
        status_code=502,
        details={"reason": "unexpected_shape"},
    )


async def fetch_spot_public_trades_json_with_fallbacks(
    *,
    openapi_base_url: str,
    symbol_candidates: list[str],
    limit: int,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> list[dict[str, Any]]:
    """Try ``fetch_spot_public_trades_json`` with each symbol string until one succeeds."""
    if not symbol_candidates:
        raise AppError(
            code="VALIDATION_ERROR",
            message="trades symbol 候选为空",
            status_code=422,
            details={"reason": "no_symbol_candidates"},
        )
    last: AppError | None = None
    lim = _clamp_market_data_limit(limit)
    for sym in symbol_candidates:
        try:
            return await fetch_spot_public_trades_json(
                openapi_base_url=openapi_base_url,
                symbol=sym,
                limit=lim,
                timeout_s=timeout_s,
            )
        except AppError as exc:
            last = exc
            if exc.code in ("AGENT_OPENAPI_MARKET_REJECTED", "AGENT_OPENAPI_PROBE_FAILED"):
                continue
            raise
    assert last is not None
    raise last


async def post_signed_spot_order_json(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    order_body: dict[str, Any],
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """
    POST ``/sapi/v2/order`` with Coobit signed headers.

    ``order_body`` is serialized with sorted keys so the signature matches the wire body.
    See GitBook Spot · New Order (``symbol``, ``volume``, ``side``, ``type``, ``price`` for LIMIT).
    """
    base = normalize_openapi_base_url(openapi_base_url)
    url = f"{base}{_SPOT_ORDER_V2_PATH}"
    body_str = json.dumps(order_body, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    headers = _signed_headers_post(
        api_key=api_key,
        secret_key=secret_key,
        request_path=_SPOT_ORDER_V2_PATH,
        body=body_str,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.post(url, headers=headers, content=body_str.encode("utf-8"))
    except httpx.TimeoutException as exc:
        raise_exchange_write_unknown(path=_SPOT_ORDER_V2_PATH, reason="timeout")
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所 OpenAPI 下单接口",
            status_code=502,
            details={"reason": "request_error", "path": _SPOT_ORDER_V2_PATH},
        )

    try:
        data = response.json()
    except ValueError:
        raise AppError(
            code="AGENT_SPOT_ORDER_FAILED",
            message="现货下单返回非 JSON",
            status_code=502,
            details={"http_status": response.status_code, "path": _SPOT_ORDER_V2_PATH},
        ) from None

    if not isinstance(data, dict):
        raise AppError(
            code="AGENT_SPOT_ORDER_FAILED",
            message="现货下单响应格式异常",
            status_code=502,
            details={"http_status": response.status_code},
        )

    check_exchange_write_http_unknown(response.status_code, _SPOT_ORDER_V2_PATH)

    if response.status_code != 200:
        if _coobit_body_indicates_error(data):
            raise _coobit_spot_order_rejected_app_error(data, http_status=response.status_code)
        raise AppError(
            code="AGENT_SPOT_ORDER_FAILED",
            message="现货下单未成功",
            status_code=502,
            details={
                "http_status": response.status_code,
                "path": _SPOT_ORDER_V2_PATH,
                "exchange_response_preview": spot_order_response_body_timeline_preview(data),
            },
        )

    if _coobit_body_indicates_error(data):
        raise _coobit_spot_order_rejected_app_error(data)

    return data


def _coobit_parse_open_orders_json_body(data: Any) -> list[dict[str, Any]]:
    """Normalize exchange JSON to a list of order objects (flat array or wrapped)."""
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        for key in ("data", "result"):
            inner = data.get(key)
            if isinstance(inner, list):
                return [x for x in inner if isinstance(x, dict)]
    raise AppError(
        code="AGENT_SPOT_OPEN_ORDERS_FAILED",
        message="当前委托接口返回格式异常",
        status_code=502,
        details={"reason": "unexpected_shape"},
    )


async def fetch_signed_spot_open_orders_json(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    symbol: str | None = None,
    limit: int | None = None,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> list[dict[str, Any]]:
    """
    GET ``/sapi/v2/openOrders`` (GitBook Spot · Current Open Orders).

    ``symbol`` when set must already be **BASE/QUOTE** (e.g. ``BTC/USDT``). Omit both
    optional params to query all symbols (**higher weight** per GitBook).
    """
    base = normalize_openapi_base_url(openapi_base_url)
    params: dict[str, Any] = {}
    if symbol is not None and str(symbol).strip():
        params["symbol"] = str(symbol).strip()
    if limit is not None:
        params["limit"] = str(int(limit))
    sign_path = build_coobit_signed_get_request_path(_SPOT_OPEN_ORDERS_V2_PATH, params)
    url = f"{base}{sign_path}"
    headers = _signed_headers_get(
        api_key=api_key,
        secret_key=secret_key,
        request_path=sign_path,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.get(url, headers=headers)
    except httpx.TimeoutException as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="查询当前委托超时，请稍后重试",
            status_code=502,
            details={"reason": "timeout", "path": _SPOT_OPEN_ORDERS_V2_PATH},
        )
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所当前委托接口",
            status_code=502,
            details={"reason": "request_error", "path": _SPOT_OPEN_ORDERS_V2_PATH},
        )

    try:
        data = response.json()
    except ValueError:
        raise AppError(
            code="AGENT_SPOT_OPEN_ORDERS_FAILED",
            message="当前委托返回非 JSON",
            status_code=502,
            details={"http_status": response.status_code, "path": _SPOT_OPEN_ORDERS_V2_PATH},
        ) from None

    if response.status_code != 200:
        if isinstance(data, dict) and _coobit_body_indicates_error(data):
            raise _coobit_spot_order_rejected_app_error(data, http_status=response.status_code)
        raise AppError(
            code="AGENT_SPOT_OPEN_ORDERS_FAILED",
            message="查询当前委托未成功",
            status_code=502,
            details={
                "http_status": response.status_code,
                "path": _SPOT_OPEN_ORDERS_V2_PATH,
                "exchange_response_preview": spot_order_response_body_timeline_preview(data)
                if isinstance(data, dict)
                else None,
            },
        )

    if isinstance(data, dict) and _coobit_body_indicates_error(data):
        raise _coobit_spot_order_rejected_app_error(data, http_status=response.status_code)

    return _coobit_parse_open_orders_json_body(data)


def exchange_http_status_indicates_unknown(http_status: int | None) -> bool:
    """GitBook: HTTP 504 means execution result UNKNOWN (not success/fail)."""
    return http_status == 504


def app_error_indicates_exchange_unknown(exc: AppError) -> bool:
    """True when a write probe likely ended in 504 / timeout / transport unknown."""
    if exc.code in (
        "AGENT_EXCHANGE_WRITE_UNKNOWN",
        "AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED",
    ):
        return True
    if exc.code != "AGENT_OPENAPI_PROBE_FAILED":
        return False
    d = exc.details or {}
    if d.get("reason") == "timeout":
        return True
    if exchange_http_status_indicates_unknown(d.get("http_status")):
        return True
    return False


def raise_exchange_write_unknown(
    *,
    path: str,
    http_status: int | None = None,
    reason: str | None = None,
) -> NoReturn:
    """504 / write timeout on signed POST — terminal state unknown (GitBook §6)."""
    details: dict[str, Any] = {"path": path, "exchangeOutcome": "unknown"}
    if http_status is not None:
        details["http_status"] = http_status
    if reason:
        details["reason"] = reason
    if reason == "timeout":
        message = "交易所写请求超时，订单终态未知，请稍后对账重试"
    elif http_status is not None and exchange_http_status_indicates_unknown(http_status):
        message = "交易所返回 504，订单终态未知，请稍后对账重试"
    else:
        message = "交易所写请求结果未知，请稍后对账重试"
    raise AppError(
        code="AGENT_EXCHANGE_WRITE_UNKNOWN",
        message=message,
        status_code=502,
        details=details,
    )


def check_exchange_write_http_unknown(http_status: int, path: str) -> None:
    if exchange_http_status_indicates_unknown(http_status):
        raise_exchange_write_unknown(path=path, http_status=http_status)


async def fetch_signed_spot_order_json(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    symbol: str,
    order_id: str | None = None,
    client_order_id: str | None = None,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """
    GET ``/sapi/v2/order`` — single spot order query (GitBook reconcile PATH).
    """
    sym_body = normalize_coobit_spot_order_body_symbol(symbol)
    oid = (order_id or "").strip()
    cid = (client_order_id or "").strip()
    if not oid and not cid:
        raise AppError(
            code="VALIDATION_ERROR",
            message="须提供 orderId 或 clientOrderId 之一",
            status_code=422,
            details={"fields": ["orderId", "clientOrderId"]},
        )
    params: dict[str, Any] = {"symbol": sym_body}
    if oid:
        params["orderId"] = oid
    if cid:
        params["newClientOrderId"] = cid

    base = normalize_openapi_base_url(openapi_base_url)
    sign_path = build_coobit_signed_get_request_path(_SPOT_ORDER_V2_PATH, params)
    url = f"{base}{sign_path}"
    headers = _signed_headers_get(
        api_key=api_key,
        secret_key=secret_key,
        request_path=sign_path,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.get(url, headers=headers)
    except httpx.TimeoutException as exc:
        raise AppError(
            code="AGENT_EXCHANGE_WRITE_UNKNOWN",
            message="查单超时，交易所结果仍为未知，请稍后对账重试",
            status_code=502,
            details={"reason": "timeout", "path": _SPOT_ORDER_V2_PATH, "exchangeOutcome": "unknown"},
        )
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所查单接口",
            status_code=502,
            details={"reason": "request_error", "path": _SPOT_ORDER_V2_PATH},
        )

    try:
        data = response.json()
    except ValueError:
        raise AppError(
            code="AGENT_SPOT_ORDER_QUERY_FAILED",
            message="现货查单返回非 JSON",
            status_code=502,
            details={"http_status": response.status_code, "path": _SPOT_ORDER_V2_PATH},
        ) from None

    if exchange_http_status_indicates_unknown(response.status_code):
        raise AppError(
            code="AGENT_EXCHANGE_WRITE_UNKNOWN",
            message="交易所返回 504，订单终态未知，请稍后对账重试",
            status_code=502,
            details={
                "http_status": response.status_code,
                "path": _SPOT_ORDER_V2_PATH,
                "exchangeOutcome": "unknown",
            },
        )

    if response.status_code != 200:
        if isinstance(data, dict) and _coobit_body_indicates_error(data):
            raise _coobit_spot_order_rejected_app_error(data, http_status=response.status_code)
        raise AppError(
            code="AGENT_SPOT_ORDER_QUERY_FAILED",
            message="现货查单未成功",
            status_code=502,
            details={"http_status": response.status_code, "path": _SPOT_ORDER_V2_PATH},
        )

    if isinstance(data, dict) and _coobit_body_indicates_error(data):
        raise _coobit_spot_order_rejected_app_error(data, http_status=response.status_code)

    rows = _coobit_parse_open_orders_json_body(data)
    if not rows:
        raise AppError(
            code="AGENT_SPOT_ORDER_NOT_FOUND",
            message="未找到该现货委托",
            status_code=404,
            details={"symbol": sym_body, "orderId": oid or None},
        )
    return rows[0]


async def post_signed_spot_cancel_json(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    cancel_body: dict[str, Any],
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """
    POST ``/sapi/v2/cancel`` with Coobit signed headers (GitBook Spot · Cancel Order).

    Body keys typically include ``symbol`` (BASE/QUOTE), ``orderId``, optional
    ``newClientOrderId`` — serialized with sorted keys like ``POST /sapi/v2/order``.
    """
    base = normalize_openapi_base_url(openapi_base_url)
    url = f"{base}{_SPOT_CANCEL_V2_PATH}"
    body_str = json.dumps(cancel_body, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    headers = _signed_headers_post(
        api_key=api_key,
        secret_key=secret_key,
        request_path=_SPOT_CANCEL_V2_PATH,
        body=body_str,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.post(url, headers=headers, content=body_str.encode("utf-8"))
    except httpx.TimeoutException as exc:
        raise_exchange_write_unknown(path=_SPOT_CANCEL_V2_PATH, reason="timeout")
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所撤单接口",
            status_code=502,
            details={"reason": "request_error", "path": _SPOT_CANCEL_V2_PATH},
        )

    try:
        data = response.json()
    except ValueError:
        raise AppError(
            code="AGENT_SPOT_ORDER_FAILED",
            message="现货撤单返回非 JSON",
            status_code=502,
            details={"http_status": response.status_code, "path": _SPOT_CANCEL_V2_PATH},
        ) from None

    if not isinstance(data, dict):
        raise AppError(
            code="AGENT_SPOT_ORDER_FAILED",
            message="现货撤单响应格式异常",
            status_code=502,
            details={"http_status": response.status_code},
        )

    check_exchange_write_http_unknown(response.status_code, _SPOT_CANCEL_V2_PATH)

    if response.status_code != 200:
        if _coobit_body_indicates_error(data):
            raise _coobit_spot_order_rejected_app_error(data, http_status=response.status_code)
        raise AppError(
            code="AGENT_SPOT_ORDER_FAILED",
            message="现货撤单未成功",
            status_code=502,
            details={
                "http_status": response.status_code,
                "path": _SPOT_CANCEL_V2_PATH,
                "exchange_response_preview": spot_order_response_body_timeline_preview(data),
            },
        )

    if _coobit_body_indicates_error(data):
        raise _coobit_spot_order_rejected_app_error(data)

    return data


def normalize_coobit_futures_symbol(symbol: str) -> str:
    """
    Best-effort contract symbol for ``POST /fapi/v1/order`` (e.g. ``BTC_USDT``).

    Accepts ``BTC-USDT``, ``btc/usdt``, ``BTCUSDT``.
    """
    raw = symbol.strip().upper().replace("/", "_").replace("-", "_")
    if "_" in raw:
        return raw
    quotes = ("USDT", "USDC", "BTC", "ETH", "TRY", "EUR", "USD", "BUSD")
    for q in quotes:
        if raw.endswith(q) and len(raw) > len(q):
            return f"{raw[: -len(q)]}_{q}"
    return raw


def normalize_coobit_futures_contract_name(symbol: str) -> str:
    """
    Contract name for ``POST /fapi/v1/conditionOrder`` (e.g. ``E-BTC-USDT``).

    Accepts ``BTC-USDT``, ``E-BTC-USDT``, ``btc_usdt``.
    """
    raw = symbol.strip().upper().replace("/", "-").replace("_", "-")
    if raw.startswith("E-"):
        return raw
    if "-" not in raw:
        quotes = ("USDT", "USDC", "BTC", "ETH", "TRY", "EUR", "USD", "BUSD")
        for q in quotes:
            if raw.endswith(q) and len(raw) > len(q):
                raw = f"{raw[: -len(q)]}-{q}"
                break
    return f"E-{raw}"


def futures_order_response_body_timeline_preview(data: dict[str, Any]) -> dict[str, Any]:
    """Non-secret subset of Coobit ``POST /fapi/v1/order`` JSON for timelines."""
    return spot_order_response_body_timeline_preview(data)


def _coobit_futures_order_rejected_app_error(
    data: dict[str, Any],
    *,
    http_status: int | None = None,
) -> AppError:
    message = _coobit_spot_order_rejected_user_message(data)
    details: dict[str, Any] = {
        "exchange_code": data.get("code"),
        "exchange_msg": data.get("msg"),
        "exchange_response_preview": futures_order_response_body_timeline_preview(data),
    }
    if http_status is not None:
        details["http_status"] = http_status
    msg_raw = str(data.get("msg") or "").strip()
    if _spot_order_rejection_looks_like_permission_denied(msg_raw):
        details["reject_reason"] = "API_PERMISSION_OR_SUBACCOUNT"
        message = f"{message}\n\n{_SPOT_REJECT_PERMISSION_HINT_ZH}"
    return AppError(
        code="AGENT_FUTURES_ORDER_REJECTED",
        message=message,
        status_code=400,
        details=details,
    )


async def post_signed_futures_order_json(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    order_body: dict[str, Any],
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """POST ``/fapi/v1/order`` with Coobit signed headers."""
    base = normalize_openapi_base_url(openapi_base_url)
    url = f"{base}{_FUTURES_ORDER_V1_PATH}"
    body_str = json.dumps(order_body, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    headers = _signed_headers_post(
        api_key=api_key,
        secret_key=secret_key,
        request_path=_FUTURES_ORDER_V1_PATH,
        body=body_str,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.post(url, headers=headers, content=body_str.encode("utf-8"))
    except httpx.TimeoutException as exc:
        raise_exchange_write_unknown(path=_FUTURES_ORDER_V1_PATH, reason="timeout")
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所合约 OpenAPI 下单接口",
            status_code=502,
            details={"reason": "request_error", "path": _FUTURES_ORDER_V1_PATH},
        )

    try:
        data = response.json()
    except ValueError:
        raise AppError(
            code="AGENT_FUTURES_ORDER_FAILED",
            message="合约下单返回非 JSON",
            status_code=502,
            details={"http_status": response.status_code, "path": _FUTURES_ORDER_V1_PATH},
        ) from None

    if not isinstance(data, dict):
        raise AppError(
            code="AGENT_FUTURES_ORDER_FAILED",
            message="合约下单响应格式异常",
            status_code=502,
            details={"http_status": response.status_code},
        )

    check_exchange_write_http_unknown(response.status_code, _FUTURES_ORDER_V1_PATH)

    if response.status_code != 200:
        if _coobit_body_indicates_error(data):
            raise _coobit_futures_order_rejected_app_error(data, http_status=response.status_code)
        raise AppError(
            code="AGENT_FUTURES_ORDER_FAILED",
            message="合约下单未成功",
            status_code=502,
            details={
                "http_status": response.status_code,
                "path": _FUTURES_ORDER_V1_PATH,
                "exchange_response_preview": futures_order_response_body_timeline_preview(data),
            },
        )

    if _coobit_body_indicates_error(data):
        raise _coobit_futures_order_rejected_app_error(data)

    return data


def margin_order_response_body_timeline_preview(data: dict[str, Any]) -> dict[str, Any]:
    """Non-secret subset of Coobit ``POST /sapi/v2/margin/order`` JSON for timelines."""
    return spot_order_response_body_timeline_preview(data)


def _coobit_margin_order_rejected_app_error(
    data: dict[str, Any],
    *,
    http_status: int | None = None,
) -> AppError:
    message = _coobit_spot_order_rejected_user_message(data)
    details: dict[str, Any] = {
        "exchange_code": data.get("code"),
        "exchange_msg": data.get("msg"),
        "exchange_response_preview": margin_order_response_body_timeline_preview(data),
    }
    if http_status is not None:
        details["http_status"] = http_status
    msg_raw = str(data.get("msg") or "").strip()
    if _spot_order_rejection_looks_like_permission_denied(msg_raw):
        details["reject_reason"] = "API_PERMISSION_OR_SUBACCOUNT"
        message = f"{message}\n\n{_SPOT_REJECT_PERMISSION_HINT_ZH}"
    return AppError(
        code="AGENT_MARGIN_ORDER_REJECTED",
        message=message,
        status_code=400,
        details=details,
    )


async def post_signed_margin_order_json(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    order_body: dict[str, Any],
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """POST ``/sapi/v2/margin/order`` with Coobit signed headers."""
    base = normalize_openapi_base_url(openapi_base_url)
    url = f"{base}{_MARGIN_ORDER_V2_PATH}"
    body_str = json.dumps(order_body, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    headers = _signed_headers_post(
        api_key=api_key,
        secret_key=secret_key,
        request_path=_MARGIN_ORDER_V2_PATH,
        body=body_str,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.post(url, headers=headers, content=body_str.encode("utf-8"))
    except httpx.TimeoutException as exc:
        raise_exchange_write_unknown(path=_MARGIN_ORDER_V2_PATH, reason="timeout")
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所杠杆 OpenAPI 下单接口",
            status_code=502,
            details={"reason": "request_error", "path": _MARGIN_ORDER_V2_PATH},
        )

    try:
        data = response.json()
    except ValueError:
        raise AppError(
            code="AGENT_MARGIN_ORDER_FAILED",
            message="全仓杠杆下单返回非 JSON",
            status_code=502,
            details={"http_status": response.status_code, "path": _MARGIN_ORDER_V2_PATH},
        ) from None

    if not isinstance(data, dict):
        raise AppError(
            code="AGENT_MARGIN_ORDER_FAILED",
            message="全仓杠杆下单响应格式异常",
            status_code=502,
            details={"http_status": response.status_code},
        )

    check_exchange_write_http_unknown(response.status_code, _MARGIN_ORDER_V2_PATH)

    if response.status_code != 200:
        if _coobit_body_indicates_error(data):
            raise _coobit_margin_order_rejected_app_error(data, http_status=response.status_code)
        raise AppError(
            code="AGENT_MARGIN_ORDER_FAILED",
            message="全仓杠杆下单未成功",
            status_code=502,
            details={
                "http_status": response.status_code,
                "path": _MARGIN_ORDER_V2_PATH,
                "exchange_response_preview": margin_order_response_body_timeline_preview(data),
            },
        )

    if _coobit_body_indicates_error(data):
        raise _coobit_margin_order_rejected_app_error(data)

    return data


def futures_condition_order_response_body_timeline_preview(
    data: dict[str, Any],
) -> dict[str, Any]:
    """Non-secret subset of Coobit ``POST /fapi/v1/conditionOrder`` JSON for timelines."""
    return spot_order_response_body_timeline_preview(data)


def _unwrap_coobit_futures_condition_order_payload(data: dict[str, Any]) -> dict[str, Any]:
    inner = data.get("data")
    if isinstance(inner, dict) and (
        "orderId" in inner or "orderIdString" in inner or "clientOrderId" in inner
    ):
        return inner
    return data


def _coobit_futures_condition_order_rejected_app_error(
    data: dict[str, Any],
    *,
    http_status: int | None = None,
) -> AppError:
    message = _coobit_spot_order_rejected_user_message(data).replace("现货", "条件单")
    details: dict[str, Any] = {
        "exchange_code": data.get("code"),
        "exchange_msg": data.get("msg"),
        "exchange_response_preview": futures_condition_order_response_body_timeline_preview(data),
    }
    if http_status is not None:
        details["http_status"] = http_status
    return AppError(
        code="AGENT_FUTURES_CONDITION_ORDER_REJECTED",
        message=message,
        status_code=400,
        details=details,
    )


async def post_signed_futures_condition_order_json(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    order_body: dict[str, Any],
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """POST ``/fapi/v1/conditionOrder`` with Coobit signed headers."""
    base = normalize_openapi_base_url(openapi_base_url)
    url = f"{base}{_FUTURES_CONDITION_ORDER_V1_PATH}"
    body_str = json.dumps(order_body, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    headers = _signed_headers_post(
        api_key=api_key,
        secret_key=secret_key,
        request_path=_FUTURES_CONDITION_ORDER_V1_PATH,
        body=body_str,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.post(url, headers=headers, content=body_str.encode("utf-8"))
    except httpx.TimeoutException as exc:
        raise_exchange_write_unknown(
            path=_FUTURES_CONDITION_ORDER_V1_PATH, reason="timeout"
        )
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所条件单 OpenAPI 接口",
            status_code=502,
            details={"reason": "request_error", "path": _FUTURES_CONDITION_ORDER_V1_PATH},
        )

    try:
        data = response.json()
    except ValueError:
        raise AppError(
            code="AGENT_FUTURES_CONDITION_ORDER_FAILED",
            message="条件单返回非 JSON",
            status_code=502,
            details={"http_status": response.status_code, "path": _FUTURES_CONDITION_ORDER_V1_PATH},
        ) from None

    if not isinstance(data, dict):
        raise AppError(
            code="AGENT_FUTURES_CONDITION_ORDER_FAILED",
            message="条件单响应格式异常",
            status_code=502,
            details={"http_status": response.status_code},
        )

    check_exchange_write_http_unknown(response.status_code, _FUTURES_CONDITION_ORDER_V1_PATH)

    if response.status_code != 200:
        if _coobit_body_indicates_error(data):
            raise _coobit_futures_condition_order_rejected_app_error(
                data, http_status=response.status_code
            )
        raise AppError(
            code="AGENT_FUTURES_CONDITION_ORDER_FAILED",
            message="条件单未成功",
            status_code=502,
            details={
                "http_status": response.status_code,
                "path": _FUTURES_CONDITION_ORDER_V1_PATH,
                "exchange_response_preview": futures_condition_order_response_body_timeline_preview(
                    data
                ),
            },
        )

    if _coobit_body_indicates_error(data):
        raise _coobit_futures_condition_order_rejected_app_error(data)

    return _unwrap_coobit_futures_condition_order_payload(data)


def _coobit_parse_futures_orders_json_body(data: Any) -> list[dict[str, Any]]:
    """Normalize exchange JSON to a list of futures order objects."""
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        for key in ("data", "result"):
            inner = data.get(key)
            if isinstance(inner, list):
                return [x for x in inner if isinstance(x, dict)]
        if "orderId" in data or "orderIdString" in data:
            return [data]
    raise AppError(
        code="AGENT_FUTURES_OPEN_ORDERS_FAILED",
        message="合约委托接口返回格式异常",
        status_code=502,
        details={"reason": "unexpected_shape"},
    )


def _coobit_futures_cancel_rejected_app_error(
    data: dict[str, Any],
    *,
    http_status: int | None = None,
) -> AppError:
    message = _coobit_spot_order_rejected_user_message(data).replace("现货", "合约")
    details: dict[str, Any] = {
        "exchange_code": data.get("code"),
        "exchange_msg": data.get("msg"),
        "exchange_response_preview": futures_order_response_body_timeline_preview(data),
    }
    if http_status is not None:
        details["http_status"] = http_status
    msg_raw = str(data.get("msg") or "").strip()
    if _spot_order_rejection_looks_like_permission_denied(msg_raw):
        details["reject_reason"] = "API_PERMISSION_OR_SUBACCOUNT"
        message = f"{message}\n\n{_SPOT_REJECT_PERMISSION_HINT_ZH}"
    return AppError(
        code="AGENT_FUTURES_CANCEL_REJECTED",
        message=message,
        status_code=400,
        details=details,
    )


async def fetch_signed_futures_open_orders_json(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    contract_name: str | None = None,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> list[dict[str, Any]]:
    """
    GET ``/fapi/v1/openOrders`` (GitBook Futures · Open order).

    Optional ``contract_name`` (e.g. ``E-BTC-USDT``); omit to query all contracts.
    """
    base = normalize_openapi_base_url(openapi_base_url)
    params: dict[str, Any] = {}
    if contract_name is not None and str(contract_name).strip():
        params["contractName"] = str(contract_name).strip()
    sign_path = build_coobit_signed_get_request_path(_FUTURES_OPEN_ORDERS_V1_PATH, params)
    url = f"{base}{sign_path}"
    headers = _signed_headers_get(
        api_key=api_key,
        secret_key=secret_key,
        request_path=sign_path,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.get(url, headers=headers)
    except httpx.TimeoutException as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="查询合约当前委托超时，请稍后重试",
            status_code=502,
            details={"reason": "timeout", "path": _FUTURES_OPEN_ORDERS_V1_PATH},
        )
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所合约当前委托接口",
            status_code=502,
            details={"reason": "request_error", "path": _FUTURES_OPEN_ORDERS_V1_PATH},
        )

    try:
        data = response.json()
    except ValueError:
        raise AppError(
            code="AGENT_FUTURES_OPEN_ORDERS_FAILED",
            message="合约当前委托返回非 JSON",
            status_code=502,
            details={"http_status": response.status_code, "path": _FUTURES_OPEN_ORDERS_V1_PATH},
        ) from None

    if response.status_code != 200:
        if isinstance(data, dict) and _coobit_body_indicates_error(data):
            raise _coobit_futures_cancel_rejected_app_error(data, http_status=response.status_code)
        raise AppError(
            code="AGENT_FUTURES_OPEN_ORDERS_FAILED",
            message="查询合约当前委托未成功",
            status_code=502,
            details={
                "http_status": response.status_code,
                "path": _FUTURES_OPEN_ORDERS_V1_PATH,
                "exchange_response_preview": futures_order_response_body_timeline_preview(data)
                if isinstance(data, dict)
                else None,
            },
        )

    if isinstance(data, dict) and _coobit_body_indicates_error(data):
        raise _coobit_futures_cancel_rejected_app_error(data, http_status=response.status_code)

    return _coobit_parse_futures_orders_json_body(data)


async def fetch_signed_futures_order_json(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    contract_name: str,
    order_id: str | None = None,
    client_order_id: str | None = None,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """
    GET ``/fapi/v1/order`` — single order query (GitBook: contractName + orderId).
    """
    cn = contract_name.strip()
    if not cn:
        raise AppError(
            code="VALIDATION_ERROR",
            message="contractName 不可为空",
            status_code=422,
            details={"field": "contractName"},
        )
    oid = (order_id or "").strip()
    cid = (client_order_id or "").strip()
    if not oid and not cid:
        raise AppError(
            code="VALIDATION_ERROR",
            message="须提供 orderId 或 clientOrderId 之一",
            status_code=422,
            details={"fields": ["orderId", "clientOrderId"]},
        )
    params: dict[str, Any] = {"contractName": cn}
    if oid:
        params["orderId"] = oid
    if cid:
        params["clientOrderId"] = cid

    base = normalize_openapi_base_url(openapi_base_url)
    sign_path = build_coobit_signed_get_request_path(_FUTURES_ORDER_V1_PATH, params)
    url = f"{base}{sign_path}"
    headers = _signed_headers_get(
        api_key=api_key,
        secret_key=secret_key,
        request_path=sign_path,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.get(url, headers=headers)
    except httpx.TimeoutException as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="查询合约委托超时，请稍后重试",
            status_code=502,
            details={"reason": "timeout", "path": _FUTURES_ORDER_V1_PATH},
        )
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所合约委托查询接口",
            status_code=502,
            details={"reason": "request_error", "path": _FUTURES_ORDER_V1_PATH},
        )

    try:
        data = response.json()
    except ValueError:
        raise AppError(
            code="AGENT_FUTURES_ORDER_QUERY_FAILED",
            message="合约委托查询返回非 JSON",
            status_code=502,
            details={"http_status": response.status_code, "path": _FUTURES_ORDER_V1_PATH},
        ) from None

    if response.status_code != 200:
        if isinstance(data, dict) and _coobit_body_indicates_error(data):
            raise _coobit_futures_cancel_rejected_app_error(data, http_status=response.status_code)
        raise AppError(
            code="AGENT_FUTURES_ORDER_QUERY_FAILED",
            message="查询合约委托未成功",
            status_code=502,
            details={
                "http_status": response.status_code,
                "path": _FUTURES_ORDER_V1_PATH,
            },
        )

    if isinstance(data, dict) and _coobit_body_indicates_error(data):
        raise _coobit_futures_cancel_rejected_app_error(data, http_status=response.status_code)

    rows = _coobit_parse_futures_orders_json_body(data)
    if not rows:
        raise AppError(
            code="AGENT_FUTURES_ORDER_NOT_FOUND",
            message="未找到该合约委托",
            status_code=404,
            details={"contractName": cn, "orderId": oid or None},
        )
    return rows[0]


async def post_signed_futures_cancel_json(
    *,
    openapi_base_url: str,
    api_key: str,
    secret_key: str,
    cancel_body: dict[str, Any],
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """POST ``/fapi/v1/cancel`` with Coobit signed headers."""
    base = normalize_openapi_base_url(openapi_base_url)
    url = f"{base}{_FUTURES_CANCEL_V1_PATH}"
    body_str = json.dumps(cancel_body, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    headers = _signed_headers_post(
        api_key=api_key,
        secret_key=secret_key,
        request_path=_FUTURES_CANCEL_V1_PATH,
        body=body_str,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.post(url, headers=headers, content=body_str.encode("utf-8"))
    except httpx.TimeoutException as exc:
        raise_exchange_write_unknown(path=_FUTURES_CANCEL_V1_PATH, reason="timeout")
    except httpx.RequestError as exc:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所合约撤单接口",
            status_code=502,
            details={"reason": "request_error", "path": _FUTURES_CANCEL_V1_PATH},
        )

    try:
        data = response.json()
    except ValueError:
        raise AppError(
            code="AGENT_FUTURES_ORDER_FAILED",
            message="合约撤单返回非 JSON",
            status_code=502,
            details={"http_status": response.status_code, "path": _FUTURES_CANCEL_V1_PATH},
        ) from None

    if not isinstance(data, dict):
        raise AppError(
            code="AGENT_FUTURES_ORDER_FAILED",
            message="合约撤单响应格式异常",
            status_code=502,
            details={"http_status": response.status_code},
        )

    check_exchange_write_http_unknown(response.status_code, _FUTURES_CANCEL_V1_PATH)

    if response.status_code != 200:
        if _coobit_body_indicates_error(data):
            raise _coobit_futures_cancel_rejected_app_error(data, http_status=response.status_code)
        raise AppError(
            code="AGENT_FUTURES_ORDER_FAILED",
            message="合约撤单未成功",
            status_code=502,
            details={
                "http_status": response.status_code,
                "path": _FUTURES_CANCEL_V1_PATH,
                "exchange_response_preview": futures_order_response_body_timeline_preview(data),
            },
        )

    if _coobit_body_indicates_error(data):
        raise _coobit_futures_cancel_rejected_app_error(data)

    inner = data.get("data")
    if isinstance(inner, dict):
        return inner
    return data
