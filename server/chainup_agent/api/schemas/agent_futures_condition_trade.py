"""Phase 2.5 — futures condition order HTTP models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class FuturesConditionOrderRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId", description="Telegram tg_id decimal string")
    symbol: str = Field(description="Contract symbol (e.g. BTC-USDT → E-BTC-USDT)")
    side: Literal["BUY", "SELL"]
    order_type: Literal["MARKET", "LIMIT"] = Field(
        alias="orderType",
        description="Order type submitted after trigger fires",
    )
    volume: str = Field(description="Order quantity (contracts or base per exchange rules)")
    trigger_price: str = Field(alias="triggerPrice", description="Trigger price")
    trigger_type: Literal["3UP", "4DOWN"] = Field(
        alias="triggerType",
        description="3UP = rise trigger, 4DOWN = fall trigger",
    )
    price: str | None = Field(
        default=None,
        description="Required when orderType=LIMIT (execution price after trigger)",
    )
    open_close: Literal["OPEN", "CLOSE"] | None = Field(
        default=None,
        alias="openClose",
    )
    position_type: int = Field(default=1, alias="positionType", ge=1, le=2)
    order_unit: int = Field(default=2, alias="orderUnit", ge=1, le=3)


class FuturesConditionOrderResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(alias="scenarioId")
    order_id: str | None = Field(default=None, alias="orderId")
    order_id_string: str | None = Field(default=None, alias="orderIdString")
    contract_name: str | None = Field(default=None, alias="contractName")
    side: str | None = None
    type: str | None = None
    trigger_price: str | None = Field(default=None, alias="triggerPrice")
    trigger_type: str | None = Field(default=None, alias="triggerType")
    exchange_order_preview: dict[str, Any] = Field(alias="exchangeOrderPreview")


class FuturesConditionOrdersResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(
        default="automation.condition_orders_read",
        alias="scenarioId",
    )
    symbol: str | None = None
    contract_name: str | None = Field(default=None, alias="contractName")
    total_open_orders: int = Field(default=0, alias="totalOpenOrders")
    orders: list[dict[str, Any]] = Field(default_factory=list)


class FuturesConditionCancelRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId", description="Telegram tg_id decimal string")
    symbol: str = Field(description="Contract symbol (e.g. BTC-USDT)")
    order_id: str = Field(alias="orderId", description="Condition order id to cancel")


class FuturesConditionCancelResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(
        default="automation.condition_order_cancel",
        alias="scenarioId",
    )
    order_id: str | None = Field(default=None, alias="orderId")
    order_id_string: str | None = Field(default=None, alias="orderIdString")
    contract_name: str | None = Field(default=None, alias="contractName")
    symbol: str | None = None
    status: str | None = None
    exchange_order_preview: dict[str, Any] = Field(
        default_factory=dict,
        alias="exchangeOrderPreview",
    )
