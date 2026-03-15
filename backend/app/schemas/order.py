"""Pydantic schemas for trading orders."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    LIMIT = "limit"       # 지정가
    MARKET = "market"     # 시장가


# ── Request Schemas ──

class OrderCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    side: OrderSide
    order_type: OrderType
    quantity: int = Field(..., gt=0)
    price: int | None = Field(None, ge=0)  # Required for limit, ignored for market


class OrderModify(BaseModel):
    quantity: int = Field(..., gt=0)
    price: int = Field(..., ge=0)


# ── Response Schemas ──

class OrderResponse(BaseModel):
    id: str
    account_id: str
    symbol: str
    side: str
    order_type: str
    quantity: int
    price: int | None
    status: str
    filled_quantity: int
    filled_price: int | None
    kis_order_id: str | None
    submitted_at: datetime | None
    created_at: datetime


class PendingOrder(BaseModel):
    """KIS 미체결 주문 정규화."""
    order_id: str          # 원주문번호
    symbol: str
    name: str
    side: str              # buy / sell
    order_type: str
    quantity: int           # 주문수량
    price: int              # 주문가격
    unfilled_qty: int       # 미체결수량
    order_time: str         # 주문시각


class FilledOrder(BaseModel):
    """KIS 체결 내역 정규화."""
    order_id: str
    symbol: str
    name: str
    side: str
    quantity: int           # 체결수량
    price: int              # 체결가격
    total_amount: int       # 체결금액
    order_time: str
    filled_time: str


class BuyableAmount(BaseModel):
    """매수 가능 금액/수량."""
    orderable_cash: int     # 주문가능현금
    orderable_qty: int      # 주문가능수량
