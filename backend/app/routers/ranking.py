"""Ranking endpoints — volume rank, fluctuation, market cap, interest, etc."""

import logging
import traceback

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


@router.get("/diagnostics")
async def diagnostics(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    """모든 랭킹 API를 한번에 호출하여 필드 매핑·건수·샘플 데이터를 반환. 디버깅 전용."""
    results: dict = {}
    test_cases = [
        ("volume", lambda: ranking_service.get_volume_rank(account, db, market="J")),
        ("fluctuation_up", lambda: ranking_service.get_fluctuation(account, db, market="J", sort="1")),
        ("fluctuation_down", lambda: ranking_service.get_fluctuation(account, db, market="J", sort="2")),
        ("market_cap", lambda: ranking_service.get_market_cap(account, db, market="J")),
        ("interest", lambda: ranking_service.get_top_interest(account, db, market="J")),
        ("highlow_high", lambda: ranking_service.get_near_highlow(account, db, market="J", sort="1")),
        ("highlow_low", lambda: ranking_service.get_near_highlow(account, db, market="J", sort="2")),
        ("foreign", lambda: ranking_service.get_foreign_institution(account, db, market="J")),
        ("investor_005930", lambda: ranking_service.get_investor(account, "005930", db)),
    ]
    for name, fn in test_cases:
        try:
            data = await fn()
            sample = None
            if data:
                first = data[0]
                sample = first.model_dump() if hasattr(first, "model_dump") else first
            results[name] = {
                "ok": True,
                "count": len(data),
                "sample": sample,
            }
        except Exception as e:
            results[name] = {
                "ok": False,
                "error": str(e),
                "traceback": traceback.format_exc()[-500:],
            }
    return results
