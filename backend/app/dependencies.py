import uuid
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.kis_account import KISAccount, KISAccountAccess
from app.models.user import User
from app.utils.security import decode_access_token


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    access_token: str | None = Cookie(default=None),
) -> User:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(access_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


async def get_active_account(
    account_id: uuid.UUID = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KISAccount:
    """Resolve a KIS account that the user owns or has access to."""
    result = await db.execute(select(KISAccount).where(KISAccount.id == account_id))
    account = result.scalar_one_or_none()

    if not account or not account.is_active:
        raise HTTPException(status_code=404, detail="Account not found")

    # Owner has full access
    if account.owner_id == user.id:
        return account

    # Check shared access
    access = await db.execute(
        select(KISAccountAccess).where(
            KISAccountAccess.account_id == account_id,
            KISAccountAccess.user_id == user.id,
        )
    )
    if access.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="No access to this account")

    return account


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
DB = Annotated[AsyncSession, Depends(get_db)]
ActiveAccount = Annotated[KISAccount, Depends(get_active_account)]
