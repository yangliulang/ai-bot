"""Phase 1 routing: attach read-only Coobit calls for wired scenarioIds (bound users only)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.agent_runtime import RoutingExecuteRequest, RoutingExecuteResponse
from chainup_agent.application.agent_api_binding_confirm import (
    decrypt_binding_trade_credentials_for_row,
)
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.exchange.coobit_openapi import (
    fetch_signed_asset_account_by_type_json,
    fetch_signed_spot_account_json,
    fetch_spot_public_depth_json_with_fallbacks,
    fetch_spot_public_ticker_json_with_fallbacks,
    fetch_spot_public_trades_json_with_fallbacks,
    normalize_coobit_spot_order_symbol,
    normalize_coobit_spot_symbol_param,
    spot_ticker_symbol_candidates,
)
from chainup_agent.infrastructure.persistence.models.telegram_agent_trading_binding import (
    TelegramAgentTradingBinding,
)

_MAX_BALANCE_ROWS = 32
_MAX_DEPTH_SIDE_ROWS = 48
_MAX_TRADE_PREVIEW_ROWS = 32
_ALLOWED_TRADE_PREVIEW_KEYS = frozenset(
    {"id", "price", "qty", "quantity", "quoteQty", "time", "side", "isBuyerMaker"}
)


async def load_binding_row_for_telegram_user(
    session: AsyncSession,
    telegram_user_id: int,
) -> TelegramAgentTradingBinding | None:
    from sqlalchemy import select

    from chainup_agent.infrastructure.persistence.models.telegram_agent_trading_binding import (
        TelegramAgentTradingBinding,
    )

    stmt = select(TelegramAgentTradingBinding).where(
        TelegramAgentTradingBinding.telegram_user_id == telegram_user_id,
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


def _sanitize_balances_preview(raw: dict[str, Any]) -> dict[str, Any]:
    balances = raw.get("balances")
    if not isinstance(balances, list):
        return {"kind": "spot_account_balances_filtered", "items": []}

    rows: list[dict[str, str]] = []
    for b in balances[:_MAX_BALANCE_ROWS]:
        if not isinstance(b, dict):
            continue
        asset = str(b.get("asset", "")).strip().upper()
        if not asset:
            continue
        rows.append(
            {
                "asset": asset[:32],
                "free": str(b.get("free", "0"))[:64],
                "locked": str(b.get("locked", "0"))[:64],
            }
        )

    extras: dict[str, Any] = {}
    at = raw.get("accountType") or raw.get("account_type")
    if isinstance(at, str) and at.strip():
        extras["accountTypeHint"] = at.strip()[:64]
    can_trade = raw.get("canTrade")
    if isinstance(can_trade, bool):
        extras["canTradeHint"] = can_trade

    return {"kind": "spot_account_balances_filtered", "items": rows, **extras}


def _sanitize_wealth_holdings_preview(raw: dict[str, Any], *, account_type: int) -> dict[str, Any]:
    """``wealth.holdings_read`` preview — OTC ledger; mirrors balances when API returns ``balances``."""
    if isinstance(raw.get("balances"), list):
        slim = _sanitize_balances_preview(raw)
        slim["kind"] = "wealth_holdings_otc_v1"
        slim["accountTypeRequested"] = account_type
        return slim
    out: dict[str, Any] = {"kind": "wealth_holdings_otc_v1", "accountTypeRequested": account_type}
    for k in ("accountType", "accountId", "totalAssetOfBtc", "totalAsset", "makerCommission", "takerCommission"):
        if k not in raw or raw[k] is None:
            continue
        v = raw[k]
        if isinstance(v, (dict, list)):
            out[k] = str(v)[:400]
        elif isinstance(v, bool):
            out[k] = v
        elif isinstance(v, (int, float)):
            out[k] = v
        else:
            s = str(v).strip()
            if s:
                out[k] = s[:128]
    assets = raw.get("assets")
    if isinstance(assets, list) and assets:
        out["assetRowCount"] = min(len(assets), 64)
        first = [x for x in assets[:12] if isinstance(x, dict)]
        samples: list[dict[str, str]] = []
        for row in first:
            one: dict[str, str] = {}
            for kk in ("asset", "free", "locked", "borrowed"):
                if kk in row and row[kk] is not None:
                    one[kk] = str(row[kk]).strip()[:64]
            if one:
                samples.append(one)
        out["assetsSample"] = samples
    return out


_ALLOWED_TICKER_PREVIEW_KEYS = frozenset(
    {
        "symbol",
        "lastPrice",
        "lastQty",
        "bidPrice",
        "askPrice",
        "volume",
        "highPrice",
        "lowPrice",
        "quoteVolume",
        "openPrice",
        "prevClosePrice",
        "priceChangePercent",
        "closeTime",
        "openTime",
    },
)


def _sanitize_ticker_preview(raw: dict[str, Any], symbol_normalized: str) -> dict[str, Any]:
    out: dict[str, Any] = {"kind": "spot_ticker_v2_filtered", "symbolRequested": symbol_normalized}
    if not isinstance(raw, dict):
        return out
    for k in _ALLOWED_TICKER_PREVIEW_KEYS:
        if k not in raw:
            continue
        v = raw[k]
        if v is None:
            continue
        if isinstance(v, bool):
            out[k] = v
        elif isinstance(v, (int, float)):
            out[k] = v
        else:
            s = str(v).strip()
            if s:
                out[k] = s[:96]
    return out


def _sanitize_depth_preview(
    raw: dict[str, Any],
    symbol_normalized: str,
    *,
    limit_used: int,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "kind": "spot_depth_v2_filtered",
        "symbolRequested": symbol_normalized,
        "limitRequested": limit_used,
    }
    cap = min(max(1, int(limit_used)), _MAX_DEPTH_SIDE_ROWS)
    for side in ("asks", "bids"):
        arr = raw.get(side)
        if not isinstance(arr, list):
            out[side] = []
            continue
        rows: list[list[str]] = []
        for row in arr[:cap]:
            if isinstance(row, (list, tuple)) and len(row) >= 2:
                rows.append([str(row[0]).strip()[:48], str(row[1]).strip()[:48]])
            elif isinstance(row, dict):
                p = row.get("price") or row.get("0")
                q = row.get("qty") or row.get("quantity") or row.get("1")
                if p is not None and q is not None:
                    rows.append([str(p).strip()[:48], str(q).strip()[:48]])
        out[side] = rows
    return out


def _sanitize_trades_preview(rows: list[dict[str, Any]], symbol_normalized: str) -> dict[str, Any]:
    cleaned: list[dict[str, Any]] = []
    for it in rows[:_MAX_TRADE_PREVIEW_ROWS]:
        one: dict[str, Any] = {}
        for k in _ALLOWED_TRADE_PREVIEW_KEYS:
            if k not in it:
                continue
            v = it[k]
            if v is None:
                continue
            if isinstance(v, bool):
                one[k] = v
            elif isinstance(v, (int, float)):
                one[k] = v
            else:
                s = str(v).strip()
                if s:
                    one[k] = s[:96]
        if one:
            cleaned.append(one)
    return {"kind": "spot_trades_v2_filtered", "symbolRequested": symbol_normalized, "items": cleaned}


def _routing_market_limit(body: RoutingExecuteRequest) -> int:
    raw = body.market_data_limit
    if raw is None:
        return 20
    try:
        v = int(raw)
    except (TypeError, ValueError):
        return 20
    return max(1, min(v, 100))


def parse_telegram_user_id_numeric(user_id_raw: str) -> int:
    """Telegram ``tg_id`` as decimal string (used by routing / spot trade APIs)."""
    raw = user_id_raw.strip()
    if not raw.isdigit():
        raise AppError(
            code="VALIDATION_ERROR",
            message="须使用 Telegram userId（tg_id）非空数值字符串。",
            status_code=422,
            details={"field": "userId"},
        )
    return int(raw)


async def routing_execute_exchange_reads(
    *,
    session: AsyncSession,
    settings: Settings,
    body: RoutingExecuteRequest,
) -> RoutingExecuteResponse:
    tg_user = parse_telegram_user_id_numeric(body.user_id)
    row = await load_binding_row_for_telegram_user(session, tg_user)
    if row is None:
        raise AppError(
            code="AGENT_SUBACCOUNT_REQUIRED",
            message="未发现该 Telegram 用户的托管 API 绑定，请先完成 Deeplink 校验与绑定。",
            status_code=403,
            details={"scenarioId": body.scenario_id},
        )

    openapi_base, ak, sk = decrypt_binding_trade_credentials_for_row(settings, row)
    sid = body.scenario_id

    if sid == "read.market.ticker":
        sym_in = body.symbol.strip() if body.symbol else ""
        if not sym_in:
            raise AppError(
                code="VALIDATION_ERROR",
                message="read.market.ticker 须通过 symbol 传入交易对（如 BTC-USDT）。",
                status_code=422,
                details={"field": "symbol"},
            )
        sym_norm = normalize_coobit_spot_symbol_param(sym_in)
        sym_order = normalize_coobit_spot_order_symbol(sym_in)
        raw = await fetch_spot_public_ticker_json_with_fallbacks(
            openapi_base_url=openapi_base,
            symbol_candidates=spot_ticker_symbol_candidates(sym_norm, sym_order),
        )
        preview = _sanitize_ticker_preview(raw, sym_norm)
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note="只读行情：现货公开 GET /sapi/v2/ticker（免 Key）；仍要求用户已完成托管绑定。",
            exchange_read_preview=preview,
        )

    if sid == "read.market.depth":
        sym_in = body.symbol.strip() if body.symbol else ""
        if not sym_in:
            raise AppError(
                code="VALIDATION_ERROR",
                message="read.market.depth 须通过 symbol 传入交易对（如 BTC-USDT）。",
                status_code=422,
                details={"field": "symbol"},
            )
        lim = _routing_market_limit(body)
        sym_norm = normalize_coobit_spot_symbol_param(sym_in)
        sym_order = normalize_coobit_spot_order_symbol(sym_in)
        raw_d = await fetch_spot_public_depth_json_with_fallbacks(
            openapi_base_url=openapi_base,
            symbol_candidates=spot_ticker_symbol_candidates(sym_norm, sym_order),
            limit=lim,
        )
        preview = _sanitize_depth_preview(raw_d if isinstance(raw_d, dict) else {}, sym_norm, limit_used=lim)
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note="只读盘口：现货公开 GET /sapi/v2/depth（免 Key）；仍要求用户已完成托管绑定。",
            exchange_read_preview=preview,
        )

    if sid == "read.market.trades":
        sym_in = body.symbol.strip() if body.symbol else ""
        if not sym_in:
            raise AppError(
                code="VALIDATION_ERROR",
                message="read.market.trades 须通过 symbol 传入交易对（如 BTC-USDT）。",
                status_code=422,
                details={"field": "symbol"},
            )
        lim = _routing_market_limit(body)
        sym_norm = normalize_coobit_spot_symbol_param(sym_in)
        sym_order = normalize_coobit_spot_order_symbol(sym_in)
        raw_rows = await fetch_spot_public_trades_json_with_fallbacks(
            openapi_base_url=openapi_base,
            symbol_candidates=spot_ticker_symbol_candidates(sym_norm, sym_order),
            limit=lim,
        )
        preview = _sanitize_trades_preview(raw_rows, sym_norm)
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note="只读近期成交：现货公开 GET /sapi/v2/trades（免 Key）；仍要求用户已完成托管绑定。",
            exchange_read_preview=preview,
        )

    if sid == "read.account.balance":
        raw = await fetch_signed_spot_account_json(
            openapi_base_url=openapi_base,
            api_key=ak,
            secret_key=sk,
        )
        preview = _sanitize_balances_preview(raw if isinstance(raw, dict) else {})
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note="只读账户：GET /sapi/v1/account 摘要字段；不含密钥。",
            exchange_read_preview=preview,
        )

    if sid == "wealth.holdings_read":
        raw_w = await fetch_signed_asset_account_by_type_json(
            openapi_base_url=openapi_base,
            api_key=ak,
            secret_key=sk,
            account_type=4,
        )
        preview_w = _sanitize_wealth_holdings_preview(
            raw_w if isinstance(raw_w, dict) else {},
            account_type=4,
        )
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note=(
                "理财持仓只读：POST /sapi/v1/asset/account/by_type（accountType=4，otc/理财映射以所内为准）。"
            ),
            exchange_read_preview=preview_w,
        )

    if sid == "trade.spot.flash_convert":
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note=(
                "现货闪兑（市价）已提供 HTTP：确认参数后调用 "
                "POST /api/v1/agent/trade/spot/flash-convert；"
                "询价可用 GET /api/v1/agent/trade/spot/quote。\n"
                "Telegram 侧须完成类型 A 确认后再调后端写接口。"
            ),
        )

    if sid == "trade.spot.limit_order":
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note=(
                "现货限价已提供 HTTP：确认参数后调用 "
                "POST /api/v1/agent/trade/spot/limit-order（LIMIT，volume=base 数量，price=限价）；"
                "询价可用 GET /api/v1/agent/trade/spot/quote。\n"
                "Telegram 侧须完成类型 A 确认后再调后端写接口。"
            ),
        )

    if sid == "trade.spot.amend_limit_order":
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note=(
                "现货逻辑改单（CC-P0-02）已提供 HTTP：确认参数后调用 "
                "POST /api/v1/agent/trade/spot/amend-limit-order（单次授权顺序 cancel→order）；"
                "可先 GET /api/v1/agent/trade/spot/open-orders 核对在途单。\n"
                "Telegram 侧须完成类型 A「确认修改」后再调后端写接口。"
            ),
        )

    if sid == "trade.spot.open_orders":
        from chainup_agent.application.agent_spot_trade import spot_open_orders_for_bound_user

        sym_in = (body.symbol or "").strip() or None
        lim_raw = body.market_data_limit
        lim: int | None = None
        if lim_raw is not None:
            try:
                lim = max(1, min(int(lim_raw), 1000))
            except (TypeError, ValueError):
                lim = 50
        payload = await spot_open_orders_for_bound_user(
            session=session,
            settings=settings,
            user_id=str(tg_user),
            symbol=sym_in,
            limit=lim,
        )
        orders = payload.get("orders") if isinstance(payload.get("orders"), list) else []
        preview: dict[str, Any] = {
            "kind": "spot_open_orders_v1",
            "symbolFilter": payload.get("symbol"),
            "symbolOrderFilter": payload.get("symbolOrder"),
            "orderCount": len(orders),
            "items": orders[:64],
        }
        note_sym = f"（{sym_in}）" if sym_in else "（全交易对）"
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note=(
                f"现货当前委托：GET /sapi/v2/openOrders{note_sym}；"
                f"共 {len(orders)} 笔（展示至多 64 笔）。"
            ),
            exchange_read_preview=preview,
        )

    if sid == "trade.spot.cancel_order":
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note=(
                "现货撤单写路径：POST /api/v1/agent/trade/spot/cancel（Body userId、symbol、"
                "orderId 或 newClientOrderId 二选一）；Telegram 槽位齐全时走 EXECUTE_SPOT_CANCEL。"
            ),
        )

    if sid == "trade.futures.cancel_order":
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note=(
                "合约撤单：POST /api/v1/agent/trade/futures/cancel（userId、symbol、orderId）；"
                "Telegram 槽位齐全时走 EXECUTE_FUTURES_CANCEL。"
            ),
        )

    if sid == "automation.condition_orders_read":
        from chainup_agent.application.agent_futures_condition_trade import (
            futures_condition_orders_for_bound_user,
        )

        sym_in = (body.symbol or "").strip() or None
        payload = await futures_condition_orders_for_bound_user(
            session=session,
            settings=settings,
            user_id=str(tg_user),
            symbol=sym_in,
        )
        orders = payload.get("orders") if isinstance(payload.get("orders"), list) else []
        preview: dict[str, Any] = {
            "kind": "futures_condition_orders_v1",
            "contractNameFilter": payload.get("contractName"),
            "orderCount": len(orders),
            "totalOpenOrders": payload.get("totalOpenOrders"),
            "items": orders[:64],
        }
        note_sym = f"（{sym_in}）" if sym_in else "（全部合约）"
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note=(
                f"合约条件单：GET /fapi/v1/openOrders 筛选{note_sym}；"
                f"共 {len(orders)} 笔条件/计划委托（开放委托合计 "
                f"{payload.get('totalOpenOrders', 0)} 笔）。"
            ),
            exchange_read_preview=preview,
        )

    if sid == "automation.condition_order_cancel":
        return RoutingExecuteResponse(
            routed=True,
            scenario_id=sid,
            note=(
                "条件单撤销：POST /api/v1/agent/trade/futures/cancel-condition；"
                "Telegram 须类型 A 确认（ccp/ccx）。"
            ),
        )

    return RoutingExecuteResponse(
        routed=True,
        scenario_id=sid,
        note=(
            "后续路线图 scaffolding: 所写交易与计费尚未接线此 scenarioId；"
            "本轮已 wiring read.market.ticker / read.market.depth / read.market.trades / "
            "read.account.balance 与 flash-convert HTTP。"
        ),
    )
