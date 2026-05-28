"""Phase 2.3 — futures order HTTP models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class FuturesOrderRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId", description="Telegram tg_id decimal string")
    symbol: str = Field(description="Contract symbol (e.g. BTC-USDT → BTC_USDT)")
    side: Literal["BUY", "SELL"]
    order_type: Literal["MARKET", "LIMIT"] = Field(alias="orderType")
    volume: str = Field(description="Order quantity (contracts or base per exchange rules)")
    price: str | None = Field(
        default=None,
        description="Required when orderType=LIMIT",
    )
    open_close: Literal["OPEN", "CLOSE"] | None = Field(
        default=None,
        alias="openClose",
        description="Optional open/close semantics for Coobit fapi",
    )
    reduce_only: bool | None = Field(
        default=None,
        alias="reduceOnly",
        description="When true, maps to reduceOnly on exchange body",
    )
    new_client_order_id: str | None = Field(
        default=None,
        alias="newClientOrderId",
        max_length=31,
    )


class FuturesOrderResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(alias="scenarioId")
    order_id: str | None = Field(default=None, alias="orderId")
    order_id_string: str | None = Field(default=None, alias="orderIdString")
    client_order_id: str | None = Field(default=None, alias="clientOrderId")
    status: str | None = None
    symbol: str | None = None
    side: str | None = None
    type: str | None = None
    exchange_order_preview: dict[str, Any] = Field(alias="exchangeOrderPreview")


class FuturesCancelOrderRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId", description="Telegram tg_id decimal string")
    symbol: str = Field(description="Contract symbol (e.g. BTC-USDT → E-BTC-USDT)")
    order_id: str = Field(alias="orderId", description="Exchange order id to cancel")


class FuturesCancelOrderResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(default="trade.futures.cancel_order", alias="scenarioId")
    order_id: str | None = Field(default=None, alias="orderId")
    order_id_string: str | None = Field(default=None, alias="orderIdString")
    contract_name: str | None = Field(default=None, alias="contractName")
    symbol: str | None = None
    status: str | None = None
    exchange_order_preview: dict[str, Any] = Field(
        default_factory=dict,
        alias="exchangeOrderPreview",
    )
