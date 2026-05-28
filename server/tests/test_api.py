from urllib.parse import parse_qs, quote, urlparse

import pytest
from httpx import AsyncClient


def _plaintext_bind_url(send_message_body: dict) -> str:
    lines = [ln.strip() for ln in send_message_body["text"].splitlines() if ln.strip()]
    assert lines
    url = lines[-1]
    assert url.startswith("http")
    return url


def _assert_tg_query(url: str, **want: str) -> None:
    q = parse_qs(urlparse(url).query)
    for k, v in want.items():
        assert q.get(k) == [v], f"query[{k!r}] in {url!r}: expected [{v!r}], got {q.get(k)!r}"


def test_extract_symbol_for_ticker_variants() -> None:
    from chainup_agent.application.telegram_symbol_extract import extract_symbol_for_ticker

    assert extract_symbol_for_ticker("看看 BTC 行情") == "BTC-USDT"
    assert extract_symbol_for_ticker("ETH/USDT 价格") == "ETH-USDT"
    assert extract_symbol_for_ticker("BTCUSDT") == "BTC-USDT"
    assert extract_symbol_for_ticker("今天BTC-USDT的行情怎么样") == "BTC-USDT"
    assert extract_symbol_for_ticker("今天BTCUSDT的行情怎么样") == "BTC-USDT"



@pytest.mark.asyncio
async def test_health(http_client: AsyncClient) -> None:
    r = await http_client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_openapi_available(http_client: AsyncClient) -> None:
    r = await http_client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert schema["info"]["title"] == "ChainUp AI Agent API"


@pytest.mark.asyncio
async def test_api_binding_validate_200(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _mock_fetch_account_ok(monkeypatch)
    r = await http_client.post(
        "/api/v1/agent/api-binding/validate",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is True
    assert body["ok"] is True


@pytest.mark.asyncio
async def test_api_binding_validate_400_short_keys(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/api-binding/validate",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "short",
            "secret_key": "alsobad",
        },
    )
    assert r.status_code == 400
    assert r.json()["code"] == "AGENT_API_KEYS_INVALID"


@pytest.mark.asyncio
async def test_api_binding_validate_400_whitespace_only(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/api-binding/validate",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "        ",
            "secret_key": "x" * 8,
        },
    )
    assert r.status_code == 400
    assert r.json()["code"] == "AGENT_API_KEYS_INCOMPLETE"


@pytest.mark.asyncio
async def test_api_binding_validate_400_invalid_base_url(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/api-binding/validate",
        json={
            "openapi_base_url": "",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
        },
    )
    assert r.status_code == 400
    assert r.json()["code"] == "AGENT_OPENAPI_BASE_URL_INVALID"


@pytest.mark.asyncio
async def test_api_binding_validate_400_sub_account_id_required(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/api-binding/validate",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
        },
    )
    assert r.status_code == 400
    assert r.json()["code"] == "AGENT_SUB_ACCOUNT_ID_REQUIRED"


@pytest.mark.asyncio
async def test_api_binding_validate_400_sub_account_id_mismatch(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _mock_fetch_account_ok(monkeypatch, {"userId": "111"})
    r = await http_client.post(
        "/api/v1/agent/api-binding/validate",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "222",
        },
    )
    assert r.status_code == 400
    assert r.json()["code"] == "AGENT_SUB_ACCOUNT_ID_MISMATCH"


