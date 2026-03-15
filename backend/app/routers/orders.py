"""Trading order endpoints — place, modify, cancel, query."""

import logging

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import ActiveAccount, CurrentUser, DB
from app.schemas.order import (
    BuyableAmount,
    FilledOrder,
    OrderCreate,
    OrderModify,
    OrderResponse,
    PendingOrder,
)
from app.services.kis_client import KISApiError
from app.services.order_service import order_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=OrderResponse)
async def place_order(
    req: OrderCreate,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    """Place a buy or sell order."""
    # Validate: limit order must have price
    if req.order_type == "limit" and not req.price:
        raise HTTPException(400, "Limit order requires a price")

    try:
        return await order_service.place_order(account, user, req, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to place order: %s", e)
        raise HTTPException(500, "Failed to place order")


@router.put("/{trade_id}", response_model=OrderResponse)
async def modify_order(
    trade_id: str,
    req: OrderModify,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    """Modify an existing order (change quantity/price)."""
    try:
        return await order_service.modify_order(account, user, trade_id, req, db)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to modify order: %s", e)
        raise HTTPException(500, "Failed to modify order")


@router.delete("/{trade_id}", response_model=OrderResponse)
async def cancel_order(
    trade_id: str,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    """Cancel a pending order."""
    try:
        return await order_service.cancel_order(account, user, trade_id, db)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
    except Exception as e:
        logger.error("Failed to cancel order: %s", e)
        raise HTTPException(500, "Failed to cancel order")


@router.get("/pending", response_model=list[PendingOrder])
async def get_pending_orders(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    """Get unfilled/pending orders from KIS."""
    try:
        return await order_service.get_pending_orders(account, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")


@router.get("/filled", response_model=list[FilledOrder])
async def get_filled_orders(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    """Get filled order history from KIS."""
    try:
        return await order_service.get_filled_orders(account, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")


@router.get("/buyable", response_model=BuyableAmount)
async def get_buyable_amount(
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
    symbol: str = Query(..., min_length=1),
    price: int = Query(..., gt=0),
):
    """Get buyable amount/quantity for a stock at given price."""
    try:
        return await order_service.get_buyable_amount(account, symbol, price, db)
    except KISApiError as e:
        raise HTTPException(400, f"KIS API error: {e.msg}")
