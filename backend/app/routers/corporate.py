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
        logger.info("KIS API error for corporate: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get dividend for %s: %s", symbol, e)
        return []


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
        logger.info("KIS API error for corporate: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get dividend rate ranking: %s", e)
        return []


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
        logger.info("KIS API error for corporate: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get news for %s: %s", symbol, e)
        return []


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
        logger.info("KIS API error for corporate: %s", e.msg)
        return StockInfoDetail(
            symbol=symbol, name=symbol, market="", sector=None,
            listing_date=None, face_value=None,
            shares_outstanding=None, capital=None,
        )
    except Exception as e:
        logger.warning("Failed to get stock info for %s: %s", symbol, e)
        return StockInfoDetail(
            symbol=symbol, name=symbol, market="", sector=None,
            listing_date=None, face_value=None,
            shares_outstanding=None, capital=None,
        )
