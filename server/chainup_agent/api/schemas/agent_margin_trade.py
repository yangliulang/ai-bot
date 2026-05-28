"""Phase 2.4 — cross margin order HTTP models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class MarginOrderRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId", description="Telegram tg_id decimal string")
    symbol: str = Field(description="Trading pair (e.g. BTC-USDT → BTC/USDT on wire)")
    side: Literal["BUY", "SELL"]
    order_type: Literal["MARKET", "LIMIT"] = Field(alias="orderType")
    volume: str = Field(
        description="MARKET BUY: base qty converted to quote amount on wire; else base qty"
    )
    price: str | None = Field(
        default=None,
        description="Required when orderType=LIMIT",
    )
    new_client_order_id: str | None = Field(
        default=None,
        alias="newClientOrderId",
        max_length=31,
    )


class MarginOrderResponse(BaseModel):
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
