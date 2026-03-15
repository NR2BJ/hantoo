"""Finance endpoints — financial statements, estimates, investment opinions."""

import logging

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import ActiveAccount, CurrentUser, DB
from app.schemas.analysis import (
    BalanceSheetItem,
    EstimateItem,
    FinancialRatioItem,
    IncomeStatementItem,
    InvestOpinionItem,
)
from app.services.finance_service import finance_service
from app.services.kis_client import KISApiError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/income-statement", response_model=list[IncomeStatementItem])
async def get_income_statement(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    symbol: str = Query(..., description="종목코드"),
    period: str = Query("A", description="A=연간, Q=분기"),
):
    """손익계산서."""
    try:
        return await finance_service.get_income_statement(account, symbol, db, period=period)
    except KISApiError as e:
        logger.info("KIS API error for finance: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get income statement for %s: %s", symbol, e)
        return []


@router.get("/balance-sheet", response_model=list[BalanceSheetItem])
async def get_balance_sheet(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    symbol: str = Query(..., description="종목코드"),
    period: str = Query("A", description="A=연간, Q=분기"),
):
    """재무상태표."""
    try:
        return await finance_service.get_balance_sheet(account, symbol, db, period=period)
    except KISApiError as e:
        logger.info("KIS API error for finance: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get balance sheet for %s: %s", symbol, e)
        return []


@router.get("/financial-ratio", response_model=list[FinancialRatioItem])
async def get_financial_ratio(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    symbol: str = Query(..., description="종목코드"),
    period: str = Query("A", description="A=연간, Q=분기"),
):
    """재무비율."""
    try:
        return await finance_service.get_financial_ratio(account, symbol, db, period=period)
    except KISApiError as e:
        logger.info("KIS API error for finance: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get financial ratio for %s: %s", symbol, e)
        return []


@router.get("/estimate", response_model=list[EstimateItem])
async def get_estimate(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    symbol: str = Query(..., description="종목코드"),
):
    """실적추정치."""
    try:
        return await finance_service.get_estimate(account, symbol, db)
    except KISApiError as e:
        logger.info("KIS API error for finance: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get estimate for %s: %s", symbol, e)
        return []


@router.get("/opinion", response_model=list[InvestOpinionItem])
async def get_invest_opinion(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    symbol: str = Query(..., description="종목코드"),
):
    """투자의견/컨센서스."""
    try:
        return await finance_service.get_invest_opinion(account, symbol, db)
    except KISApiError as e:
        logger.info("KIS API error for finance: %s", e.msg)
        return []
    except Exception as e:
        logger.warning("Failed to get invest opinion for %s: %s", symbol, e)
        return []