@pytest.mark.asyncio
async def test_api_binding_validate_502_probe_failed(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Exchange probe raises AppError (e.g. network) → 502 body."""
    from unittest.mock import AsyncMock

    from chainup_agent.core.errors import AppError

    async def _fail(**_kw: object) -> None:
        raise AppError(
            code="AGENT_OPENAPI_PROBE_FAILED",
            message="无法连接交易所 OpenAPI，请检查 base URL 与网络",
            status_code=502,
            details={"reason": "request_error"},
        )

    monkeypatch.setattr(
        "chainup_agent.application.agent_api_binding.fetch_signed_spot_account_json",
        AsyncMock(side_effect=_fail),
    )
    r = await http_client.post(
        "/api/v1/agent/api-binding/validate",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
        },
    )
    assert r.status_code == 502
    assert r.json()["code"] == "AGENT_OPENAPI_PROBE_FAILED"


async def _init_binding_sqlite(monkeypatch: pytest.MonkeyPatch, tmp_path, fernet_key: str) -> None:
    import chainup_agent.infrastructure.persistence.models  # noqa: F401
    from chainup_agent.core.config import reset_settings_cache
    from chainup_agent.infrastructure.persistence.base import dispose_engine, get_engine
    from chainup_agent.infrastructure.persistence.models.base import Base

    db_file = (tmp_path / "binding.sqlite3").resolve()
    monkeypatch.setenv(
        "CHAINUP_AGENT_DATABASE_URL",
        f"sqlite+aiosqlite:///{db_file.as_posix()}",
    )
    monkeypatch.setenv("CHAINUP_AGENT_BINDING_SECRETS_FERNET_KEY", fernet_key)
    reset_settings_cache()
    await dispose_engine()
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _init_schema_sqlite(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Fresh SQLite + ORM create_all (AI Settings tests; no Fernet required)."""
    import chainup_agent.infrastructure.persistence.models  # noqa: F401
    from chainup_agent.core.config import reset_settings_cache
    from chainup_agent.infrastructure.persistence.base import dispose_engine, get_engine
    from chainup_agent.infrastructure.persistence.models.base import Base

    db_file = (tmp_path / "schema.sqlite3").resolve()
    monkeypatch.setenv(
        "CHAINUP_AGENT_DATABASE_URL",
        f"sqlite+aiosqlite:///{db_file.as_posix()}",
    )
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY", "true")
    reset_settings_cache()
    await dispose_engine()
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def _mock_fetch_account_ok(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict | None = None,
) -> None:
    from unittest.mock import AsyncMock

    async def _fetch(**_kw: object) -> dict:
        return {} if payload is None else payload

    monkeypatch.setattr(
        "chainup_agent.application.agent_api_binding.fetch_signed_spot_account_json",
        AsyncMock(side_effect=_fetch),
    )


def _mock_probe_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Deprecated alias: exchange probe mocks ``fetch_signed_spot_account_json``."""
    _mock_fetch_account_ok(monkeypatch)


@pytest.mark.asyncio
async def test_api_binding_confirm_503_without_fernet(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_binding_sqlite(monkeypatch, tmp_path, "")
    _mock_probe_ok(monkeypatch)
    r = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "42"},
        },
    )
    assert r.status_code == 503
    assert r.json()["code"] == "AGENT_BINDING_STORAGE_UNAVAILABLE"


@pytest.mark.asyncio
async def test_api_binding_confirm_400_missing_telegram(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    r = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
        },
    )
    assert r.status_code == 400
    assert r.json()["code"] == "AGENT_TELEGRAM_CONTEXT_REQUIRED"


@pytest.mark.asyncio
async def test_api_binding_confirm_200_roundtrip(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    r = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid/",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "4242", "tg_username": "ann"},
        },
    )
    assert r.status_code == 200
    j = r.json()
    assert j["telegram_user_id"] == 4242
    assert j.get("instanceId", "").startswith("inst_")
    assert j.get("agentSubAccountId") == "900001"


@pytest.mark.asyncio
async def test_me_trading_api_bindings_accepts_camel_case(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    r = await http_client.post(
        "/api/v1/me/agent/bindings/trading-api",
        json={
            "openapiBaseUrl": "https://openapi.example.invalid",
            "apiKey": "k" * 8,
            "apiSecret": "s" * 8,
            "idempotencyKey": "idem-1",
            "subAccountId": "900001",
            "telegram": {"tg_id": "77"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("saved") is True
    assert body.get("binding_row_created") is True or body.get("bindingRowCreated") is True

    r2 = await http_client.post(
        "/api/v1/me/agent/bindings/trading-api",
        json={
            "openapiBaseUrl": "https://openapi.example.invalid",
            "apiKey": "k" * 8,
            "apiSecret": "s" * 8,
            "idempotencyKey": "idem-2",
            "subAccountId": "900001",
            "telegram": {"tg_id": "77"},
        },
    )
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2.get("binding_row_created") is False or body2.get("bindingRowCreated") is False


@pytest.mark.asyncio
async def test_admin_trading_bindings_list(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    r = await http_client.post(
        "/api/v1/me/agent/bindings/trading-api",
        json={
            "openapiBaseUrl": "https://openapi.example.invalid",
            "apiKey": "k" * 8,
            "apiSecret": "s" * 8,
            "idempotencyKey": "idem-admin-list",
            "subAccountId": "900001",
            "deeplinkToken": "token-secret-value-here",
            "telegram": {"tg_id": "991", "tg_username": "ops_user"},
        },
    )
    assert r.status_code == 200
    lst = await http_client.get(
        "/api/v1/admin/agent/trading-bindings",
        params={"limit": 10, "offset": 0},
    )
    assert lst.status_code == 200
    data = lst.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    row = next(i for i in data["items"] if i["telegramUserId"] == 991)
    assert row["openapiBaseUrl"] == "https://openapi.example.invalid"
    assert row["tgUsername"] == "ops_user"
    assert row["deeplinkTokenLastMasked"] is not None
    assert "…" in row["deeplinkTokenLastMasked"]


@pytest.mark.asyncio
async def test_admin_trading_bindings_delete(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    bind = await http_client.post(
        "/api/v1/me/agent/bindings/trading-api",
        json={
            "openapiBaseUrl": "https://openapi.example.invalid",
            "apiKey": "k" * 8,
            "apiSecret": "s" * 8,
            "idempotencyKey": "idem-del",
            "subAccountId": "900001",
            "telegram": {"tg_id": "1001"},
        },
    )
    assert bind.status_code == 200
    lst = await http_client.get("/api/v1/admin/agent/trading-bindings")
    assert lst.status_code == 200
    bid = next(i["id"] for i in lst.json()["items"] if i["telegramUserId"] == 1001)
    rm = await http_client.delete(f"/api/v1/admin/agent/trading-bindings/{bid}")
    assert rm.status_code == 204
    lst2 = await http_client.get("/api/v1/admin/agent/trading-bindings")
    assert lst2.status_code == 200
    assert all(i["telegramUserId"] != 1001 for i in lst2.json()["items"])
    nf = await http_client.delete(f"/api/v1/admin/agent/trading-bindings/{999999}")
    assert nf.status_code == 404

    rebound = await http_client.post(
        "/api/v1/me/agent/bindings/trading-api",
        json={
            "openapiBaseUrl": "https://openapi.example.invalid",
            "apiKey": "k" * 8,
            "apiSecret": "s" * 8,
            "idempotencyKey": "idem-rebind",
            "subAccountId": "900001",
            "telegram": {"tg_id": "1001"},
        },
    )
    assert rebound.status_code == 200
    re_body = rebound.json()
    assert re_body.get("binding_row_created") is True or re_body.get("bindingRowCreated") is True


@pytest.mark.asyncio
async def test_admin_agent_instances_list_and_get(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    bind = await http_client.post(
        "/api/v1/me/agent/bindings/trading-api",
        json={
            "openapiBaseUrl": "https://openapi.example.invalid",
            "apiKey": "k" * 8,
            "apiSecret": "s" * 8,
            "idempotencyKey": "idem-inst-admin",
            "subAccountId": "900001",
            "telegram": {"tg_id": "5005"},
        },
    )
    assert bind.status_code == 200
    inst_id = bind.json().get("instanceId")
    assert inst_id and str(inst_id).startswith("inst_")

    lst = await http_client.get("/api/v1/admin/agents/instances")
    assert lst.status_code == 200
    data = lst.json()
    assert data["total"] >= 1
    row = next(i for i in data["items"] if i["telegramUserId"] == "5005")
    assert row["instanceId"] == inst_id
    assert row["tradingApiBindingStatus"] == "BOUND"
    assert row["subAccountStatus"] == "LINKED"

    det = await http_client.get(f"/api/v1/admin/agents/instances/{inst_id}")
    assert det.status_code == 200
    dj = det.json()
    assert dj["exchangeSubAccountUserId"] == "900001"

    nf = await http_client.get("/api/v1/admin/agents/instances/inst_nonexistent_xx")
    assert nf.status_code == 404
    assert nf.json()["code"] == "AGENT_ADMIN_INSTANCE_NOT_FOUND"

    bad_q = await http_client.get(
        "/api/v1/admin/agents/instances",
        params={"telegramUserId": "not-num"},
    )
    assert bad_q.status_code == 422


@pytest.mark.asyncio
async def test_admin_agent_instance_delete_204_and_404(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    bind = await http_client.post(
        "/api/v1/me/agent/bindings/trading-api",
        json={
            "openapiBaseUrl": "https://openapi.example.invalid",
            "apiKey": "k" * 8,
            "apiSecret": "s" * 8,
            "idempotencyKey": "idem-inst-del",
            "subAccountId": "900002",
            "telegram": {"tg_id": "5006"},
        },
    )
    assert bind.status_code == 200
    inst_id = bind.json().get("instanceId")
    assert inst_id

    rm = await http_client.delete(f"/api/v1/admin/agents/instances/{inst_id}")
    assert rm.status_code == 204

    det = await http_client.get(f"/api/v1/admin/agents/instances/{inst_id}")
    assert det.status_code == 404

    lst = await http_client.get("/api/v1/admin/agent/trading-bindings")
    assert lst.status_code == 200
    assert all(b["telegramUserId"] != 5006 for b in lst.json().get("items", []))

    ini = await http_client.post(
        "/api/v1/agent/onboarding/initiate",
        json={"telegram": {"tg_id": "5006"}},
    )
    assert ini.status_code == 200
    assert ini.json()["nextStep"] == "bind_trading_api"
    assert ini.json()["agentTradingApiBindingStatus"] == "NONE"

    rebound = await http_client.post(
        "/api/v1/me/agent/bindings/trading-api",
        json={
            "openapiBaseUrl": "https://openapi.example.invalid",
            "apiKey": "k" * 8,
            "apiSecret": "s" * 8,
            "idempotencyKey": "idem-inst-rebind",
            "subAccountId": "900002",
            "telegram": {"tg_id": "5006"},
        },
    )
    assert rebound.status_code == 200
    new_inst = rebound.json().get("instanceId")
    assert new_inst and new_inst != inst_id

    det2 = await http_client.get(f"/api/v1/admin/agents/instances/{new_inst}")
    assert det2.status_code == 200

    nf = await http_client.delete("/api/v1/admin/agents/instances/inst_nonexistent_del")
    assert nf.status_code == 404
    assert nf.json()["code"] == "AGENT_ADMIN_INSTANCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_admin_agent_instance_delete_blocked_open_execution(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    bind = await http_client.post(
        "/api/v1/me/agent/bindings/trading-api",
        json={
            "openapiBaseUrl": "https://openapi.example.invalid",
            "apiKey": "k" * 8,
            "apiSecret": "s" * 8,
            "idempotencyKey": "idem-inst-del-block",
            "subAccountId": "900003",
            "telegram": {"tg_id": "5007"},
        },
    )
    assert bind.status_code == 200
    inst_id = bind.json()["instanceId"]

    acc = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={"userId": "5007", "scenarioId": "read.market.ticker", "channel": "telegram"},
    )
    assert acc.status_code == 200

    blocked = await http_client.delete(f"/api/v1/admin/agents/instances/{inst_id}")
    assert blocked.status_code == 422
    body = blocked.json()
    assert body["code"] == "AGENT_ADMIN_INSTANCE_DELETE_BLOCKED"
    assert body["details"]["openExecutions"] >= 1

    still = await http_client.get(f"/api/v1/admin/agents/instances/{inst_id}")
    assert still.status_code == 200


@pytest.mark.asyncio
async def test_telegram_webhook_skip_bind_when_db_binding_exists(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    async def fake_ticker_json(*, openapi_base_url: str, symbol_candidates: list[str]) -> dict:
        sym = symbol_candidates[0] if symbol_candidates else ""
        return {
            "symbol": sym,
            "lastPrice": "12345.67",
            "volume": "999",
        }

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_ticker_json_with_fallbacks",
        fake_ticker_json,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    c = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "99"},
        },
    )
    assert c.status_code == 200

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 2}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    path = f"/webhook/telegram/{enc}"
    payload = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {
                "id": 99,
                "is_bot": False,
                "username": "alice",
            },
            "chat": {"id": 424242, "type": "private"},
            "text": "看看 BTC 行情",
        },
    }
    r = await http_client.post(path, json=payload)
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    assert body.get("reply_markup") is None
    assert "绑定页面" not in body["text"]
    assert "已收到你的消息" not in body["text"]
    assert "你说：" not in body["text"]
    assert "read.market.ticker" in body["text"]
    assert "12345.67" in body["text"]
    assert "Deeplink（H5 落地页）访问链接：" not in body["text"]


@pytest.mark.asyncio
async def test_telegram_webhook_read_market_ticker_llm_narration_success(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    async def fake_ticker_json(*, openapi_base_url: str, symbol_candidates: list[str]) -> dict:
        sym = symbol_candidates[0] if symbol_candidates else ""
        return {"symbol": sym, "lastPrice": "12345.67", "volume": "999"}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_ticker_json_with_fallbacks",
        fake_ticker_json,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    c = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "99"},
        },
    )
    assert c.status_code == 200

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER", "true")
    reset_settings_cache()

    llm_mock = AsyncMock(
        return_value=("这是 LLM 对行情的简述。", None, {"gatewayModelId": "gpt-mini"}),
    )
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        llm_mock,
    )

    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 12}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    path = f"/webhook/telegram/{enc}"
    payload = {
        "update_id": 1,
        "message": {
            "message_id": 11,
            "from": {"id": 99, "is_bot": False, "username": "alice"},
            "chat": {"id": 424243, "type": "private"},
            "text": "看看 BTC 行情",
        },
    }
    r = await http_client.post(path, json=payload)
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    assert "这是 LLM 对行情的简述。" in body["text"]
    assert "数据来源：现货公共 ticker（只读）" in body["text"]

    llm_mock.assert_awaited_once()
    k = llm_mock.await_args.kwargs
    assert k["scenario_id"] == "read.market.ticker"
    assert k["runtime_context"]["kind"] == "read.market.ticker"
    assert str(k["runtime_context"]["exchangeReadPreview"]).find("12345.67") != -1


@pytest.mark.asyncio
async def test_telegram_webhook_read_market_ticker_llm_narration_falls_back(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """When narration flag on but LLM returns error, deterministic ticker lines remain."""
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    async def fake_ticker_json(*, openapi_base_url: str, symbol_candidates: list[str]) -> dict:
        sym = symbol_candidates[0] if symbol_candidates else ""
        return {"symbol": sym, "lastPrice": "12345.67", "volume": "999"}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_ticker_json_with_fallbacks",
        fake_ticker_json,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    confirm = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "99"},
        },
    )
    assert confirm.status_code == 200

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER", "true")
    reset_settings_cache()

    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        AsyncMock(return_value=(None, "[测试] LLM down", {})),
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 13}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 12,
                "from": {"id": 99, "is_bot": False, "username": "alice"},
                "chat": {"id": 424244, "type": "private"},
                "text": "BTC 价格",
            },
        },
    )
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    assert "12345.67" in body["text"]
    assert "数据来源：现货公共 ticker（只读）" not in body["text"]


@pytest.mark.asyncio
async def test_telegram_read_market_ticker_llm_timeline_event(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    async def fake_ticker_json(*, openapi_base_url: str, symbol_candidates: list[str]) -> dict:
        return {"symbol": "BTC-USDT", "lastPrice": "1", "volume": "1"}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_ticker_json_with_fallbacks",
        fake_ticker_json,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        (
            await http_client.post(
                "/api/v1/agent/api-binding/confirm",
                json={
                    "openapi_base_url": "https://openapi.example.invalid",
                    "api_key": "k" * 8,
                    "secret_key": "s" * 8,
                    "sub_account_id": "900001",
                    "telegram": {"tg_id": "502"},
                },
            )
        ).status_code
        == 200
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER", "true")
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        AsyncMock(return_value=(None, "err", {"gatewayModelId": "gpt-4"})),
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 31}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 81,
                "from": {"id": 502, "is_bot": False, "username": "tuser"},
                "chat": {"id": 424250, "type": "private"},
                "text": "ETH 价格",
            },
        },
    )
    assert r.status_code == 200

    lst = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"userId": "502", "limit": 5},
    )
    assert lst.status_code == 200
    exec_items = lst.json()["items"]
    assert exec_items
    eid = exec_items[0]["executionId"]
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    names = [x["eventName"] for x in tl.json()["items"]]
    assert "llm.read.market.ticker" in names


@pytest.mark.asyncio
async def test_telegram_read_market_depth_llm_narration_success(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    async def fake_depth(*, openapi_base_url: str, symbol_candidates: list[str], limit: int):
        _ = openapi_base_url, limit
        return {"asks": [["1", "1"]], "bids": [["0.9", "2"]]}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_depth_json_with_fallbacks",
        fake_depth,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        (
            await http_client.post(
                "/api/v1/agent/api-binding/confirm",
                json={
                    "openapi_base_url": "https://openapi.example.invalid",
                    "api_key": "k" * 8,
                    "secret_key": "s" * 8,
                    "sub_account_id": "900001",
                    "telegram": {"tg_id": "50310"},
                },
            )
        ).status_code
        == 200
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_DEPTH", "true")
    reset_settings_cache()

    llm_mock = AsyncMock(
        return_value=("盘口简报 LLM。", None, {"gatewayModelId": "gpt-mini"}),
    )
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        llm_mock,
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 44}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 140,
                "from": {"id": 50310, "is_bot": False, "username": "duser"},
                "chat": {"id": 534340, "type": "private"},
                "text": "BTC-USDT 盘口怎么样",
            },
        },
    )
    assert r.status_code == 200
    reply = mocked.await_args.kwargs["json_payload"]["text"]
    assert "盘口简报 LLM。" in reply
    assert "现货公开盘口深度（只读）" in reply
    llm_mock.assert_awaited_once()
    assert llm_mock.await_args.kwargs["scenario_id"] == "read.market.depth"


@pytest.mark.asyncio
async def test_telegram_read_market_trades_llm_timeline_event(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    async def fake_trades(*, openapi_base_url: str, symbol_candidates: list[str], limit: int):
        _ = openapi_base_url, limit
        return [{"price": "2", "amount": "1", "side": "BUY"}]

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_trades_json_with_fallbacks",
        fake_trades,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        (
            await http_client.post(
                "/api/v1/agent/api-binding/confirm",
                json={
                    "openapi_base_url": "https://openapi.example.invalid",
                    "api_key": "k" * 8,
                    "secret_key": "s" * 8,
                    "sub_account_id": "900001",
                    "telegram": {"tg_id": "50320"},
                },
            )
        ).status_code
        == 200
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TRADES", "true")
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        AsyncMock(return_value=(None, "noop", {})),
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 55}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 141,
                "from": {"id": 50320, "is_bot": False, "username": "tusr"},
                "chat": {"id": 534350, "type": "private"},
                "text": "ETH-USDT 近期成交",
            },
        },
    )
    assert r.status_code == 200

    lst = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"userId": "50320", "limit": 5},
    )
    assert lst.status_code == 200
    eid = lst.json()["items"][0]["executionId"]
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    names = [x["eventName"] for x in tl.json()["items"]]
    assert "llm.read.market.trades" in names


@pytest.mark.asyncio
async def test_telegram_read_account_balance_llm_narration_success(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    async def fake_account_json(*, openapi_base_url: str, api_key: str, secret_key: str):
        _ = openapi_base_url, api_key, secret_key
        return {"balances": [{"asset": "USDT", "free": "12.5", "locked": "0"}]}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_signed_spot_account_json",
        fake_account_json,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        (
            await http_client.post(
                "/api/v1/agent/api-binding/confirm",
                json={
                    "openapi_base_url": "https://openapi.example.invalid",
                    "api_key": "k" * 8,
                    "secret_key": "s" * 8,
                    "sub_account_id": "900001",
                    "telegram": {"tg_id": "50330"},
                },
            )
        ).status_code
        == 200
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_ACCOUNT_BALANCE", "true")
    reset_settings_cache()

    llm_mock = AsyncMock(
        return_value=("余额简报 LLM。", None, {"gatewayModelId": "gpt-mini"}),
    )
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        llm_mock,
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 60}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 161,
                "from": {"id": 50330, "is_bot": False, "username": "buser"},
                "chat": {"id": 534360, "type": "private"},
                "text": "查余额",
            },
        },
    )
    assert r.status_code == 200
    reply = mocked.await_args.kwargs["json_payload"]["text"]
    assert "余额简报 LLM。" in reply
    assert "read.account.balance" in reply
    llm_mock.assert_awaited_once()
    assert llm_mock.await_args.kwargs["scenario_id"] == "read.account.balance"


@pytest.mark.asyncio
async def test_telegram_read_account_balance_llm_timeline_event(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    async def fake_account_json(*, openapi_base_url: str, api_key: str, secret_key: str):
        _ = openapi_base_url, api_key, secret_key
        return {"balances": [{"asset": "BTC", "free": "0", "locked": "0"}]}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_signed_spot_account_json",
        fake_account_json,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        (
            await http_client.post(
                "/api/v1/agent/api-binding/confirm",
                json={
                    "openapi_base_url": "https://openapi.example.invalid",
                    "api_key": "k" * 8,
                    "secret_key": "s" * 8,
                    "sub_account_id": "900001",
                    "telegram": {"tg_id": "50331"},
                },
            )
        ).status_code
        == 200
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_ACCOUNT_BALANCE", "true")
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        AsyncMock(return_value=(None, "noop", {})),
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 62}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 163,
                "from": {"id": 50331, "is_bot": False, "username": "buser2"},
                "chat": {"id": 534361, "type": "private"},
                "text": "账户余额",
            },
        },
    )
    assert r.status_code == 200

    lst = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"userId": "50331", "limit": 5},
    )
    assert lst.status_code == 200
    eid = lst.json()["items"][0]["executionId"]
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    names = [x["eventName"] for x in tl.json()["items"]]
    assert "llm.read.account.balance" in names


@pytest.mark.asyncio
async def test_telegram_wealth_holdings_read_llm_timeline_event(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    async def fake_by_type(
        *,
        openapi_base_url: str,
        api_key: str,
        secret_key: str,
        account_type: int = 4,
        timeout_s: float = 10.0,
    ):
        _ = openapi_base_url, api_key, secret_key, timeout_s
        assert account_type == 4
        return {"balances": [{"asset": "USDT", "free": "1", "locked": "0"}]}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_signed_asset_account_by_type_json",
        fake_by_type,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        (
            await http_client.post(
                "/api/v1/agent/api-binding/confirm",
                json={
                    "openapi_base_url": "https://openapi.example.invalid",
                    "api_key": "k" * 8,
                    "secret_key": "s" * 8,
                    "sub_account_id": "900001",
                    "telegram": {"tg_id": "50340"},
                },
            )
        ).status_code
        == 200
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_WEALTH_HOLDINGS_READ", "true")
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        AsyncMock(return_value=(None, "noop", {})),
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 61}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 162,
                "from": {"id": 50340, "is_bot": False, "username": "wuser"},
                "chat": {"id": 534370, "type": "private"},
                "text": "帮我看下理财持仓",
            },
        },
    )
    assert r.status_code == 200

    lst = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"userId": "50340", "limit": 5},
    )
    assert lst.status_code == 200
    eid = lst.json()["items"][0]["executionId"]
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    names = [x["eventName"] for x in tl.json()["items"]]
    assert "llm.wealth.holdings_read" in names


@pytest.mark.asyncio
async def test_telegram_wealth_holdings_read_llm_narration_success(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    async def fake_by_type(
        *,
        openapi_base_url: str,
        api_key: str,
        secret_key: str,
        account_type: int = 4,
        timeout_s: float = 10.0,
    ):
        _ = openapi_base_url, api_key, secret_key, timeout_s
        assert account_type == 4
        return {"balances": [{"asset": "USDT", "free": "2", "locked": "0"}]}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_signed_asset_account_by_type_json",
        fake_by_type,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        (
            await http_client.post(
                "/api/v1/agent/api-binding/confirm",
                json={
                    "openapi_base_url": "https://openapi.example.invalid",
                    "api_key": "k" * 8,
                    "secret_key": "s" * 8,
                    "sub_account_id": "900001",
                    "telegram": {"tg_id": "50342"},
                },
            )
        ).status_code
        == 200
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_WEALTH_HOLDINGS_READ", "true")
    reset_settings_cache()

    llm_mock = AsyncMock(
        return_value=("理财简报 LLM。", None, {"gatewayModelId": "gpt-mini"}),
    )
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        llm_mock,
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 63}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 164,
                "from": {"id": 50342, "is_bot": False, "username": "wuser2"},
                "chat": {"id": 534372, "type": "private"},
                "text": "理财持仓什么样",
            },
        },
    )
    assert r.status_code == 200
    reply = mocked.await_args.kwargs["json_payload"]["text"]
    assert "理财简报 LLM。" in reply
    assert "wealth.holdings_read" in reply
    llm_mock.assert_awaited_once()
    assert llm_mock.await_args.kwargs["scenario_id"] == "wealth.holdings_read"


@pytest.mark.asyncio
async def test_access_evaluate_allowlist_matches_telegram_chat_id(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "424242")
    reset_settings_cache()

    r = await http_client.post(
        "/api/v1/agent/access/evaluate",
        json={"userId": "99", "telegramChatId": 424242},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["allowed"] is True
    assert data.get("capabilities", {}).get("boundChatAllowlist") is True
    assert data.get("requiresMainSite") is False


@pytest.mark.asyncio
async def test_onboarding_and_binding_status_flow(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)

    r_bad = await http_client.get("/api/v1/agent/api-binding/status", params={"userId": "x"})
    assert r_bad.status_code == 422
    assert r_bad.json()["code"] == "VALIDATION_ERROR"

    r_none = await http_client.get("/api/v1/agent/api-binding/status", params={"userId": "777"})
    assert r_none.status_code == 200
    nj = r_none.json()
    assert nj["telegramUserId"] == 777
    assert nj["agentTradingApiBindingStatus"] == "NONE"

    r_sub = await http_client.get("/api/v1/agent/subaccount/status", params={"userId": "777"})
    assert r_sub.status_code == 200
    sj = r_sub.json()
    assert sj["subaccountReady"] is False
    assert sj["tradingApiBindingStatus"] == "NONE"
    assert sj["agentSubAccountId"] is None

    ini = await http_client.post("/api/v1/agent/onboarding/initiate", json={})
    assert ini.status_code == 400
    assert ini.json()["code"] == "AGENT_TELEGRAM_CONTEXT_REQUIRED"

    ini2 = await http_client.post(
        "/api/v1/agent/onboarding/initiate",
        json={"telegram": {"tg_id": "777"}},
    )
    assert ini2.status_code == 200
    oj = ini2.json()
    assert len(oj.get("onboardingId", "")) >= 8
    assert oj["nextStep"] == "bind_trading_api"
    assert oj["agentTradingApiBindingStatus"] == "NONE"
    assert oj["telegramUserId"] == 777

    defer = await http_client.post("/api/v1/agent/subaccount/create")
    assert defer.status_code == 200
    dj = defer.json()
    assert dj["accepted"] is False
    assert dj["code"] == "AGENT_SUBACCOUNT_CREATE_PHASE1_NOT_AUTOMATED"
    assert dj["status"] == "DEFERRED_EXCHANGE_CONSOLE"

    confirm = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid/",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "777"},
        },
    )
    assert confirm.status_code == 200

    r_bound = await http_client.get("/api/v1/agent/api-binding/status", params={"userId": "777"})
    assert r_bound.status_code == 200
    bj = r_bound.json()
    assert bj["agentTradingApiBindingStatus"] == "BOUND"
    assert bj["openapiBaseUrl"].rstrip("/") == "https://openapi.example.invalid"
    assert bj["bindingId"] is not None

    r_eval_sub = await http_client.post(
        "/api/v1/agent/access/evaluate",
        json={"subAccountId": "900001"},
    )
    assert r_eval_sub.status_code == 200
    ev = r_eval_sub.json()
    assert ev["allowed"] is True
    assert ev.get("capabilities", {}).get("telegramUserId") == "777"
    assert ev.get("capabilities", {}).get("bindingVerified") is True
    assert ev.get("requiresMainSite") is False

    r_eval_bad_sub = await http_client.post(
        "/api/v1/agent/access/evaluate",
        json={"subAccountId": "no_such_sub"},
    )
    assert r_eval_bad_sub.status_code == 422
    assert r_eval_bad_sub.json()["code"] == "VALIDATION_ERROR"

    ini3 = await http_client.post(
        "/api/v1/agent/onboarding/initiate",
        json={"telegram": {"tg_id": "777"}},
    )
    assert ini3.status_code == 200
    assert ini3.json()["nextStep"] == "complete"
    assert ini3.json()["agentTradingApiBindingStatus"] == "BOUND"

    r_sub2 = await http_client.get("/api/v1/agent/subaccount/status", params={"userId": "777"})
    assert r_sub2.status_code == 200
    assert r_sub2.json()["subaccountReady"] is True
    assert r_sub2.json()["tradingApiBindingStatus"] == "BOUND"


@pytest.mark.asyncio
async def test_runtime_access_evaluate_subaccount_required(
    http_client: AsyncClient,
) -> None:
    r = await http_client.post(
        "/api/v1/agent/access/evaluate",
        json={"userId": "9123459876543210987", "channel": "telegram"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["allowed"] is False
    assert body["code"] == "AGENT_SUBACCOUNT_REQUIRED"
    assert body.get("requiresMainSite") is True


@pytest.mark.asyncio
async def test_runtime_access_evaluate_allowlist(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "42")
    reset_settings_cache()
    r = await http_client.post(
        "/api/v1/agent/access/evaluate",
        json={"userId": "42", "channel": "telegram"},
    )
    assert r.status_code == 200
    assert r.json()["allowed"] is True
    caps = r.json().get("capabilities") or {}
    assert caps.get("boundChatAllowlist") is True
    assert r.json().get("requiresMainSite") is False


@pytest.mark.asyncio
async def test_runtime_intent_market_keyword(http_client: AsyncClient) -> None:
    r = await http_client.post("/api/v1/agent/intent/recognize", json={"text": "ETH 现在有行情吗"})
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "read.market.ticker"
    assert body.get("plan", {}).get("nextStep") == "ROUTE_READ_SKILL"
    assert body.get("orchestrationVersion")


@pytest.mark.asyncio
async def test_intent_recognize_nlu_plan_shape(http_client: AsyncClient) -> None:
    r = await http_client.post("/api/v1/agent/intent/recognize", json={"text": "BTC-USDT 行情"})
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "read.market.ticker"
    assert body.get("plan", {}).get("nextStep") == "ROUTE_READ_SKILL"
    assert body.get("nlu", {}).get("source") == "keyword_v1"
    assert body.get("nlu", {}).get("slots", {}).get("symbol")


@pytest.mark.asyncio
async def test_intent_recognize_fr_ao02_trade_track_conflict(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "限价闪兑 0.1 BTC"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("scenarioId") is None
    assert body["plan"]["nextStep"] == "CLARIFY"
    assert "FR_AO02_AMBIGUOUS" in body["plan"].get("policyCodes", [])


@pytest.mark.asyncio
async def test_intent_recognize_flash_convert_confirm_type_a(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "市价买入 0.1 BTC-USDT"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["plan"]["nextStep"] == "CONFIRM_TYPE_A"
    assert body["scenarioId"] == "trade.spot.flash_convert"


@pytest.mark.asyncio
async def test_intent_recognize_limit_order_confirm_type_a(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "BTC-USDT 限价买入 价格 65000 数量 0.01"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["plan"]["nextStep"] == "CONFIRM_TYPE_A"
    assert body["scenarioId"] == "trade.spot.limit_order"
    assert body["nlu"]["slots"].get("price") == "65000"
    assert body["nlu"]["slots"].get("quantity") == "0.01"


@pytest.mark.asyncio
async def test_intent_recognize_cancel_execute_spot_cancel(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={
            "text": "撤单 BTC-USDT 订单号 499890200602846976",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.spot.cancel_order"
    assert body["plan"]["nextStep"] == "EXECUTE_SPOT_CANCEL"
    assert body["nlu"]["slots"].get("orderId") == "499890200602846976"
    assert body["nlu"]["slots"].get("symbol") == "BTC-USDT"


@pytest.mark.asyncio
async def test_intent_recognize_cancel_clarify_missing_order_id(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "撤单 BTC-USDT"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.spot.cancel_order"
    assert body["plan"]["nextStep"] == "CLARIFY"


@pytest.mark.asyncio
async def test_intent_recognize_llm_nlu_when_enabled(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``CHAINUP_AGENT_INTENT_NLU_USE_LLM`` wires try_llm_intent_nlu_draft (mocked)."""
    from unittest.mock import AsyncMock

    from chainup_agent.api.schemas.agent_runtime import IntentNluDraft, IntentScenarioCandidateDraft

    monkeypatch.setenv("CHAINUP_AGENT_INTENT_NLU_USE_LLM", "true")
    monkeypatch.setattr(
        "chainup_agent.application.agent_llm_intent_nlu.try_llm_intent_nlu_draft",
        AsyncMock(
            return_value=(
                IntentNluDraft(
                    source="llm_structured_v1",
                    primary_intent_family="chat",
                    scenario_id_candidates=[
                        IntentScenarioCandidateDraft(scenario_id="chat.faq", confidence=0.92),
                    ],
                    slots={},
                    order_type_hint="unknown",
                    clarify_hints=[],
                ),
                [("chat.faq", 0.92)],
            )
        ),
    )
    r = await http_client.post("/api/v1/agent/intent/recognize", json={"text": "hello"})
    assert r.status_code == 200
    body = r.json()
    assert body["nlu"]["source"] == "llm_structured_v1"
    assert body["effectiveIntentNluUseLlm"] is True
    assert body["plan"]["nextStep"] == "ROUTE_CHAT_FAQ"


@pytest.mark.asyncio
async def test_intent_recognize_llm_limit_coerced_to_flash_on_market_buy(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LLM may mislabel 市价买入 as limit; lexical guard prefers flash_convert."""
    from unittest.mock import AsyncMock

    from chainup_agent.api.schemas.agent_runtime import IntentNluDraft, IntentScenarioCandidateDraft

    monkeypatch.setenv("CHAINUP_AGENT_INTENT_NLU_USE_LLM", "true")
    monkeypatch.setattr(
        "chainup_agent.application.agent_llm_intent_nlu.try_llm_intent_nlu_draft",
        AsyncMock(
            return_value=(
                IntentNluDraft(
                    source="llm_structured_v1",
                    primary_intent_family="trade_write",
                    scenario_id_candidates=[
                        IntentScenarioCandidateDraft(
                            scenario_id="trade.spot.limit_order",
                            confidence=0.92,
                        ),
                    ],
                    slots={"symbol": "BTC-USDT", "side": "BUY", "quantity": "0.001"},
                    order_type_hint="limit",
                    clarify_hints=[],
                ),
                [("trade.spot.limit_order", 0.92)],
            )
        ),
    )
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "市价买入 0.001 BTC-USD"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.spot.flash_convert"
    assert body["plan"]["nextStep"] == "CONFIRM_TYPE_A"


@pytest.mark.asyncio
async def test_intent_recognize_feature_trading_off(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHAINUP_AGENT_FEATURE_TRADING", "false")
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "市价买入 0.1 BTC-USDT"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["plan"]["nextStep"] == "BLOCKED_FEATURE"
    assert "FEATURE_TRADING_OFF" in body["plan"].get("policyCodes", [])


@pytest.mark.asyncio
async def test_runtime_execution_accept_get_finalize(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    accept = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={"userId": "42", "scenarioId": "read.market.ticker", "channel": "telegram"},
    )
    assert accept.status_code == 200
    eid = accept.json()["executionId"]
    row = await http_client.get(f"/api/v1/agent/execution/{eid}")
    assert row.status_code == 200
    rj = row.json()
    assert rj["executionId"] == eid
    assert rj.get("promptPackVersion") is None
    assert rj.get("resolvedPromptBinding") is None

    missing = await http_client.get("/api/v1/agent/execution/exec-nonexistent-xxxx")
    assert missing.status_code == 404

    fin = await http_client.post(
        "/api/v1/agent/execution/finalize",
        json={"executionId": eid, "outcome": "SUCCESS"},
    )
    assert fin.status_code == 200
    assert fin.json()["state"] == "SUCCEEDED"


@pytest.mark.asyncio
async def test_execution_accept_stores_prompt_snapshot_when_pack_published(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    c = await http_client.post(
        "/api/v1/admin/prompt-packs",
        json={
            "promptPackType": "TRADING",
            "scenarioId": "read.market.ticker",
            "promptPackId": "pack_exec_snap_ticker",
        },
    )
    assert c.status_code == 201
    patch = await http_client.patch(
        "/api/v1/admin/prompt-packs/pack_exec_snap_ticker",
        json={"messages": [{"role": "system", "content": "v1 summary for ticker"}]},
    )
    assert patch.status_code == 200
    pub = await http_client.post("/api/v1/admin/prompt-packs/pack_exec_snap_ticker/publish")
    assert pub.status_code == 200
    assert pub.json()["lifecycle"] == "PUBLISHED"

    accept = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={"userId": "99", "scenarioId": "read.market.ticker", "channel": "telegram"},
    )
    assert accept.status_code == 200
    eid = accept.json()["executionId"]
    row = await http_client.get(f"/api/v1/agent/execution/{eid}")
    assert row.status_code == 200
    rj = row.json()
    assert rj["promptPackVersion"] == "3"
    assert isinstance(rj.get("resolvedPromptBinding"), dict)
    assert rj["resolvedPromptBinding"].get("scenarioId") == "read.market.ticker"


@pytest.mark.asyncio
async def test_intent_recognize_returns_effective_locale(
    http_client: AsyncClient,
) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "BTC-USDT 行情", "locale": "zh-TW"},
    )
    assert r.status_code == 200
    assert r.json().get("effectiveLocale") == "zh-Hant"


@pytest.mark.asyncio
async def test_admin_observability_executions_list_and_get(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    accept = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={"userId": "4242", "scenarioId": "chat.faq", "channel": "telegram"},
    )
    assert accept.status_code == 200
    eid = accept.json()["executionId"]

    lst = await http_client.get("/api/v1/admin/observability/executions")
    assert lst.status_code == 200
    data = lst.json()
    assert data["total"] >= 1
    row = next(i for i in data["items"] if i["executionId"] == eid)
    assert row["userId"] == "4242"
    assert row["state"] == "ACCEPTED"
    assert row["channel"] == "telegram"

    det = await http_client.get(f"/api/v1/admin/observability/executions/{eid}")
    assert det.status_code == 200
    dj = det.json()
    assert dj["executionId"] == eid
    assert dj["scenarioId"] == "chat.faq"

    nf = await http_client.get("/api/v1/admin/observability/executions/exec_missing_xx")
    assert nf.status_code == 404
    assert nf.json()["code"] == "AGENT_ADMIN_EXECUTION_NOT_FOUND"

    bad_state = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"state": "nope"},
    )
    assert bad_state.status_code == 422

    suffix = eid[-6:]
    kw = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"keyword": suffix},
    )
    assert kw.status_code == 200
    assert any(i["executionId"] == eid for i in kw.json()["items"])

    await http_client.post(
        "/api/v1/agent/execution/finalize",
        json={"executionId": eid, "outcome": "SUCCESS"},
    )
    succ = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"state": "SUCCEEDED"},
    )
    assert succ.status_code == 200
    assert any(i["executionId"] == eid for i in succ.json()["items"])


@pytest.mark.asyncio
async def test_admin_observability_execution_delete(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    accept = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={"userId": "999", "scenarioId": "chat.faq", "channel": "telegram"},
    )
    assert accept.status_code == 200
    eid = accept.json()["executionId"]

    rm = await http_client.delete(f"/api/v1/admin/observability/executions/{eid}")
    assert rm.status_code == 204

    gone = await http_client.get(f"/api/v1/admin/observability/executions/{eid}")
    assert gone.status_code == 404

    again = await http_client.delete(f"/api/v1/admin/observability/executions/{eid}")
    assert again.status_code == 404
    assert again.json()["code"] == "AGENT_ADMIN_EXECUTION_NOT_FOUND"


@pytest.mark.asyncio
async def test_admin_observability_execution_timeline_empty_and_populated(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from chainup_agent.application.agent_execution_events import append_execution_timeline_event
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    await _init_schema_sqlite(monkeypatch, tmp_path)
    accept = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={
            "userId": "7171",
            "scenarioId": "trade.spot.flash_convert",
            "channel": "telegram",
        },
    )
    assert accept.status_code == 200
    eid = accept.json()["executionId"]

    tl0 = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl0.status_code == 200
    assert tl0.json()["items"] == []

    factory = get_session_factory()
    async with factory() as session:
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id="7171",
            event_name="agent.execution.step",
            step_kind="submit_order",
            outcome="success",
            payload={"symbol": "BTC-USDT"},
        )
        await append_execution_timeline_event(
            session,
            execution_id=eid,
            user_id="7171",
            event_name="trading.exchange_private",
            outcome="fail",
            payload={"methodPathSummary": "POST /sapi/v2/order", "exchangeMsg": "no"},
        )
        await session.commit()

    tl1 = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl1.status_code == 200
    items = tl1.json()["items"]
    assert len(items) == 2
    assert items[0]["eventName"] == "agent.execution.step"
    assert items[0]["summary"]["symbol"] == "BTC-USDT"
    assert items[0]["summary"]["stepKind"] == "submit_order"
    assert items[1]["eventName"] == "trading.exchange_private"
    assert items[1]["summary"]["exchangeMsg"] == "no"

    nf = await http_client.get("/api/v1/admin/observability/executions/exec_missing_yy/timeline")
    assert nf.status_code == 404


@pytest.mark.asyncio
async def test_runtime_access_reasons_catalog(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/agent/access/reasons")
    assert r.status_code == 200
    reasons = r.json()["reasons"]
    codes = {x["code"] for x in reasons}
    assert "AGENT_SUBACCOUNT_REQUIRED" in codes


@pytest.mark.asyncio
async def test_runtime_scenarios_list(http_client: AsyncClient) -> None:
    r = await http_client.get("/api/v1/agent/scenarios")
    assert r.status_code == 200
    body = r.json()
    assert body.get("orchestrationRegistryVersion") == "2026.05-orc-v1"
    ids = {s["scenarioId"] for s in body.get("scenarios", [])}
    assert "read.market.ticker" in ids
    assert "read.market.depth" in ids
    assert "read.market.trades" in ids
    assert "wealth.holdings_read" in ids
    assert "trade.futures.limit_order" in ids
    assert "automation.condition_order" in ids


@pytest.mark.asyncio
async def test_runtime_intent_wealth_keyword(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "帮我看下理财持仓"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "wealth.holdings_read"
    assert body.get("plan", {}).get("nextStep") == "ROUTE_READ_SKILL"


@pytest.mark.asyncio
async def test_runtime_intent_depth_keyword(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "帮我看看 BTC-USDT 盘口"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "read.market.depth"
    assert body.get("plan", {}).get("nextStep") == "ROUTE_READ_SKILL"


@pytest.mark.asyncio
async def test_runtime_intent_trades_keyword(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "ETH-USDT 近期成交"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "read.market.trades"
    assert body.get("plan", {}).get("nextStep") == "ROUTE_READ_SKILL"


@pytest.mark.asyncio
async def test_runtime_intent_futures_market_keyword(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "BTC永续市价买入 0.01"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.futures.market_order"
    assert body.get("plan", {}).get("nextStep") in ("CONFIRM_TYPE_A", "CLARIFY")


@pytest.mark.asyncio
async def test_runtime_intent_futures_limit_keyword(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "ETH永续限价委托 62000"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.futures.limit_order"
    assert body.get("plan", {}).get("nextStep") in ("CONFIRM_TYPE_A", "CLARIFY")


@pytest.mark.asyncio
async def test_runtime_intent_condition_order_keyword(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "BTC-USDT 条件单 触发价 91000"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "automation.condition_order"
    assert body.get("plan", {}).get("nextStep") == "CLARIFY"


@pytest.mark.asyncio
async def test_runtime_intent_margin_keyword(http_client: AsyncClient) -> None:
    r = await http_client.post(
        "/api/v1/agent/intent/recognize",
        json={"text": "全仓杠杆市价买入 BTC-USDT"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "margin.cross.market_order"
    assert body.get("plan", {}).get("nextStep") in (
        "CONFIRM_TYPE_A",
        "CLARIFY",
        "RESOLVE_TRADE_NOTIONAL",
    )


@pytest.mark.asyncio
async def test_routing_execute_read_market_depth_mocked(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    async def fake_depth(*, openapi_base_url: str, symbol_candidates: list[str], limit: int):
        assert symbol_candidates
        _ = openapi_base_url, limit
        return {"asks": [["65000", "0.1"]], "bids": [["64999", "0.2"]]}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_spot_public_depth_json_with_fallbacks",
        fake_depth,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    c = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "7701"},
        },
    )
    assert c.status_code == 200

    r = await http_client.post(
        "/api/v1/agent/routing/execute",
        json={
            "userId": "7701",
            "scenarioId": "read.market.depth",
            "symbol": "BTC-USDT",
            "marketDataLimit": 5,
        },
    )
    assert r.status_code == 200
    j = r.json()
    assert j.get("routed") is True
    eid = j.get("executionId")
    assert eid and str(eid).startswith("exec-")
    prev = j.get("exchangeReadPreview") or {}
    assert prev.get("kind") == "spot_depth_v2_filtered"
    assert prev.get("limitRequested") == 5

    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    items = tl.json().get("items") or []
    assert len(items) >= 1
    assert items[0].get("eventName") == "trading.exchange_public"
    assert items[0].get("summary", {}).get("transitionTrigger") == "routing.read.public_depth"


@pytest.mark.asyncio
async def test_routing_execute_wealth_holdings_mocked(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    async def fake_by_type(
        *,
        openapi_base_url: str,
        api_key: str,
        secret_key: str,
        account_type: int = 4,
        timeout_s: float = 10.0,
    ):
        _ = openapi_base_url, api_key, secret_key, timeout_s
        assert account_type == 4
        return {"balances": [{"asset": "USDT", "free": "1", "locked": "0"}]}

    monkeypatch.setattr(
        "chainup_agent.application.agent_routing_exchange_read.fetch_signed_asset_account_by_type_json",
        fake_by_type,
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    c = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "7702"},
        },
    )
    assert c.status_code == 200

    r = await http_client.post(
        "/api/v1/agent/routing/execute",
        json={
            "userId": "7702",
            "scenarioId": "wealth.holdings_read",
        },
    )
    assert r.status_code == 200
    j = r.json()
    assert j.get("routed") is True
    prev = j.get("exchangeReadPreview") or {}
    assert prev.get("kind") == "wealth_holdings_otc_v1"
    assert prev.get("accountTypeRequested") == 4

    eid = j.get("executionId")
    assert eid
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    items = tl.json().get("items") or []
    assert len(items) >= 1
    assert items[0].get("eventName") == "trading.exchange_private"
    assert items[0].get("summary", {}).get("transitionTrigger") == "routing.read.private_wealth"


@pytest.mark.asyncio
async def test_routing_execute_open_orders_mocked(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_signed_spot_open_orders_json",
        AsyncMock(
            return_value=[
                {
                    "orderIdString": "111",
                    "symbol": "BTCUSDT",
                    "status": "NEW",
                    "type": "LIMIT",
                    "side": "BUY",
                    "price": "60000",
                    "origQty": "0.01",
                }
            ]
        ),
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    c = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900001",
            "telegram": {"tg_id": "7703"},
        },
    )
    assert c.status_code == 200

    r = await http_client.post(
        "/api/v1/agent/routing/execute",
        json={
            "userId": "7703",
            "scenarioId": "trade.spot.open_orders",
            "symbol": "BTC-USDT",
            "marketDataLimit": 50,
        },
    )
    assert r.status_code == 200
    j = r.json()
    assert j.get("routed") is True
    prev = j.get("exchangeReadPreview") or {}
    assert prev.get("kind") == "spot_open_orders_v1"
    assert prev.get("orderCount") == 1
    eid = j.get("executionId")
    assert eid
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    items = tl.json().get("items") or []
    assert items[0].get("eventName") == "trading.exchange_private"
    assert items[0].get("summary", {}).get("transitionTrigger") == "routing.read.spot_open_orders"


@pytest.mark.asyncio
async def test_routing_execute_http_records_failed_execution_on_subaccount_required(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Unbound user: accept → exchange attempt → timeline failure row → finalize FAILED."""
    from sqlalchemy import select

    from chainup_agent.infrastructure.persistence.base import get_session_factory
    from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    r = await http_client.post(
        "/api/v1/agent/routing/execute",
        json={
            "userId": "88002",
            "scenarioId": "read.market.ticker",
            "symbol": "BTC-USDT",
        },
    )
    assert r.status_code == 403

    factory = get_session_factory()
    async with factory() as session:
        res = await session.execute(
            select(AgentExecution)
            .where(AgentExecution.user_id == "88002")
            .order_by(AgentExecution.created_at.desc())
            .limit(1)
        )
        row = res.scalar_one_or_none()
    assert row is not None
    assert row.state == "FAILED"


@pytest.mark.asyncio
async def test_request_id_roundtrip(http_client: AsyncClient) -> None:
    r = await http_client.get("/health", headers={"x-request-id": "abc-123"})
    assert r.headers.get("x-request-id") == "abc-123"


@pytest.mark.asyncio
async def test_admin_login_disabled_when_unconfigured(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_PANEL_USERNAME", "")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_PANEL_PASSWORD", "")
    reset_settings_cache()
    r = await http_client.post("/api/auth/login", json={"username": "x", "password": "y"})
    assert r.status_code == 503
    assert r.json()["code"] == "ADMIN_CONSOLE_AUTH_DISABLED"


@pytest.mark.asyncio
async def test_admin_login_success(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_PANEL_USERNAME", "ops")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_PANEL_PASSWORD", "secret")
    reset_settings_cache()
    r = await http_client.post("/api/auth/login", json={"username": "ops", "password": "secret"})
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == "ops"
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 10


@pytest.mark.asyncio
async def test_admin_login_invalid_password(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_PANEL_USERNAME", "ops")
    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_PANEL_PASSWORD", "secret")
    reset_settings_cache()
    r = await http_client.post("/api/auth/login", json={"username": "ops", "password": "wrong"})
    assert r.status_code == 401
    assert r.json()["code"] == "ADMIN_CONSOLE_AUTH_INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_telegram_webhook_503_when_token_not_configured(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "")
    reset_settings_cache()
    r = await http_client.post("/webhook/telegram/anything", content=b"{}")
    assert r.status_code == 503
    assert r.json()["code"] == "TELEGRAM_WEBHOOK_NOT_CONFIGURED"


@pytest.mark.asyncio
async def test_telegram_webhook_404_when_path_token_mismatch(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa")
    reset_settings_cache()
    r = await http_client.post("/webhook/telegram/wrong:aaaaaaaaaaaaaaaaaaaaaaaaaa", content=b"{}")
    assert r.status_code == 404
    assert r.json()["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_telegram_webhook_200_when_path_matches_config(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 1}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    path = f"/webhook/telegram/{enc}"
    r = await http_client.post(path, content=b"{}")
    assert r.status_code == 200
    assert r.text == ""
    mocked.assert_not_awaited()


@pytest.mark.asyncio
async def test_telegram_webhook_send_message_on_text(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 2}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    path = f"/webhook/telegram/{enc}"
    payload = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {
                "id": 99,
                "is_bot": False,
                "username": "alice",
                "first_name": "Al",
                "last_name": "Ice",
                "language_code": "en",
            },
            "chat": {"id": 424242, "type": "private"},
            "text": "你好",
        },
    }
    r = await http_client.post(path, json=payload)
    assert r.status_code == 200
    mocked.assert_awaited_once()
    args, kwargs = mocked.await_args
    assert args[1] == "sendMessage"
    body = kwargs["json_payload"]
    assert body["chat_id"] == 424242
    assert "要使用交易助手" in body["text"]
    assert "你刚发的内容摘要" not in body["text"]
    deeplink_example = "https://exchange.example/agent/telegram-bind"
    assert deeplink_example not in body["text"]
    btn_url = body["reply_markup"]["inline_keyboard"][0][0]["url"]
    assert btn_url.startswith(deeplink_example)
    _assert_tg_query(
        btn_url,
        tg_id="99",
        tg_username="alice",
        tg_first_name="Al",
        tg_last_name="Ice",
        tg_lang="en",
    )


@pytest.mark.asyncio
async def test_telegram_webhook_build_reply_exception_still_send_message(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression: errors during reply build must still trigger sendMessage (fallback text)."""
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound._build_bound_user_reply",
        AsyncMock(side_effect=RuntimeError("simulated defect")),
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 99}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    path = f"/webhook/telegram/{enc}"
    payload = {
        "update_id": 991,
        "message": {
            "message_id": 1,
            "from": {"id": 55, "is_bot": False},
            "chat": {"id": 313131, "type": "private"},
            "text": "你好",
        },
    }
    r = await http_client.post(path, json=payload)
    assert r.status_code == 200
    mocked.assert_awaited_once()
    body = mocked.await_args.kwargs["json_payload"]
    assert body["chat_id"] == 313131
    assert "服务端异常" in body["text"]


@pytest.mark.asyncio
async def test_telegram_webhook_private_chat_fallback_tg_id_without_from(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When ``from.id`` absent in a private chat, prefill ``tg_id`` from ``chat.id``."""
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 2}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    path = f"/webhook/telegram/{enc}"
    payload = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "chat": {"id": 424242, "type": "private"},
            "text": "你好",
        },
    }
    r = await http_client.post(path, json=payload)
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    btn_url = body["reply_markup"]["inline_keyboard"][0][0]["url"]
    _assert_tg_query(btn_url, tg_id="424242")


@pytest.mark.asyncio
async def test_telegram_webhook_send_message_on_photo_caption_only(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """treats caption as user text when `text` absent."""
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 12}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    path = f"/webhook/telegram/{enc}"
    payload = {
        "update_id": 9,
        "message": {
            "message_id": 2,
            "from": {"id": 501, "is_bot": False, "username": "bob"},
            "chat": {"id": 424242, "type": "private"},
            "photo": [{"file_id": "x"}],
            "caption": "看这张图",
        },
    }
    r = await http_client.post(path, json=payload)
    assert r.status_code == 200
    mocked.assert_awaited_once()
    body = mocked.await_args.kwargs["json_payload"]
    assert "要使用交易助手" in body["text"]
    assert "看这张图" not in body["text"]


@pytest.mark.asyncio
async def test_telegram_webhook_localhost_http_no_inline_keyboard_plaintext_only(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Telegram API rejects localhost http as inline url; we skip button and rely on plaintext."""
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL", "http://localhost:5174/")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 9}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    path = f"/webhook/telegram/{enc}"
    payload = {
        "update_id": 1,
        "message": {
            "message_id": 3,
            "from": {"id": 77, "is_bot": False, "username": "localuser"},
            "chat": {"id": 424242, "type": "private"},
            "text": "hi",
        },
    }
    r = await http_client.post(path, json=payload)
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    assert body.get("reply_markup") is None
    plain = _plaintext_bind_url(body)
    assert plain.startswith("http://localhost:5174/")
    _assert_tg_query(plain, tg_id="77", tg_username="localuser")
    assert "你刚发的内容摘要" not in body["text"]


@pytest.mark.asyncio
async def test_telegram_webhook_allowlist_without_db_binding_still_shows_bind_cta(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Allowlist alone does not skip bind CTA; only hosted binding + instance does."""
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "424242")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_INTENT_PREVIEW_IN_REPLY", "true")
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        AsyncMock(return_value=(None, "[测试] 上游 LLM 未接通", None)),
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 3}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    path = f"/webhook/telegram/{enc}"
    payload = {
        "update_id": 1,
        "message": {
            "message_id": 4,
            "from": {"id": 1001, "is_bot": False, "username": "bounduser"},
            "chat": {"id": 424242, "type": "private"},
            "text": "ping",
        },
    }
    r = await http_client.post(path, json=payload)
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    assert body.get("reply_markup") is not None
    assert "前往绑定页面" in str(body["reply_markup"])
    assert "要使用交易助手" in body["text"]
    assert "前往绑定页面" in str(body["reply_markup"])
    assert "你刚发的内容摘要" not in body["text"]
    assert "Deeplink（H5 落地页）访问链接：" not in body["text"]


