import asyncio

from fastapi import APIRouter, Query

from app.dependencies import ActiveAccount, CurrentUser, DB
from app.schemas.market import (
    Candle,
    IndexQuote,
    Orderbook,
    SearchResult,
    StockQuote,
    TradeRecord,
)
from app.services.quote_service import quote_service

router = APIRouter()

MAJOR_INDICES = [
    ("0001", "코스피"),
    ("1001", "코스닥"),
    ("2001", "코스피200"),
]


@router.get("/quote", response_model=StockQuote)
async def get_quote(
    symbol: str,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    return await quote_service.get_current_price(account, symbol, db)


@router.get("/candles", response_model=list[Candle])
async def get_candles(
    symbol: str,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    period: str = Query("D", pattern=r"^[DWM]$"),
    count: int = Query(100, ge=1, le=300),
):
    return await quote_service.get_daily_candles(account, symbol, period, count, db)


@router.get("/candles/minute", response_model=list[Candle])
async def get_minute_candles(
    symbol: str,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    interval: int = Query(1, ge=1, le=60),
):
    return await quote_service.get_minute_candles(account, symbol, interval, db)


@router.get("/orderbook", response_model=Orderbook)
async def get_orderbook(
    symbol: str,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    return await quote_service.get_orderbook(account, symbol, db)


@router.get("/trades", response_model=list[TradeRecord])
async def get_trades(
    symbol: str,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    return await quote_service.get_trades(account, symbol, db)


@router.get("/indices", response_model=list[IndexQuote])
async def get_indices(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    tasks = [
        quote_service.get_index_price(account, code, db)
        for code, _ in MAJOR_INDICES
    ]
    return await asyncio.gather(*tasks)


@router.get("/search", response_model=list[SearchResult])
async def search_stocks(
    q: str = Query(..., min_length=1),
    user: CurrentUser = None,
    account: ActiveAccount = None,
    db: DB = None,
):
    return await quote_service.search_stocks(account, q, db)
