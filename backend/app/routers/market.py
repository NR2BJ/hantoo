import asyncio
import logging

from fastapi import APIRouter, Query

from app.dependencies import ActiveAccount, CurrentUser, DB
from app.schemas.market import (
    Candle,
    IndexQuote,
    Orderbook,
    OrderbookEntry,
    SearchResult,
    StockQuote,
    TradeRecord,
)
from app.services.kis_client import KISApiError
from app.services.quote_service import quote_service

logger = logging.getLogger(__name__)

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
    try:
        return await quote_service.get_current_price(account, symbol, db)
    except KISApiError as e:
        logger.info("KIS API error for quote %s: %s", symbol, e.msg)
        return StockQuote(symbol=symbol, name=symbol, current_price=0, change=0,
                          change_rate=0.0, change_sign="3", open_price=0, high_price=0,
                          low_price=0, volume=0, trade_amount=0, prev_close=0, market_cap=0)
    except Exception:
        logger.exception("Failed to get quote for %s", symbol)
        return StockQuote(symbol=symbol, name=symbol, current_price=0, change=0,
                          change_rate=0.0, change_sign="3", open_price=0, high_price=0,
                          low_price=0, volume=0, trade_amount=0, prev_close=0, market_cap=0)


@router.get("/candles", response_model=list[Candle])
async def get_candles(
    symbol: str,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    period: str = Query("D", pattern=r"^[DWM]$"),
    count: int = Query(100, ge=1, le=300),
):
    try:
        return await quote_service.get_daily_candles(account, symbol, period, count, db)
    except KISApiError as e:
        logger.info("KIS API error for candles %s: %s", symbol, e.msg)
        return []
    except Exception:
        logger.exception("Failed to get candles for %s", symbol)
        return []


@router.get("/candles/minute", response_model=list[Candle])
async def get_minute_candles(
    symbol: str,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    interval: int = Query(1, ge=1, le=60),
):
    try:
        return await quote_service.get_minute_candles(account, symbol, interval, db)
    except KISApiError as e:
        logger.info("KIS API error for minute candles %s: %s", symbol, e.msg)
        return []
    except Exception:
        logger.exception("Failed to get minute candles for %s", symbol)
        return []


@router.get("/orderbook", response_model=Orderbook)
async def get_orderbook(
    symbol: str,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    try:
        return await quote_service.get_orderbook(account, symbol, db)
    except KISApiError as e:
        logger.info("KIS API error for orderbook %s: %s", symbol, e.msg)
        return Orderbook(symbol=symbol, ask=[OrderbookEntry(price=0, volume=0)] * 10,
                         bid=[OrderbookEntry(price=0, volume=0)] * 10,
                         total_ask_volume=0, total_bid_volume=0)
    except Exception:
        logger.exception("Failed to get orderbook for %s", symbol)
        return Orderbook(symbol=symbol, ask=[OrderbookEntry(price=0, volume=0)] * 10,
                         bid=[OrderbookEntry(price=0, volume=0)] * 10,
                         total_ask_volume=0, total_bid_volume=0)


@router.get("/trades", response_model=list[TradeRecord])
async def get_trades(
    symbol: str,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    try:
        return await quote_service.get_trades(account, symbol, db)
    except KISApiError as e:
        logger.info("KIS API error for trades %s: %s", symbol, e.msg)
        return []
    except Exception:
        logger.exception("Failed to get trades for %s", symbol)
        return []


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
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out failed index queries (e.g. paper trading server doesn't support indices)
    indices = []
    for (code, name), result in zip(MAJOR_INDICES, results):
        if isinstance(result, Exception):
            logger.warning("Failed to fetch index %s (%s): %s", code, name, result)
            continue
        indices.append(result)
    return indices


@router.get("/search", response_model=list[SearchResult])
async def search_stocks(
    user: CurrentUser,
    q: str = Query(..., min_length=1),
):
    """Search stocks locally (KRX stock list, no KIS account needed)."""
    return await quote_service.search_stocks(q)