@pytest.mark.asyncio
async def test_telegram_webhook_shows_bind_after_admin_instance_delete(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    bind = await http_client.post(
        "/api/v1/me/agent/bindings/trading-api",
        json={
            "openapiBaseUrl": "https://openapi.example.invalid",
            "apiKey": "k" * 8,
            "apiSecret": "s" * 8,
            "idempotencyKey": "idem-tg-unbind",
            "subAccountId": "900010",
            "telegram": {"tg_id": "88001"},
        },
    )
    assert bind.status_code == 200
    inst_id = bind.json()["instanceId"]

    rm = await http_client.delete(f"/api/v1/admin/agents/instances/{inst_id}")
    assert rm.status_code == 204

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "88001")
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 9}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    path = f"/webhook/telegram/{enc}"
    payload = {
        "update_id": 2,
        "message": {
            "message_id": 5,
            "from": {"id": 88001, "is_bot": False, "username": "unbounduser"},
            "chat": {"id": 88001, "type": "private"},
            "text": "hello after delete",
        },
    }
    r = await http_client.post(path, json=payload)
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    assert body.get("reply_markup") is not None
    assert "前往绑定页面" in str(body["reply_markup"])
    assert "要使用交易助手" in body["text"]
    assert "你刚发的内容摘要" not in body["text"]


