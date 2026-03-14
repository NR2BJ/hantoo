import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from app.dependencies import DB, CurrentUser
from app.models.kis_account import KISAccount, KISAccountAccess
from app.schemas.account import KISAccountAccessGrant, KISAccountCreate, KISAccountResponse
from app.utils.encryption import encrypt_value

router = APIRouter()


def _to_response(account: KISAccount) -> KISAccountResponse:
    has_token = (
        account.access_token is not None
        and account.token_expires_at is not None
        and account.token_expires_at > datetime.now(timezone.utc)
    )
    return KISAccountResponse(
        id=account.id,
        label=account.label,
        account_type=account.account_type,
        environment=account.environment,
        account_number=account.account_number,
        product_code=account.product_code,
        hts_id=account.hts_id,
        is_active=account.is_active,
        has_valid_token=has_token,
    )


@router.get("/", response_model=list[KISAccountResponse])
async def list_accounts(user: CurrentUser, db: DB):
    """List all accounts the user owns or has access to."""
    result = await db.execute(
        select(KISAccount).where(
            or_(
                KISAccount.owner_id == user.id,
                KISAccount.id.in_(
                    select(KISAccountAccess.account_id).where(
                        KISAccountAccess.user_id == user.id
                    )
                ),
            ),
            KISAccount.is_active == True,  # noqa: E712
        )
    )
    accounts = result.scalars().all()
    return [_to_response(a) for a in accounts]


@router.post("/", response_model=KISAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(request: KISAccountCreate, user: CurrentUser, db: DB):
    account = KISAccount(
        owner_id=user.id,
        label=request.label,
        account_type=request.account_type,
        environment=request.environment,
        app_key_enc=encrypt_value(request.app_key),
        app_secret_enc=encrypt_value(request.app_secret),
        account_number=request.account_number,
        product_code=request.product_code,
        hts_id=request.hts_id,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return _to_response(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: uuid.UUID, user: CurrentUser, db: DB):
    result = await db.execute(
        select(KISAccount).where(KISAccount.id == account_id, KISAccount.owner_id == user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.is_active = False
    await db.commit()


# Share account access
@router.post("/{account_id}/access", status_code=status.HTTP_201_CREATED)
async def grant_access(
    account_id: uuid.UUID, request: KISAccountAccessGrant, user: CurrentUser, db: DB
):
    result = await db.execute(
        select(KISAccount).where(KISAccount.id == account_id, KISAccount.owner_id == user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or not owner")

    if account.account_type != "shared":
        raise HTTPException(status_code=400, detail="Can only share 'shared' type accounts")

    access = KISAccountAccess(
        account_id=account_id,
        user_id=request.user_id,
        permission=request.permission,
        granted_by=user.id,
    )
    db.add(access)
    await db.commit()
    return {"message": "Access granted"}


@router.delete("/{account_id}/access/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_access(
    account_id: uuid.UUID, target_user_id: uuid.UUID, user: CurrentUser, db: DB
):
    result = await db.execute(
        select(KISAccount).where(KISAccount.id == account_id, KISAccount.owner_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Account not found or not owner")

    result = await db.execute(
        select(KISAccountAccess).where(
            KISAccountAccess.account_id == account_id,
            KISAccountAccess.user_id == target_user_id,
        )
    )
    access = result.scalar_one_or_none()
    if not access:
        raise HTTPException(status_code=404, detail="Access grant not found")

    await db.delete(access)
    await db.commit()
