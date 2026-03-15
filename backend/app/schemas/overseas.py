"""Pydantic schemas for overseas stock trading."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ── Quote Schemas ──


class OverseasQuote(BaseModel):
    """해외주식 현재가."""

    symbol: str
    name: str
    exchange: str  # NAS, NYS, AMS
    current_price: float  # USD
    change: float
    change_rate: float
    change_sign: str  # 1=상한 2=상승 3=보합 4=하한 5=하락
    open_price: float
    high_price: float
    low_price: float
    volume: int
    prev_close: float


class OverseasCandle(BaseModel):
    """해외주식 봉 데이터."""

    date: str  # YYYYMMDD
    open: float
    high: float
    low: float
    close: float
    volume: int


class OverseasSearchResult(BaseModel):
    """해외종목 검색 결과."""

    symbol: str
    name: str
    exchange: str  # NAS / NYS / AMS


# ── Order Schemas ──


class OverseasOrderCreate(BaseModel):
    """해외주식 주문 요청."""

    symbol: str = Field(..., min_length=1, max_length=20)
    exchange: str = Field(..., pattern=r"^(NAS|NYS|AMS)$")
    side: Literal["buy", "sell"]
    order_type: Literal["limit", "market"]
    quantity: int = Field(..., gt=0)
    price: float | None = Field(None, ge=0)


class OverseasOrderModify(BaseModel):
    """해외주식 주문 정정."""

    quantity: int = Field(..., gt=0)
    price: float = Field(..., ge=0)


class OverseasOrderResponse(BaseModel):
    """해외주식 주문 응답."""

    id: str
    account_id: str
    symbol: str
    exchange: str
    side: str
    order_type: str
    quantity: int
    price: float | None
    status: str
    filled_quantity: int
    filled_price: float | None
    kis_order_id: str | None
    submitted_at: datetime | None
    created_at: datetime


class OverseasFilledOrder(BaseModel):
    """해외주식 체결 내역."""

    order_id: str
    symbol: str
    name: str
    exchange: str
    side: str
    quantity: int
    price: float  # USD
    total_amount: float
    order_time: str
    filled_time: str


class OverseasBuyableAmount(BaseModel):
    """해외주식 매수 가능금액."""

    orderable_cash_foreign: float  # 주문가능 외화
    orderable_qty: int  # 주문가능 수량
    exchange_rate: float  # 적용 환율