@pytest.mark.asyncio
async def test_telegram_bound_chat_faq_timeline_includes_prompt_and_llm_events(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """AC-09k: Telegram ROUTE_CHAT_FAQ appends intent prompt snapshot + per-LLM chat.faq rows."""
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    c = await http_client.post(
        "/api/v1/agent/api-binding/confirm",
        json={
            "openapi_base_url": "https://openapi.example.invalid",
            "api_key": "k" * 8,
            "secret_key": "s" * 8,
            "sub_account_id": "900424",
            "telegram": {"tg_id": "1001"},
        },
    )
    assert c.status_code == 200

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "424242")
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        AsyncMock(
            return_value=(
                None,
                "[测试] 上游 LLM 未接通",
                {
                    "gatewayModelId": "gpt-4.1-mini",
                    "gatewayProviderId": "demo",
                    "useArkProtocol": False,
                },
            )
        ),
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 31}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 41,
                "from": {"id": 1001, "is_bot": False, "username": "bounduser"},
                "chat": {"id": 424242, "type": "private"},
                "text": "ping",
            },
        },
    )
    assert r.status_code == 200

    lst = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"userId": "1001", "limit": 5},
    )
    assert lst.status_code == 200
    exec_items = lst.json()["items"]
    assert exec_items
    eid = exec_items[0]["executionId"]
    assert exec_items[0]["userId"] == "1001"

    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    titems = tl.json()["items"]
    names = [x["eventName"] for x in titems]
    assert "prompt.snapshot" in names
    assert "llm.chat.faq" in names
    snap = next(x for x in titems if x["eventName"] == "prompt.snapshot")
    assert snap["summary"].get("stepKind") == "intent_nlu"
    assert snap["summary"].get("scenarioId") == "agent.runtime.intent_nlu"
    llm_row = next(x for x in titems if x["eventName"] == "llm.chat.faq")
    assert llm_row["summary"].get("gatewayModelId") == "gpt-4.1-mini"
    assert llm_row["summary"].get("outcome") == "failure"


