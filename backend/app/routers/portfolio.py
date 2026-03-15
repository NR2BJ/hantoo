"""Portfolio endpoints — balance, holdings, overseas holdings."""

import logging

from fastapi import APIRouter, HTTPException

from app.dependencies import ActiveAccount, CurrentUser, DB
from app.schemas.portfolio import AccountBalance, Holding, OverseasHolding
from app.services.kis_client import KISApiError
from app.services.portfolio_service import portfolio_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/balance", response_model=AccountBalance)
async def get_balance(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    """Get account balance summary (cash, total value, P&L)."""
    try:
        return await portfolio_service.get_balance(account, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to get balance: %s", e)
        raise HTTPException(500, "Failed to get balance")


@router.get("/holdings", response_model=list[Holding])
async def get_holdings(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    """Get list of current domestic holdings with live prices."""
    try:
        return await portfolio_service.get_holdings(account, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to get holdings: %s", e)
        raise HTTPException(500, "Failed to get holdings")


@router.get("/overseas-holdings", response_model=list[OverseasHolding])
async def get_overseas_holdings(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    """Get list of overseas stock holdings (USD, etc.) with live prices."""
    try:
        return await portfolio_service.get_overseas_holdings(account, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to get overseas holdings: %s", e)
        raise HTTPException(500, "Failed to get overseas holdings")
