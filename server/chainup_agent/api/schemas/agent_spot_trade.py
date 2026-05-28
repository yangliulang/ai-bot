"""Phase 2.1 — spot flash convert (MARKET) HTTP models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SpotQuoteResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(
        default="trade.spot.flash_convert",
        alias="scenarioId",
        description="Orchestration anchor for 闪兑 / 现货市价族",
    )
    symbol: str = Field(description="Normalized pair for public ticker (e.g. BTC-USDT)")
    symbol_order: str = Field(
        alias="symbolOrder",
        description="Compact pair id (e.g. BTCUSDT) for display/ticker fallbacks; signed POST /sapi/v2/order uses BASE/QUOTE (e.g. BTC/USDT) per GitBook v2",
    )
    quote_preview: dict[str, Any] = Field(alias="quotePreview")


class SpotFlashConvertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId", description="Telegram tg_id decimal string")
    symbol: str = Field(description="Trading pair (e.g. BTC-USDT, ETH/USDT)")
    side: Literal["BUY", "SELL"]
    volume: str = Field(
        description=(
            "标的资产（base）数量十进制字符串，例如 BTC-USDT 下的 BTC 数量；"
            "服务端对 MARKET BUY 会按公开 ticker 最新价换算为计价资产 amount 后再 POST 交易所（GitBook：市价买单 volume=amount）"
        ),
    )
    new_client_order_id: str | None = Field(
        default=None,
        alias="newClientOrderId",
        max_length=31,
        description="可选客户端委托号；须少于 32 字符（交易所约束）。缺省则由服务端生成 cu_agent_<hex>（总长 ≤31）",
    )


class SpotFlashConvertResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(default="trade.spot.flash_convert", alias="scenarioId")
    order_id: str | None = Field(default=None, alias="orderId")
    order_id_string: str | None = Field(default=None, alias="orderIdString")
    client_order_id: str | None = Field(default=None, alias="clientOrderId")
    status: str | None = None
    symbol: str | None = None
    side: str | None = None
    order_type: str | None = Field(default=None, alias="type")
    exchange_order_preview: dict[str, Any] = Field(
        default_factory=dict,
        alias="exchangeOrderPreview",
        description="Filtered exchange JSON (no secrets)",
    )


class SpotLimitOrderRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId", description="Telegram tg_id decimal string")
    symbol: str = Field(description="Trading pair (e.g. BTC-USDT, ETH/USDT)")
    side: Literal["BUY", "SELL"]
    volume: str = Field(
        description="LIMIT：标的 base 数量十进制字符串（与闪兑用户口径一致；非市价买 quote amount）",
    )
    price: str = Field(description="LIMIT 价格十进制字符串（与交易所 ``price`` 字段对齐）")
    time_in_force: Literal["GTC", "IOC", "FOK"] | None = Field(
        default=None,
        alias="timeInForce",
        description="默认 GTC；与 GitBook v2 Spot 撮合时效一致",
    )
    new_client_order_id: str | None = Field(
        default=None,
        alias="newClientOrderId",
        max_length=31,
        description="可选客户端委托号；须少于 32 字符（交易所约束）。缺省则由服务端生成 cu_agent_<hex>（总长 ≤31）",
    )


class SpotLimitOrderResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(default="trade.spot.limit_order", alias="scenarioId")
    order_id: str | None = Field(default=None, alias="orderId")
    order_id_string: str | None = Field(default=None, alias="orderIdString")
    client_order_id: str | None = Field(default=None, alias="clientOrderId")
    status: str | None = None
    symbol: str | None = None
    side: str | None = None
    order_type: str | None = Field(default=None, alias="type")
    exchange_order_preview: dict[str, Any] = Field(
        default_factory=dict,
        alias="exchangeOrderPreview",
        description="Filtered exchange JSON (no secrets)",
    )


class SpotCancelOrderRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId", description="Telegram tg_id decimal string")
    symbol: str = Field(description="Trading pair (e.g. BTC-USDT); cancel body uses BASE/QUOTE")
    order_id: str | None = Field(
        default=None,
        alias="orderId",
        description="Exchange order id（与 newClientOrderId 二选一必填其一）",
    )
    new_client_order_id: str | None = Field(
        default=None,
        alias="newClientOrderId",
        max_length=31,
        description="客户端委托号（可选替代 orderId）；须少于 32 字符",
    )


class SpotCancelOrderResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(default="trade.spot.cancel_order", alias="scenarioId")
    order_id: str | None = Field(default=None, alias="orderId")
    order_id_string: str | None = Field(default=None, alias="orderIdString")
    client_order_id: str | None = Field(default=None, alias="clientOrderId")
    status: str | None = None
    symbol: str | None = None
    side: str | None = None
    order_type: str | None = Field(default=None, alias="type")
    exchange_order_preview: dict[str, Any] = Field(
        default_factory=dict,
        alias="exchangeOrderPreview",
        description="Filtered exchange JSON (no secrets)",
    )


class SpotAmendLimitOrderRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId", description="Telegram tg_id decimal string")
    symbol: str = Field(description="Trading pair (e.g. BTC-USDT)")
    order_id: str = Field(alias="orderId", description="待修改的在途限价委托 orderId")
    price: str | None = Field(
        default=None,
        description="新限价；缺省则沿用原委托价格（须同时提供 volume 变更或显式 price）",
    )
    volume: str | None = Field(
        default=None,
        description="新 base 数量；缺省则沿用原委托 origQty",
    )
    time_in_force: Literal["GTC", "IOC", "FOK"] | None = Field(
        default=None,
        alias="timeInForce",
        description="默认沿用原单或 GTC",
    )
    new_client_order_id: str | None = Field(
        default=None,
        alias="newClientOrderId",
        max_length=31,
        description="替换单客户端委托号；须少于 32 字符",
    )


class SpotAmendLimitOrderResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(default="trade.spot.amend_limit_order", alias="scenarioId")
    amend_correlation_id: str = Field(alias="amendCorrelationId")
    cancelled_order_id: str | None = Field(default=None, alias="cancelledOrderId")
    cancelled_order_preview: dict[str, Any] = Field(
        default_factory=dict,
        alias="cancelledOrderPreview",
    )
    prior_order_preview: dict[str, Any] = Field(
        default_factory=dict,
        alias="priorOrderPreview",
    )
    order_id: str | None = Field(default=None, alias="orderId")
    order_id_string: str | None = Field(default=None, alias="orderIdString")
    client_order_id: str | None = Field(default=None, alias="clientOrderId")
    status: str | None = None
    symbol: str | None = None
    side: str | None = None
    order_type: str | None = Field(default=None, alias="type")
    exchange_order_preview: dict[str, Any] = Field(
        default_factory=dict,
        alias="exchangeOrderPreview",
    )


class SpotOpenOrdersResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(default="trade.spot.open_orders", alias="scenarioId")
    symbol: str | None = Field(
        default=None,
        description="筛选所用的 normalized ticker（如 BTC-USDT）；未筛选时为 null",
    )
    symbol_order: str | None = Field(
        default=None,
        alias="symbolOrder",
        description="紧凑交易对 id（未筛选时为 null）",
    )
    orders: list[dict[str, Any]] = Field(
        description="当前委托列表（字段已从交易所响应裁剪，不含密钥）",
    )