@pytest.mark.asyncio
async def test_telegram_webhook_bind_url_missing_no_inline_keyboard(
    http_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL", "")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 4}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    path = f"/webhook/telegram/{enc}"
    payload = {"update_id": 1, "message": {"chat": {"id": 424242}, "text": "你好"}}
    r = await http_client.post(path, json=payload)
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    assert body.get("reply_markup") is None
    assert "TELEGRAM_BIND_PAGE_URL" in body["text"]


@pytest.mark.asyncio
async def test_admin_telegram_webhook_get_503_unconfigured(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "")
    reset_settings_cache()
    r = await http_client.get("/api/v1/admin/channels/telegram/webhook")
    assert r.status_code == 503
    assert r.json()["code"] == "TELEGRAM_WEBHOOK_NOT_CONFIGURED"


@pytest.mark.asyncio
async def test_admin_telegram_webhook_get_200_mocked(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "t")
    reset_settings_cache()

    mocked = AsyncMock(
        return_value={
            "ok": True,
            "result": {
                "url": "https://example.com/hook",
                "has_custom_certificate": False,
                "pending_update_count": 2,
                "last_error_date": None,
                "last_error_message": None,
                "max_connections": 40,
            },
        }
    )
    monkeypatch.setattr(
        "chainup_agent.application.telegram_webhook_admin.call_telegram_bot_api",
        mocked,
    )

    r = await http_client.get("/api/v1/admin/channels/telegram/webhook")
    assert r.status_code == 200
    data = r.json()
    assert data["url"] == "https://example.com/hook"
    assert data["pendingUpdateCount"] == 2
    assert data["hasCustomCertificate"] is False
    mocked.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_telegram_bot_get_200_mocked(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "123:abc")
    reset_settings_cache()

    mocked = AsyncMock(
        return_value={
            "ok": True,
            "result": {
                "id": 8944674236,
                "is_bot": True,
                "first_name": "Demo",
                "username": "demo_bot",
            },
        }
    )
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bot_admin.call_telegram_bot_api",
        mocked,
    )

    r = await http_client.get("/api/v1/admin/channels/telegram/bot")
    assert r.status_code == 200
    data = r.json()
    assert data["tokenConfigured"] is True
    assert data["bot"]["username"] == "demo_bot"
    assert data["secretRefFingerprint"].endswith("abc")
    assert "publicBaseUrl" in data
    assert "defaultWebhookUrl" in data
    mocked.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_telegram_bot_patch_200_merges_runtime_params(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "123:abc")
    reset_settings_cache()

    mocked = AsyncMock(
        return_value={
            "ok": True,
            "result": {"id": 1, "first_name": "X", "username": "x_bot"},
        }
    )
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bot_admin.call_telegram_bot_api",
        mocked,
    )

    r = await http_client.patch(
        "/api/v1/admin/channels/telegram/bot",
        json={
            "runtimeParams": {
                "TELEGRAM_DEFAULT_LOCALE": "zh-Hans",
                "TELEGRAM_CHANNEL_TRADE_OK": True,
            },
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["runtimeParams"]["TELEGRAM_DEFAULT_LOCALE"] == "zh-Hans"
    assert data["runtimeParams"]["TELEGRAM_CHANNEL_TRADE_OK"] is True
    assert data["configVersion"] == 2

    r2 = await http_client.get("/api/v1/admin/channels/telegram/bot")
    assert r2.status_code == 200
    assert r2.json()["configVersion"] == 2


@pytest.mark.asyncio
async def test_admin_telegram_bot_patch_409_if_match_conflict(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "t")
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bot_admin.call_telegram_bot_api",
        AsyncMock(
            return_value={
                "ok": True,
                "result": {"id": 1, "first_name": "X", "username": "x_bot"},
            }
        ),
    )

    await http_client.patch(
        "/api/v1/admin/channels/telegram/bot",
        json={"runtimeParams": {"TELEGRAM_DEFAULT_LOCALE": "en"}},
    )

    r = await http_client.patch(
        "/api/v1/admin/channels/telegram/bot",
        json={"runtimeParams": {"TELEGRAM_DEFAULT_LOCALE": "zh-Hans"}},
        headers={"If-Match": '"1"'},
    )
    assert r.status_code == 409
    assert r.json()["code"] == "AGENT_AI_SETTINGS_VERSION_CONFLICT"


@pytest.mark.asyncio
async def test_admin_telegram_self_test_200_mocked(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "t")
    reset_settings_cache()

    async def _side_effect(
        _token: str,
        method: str,
        *,
        http_method: str = "POST",
        json_payload: dict | None = None,
    ) -> dict:
        _ = http_method, json_payload
        if method == "getMe":
            return {"ok": True, "result": {"id": 1, "first_name": "X", "username": "x_bot"}}
        if method == "getWebhookInfo":
            return {
                "ok": True,
                "result": {
                    "url": "https://example.com/hook",
                    "has_custom_certificate": False,
                    "pending_update_count": 0,
                    "last_error_date": None,
                    "last_error_message": None,
                    "max_connections": 40,
                },
            }
        raise AssertionError(method)

    monkeypatch.setattr(
        "chainup_agent.application.telegram_bot_admin.call_telegram_bot_api",
        _side_effect,
    )
    monkeypatch.setattr(
        "chainup_agent.application.telegram_webhook_admin.call_telegram_bot_api",
        _side_effect,
    )

    r = await http_client.post("/api/v1/admin/channels/telegram/self-test")
    assert r.status_code == 200
    data = r.json()
    assert data["getMeOk"] is True
    assert data["getWebhookInfoOk"] is True
    assert data.get("errorSummary") in (None, "")


@pytest.mark.asyncio
async def test_admin_telegram_webhook_post_200_mocked(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("CHAINUP_AGENT_PUBLIC_BASE_URL", "https://pub.example")
    reset_settings_cache()

    async def _side_effect(
        _token: str,
        method: str,
        *,
        http_method: str = "POST",
        json_payload: dict | None = None,
    ) -> dict:
        _ = http_method
        if method == "setWebhook":
            assert json_payload is not None
            assert json_payload["url"].startswith("https://pub.example/webhook/telegram/")
            return {"ok": True, "result": True, "description": "ok"}
        if method == "getWebhookInfo":
            return {
                "ok": True,
                "result": {
                    "url": "https://pub.example/webhook/telegram/",
                    "has_custom_certificate": False,
                    "pending_update_count": 0,
                    "last_error_date": None,
                    "last_error_message": None,
                    "max_connections": 40,
                },
            }
        msg = f"unexpected {method}"
        raise AssertionError(msg)

    mocked = AsyncMock(side_effect=_side_effect)
    monkeypatch.setattr(
        "chainup_agent.application.telegram_webhook_admin.call_telegram_bot_api",
        mocked,
    )

    r = await http_client.post("/api/v1/admin/channels/telegram/webhook")
    assert r.status_code == 200
    assert mocked.await_count == 2


@pytest.mark.asyncio
async def test_admin_telegram_webhook_post_400_when_http_only_base_url(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("CHAINUP_AGENT_PUBLIC_BASE_URL", "http://localhost:8080")
    reset_settings_cache()

    mocked = AsyncMock()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_webhook_admin.call_telegram_bot_api",
        mocked,
    )

    r = await http_client.post("/api/v1/admin/channels/telegram/webhook", json={})
    assert r.status_code == 400
    body = r.json()
    assert body["code"] == "ADMIN_TELEGRAM_WEBHOOK_HTTPS_REQUIRED"
    mocked.assert_not_called()


@pytest.mark.asyncio
async def test_admin_telegram_webhook_delete_200_mocked(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", "x")
    reset_settings_cache()

    async def _side_effect(_token: str, method: str, **kwargs: object) -> dict:
        del kwargs
        if method == "deleteWebhook":
            return {"ok": True, "result": True}
        if method == "getWebhookInfo":
            return {
                "ok": True,
                "result": {
                    "url": "",
                    "has_custom_certificate": False,
                    "pending_update_count": 0,
                },
            }
        msg = f"unexpected {method}"
        raise AssertionError(msg)

    monkeypatch.setattr(
        "chainup_agent.application.telegram_webhook_admin.call_telegram_bot_api",
        AsyncMock(side_effect=_side_effect),
    )

    r = await http_client.delete("/api/v1/admin/channels/telegram/webhook")
    assert r.status_code == 200
    assert r.json()["url"] == ""


@pytest.mark.asyncio
async def test_admin_ai_settings_providers_defaults_models(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)

    pr = await http_client.get("/api/v1/admin/ai/providers")
    assert pr.status_code == 200
    pj = pr.json()
    assert any(i["providerId"] == "demo" for i in pj["items"])

    mr = await http_client.get("/api/v1/admin/ai/models", params={"providerId": "demo"})
    assert mr.status_code == 200
    ids = {x["modelId"] for x in mr.json()["items"]}
    assert "gpt-4.1-mini" in ids

    pc = await http_client.post(
        "/api/v1/admin/ai/providers",
        json={"displayName": "Inline Provider", "baseUrl": "https://api.inline.example/v1"},
    )
    assert pc.status_code == 201
    assert pc.json()["providerId"]
    assert pc.json()["configured"] is False

    nm = await http_client.post(
        "/api/v1/admin/ai/models",
        json={
            "providerId": "demo",
            "modelId": "custom-inline-model",
            "contextWindowTokens": 8192,
        },
    )
    assert nm.status_code == 201
    assert nm.json()["modelId"] == "custom-inline-model"
    assert nm.json()["providerId"] == "demo"

    dup = await http_client.post(
        "/api/v1/admin/ai/models",
        json={"providerId": "demo", "modelId": "custom-inline-model"},
    )
    assert dup.status_code == 409

    badp = await http_client.post(
        "/api/v1/admin/ai/models",
        json={"providerId": "no-such-provider-xyz", "modelId": "orphan-model"},
    )
    assert badp.status_code == 404

    gd = await http_client.get("/api/v1/admin/ai/models/custom-inline-model")
    assert gd.status_code == 200
    assert gd.json()["providerId"] == "demo"

    pid_inline = pc.json()["providerId"]
    mv = await http_client.patch(
        "/api/v1/admin/ai/models/custom-inline-model",
        json={"providerId": pid_inline, "status": "disabled"},
    )
    assert mv.status_code == 200
    assert mv.json()["providerId"] == pid_inline
    assert mv.json()["status"] == "disabled"

    bad_prov_patch = await http_client.patch(
        "/api/v1/admin/ai/models/custom-inline-model",
        json={"providerId": "no-such-provider-xyz"},
    )
    assert bad_prov_patch.status_code == 404

    delr = await http_client.delete("/api/v1/admin/ai/models/custom-inline-model")
    assert delr.status_code == 204

    gone = await http_client.get("/api/v1/admin/ai/models/custom-inline-model")
    assert gone.status_code == 404

    del404 = await http_client.delete("/api/v1/admin/ai/models/nonexistent-model-xyz")
    assert del404.status_code == 404

    delprov = await http_client.delete(f"/api/v1/admin/ai/providers/{pid_inline}")
    assert delprov.status_code == 204
    assert (
        await http_client.get(f"/api/v1/admin/ai/providers/{pid_inline}")
    ).status_code == 404
    assert (
        await http_client.delete("/api/v1/admin/ai/providers/no-such-provider-abc")
    ).status_code == 404

    dr = await http_client.get("/api/v1/admin/ai/defaults")
    assert dr.status_code == 200
    d = dr.json()
    assert d["defaultProviderId"] == "demo"
    assert d["scenarioChatModel"] == "gpt-4.1-mini"
    assert d.get("intentNluUseLlm") is False
    assert d["orchestrationExecutionBudget"]["maxToolCallsPerExecution"] == 32


@pytest.mark.asyncio
async def test_admin_ai_delete_demo_not_resurrected_when_seed_disabled(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from chainup_agent.core.config import reset_settings_cache

    await _init_schema_sqlite(monkeypatch, tmp_path)
    pr = await http_client.get("/api/v1/admin/ai/providers")
    assert pr.status_code == 200
    assert any(i["providerId"] == "demo" for i in pr.json()["items"])

    monkeypatch.setenv("CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY", "false")
    reset_settings_cache()

    assert (
        await http_client.delete("/api/v1/admin/ai/providers/demo")
    ).status_code == 204
    empty = await http_client.get("/api/v1/admin/ai/providers")
    assert empty.status_code == 200
    assert empty.json()["items"] == []

    again = await http_client.get("/api/v1/admin/ai/providers")
    assert again.json()["items"] == []


@pytest.mark.asyncio
async def test_admin_ai_settings_gateway_patch_conflict_and_health_probe_mock(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    await _init_schema_sqlite(monkeypatch, tmp_path)

    bad = await http_client.patch(
        "/api/v1/admin/ai/defaults",
        json={"timeoutSec": 77},
        headers={"If-Match": '"999"'},
    )
    assert bad.status_code == 409

    ok = await http_client.patch("/api/v1/admin/ai/defaults", json={"timeoutSec": 77})
    assert ok.status_code == 200
    assert ok.json()["timeoutSec"] == 77

    monkeypatch.setattr(
        "chainup_agent.api.routers.admin_ai_settings.probe_provider_health",
        AsyncMock(
            return_value={
                "ok": True,
                "latencyMs": 12,
                "checkedAt": "2026-05-13T00:00:00Z",
                "message": "mock",
            }
        ),
    )
    hr = await http_client.post("/api/v1/admin/ai/providers/demo/health")
    assert hr.status_code == 200
    assert hr.json()["ok"] is True


@pytest.mark.asyncio
async def test_admin_ai_gateway_defaults_patch_422_unknown_model_id(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    ghost = "__ghost_catalog_model_id__not_registered__"
    r = await http_client.patch("/api/v1/admin/ai/defaults", json={"scenarioChatModel": ghost})
    assert r.status_code == 422
    body = r.json()
    assert body["code"] == "AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG"
    missing = body["details"]["missing"]
    assert any(m.get("modelId") == ghost and m.get("field") == "scenarioChatModel" for m in missing)


@pytest.mark.asyncio
async def test_admin_ai_model_api_model_roundtrip(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    wid = "deepseek-ai/DeepSeek-V4-Flash"
    # catalog id must avoid raw ``/`` when used in ``GET …/models/{modelId}`` path segment
    cat = "volc__catalog-ds-flash-v1"
    cr = await http_client.post(
        "/api/v1/admin/ai/models",
        json={"providerId": "demo", "modelId": cat, "apiModel": wid},
    )
    assert cr.status_code == 201
    assert cr.json()["modelId"] == cat
    assert cr.json()["apiModel"] == wid

    gr = await http_client.get(f"/api/v1/admin/ai/models/{cat}")
    assert gr.status_code == 200
    assert gr.json()["apiModel"] == wid


@pytest.mark.asyncio
async def test_admin_ai_model_slash_id_get_patch_delete_via_query(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Catalog ``model_id`` may equal upstream wire id (contains ``/``); use Query, not path segment."""
    await _init_schema_sqlite(monkeypatch, tmp_path)
    mid = "deepseek-ai/DeepSeek-V4-Flash"
    cr = await http_client.post("/api/v1/admin/ai/models", json={"providerId": "demo", "modelId": mid})
    assert cr.status_code == 201

    g = await http_client.get("/api/v1/admin/ai/models", params={"modelId": mid})
    assert g.status_code == 200
    assert len(g.json()["items"]) == 1
    assert g.json()["items"][0]["modelId"] == mid

    clash = await http_client.get("/api/v1/admin/ai/models", params={"modelId": mid, "providerId": "demo"})
    assert clash.status_code == 422

    pr = await http_client.patch("/api/v1/admin/ai/models", params={"modelId": mid}, json={"status": "disabled"})
    assert pr.status_code == 200
    assert pr.json()["status"] == "disabled"

    dl = await http_client.delete("/api/v1/admin/ai/models", params={"modelId": mid})
    assert dl.status_code == 204
    nf = await http_client.get("/api/v1/admin/ai/models", params={"modelId": mid})
    assert nf.status_code == 404


@pytest.mark.asyncio
async def test_spot_quote_403_without_binding(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    r = await http_client.get(
        "/api/v1/agent/trade/spot/quote",
        params={"userId": "40404", "symbol": "BTC-USDT"},
    )
    assert r.status_code == 403
    assert r.json()["code"] == "AGENT_SUBACCOUNT_REQUIRED"


@pytest.mark.asyncio
async def test_spot_quote_200_with_binding_mock_ticker(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "70707"},
            },
        )
    ).status_code == 200

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(
            return_value={"symbol": "BTC-USDT", "lastPrice": "65000.1", "bidPrice": "65000"},
        ),
    )
    r = await http_client.get(
        "/api/v1/agent/trade/spot/quote",
        params={"userId": "70707", "symbol": "BTC-USDT"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["symbol"] == "BTC-USDT"
    assert body["symbolOrder"] == "BTCUSDT"
    assert body["quotePreview"]["lastPrice"] == "65000.1"


@pytest.mark.asyncio
async def test_spot_flash_convert_200_mock_order(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "80808"},
            },
        )
    ).status_code == 200

    post_mock = AsyncMock(
        return_value={
            "orderIdString": "499890200602846976",
            "clientOrderId": "cu_agent_test",
            "status": "0",
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
        },
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        post_mock,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "50000"}),
    )
    r = await http_client.post(
        "/api/v1/agent/trade/spot/flash-convert",
        json={
            "userId": "80808",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "volume": "0.01",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["orderId"] == "499890200602846976"
    assert body["clientOrderId"] == "cu_agent_test"
    assert body["type"] == "MARKET"
    ob = post_mock.await_args.kwargs["order_body"]
    assert ob["side"] == "BUY"
    assert ob["type"] == "MARKET"
    assert ob["volume"] == 500.0
    assert ob["symbol"] == "BTC/USDT"
    ncid = ob["newClientOrderId"]
    assert ncid.startswith("cu_agent_")
    assert len(ncid) < 32
    assert len(ncid) == 31

    lst = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"userId": "80808", "limit": 5},
    )
    assert lst.status_code == 200
    eid_http = lst.json()["items"][0]["executionId"]
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid_http}/timeline")
    assert tl.status_code == 200
    http_ev = tl.json()["items"]
    step_kinds = [e["summary"].get("stepKind") for e in http_ev if e["eventName"] == "agent.execution.step"]
    assert step_kinds == ["quote", "submit_order"]
    assert http_ev[-1]["eventName"] == "trading.exchange_private"
    assert len(http_ev) == 3
    ex_sum = http_ev[-1]["summary"]
    assert ex_sum.get("orderRequest", {}).get("side") == "BUY"
    assert ex_sum.get("orderRequest", {}).get("type") == "MARKET"
    assert ex_sum.get("orderRequest", {}).get("symbol") == "BTC/USDT"
    assert ex_sum.get("orderRequest", {}).get("volume") == 500.0
    orn = ex_sum.get("orderRequest", {}).get("newClientOrderId")
    assert isinstance(orn, str) and orn.startswith("cu_agent_") and len(orn) < 32
    fm = ex_sum.get("orderRequest", {}).get("flashMarketMeta") or {}
    assert fm.get("volumeSemantics") == "market_buy_quote_amount"
    assert fm.get("baseQtyUserRequested") == "0.01"
    assert fm.get("quoteAmountOnWire") == 500.0
    assert fm.get("lastPriceUsed") == "50000"
    assert ex_sum.get("exchangeResponsePreview", {}).get("orderIdString") == "499890200602846976"


@pytest.mark.asyncio
async def test_spot_flash_convert_market_buy_quote_volume_two_decimals(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """MARKET BUY wire ``volume`` (quote) is ``floor``d to 2 decimal places."""
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "808081"},
            },
        )
    ).status_code == 200

    post_mock = AsyncMock(
        return_value={
            "orderIdString": "1",
            "status": "0",
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
        },
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        post_mock,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "50000.333"}),
    )
    r = await http_client.post(
        "/api/v1/agent/trade/spot/flash-convert",
        json={
            "userId": "808081",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "volume": "0.1",
        },
    )
    assert r.status_code == 200
    ob = post_mock.await_args.kwargs["order_body"]
    assert ob["volume"] == 5000.03


@pytest.mark.asyncio
async def test_spot_flash_convert_new_client_order_id_max_length_422(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Spot：`newClientOrderId` 须严格少于 32 字符（OpenAPI max_length=31）。"""
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "818181"},
            },
        )
    ).status_code == 200

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "50000"}),
    )
    r = await http_client.post(
        "/api/v1/agent/trade/spot/flash-convert",
        json={
            "userId": "818181",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "volume": "0.01",
            "newClientOrderId": "y" * 32,
        },
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_spot_limit_order_http_mock(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "91919"},
            },
        )
    ).status_code == 200

    post_mock = AsyncMock(
        return_value={
            "orderIdString": "599890200602846977",
            "clientOrderId": "cu_agent_limit",
            "status": "0",
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "LIMIT",
            "price": "48000.0",
        },
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        post_mock,
    )
    r = await http_client.post(
        "/api/v1/agent/trade/spot/limit-order",
        json={
            "userId": "91919",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "volume": "0.02",
            "price": "48000",
            "timeInForce": "GTC",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.spot.limit_order"
    assert body["orderId"] == "599890200602846977"
    assert body["type"] == "LIMIT"
    ob = post_mock.await_args.kwargs["order_body"]
    assert ob["side"] == "BUY"
    assert ob["type"] == "LIMIT"
    assert ob["volume"] == 0.02
    assert ob["price"] == 48000.0
    assert ob["timeInForce"] == "GTC"
    assert ob["symbol"] == "BTC/USDT"
    lnid = ob["newClientOrderId"]
    assert lnid.startswith("cu_agent_")
    assert len(lnid) == 31


@pytest.mark.asyncio
async def test_spot_flash_convert_timeline_includes_exchange_response_on_reject(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Rejected order JSON (code/msg) appears in timeline ``exchangeResponsePreview``."""
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    from chainup_agent.infrastructure.exchange.coobit_openapi import (
        _coobit_spot_order_rejected_app_error,
    )

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "91919"},
            },
        )
    ).status_code == 200

    rej = _coobit_spot_order_rejected_app_error(
        {"code": -1021, "msg": "Invalid timestamp, time offset is too large"},
        http_status=400,
    )

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        AsyncMock(side_effect=rej),
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "50000"}),
    )
    r = await http_client.post(
        "/api/v1/agent/trade/spot/flash-convert",
        json={
            "userId": "91919",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "volume": "0.01",
        },
    )
    assert r.status_code == 400

    lst = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"userId": "91919", "limit": 1},
    )
    assert lst.status_code == 200
    eid = lst.json()["items"][0]["executionId"]
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    priv = [x for x in tl.json()["items"] if x["eventName"] == "trading.exchange_private"][
        -1
    ]
    s = priv["summary"]
    assert s.get("venue") == "coobit"
    assert s.get("canonicalOp") == "place_order"
    prev = priv["summary"].get("exchangeResponsePreview")
    assert isinstance(prev, dict)
    assert prev.get("code") == -1021
    assert "timestamp" in (prev.get("msg") or "").lower()


@pytest.mark.asyncio
async def test_spot_flash_convert_sell_passes_base_volume(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """MARKET SELL: wire volume is base qty; no ticker fetch."""
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "81818"},
            },
        )
    ).status_code == 200

    post_mock = AsyncMock(
        return_value={
            "orderIdString": "500",
            "symbol": "BTCUSDT",
            "side": "SELL",
            "type": "MARKET",
        },
    )
    fetch_mock = AsyncMock(
        side_effect=AssertionError("fetch_spot_public_ticker_json_with_fallbacks must not run for SELL"),
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        post_mock,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        fetch_mock,
    )
    r = await http_client.post(
        "/api/v1/agent/trade/spot/flash-convert",
        json={
            "userId": "81818",
            "symbol": "BTC-USDT",
            "side": "SELL",
            "volume": "0.05",
        },
    )
    assert r.status_code == 200
    assert fetch_mock.await_count == 0
    ob = post_mock.await_args.kwargs["order_body"]
    assert ob["volume"] == 0.05
    assert ob["side"] == "SELL"
    assert ob["symbol"] == "BTC/USDT"


def test_normalize_coobit_spot_order_body_symbol_slash_format() -> None:
    from chainup_agent.infrastructure.exchange.coobit_openapi import (
        normalize_coobit_spot_order_body_symbol,
    )

    assert normalize_coobit_spot_order_body_symbol("BTC-USDT") == "BTC/USDT"
    assert normalize_coobit_spot_order_body_symbol("eth/usdt") == "ETH/USDT"
    assert normalize_coobit_spot_order_body_symbol("BTCUSDT") == "BTC/USDT"


def test_check_spot_limit_price_agent_band_rejects_when_over_max() -> None:
    from decimal import Decimal

    from chainup_agent.application.agent_spot_trade import check_spot_limit_price_agent_band
    from chainup_agent.core.config import Settings
    from chainup_agent.core.errors import AppError

    settings = Settings(
        trade_spot_limit_price_band_enabled=True,
        trade_spot_limit_price_band_max_pct=1.0,
    )
    with pytest.raises(AppError) as ei:
        check_spot_limit_price_agent_band(
            settings=settings,
            limit_price=Decimal("60000"),
            last_price=Decimal("50000"),
        )
    assert ei.value.code == "PRICE_REJECTED_AGENT_BAND"


def test_check_spot_limit_price_agent_band_skipped_when_disabled() -> None:
    from decimal import Decimal

    from chainup_agent.application.agent_spot_trade import check_spot_limit_price_agent_band
    from chainup_agent.core.config import Settings

    settings = Settings(trade_spot_limit_price_band_enabled=False)
    out = check_spot_limit_price_agent_band(
        settings=settings,
        limit_price=Decimal("99999"),
        last_price=Decimal("1"),
    )
    assert out["bandCheck"] == "false"


def test_coobit_body_code_200_is_not_error() -> None:
    from chainup_agent.infrastructure.exchange.coobit_openapi import _coobit_body_indicates_error

    assert (
        _coobit_body_indicates_error({"code": 200, "msg": "ok", "data": {"last": "1"}})
        is False
    )
    assert _coobit_body_indicates_error({"code": -1, "msg": "bad"}) is True


def test_spot_order_rejected_permission_adds_hint_and_reason() -> None:
    from chainup_agent.infrastructure.exchange.coobit_openapi import _coobit_spot_order_rejected_app_error

    err = _coobit_spot_order_rejected_app_error(
        {"code": -1, "msg": "Users don't have permission to access"},
        http_status=400,
    )
    assert err.code == "AGENT_SPOT_ORDER_REJECTED"
    assert "处理建议" in err.message
    assert err.details.get("reject_reason") == "API_PERMISSION_OR_SUBACCOUNT"
    assert err.details.get("http_status") == 400
    prev = err.details.get("exchange_response_preview")
    assert isinstance(prev, dict)
    assert prev.get("code") == -1
    assert "permission" in (prev.get("msg") or "").lower()


def test_spot_order_rejected_other_msg_no_extra_reason() -> None:
    from chainup_agent.infrastructure.exchange.coobit_openapi import _coobit_spot_order_rejected_app_error

    err = _coobit_spot_order_rejected_app_error({"code": -1, "msg": "MIN_NOTIONAL"})
    assert "处理建议" not in err.message
    assert err.details.get("reject_reason") is None
    assert err.details.get("exchange_response_preview", {}).get("msg") == "MIN_NOTIONAL"


def test_last_price_unwraps_wrapped_ticker_data() -> None:
    from decimal import Decimal

    from chainup_agent.application.agent_spot_trade import _last_price_from_coobit_ticker

    assert _last_price_from_coobit_ticker(
        {"code": 0, "msg": "success", "data": {"last": "65000.12"}}
    ) == Decimal("65000.12")


@pytest.mark.asyncio
async def test_spot_quote_openapi_lists_new_paths(http_client: AsyncClient) -> None:
    r = await http_client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    assert "/api/v1/agent/trade/spot/quote" in paths
    assert "/api/v1/agent/trade/spot/flash-convert" in paths
    assert "/api/v1/agent/trade/spot/limit-order" in paths
    assert "/api/v1/agent/trade/spot/open-orders" in paths
    assert "/api/v1/agent/trade/spot/cancel" in paths


def test_build_coobit_signed_get_request_path_sorts_query() -> None:
    from chainup_agent.infrastructure.exchange.coobit_openapi import (
        _SPOT_OPEN_ORDERS_V2_PATH,
        build_coobit_signed_get_request_path,
    )

    p = build_coobit_signed_get_request_path(
        _SPOT_OPEN_ORDERS_V2_PATH,
        {"symbol": "BTC/USDT", "limit": "50"},
    )
    assert p.startswith(f"{_SPOT_OPEN_ORDERS_V2_PATH}?")
    assert "limit=50" in p
    assert "symbol=" in p
    assert p.index("limit") < p.index("symbol")


@pytest.mark.asyncio
async def test_spot_open_orders_200_mock(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "91919"},
            },
        )
    ).status_code == 200

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_signed_spot_open_orders_json",
        AsyncMock(
            return_value=[
                {
                    "orderIdString": "111",
                    "symbol": "BTCUSDT",
                    "status": "NEW",
                    "type": "LIMIT",
                    "side": "BUY",
                    "price": "60000",
                    "origQty": "0.01",
                }
            ]
        ),
    )
    r = await http_client.get(
        "/api/v1/agent/trade/spot/open-orders",
        params={"userId": "91919", "symbol": "BTC-USDT", "limit": 50},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.spot.open_orders"
    assert body["symbol"] == "BTC-USDT"
    assert body["symbolOrder"] == "BTCUSDT"
    assert len(body["orders"]) == 1
    assert body["orders"][0].get("orderIdString") == "111"


@pytest.mark.asyncio
async def test_spot_cancel_order_200_mock(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "92929"},
            },
        )
    ).status_code == 200

    cancel_mock = AsyncMock(
        return_value={
            "orderIdString": "499890200602846976",
            "status": "CANCELED",
            "symbol": "BTCUSDT",
            "clientOrderId": "cu_agent_x",
        },
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_cancel_json",
        cancel_mock,
    )
    r = await http_client.post(
        "/api/v1/agent/trade/spot/cancel",
        json={
            "userId": "92929",
            "symbol": "BTC-USDT",
            "orderId": "499890200602846976",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["scenarioId"] == "trade.spot.cancel_order"
    assert body["status"] == "CANCELED"
    cb = cancel_mock.await_args.kwargs["cancel_body"]
    assert cb["symbol"] == "BTC/USDT"
    assert cb["orderId"] == "499890200602846976"


@pytest.mark.asyncio
async def test_telegram_spot_open_orders_bound_user(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_signed_spot_open_orders_json",
        AsyncMock(
            return_value=[
                {
                    "orderIdString": "222",
                    "symbol": "ETHUSDT",
                    "status": "NEW",
                    "type": "LIMIT",
                    "side": "SELL",
                    "price": "3000",
                    "origQty": "0.5",
                }
            ]
        ),
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "50340"},
            },
        )
    ).status_code == 200

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 70}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 171,
                "from": {"id": 50340, "is_bot": False, "username": "ouser"},
                "chat": {"id": 534370, "type": "private"},
                "text": "ETH-USDT 当前委托",
            },
        },
    )
    assert r.status_code == 200
    reply = mocked.await_args.kwargs["json_payload"]["text"]
    assert "现货当前委托" in reply
    assert "222" in reply
    assert "trade.spot.open_orders" in reply


@pytest.mark.asyncio
async def test_telegram_spot_cancel_bound_user(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_cancel_json",
        AsyncMock(
            return_value={
                "orderIdString": "499890200602846976",
                "status": "CANCELED",
                "symbol": "BTCUSDT",
            }
        ),
    )

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "50341"},
            },
        )
    ).status_code == 200

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 71}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 1,
            "message": {
                "message_id": 172,
                "from": {"id": 50341, "is_bot": False, "username": "cuser"},
                "chat": {"id": 534371, "type": "private"},
                "text": "撤单 BTC-USDT 订单号 499890200602846976",
            },
        },
    )
    assert r.status_code == 200
    reply = mocked.await_args.kwargs["json_payload"]["text"]
    assert "撤单已提交" in reply
    assert "CANCELED" in reply
    assert "trade.spot.cancel_order" in reply

    lst = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"userId": "50341", "limit": 3},
    )
    assert lst.status_code == 200
    eid = lst.json()["items"][0]["executionId"]
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid}/timeline")
    assert tl.status_code == 200
    names = [x["eventName"] for x in tl.json()["items"]]
    assert "trading.exchange_private" in names


@pytest.mark.asyncio
async def test_telegram_limit_type_a_offers_inline_keyboard(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "50350"},
            },
        )
    ).status_code == 200

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "64000"}),
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST", "")
    reset_settings_cache()
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 80}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 2,
            "message": {
                "message_id": 181,
                "from": {"id": 50350, "is_bot": False, "username": "luser"},
                "chat": {"id": 534380, "type": "private"},
                "text": "BTC-USDT 限价买入 价格 65000 数量 0.01",
            },
        },
    )
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    markup = body.get("reply_markup") or {}
    rows = markup.get("inline_keyboard") or []
    assert rows
    cb = rows[0][0].get("callback_data") or ""
    assert cb.startswith("lcp")
    assert "65000" in body["text"]
    assert "trade.spot.limit_order" in body["text"] or "限价" in body["text"]


@pytest.mark.asyncio
async def test_telegram_limit_type_a_band_rejected_before_confirm_markup(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Price band fails before Type-A — no pending row, no inline keyboard."""
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "50351"},
            },
        )
    ).status_code == 200

    monkeypatch.setenv("CHAINUP_AGENT_TRADE_SPOT_LIMIT_PRICE_BAND_ENABLED", "true")
    monkeypatch.setenv("CHAINUP_AGENT_TRADE_SPOT_LIMIT_PRICE_BAND_MAX_PCT", "1")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_ERROR_LLM_REWRITE", "false")
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "50000"}),
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv(
        "CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL",
        "https://exchange.example/agent/telegram-bind",
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 81}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 4,
            "message": {
                "message_id": 182,
                "from": {"id": 50351, "is_bot": False},
                "chat": {"id": 534381, "type": "private"},
                "text": "BTC-USDT 限价买入 价格 60000 数量 0.01",
            },
        },
    )
    assert r.status_code == 200
    body = mocked.await_args.kwargs["json_payload"]
    assert body.get("reply_markup") is None
    assert "偏离" in body["text"] or "价格" in body["text"]

    from sqlalchemy import func, select

    from chainup_agent.infrastructure.persistence.base import get_session_factory
    from chainup_agent.infrastructure.persistence.models.agent_telegram_pending_confirm import (
        AgentTelegramPendingConfirm,
    )

    factory = get_session_factory()
    async with factory() as session:
        n = await session.scalar(select(func.count()).select_from(AgentTelegramPendingConfirm))
    assert n == 0

    tl = await http_client.get(
        "/api/v1/admin/observability/executions",
        params={"userId": "50351", "limit": 1},
    )
    eid = tl.json()["items"][0]["executionId"]
    timeline = await http_client.get(
        f"/api/v1/admin/observability/executions/{eid}/timeline"
    )
    triggers = [
        x["summary"].get("transitionTrigger")
        for x in timeline.json()["items"]
        if x["eventName"] == "agent.execution.step"
    ]
    assert "limit.price_band_rejected_pre_confirm" in triggers
    assert "limit.confirm.type_a_offered" not in triggers


