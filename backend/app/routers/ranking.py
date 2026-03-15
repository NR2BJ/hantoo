"""Ranking endpoints — volume rank, fluctuation, market cap, interest, etc."""

import logging

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import ActiveAccount, CurrentUser, DB
from app.schemas.market import InvestorItem, RankItem
from app.services.kis_client import KISApiError
from app.services.ranking_service import ranking_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/volume", response_model=list[RankItem])
async def get_volume_rank(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    market: str = Query("J", description="J=전체, NX=코스닥"),
):
    """거래량 순위."""
    try:
        return await ranking_service.get_volume_rank(account, db, market=market)
    except KISApiError as e:
        logger.info("KIS API error for ranking: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get volume rank: %s", e)
        return []


@router.get("/fluctuation", response_model=list[RankItem])
async def get_fluctuation(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    market: str = Query("J", description="J=전체, NX=코스닥"),
    sort: str = Query("1", description="1=상승, 2=하락"),
):
    """등락률 순위."""
    try:
        return await ranking_service.get_fluctuation(account, db, market=market, sort=sort)
    except KISApiError as e:
        logger.info("KIS API error for ranking: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get fluctuation: %s", e)
        return []


@router.get("/market-cap", response_model=list[RankItem])
async def get_market_cap(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    market: str = Query("J", description="J=전체, NX=코스닥"),
):
    """시가총액 순위."""
    try:
        return await ranking_service.get_market_cap(account, db, market=market)
    except KISApiError as e:
        logger.info("KIS API error for ranking: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get market cap rank: %s", e)
        return []


@router.get("/interest", response_model=list[RankItem])
async def get_top_interest(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    market: str = Query("J", description="J=전체, NX=코스닥"),
):
    """인기종목 (관심등록 순위)."""
    try:
        return await ranking_service.get_top_interest(account, db, market=market)
    except KISApiError as e:
        logger.info("KIS API error for ranking: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get top interest: %s", e)
        return []


@router.get("/highlow", response_model=list[RankItem])
async def get_near_highlow(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    market: str = Query("J", description="J=전체, NX=코스닥"),
    sort: str = Query("1", description="1=신고가, 2=신저가"),
):
    """신고가/신저가 근접 종목."""
    try:
        return await ranking_service.get_near_highlow(account, db, market=market, sort=sort)
    except KISApiError as e:
        logger.info("KIS API error for ranking: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get highlow rank: %s", e)
        return []


@router.get("/investor", response_model=list[InvestorItem])
async def get_investor(
    symbol: str,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    """종목별 투자자 매매동향."""
    try:
        return await ranking_service.get_investor(account, symbol, db)
    except KISApiError as e:
        logger.info("KIS API error for ranking: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get investor data: %s", e)
        return []


@router.get("/foreign", response_model=list[RankItem])
async def get_foreign_institution(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    market: str = Query("J", description="J=전체, NX=코스닥"),
):
    """외국인/기관 순매수 종목."""
    try:
        return await ranking_service.get_foreign_institution(account, db, market=market)
    except KISApiError as e:
        logger.info("KIS API error for ranking: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get foreign institution data: %s", e)
        return []
