import asyncio
import uuid

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.dependencies import ActiveAccount, CurrentUser, DB
from app.models.watchlist import Watchlist, WatchlistItem
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistItemAdd,
    WatchlistItemResponse,
    WatchlistRename,
    WatchlistResponse,
)
from app.services.quote_service import quote_service

router = APIRouter()


async def _get_user_watchlist(watchlist_id: uuid.UUID, user_id: uuid.UUID, db) -> Watchlist:
    result = await db.execute(
        select(Watchlist)
        .options(selectinload(Watchlist.items))
        .where(Watchlist.id == watchlist_id, Watchlist.user_id == user_id)
    )
    wl = result.scalar_one_or_none()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return wl


@router.get("", response_model=list[WatchlistResponse])
async def list_watchlists(user: CurrentUser, db: DB):
    result = await db.execute(
        select(Watchlist)
        .options(selectinload(Watchlist.items))
        .where(Watchlist.user_id == user.id)
        .order_by(Watchlist.created_at)
    )
    return result.scalars().all()


@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def create_watchlist(request: WatchlistCreate, user: CurrentUser, db: DB):
    wl = Watchlist(name=request.name, user_id=user.id)
    db.add(wl)
    await db.commit()
    await db.refresh(wl, ["items"])
    return wl


@router.put("/{watchlist_id}", response_model=WatchlistResponse)
async def rename_watchlist(
    watchlist_id: uuid.UUID, request: WatchlistRename, user: CurrentUser, db: DB
):
    wl = await _get_user_watchlist(watchlist_id, user.id, db)
    wl.name = request.name
    await db.commit()
    await db.refresh(wl, ["items"])
    return wl


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(watchlist_id: uuid.UUID, user: CurrentUser, db: DB):
    wl = await _get_user_watchlist(watchlist_id, user.id, db)
    await db.delete(wl)
    await db.commit()


@router.post("/{watchlist_id}/items", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    watchlist_id: uuid.UUID, request: WatchlistItemAdd, user: CurrentUser, db: DB
):
    wl = await _get_user_watchlist(watchlist_id, user.id, db)

    # Check duplicate
    for item in wl.items:
        if item.symbol == request.symbol and item.market == request.market:
            raise HTTPException(status_code=409, detail="Already in watchlist")

    item = WatchlistItem(
        watchlist_id=wl.id, symbol=request.symbol, market=request.market
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{watchlist_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(
    watchlist_id: uuid.UUID, item_id: uuid.UUID, user: CurrentUser, db: DB
):
    await _get_user_watchlist(watchlist_id, user.id, db)
    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.id == item_id, WatchlistItem.watchlist_id == watchlist_id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(item)
    await db.commit()


@router.get("/{watchlist_id}/quotes", response_model=WatchlistResponse)
async def get_watchlist_with_quotes(
    watchlist_id: uuid.UUID,
    user: CurrentUser,
    account: ActiveAccount,
    db: DB,
):
    wl = await _get_user_watchlist(watchlist_id, user.id, db)

    # Fetch quotes for all items in parallel
    async def fetch_item_quote(item):
        try:
            quote = await quote_service.get_current_price(account, item.symbol, db)
            return WatchlistItemResponse(
                id=item.id,
                symbol=item.symbol,
                market=item.market,
                added_at=item.added_at,
                quote=quote,
            )
        except Exception:
            return WatchlistItemResponse(
                id=item.id,
                symbol=item.symbol,
                market=item.market,
                added_at=item.added_at,
                quote=None,
            )

    items_with_quotes = await asyncio.gather(
        *[fetch_item_quote(item) for item in wl.items]
    )

    return WatchlistResponse(
        id=wl.id,
        name=wl.name,
        created_at=wl.created_at,
        items=items_with_quotes,
    )