@pytest.mark.asyncio
async def test_telegram_webhook_callback_limit_confirm(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    from chainup_agent.application.telegram_flash_pending import create_spot_limit_pending
    from chainup_agent.core.config import reset_settings_cache
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "1003"},
            },
        )
    ).status_code == 200

    token = ""
    factory = get_session_factory()
    async with factory() as session:
        token = await create_spot_limit_pending(
            session,
            telegram_user_id=1003,
            chat_id=434343,
            symbol="BTC-USDT",
            side="BUY",
            quantity="0.01",
            price="65000",
            time_in_force="GTC",
        )
        await session.commit()

    bot_tok = "configured:dddddddddddddddddddddddddd"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    reset_settings_cache()

    mocked = AsyncMock(return_value={"ok": True, "result": {}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_callback_handler.call_telegram_bot_api",
        mocked,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        AsyncMock(
            return_value={
                "orderIdString": "599890200602846977",
                "clientOrderId": "cu_agent_limit_cb",
                "status": "0",
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "LIMIT",
                "price": "65000",
            }
        ),
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "64000"}),
    )

    enc = quote(bot_tok, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 43,
            "callback_query": {
                "id": "cq-l1",
                "from": {"id": 1003, "is_bot": False},
                "message": {"message_id": 4, "chat": {"id": 434343, "type": "private"}},
                "data": f"lcp{token}",
            },
        },
    )
    assert r.status_code == 200
    methods = [c.args[1] for c in mocked.await_args_list if len(c.args) >= 2]
    assert "answerCallbackQuery" in methods
    assert "sendMessage" in methods

    from sqlalchemy import select

    from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution

    factory = get_session_factory()
    async with factory() as session:
        res = await session.execute(
            select(AgentExecution.execution_id)
            .where(AgentExecution.user_id == "1003")
            .order_by(AgentExecution.created_at.desc())
            .limit(1)
        )
        eid_row = res.scalar_one()
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid_row}/timeline")
    assert tl.status_code == 200
    titems = tl.json()["items"]
    step_events = [x for x in titems if x["eventName"] == "agent.execution.step"]
    assert len(step_events) == 3
    assert [x["summary"].get("stepKind") for x in step_events] == [
        "confirm_accept",
        "quote",
        "submit_order",
    ]
    assert titems[-1]["eventName"] == "trading.exchange_private"
    ob = titems[-1]["summary"].get("orderRequest") or {}
    assert ob.get("type") == "LIMIT"
    assert ob.get("symbol") == "BTC/USDT"


