"""Corporate endpoints — dividends, news, stock info."""

import logging

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import ActiveAccount, CurrentUser, DB
from app.schemas.analysis import (
    DividendItem,
    DividendRankItem,
    NewsItem,
    StockInfoDetail,
)
from app.services.corporate_service import corporate_service
from app.services.kis_client import KISApiError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dividend", response_model=list[DividendItem])
async def get_dividend(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    symbol: str = Query(..., description="종목코드"),
):
    """배당정보."""
    try:
        return await corporate_service.get_dividend(account, symbol, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to get dividend for %s: %s", symbol, e)
        raise HTTPException(500, "Failed to get dividend info")


@router.get("/dividend-rate", response_model=list[DividendRankItem])
async def get_dividend_rate_ranking(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    market: str = Query("J", description="J=전체, NX=코스닥"),
):
    """배당수익률 랭킹."""
    try:
        return await corporate_service.get_dividend_rate_ranking(account, db, market=market)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to get dividend rate ranking: %s", e)
        raise HTTPException(500, "Failed to get dividend rate ranking")


@router.get("/news", response_model=list[NewsItem])
async def get_news(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    symbol: str = Query(..., description="종목코드"),
):
    """종목 뉴스 제목."""
    try:
        return await corporate_service.get_news(account, symbol, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to get news for %s: %s", symbol, e)
        raise HTTPException(500, "Failed to get news")


@router.get("/stock-info", response_model=StockInfoDetail)
async def get_stock_info(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    symbol: str = Query(..., description="종목코드"),
):
    """종목 기본정보."""
    try:
        return await corporate_service.get_stock_info(account, symbol, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to get stock info for %s: %s", symbol, e)
        raise HTTPException(500, "Failed to get stock info")
