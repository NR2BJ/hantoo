"""Overseas stock trading endpoints — quotes, search, orders (US market)."""

import logging

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import ActiveAccount, CurrentUser, DB
from app.schemas.overseas import (
    OverseasBuyableAmount,
    OverseasCandle,
    OverseasFilledOrder,
    OverseasOrderCreate,
    OverseasOrderModify,
    OverseasOrderResponse,
    OverseasQuote,
    OverseasSearchResult,
)
from app.services.kis_client import KISApiError
from app.services.overseas_order_service import overseas_order_service
from app.services.overseas_quote_service import overseas_quote_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Quote Endpoints ──


@router.get("/quote", response_model=OverseasQuote)
async def get_overseas_quote(
    symbol: str,
    exchange: str = Query(..., pattern=r"^(NAS|NYS|AMS)$"),
    user: CurrentUser = None,
    account: ActiveAccount = None,
    db: DB = None,
):
    """해외주식 현재가 조회."""
    try:
        return await overseas_quote_service.get_current_price(account, symbol, exchange, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to get overseas quote: %s", e)
        raise HTTPException(500, "Failed to get overseas quote")


@router.get("/candles", response_model=list[OverseasCandle])
async def get_overseas_candles(
    symbol: str,
    exchange: str = Query(..., pattern=r"^(NAS|NYS|AMS)$"),
    user: CurrentUser = None,
    account: ActiveAccount = None,
    db: DB = None,
    period: str = Query("D", pattern=r"^[DWM]$"),
    count: int = Query(100, ge=1, le=300),
):
    """해외주식 일봉/주봉/월봉 조회."""
    try:
        return await overseas_quote_service.get_daily_candles(
            account, symbol, exchange, period, count, db
        )
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to get overseas candles: %s", e)
        raise HTTPException(500, "Failed to get overseas candles")


@router.get("/search", response_model=list[OverseasSearchResult])
async def search_overseas_stocks(
    q: str = Query(..., min_length=1),
    user: CurrentUser = None,
    account: ActiveAccount = None,
    db: DB = None,
):
    """해외종목 검색 (NASDAQ, NYSE, AMEX)."""
    try:
        return await overseas_quote_service.search_stocks(account, q, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to search overseas stocks: %s", e)
        raise HTTPException(500, "Failed to search overseas stocks")


# ── Order Endpoints ──


@router.post("/orders", response_model=OverseasOrderResponse)
async def place_overseas_order(
    req: OverseasOrderCreate,
    user: CurrentUser = None,
    account: ActiveAccount = None,
    db: DB = None,
):
    """해외주식 매수/매도 주문."""
    if req.order_type == "limit" and not req.price:
        raise HTTPException(400, "Limit order requires a price")

    try:
        return await overseas_order_service.place_order(account, user, req, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to place overseas order: %s", e)
        raise HTTPException(500, "Failed to place overseas order")


@router.put("/orders/{trade_id}", response_model=OverseasOrderResponse)
async def modify_overseas_order(
    trade_id: str,
    req: OverseasOrderModify,
    user: CurrentUser = None,
    account: ActiveAccount = None,
    db: DB = None,
):
    """해외주식 주문 정정."""
    try:
        return await overseas_order_service.modify_order(account, user, trade_id, req, db)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to modify overseas order: %s", e)
        raise HTTPException(500, "Failed to modify overseas order")


@router.delete("/orders/{trade_id}", response_model=OverseasOrderResponse)
async def cancel_overseas_order(
    trade_id: str,
    user: CurrentUser = None,
    account: ActiveAccount = None,
    db: DB = None,
):
    """해외주식 주문 취소."""
    try:
        return await overseas_order_service.cancel_order(account, user, trade_id, db)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to cancel overseas order: %s", e)
        raise HTTPException(500, "Failed to cancel overseas order")


@router.get("/orders/filled", response_model=list[OverseasFilledOrder])
async def get_overseas_filled_orders(
    user: CurrentUser = None,
    account: ActiveAccount = None,
    db: DB = None,
):
    """해외주식 체결 내역 조회."""
    try:
        return await overseas_order_service.get_filled_orders(account, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to get overseas filled orders: %s", e)
        return []


@router.get("/orders/buyable", response_model=OverseasBuyableAmount)
async def get_overseas_buyable(
    symbol: str = Query(..., min_length=1),
    exchange: str = Query(..., pattern=r"^(NAS|NYS|AMS)$"),
    price: float = Query(..., gt=0),
    user: CurrentUser = None,
    account: ActiveAccount = None,
    db: DB = None,
):
    """해외주식 매수 가능금액/수량 조회."""
    try:
        return await overseas_order_service.get_buyable_amount(
            account, symbol, exchange, price, db
        )
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to get overseas buyable: %s", e)
        raise HTTPException(500, "Failed to get overseas buyable amount")