@pytest.mark.asyncio
async def test_telegram_limit_callback_skips_second_quote_when_pending_has_execution_id(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    from chainup_agent.application.telegram_flash_pending import create_spot_limit_pending
    from chainup_agent.core.config import reset_settings_cache
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "2003"},
            },
        )
    ).status_code == 200

    r_acc = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={
            "userId": "2003",
            "scenarioId": "trade.spot.limit_order",
            "channel": "telegram",
        },
    )
    assert r_acc.status_code == 200
    turn_exec = r_acc.json()["executionId"]

    token = ""
    factory = get_session_factory()
    async with factory() as session:
        token = await create_spot_limit_pending(
            session,
            telegram_user_id=2003,
            chat_id=929292,
            symbol="BTC-USDT",
            side="BUY",
            quantity="0.02",
            price="62000",
            time_in_force="GTC",
            execution_id=turn_exec,
        )
        await session.commit()

    bot_tok = "configured:eeeeeeeeeeeeeeeeeeeeeeeeeeee"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    reset_settings_cache()

    mocked = AsyncMock(return_value={"ok": True, "result": {}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_callback_handler.call_telegram_bot_api",
        mocked,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        AsyncMock(
            return_value={
                "orderIdString": "888",
                "clientOrderId": "cu_agent_limit_unified",
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "LIMIT",
            }
        ),
    )

    enc = quote(bot_tok, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 100,
            "callback_query": {
                "id": "cq-lu",
                "from": {"id": 2003, "is_bot": False},
                "message": {"message_id": 2, "chat": {"id": 929292, "type": "private"}},
                "data": f"lcp{token}",
            },
        },
    )
    assert r.status_code == 200

    tl = await http_client.get(
        f"/api/v1/admin/observability/executions/{turn_exec}/timeline"
    )
    assert tl.status_code == 200
    titems = tl.json()["items"]
    kinds = [
        x["summary"].get("stepKind") for x in titems if x["eventName"] == "agent.execution.step"
    ]
    assert kinds == ["confirm_accept", "submit_order"]
    step_quotes = [
        x
        for x in titems
        if x["eventName"] == "agent.execution.step" and x["summary"].get("stepKind") == "quote"
    ]
    assert step_quotes == []


@pytest.mark.asyncio
async def test_spot_limit_order_price_band_rejected_http(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    monkeypatch.setenv("CHAINUP_AGENT_TRADE_SPOT_LIMIT_PRICE_BAND_ENABLED", "true")
    monkeypatch.setenv("CHAINUP_AGENT_TRADE_SPOT_LIMIT_PRICE_BAND_MAX_PCT", "1")
    reset_settings_cache()
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "50360"},
            },
        )
    ).status_code == 200

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "50000"}),
    )
    r = await http_client.post(
        "/api/v1/agent/trade/spot/limit-order",
        json={
            "userId": "50360",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "volume": "0.01",
            "price": "60000",
            "timeInForce": "GTC",
        },
    )
    assert r.status_code == 422
    assert r.json()["code"] == "PRICE_REJECTED_AGENT_BAND"


@pytest.mark.asyncio
async def test_telegram_flash_callback_order_rejected_user_message(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    from chainup_agent.application.telegram_flash_pending import create_flash_convert_pending
    from chainup_agent.core.config import reset_settings_cache
    from chainup_agent.infrastructure.exchange.coobit_openapi import (
        _coobit_spot_order_rejected_app_error,
    )
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "1004"},
            },
        )
    ).status_code == 200

    token = ""
    factory = get_session_factory()
    async with factory() as session:
        token = await create_flash_convert_pending(
            session,
            telegram_user_id=1004,
            chat_id=444444,
            symbol="BTC-USDT",
            side="BUY",
            quantity="0.01",
        )
        await session.commit()

    rej = _coobit_spot_order_rejected_app_error(
        {"code": -1, "msg": "MIN_NOTIONAL"},
        http_status=400,
    )
    bot_tok = "configured:ffffffffffffffffffffffffffff"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_ERROR_LLM_REWRITE", "false")
    reset_settings_cache()

    mocked = AsyncMock(return_value={"ok": True, "result": {}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_callback_handler.call_telegram_bot_api",
        mocked,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        AsyncMock(side_effect=rej),
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "50000"}),
    )

    enc = quote(bot_tok, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 44,
            "callback_query": {
                "id": "cq-fr",
                "from": {"id": 1004, "is_bot": False},
                "message": {"message_id": 5, "chat": {"id": 444444, "type": "private"}},
                "data": f"fcp{token}",
            },
        },
    )
    assert r.status_code == 200
    texts = [
        c.kwargs.get("json_payload", {}).get("text", "")
        for c in mocked.await_args_list
        if c.args and len(c.args) >= 2 and c.args[1] == "sendMessage"
    ]
    assert any("MIN_NOTIONAL" in t or "交易所" in t or "拒绝" in t for t in texts)


@pytest.mark.asyncio
async def test_telegram_limit_callback_price_band_rejected(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    from chainup_agent.application.telegram_flash_pending import create_spot_limit_pending
    from chainup_agent.core.config import reset_settings_cache
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    monkeypatch.setenv("CHAINUP_AGENT_TRADE_SPOT_LIMIT_PRICE_BAND_ENABLED", "true")
    monkeypatch.setenv("CHAINUP_AGENT_TRADE_SPOT_LIMIT_PRICE_BAND_MAX_PCT", "1")
    reset_settings_cache()
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "1005"},
            },
        )
    ).status_code == 200

    token = ""
    factory = get_session_factory()
    async with factory() as session:
        token = await create_spot_limit_pending(
            session,
            telegram_user_id=1005,
            chat_id=555555,
            symbol="BTC-USDT",
            side="BUY",
            quantity="0.01",
            price="60000",
            time_in_force="GTC",
        )
        await session.commit()

    bot_tok = "configured:1111111111111111111111111111"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_ERROR_LLM_REWRITE", "false")
    reset_settings_cache()

    mocked = AsyncMock(return_value={"ok": True, "result": {}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_callback_handler.call_telegram_bot_api",
        mocked,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "50000"}),
    )

    enc = quote(bot_tok, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 45,
            "callback_query": {
                "id": "cq-lb",
                "from": {"id": 1005, "is_bot": False},
                "message": {"message_id": 6, "chat": {"id": 555555, "type": "private"}},
                "data": f"lcp{token}",
            },
        },
    )
    assert r.status_code == 200
    texts = [
        c.kwargs.get("json_payload", {}).get("text", "")
        for c in mocked.await_args_list
        if len(c.args) >= 2 and c.args[1] == "sendMessage"
    ]
    assert any("偏离" in t or "PRICE_REJECTED" in t or "价格" in t for t in texts)


@pytest.mark.asyncio
async def test_telegram_flash_type_a_llm_preamble_prepended(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from unittest.mock import AsyncMock

    from chainup_agent.core.config import reset_settings_cache
    from cryptography.fernet import Fernet

    await _init_binding_sqlite(monkeypatch, tmp_path, Fernet.generate_key().decode())
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "50370"},
            },
        )
    ).status_code == 200

    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "50000"}),
    )

    token = "configured:aaaaaaaaaaaaaaaaaaaaaaaaaa"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL", "https://example.com/bind")
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_SPOT_FLASH_CONFIRM", "true")
    reset_settings_cache()
    monkeypatch.setattr(
        "chainup_agent.application.telegram_bound_reply.invoke_llm_chat_for_telegram",
        AsyncMock(return_value=("市价单请注意滑点风险。", None, {"gatewayModelId": "gpt-4.1-mini"})),
    )
    mocked = AsyncMock(return_value={"ok": True, "result": {"message_id": 90}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_inbound.call_telegram_bot_api",
        mocked,
    )

    enc = quote(token, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 3,
            "message": {
                "message_id": 191,
                "from": {"id": 50370, "is_bot": False},
                "chat": {"id": 534390, "type": "private"},
                "text": "市价买入 0.01 BTC-USDT",
            },
        },
    )
    assert r.status_code == 200
    reply = mocked.await_args.kwargs["json_payload"]["text"]
    assert "滑点风险" in reply
    assert "确认下单" in reply or "fcp" in str(mocked.await_args.kwargs.get("json_payload", {}))
    markup = mocked.await_args.kwargs["json_payload"].get("reply_markup") or {}
    assert markup.get("inline_keyboard")


@pytest.mark.asyncio
async def test_spot_cancel_order_validation_422(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "93939"},
            },
        )
    ).status_code == 200

    r = await http_client.post(
        "/api/v1/agent/trade/spot/cancel",
        json={
            "userId": "93939",
            "symbol": "BTC-USDT",
        },
    )
    assert r.status_code == 422
    assert r.json()["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_internal_prompt_effective_404_when_no_pack(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    await _init_schema_sqlite(monkeypatch, tmp_path)
    r = await http_client.get(
        "/api/v1/internal/prompts/effective",
        params={"scenarioId": "agent.runtime.intent_nlu"},
    )
    assert r.status_code == 404
    assert r.json()["code"] == "AGENT_PROMPT_PACK_NOT_FOUND"


@pytest.mark.asyncio
async def test_internal_prompt_effective_200(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    import json

    from chainup_agent.infrastructure.persistence.base import get_session_factory
    from chainup_agent.infrastructure.persistence.models.admin_prompt_pack import AdminPromptPack

    await _init_schema_sqlite(monkeypatch, tmp_path)
    factory = get_session_factory()
    async with factory() as session:
        session.add(
            AdminPromptPack(
                prompt_pack_id="pack_test_nlu",
                prompt_pack_type="SYSTEM",
                scenario_id="agent.runtime.intent_nlu",
                lifecycle="PUBLISHED",
                prompt_pack_version="1",
                etag='W/"t1"',
                messages_json=json.dumps([{"role": "system", "content": "hello prompt"}]),
            )
        )
        await session.commit()

    r = await http_client.get(
        "/api/v1/internal/prompts/effective",
        params={"scenarioId": "agent.runtime.intent_nlu"},
    )
    assert r.status_code == 200
    j = r.json()
    assert j["scenarioId"] == "agent.runtime.intent_nlu"
    assert j["messages"][0]["content"] == "hello prompt"


@pytest.mark.asyncio
async def test_telegram_webhook_callback_flash_confirm(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    from chainup_agent.application.telegram_flash_pending import create_flash_convert_pending
    from chainup_agent.core.config import reset_settings_cache
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "1001"},
            },
        )
    ).status_code == 200

    token = ""
    factory = get_session_factory()
    async with factory() as session:
        token = await create_flash_convert_pending(
            session,
            telegram_user_id=1001,
            chat_id=424242,
            symbol="BTC-USDT",
            side="BUY",
            quantity="0.01",
        )
        await session.commit()

    bot_tok = "configured:bbbbbbbbbbbbbbbbbbbbbbbbbb"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    reset_settings_cache()

    mocked = AsyncMock(return_value={"ok": True, "result": {}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_callback_handler.call_telegram_bot_api",
        mocked,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        AsyncMock(
            return_value={
                "orderIdString": "499890200602846976",
                "clientOrderId": "cu_agent_cb",
                "status": "0",
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
            }
        ),
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "50000"}),
    )

    enc = quote(bot_tok, safe="")
    path = f"/webhook/telegram/{enc}"
    payload = {
        "update_id": 42,
        "callback_query": {
            "id": "cq-9",
            "from": {"id": 1001, "is_bot": False},
            "message": {"message_id": 3, "chat": {"id": 424242, "type": "private"}},
            "data": f"fcp{token}",
        },
    }
    r = await http_client.post(path, json=payload)
    assert r.status_code == 200
    methods = [c.args[1] for c in mocked.await_args_list if len(c.args) >= 2]
    assert "answerCallbackQuery" in methods
    assert "sendMessage" in methods

    from sqlalchemy import select

    from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution

    factory = get_session_factory()
    async with factory() as session:
        res = await session.execute(
            select(AgentExecution.execution_id)
            .where(AgentExecution.user_id == "1001")
            .order_by(AgentExecution.created_at.desc())
            .limit(1)
        )
        eid_row = res.scalar_one()
    tl = await http_client.get(f"/api/v1/admin/observability/executions/{eid_row}/timeline")
    assert tl.status_code == 200
    titems = tl.json()["items"]
    step_events = [x for x in titems if x["eventName"] == "agent.execution.step"]
    assert len(step_events) == 3
    assert [x["summary"].get("stepKind") for x in step_events] == [
        "confirm_accept",
        "quote",
        "submit_order",
    ]
    assert titems[-1]["eventName"] == "trading.exchange_private"
    assert titems[-1]["summary"].get("methodPathSummary") == "POST /sapi/v2/order"
    tg_ex = titems[-1]["summary"]
    assert tg_ex.get("orderRequest", {}).get("symbol") == "BTC/USDT"
    assert tg_ex.get("exchangeResponsePreview", {}).get("orderIdString") == "499890200602846976"


@pytest.mark.asyncio
async def test_telegram_flash_callback_skips_second_quote_when_pending_has_execution_id(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Type-A 回合写入的 executionId 与 pending 对齐时，callback 不再重复 quote 事件。"""
    from cryptography.fernet import Fernet
    from unittest.mock import AsyncMock

    from chainup_agent.application.telegram_flash_pending import create_flash_convert_pending
    from chainup_agent.core.config import reset_settings_cache
    from chainup_agent.infrastructure.persistence.base import get_session_factory

    key = Fernet.generate_key().decode()
    await _init_binding_sqlite(monkeypatch, tmp_path, key)
    _mock_probe_ok(monkeypatch)
    assert (
        await http_client.post(
            "/api/v1/agent/api-binding/confirm",
            json={
                "openapi_base_url": "https://openapi.example.invalid",
                "api_key": "k" * 8,
                "secret_key": "s" * 8,
                "sub_account_id": "900001",
                "telegram": {"tg_id": "2002"},
            },
        )
    ).status_code == 200

    r_acc = await http_client.post(
        "/api/v1/agent/execution/accept",
        json={
            "userId": "2002",
            "scenarioId": "trade.spot.flash_convert",
            "channel": "telegram",
        },
    )
    assert r_acc.status_code == 200
    turn_exec = r_acc.json()["executionId"]

    token = ""
    factory = get_session_factory()
    async with factory() as session:
        token = await create_flash_convert_pending(
            session,
            telegram_user_id=2002,
            chat_id=919191,
            symbol="BTC-USDT",
            side="BUY",
            quantity="0.02",
            execution_id=turn_exec,
        )
        await session.commit()

    bot_tok = "configured:cccccccccccccccccccccccccc"
    monkeypatch.setenv("CHAINUP_AGENT_TELEGRAM_BOT_TOKEN", bot_tok)
    reset_settings_cache()

    mocked = AsyncMock(return_value={"ok": True, "result": {}})
    monkeypatch.setattr(
        "chainup_agent.application.telegram_callback_handler.call_telegram_bot_api",
        mocked,
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.post_signed_spot_order_json",
        AsyncMock(
            return_value={
                "orderIdString": "777",
                "clientOrderId": "cu_agent_unified",
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
            }
        ),
    )
    monkeypatch.setattr(
        "chainup_agent.application.agent_spot_trade.fetch_spot_public_ticker_json_with_fallbacks",
        AsyncMock(return_value={"symbol": "BTC-USDT", "lastPrice": "51000"}),
    )

    enc = quote(bot_tok, safe="")
    r = await http_client.post(
        f"/webhook/telegram/{enc}",
        json={
            "update_id": 99,
            "callback_query": {
                "id": "cq-u",
                "from": {"id": 2002, "is_bot": False},
                "message": {"message_id": 1, "chat": {"id": 919191, "type": "private"}},
                "data": f"fcp{token}",
            },
        },
    )
    assert r.status_code == 200

    tl = await http_client.get(
        f"/api/v1/admin/observability/executions/{turn_exec}/timeline"
    )
    assert tl.status_code == 200
    titems = tl.json()["items"]
    kinds = [
        x["summary"].get("stepKind") for x in titems if x["eventName"] == "agent.execution.step"
    ]
    assert kinds == ["confirm_accept", "submit_order"]
    assert titems[-1]["eventName"] == "trading.exchange_private"
    step_quotes = [
        x for x in titems if x["eventName"] == "agent.execution.step" and x["summary"].get("stepKind") == "quote"
    ]
    assert step_quotes == []
    assert titems[-1]["summary"].get("orderRequest", {}).get("symbol") == "BTC/USDT"

    from sqlalchemy import func, select

    from chainup_agent.infrastructure.persistence.models.agent_execution import AgentExecution

    factory = get_session_factory()
    async with factory() as session:
        n_exec = await session.scalar(select(func.count()).select_from(AgentExecution))
    assert n_exec == 1
