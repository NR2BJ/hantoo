import secrets
import uuid

import pyotp
from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.dependencies import DB, AdminUser, CurrentUser
from app.models.user import InviteCode, User
from app.schemas.auth import (
    InviteCodeCreate,
    InviteCodeResponse,
    LoginRequest,
    RegisterRequest,
    Setup2FAResponse,
    TokenResponse,
    UserResponse,
    Verify2FARequest,
)
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, response: Response, db: DB):
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    # Check 2FA if enabled
    if user.totp_enabled:
        if not request.totp_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="2FA code required",
                headers={"X-Requires-2FA": "true"},
            )
        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(request.totp_code, valid_window=1):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid 2FA code"
            )

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=86400,
    )
    return TokenResponse()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: DB):
    # Validate invite code
    result = await db.execute(
        select(InviteCode).where(InviteCode.code == request.invite_code)
    )
    invite = result.scalar_one_or_none()

    if not invite or invite.use_count >= invite.max_uses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invite code")

    if invite.expires_at and invite.expires_at < __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite code expired")

    # Check username uniqueness
    existing = await db.execute(select(User).where(User.username == request.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    user = User(
        username=request.username,
        display_name=request.display_name,
        password_hash=hash_password(request.password),
        role="member",
        invited_by=invite.created_by,
    )
    db.add(user)

    invite.use_count += 1
    invite.used_by = user.id

    await db.commit()
    await db.refresh(user)
    return user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: CurrentUser):
    return user


# 2FA setup
@router.post("/2fa/setup", response_model=Setup2FAResponse)
async def setup_2fa(user: CurrentUser, db: DB):
    secret = pyotp.random_base32()
    user.totp_secret = secret
    await db.commit()

    totp = pyotp.TOTP(secret)
    otpauth_url = totp.provisioning_uri(name=user.username, issuer_name="Hantoo")
    return Setup2FAResponse(secret=secret, otpauth_url=otpauth_url)


@router.post("/2fa/verify")
async def verify_2fa(request: Verify2FARequest, user: CurrentUser, db: DB):
    if not user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA not set up")

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(request.totp_code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid code")

    user.totp_enabled = True
    await db.commit()
    return {"message": "2FA enabled"}


@router.post("/2fa/disable")
async def disable_2fa(request: Verify2FARequest, user: CurrentUser, db: DB):
    if not user.totp_enabled:
        raise HTTPException(status_code=400, detail="2FA not enabled")

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(request.totp_code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid code")

    user.totp_enabled = False
    user.totp_secret = None
    await db.commit()
    return {"message": "2FA disabled"}


# Invite codes (admin only)
@router.post("/invite-codes", response_model=InviteCodeResponse)
async def create_invite_code(request: InviteCodeCreate, admin: AdminUser, db: DB):
    code = secrets.token_urlsafe(12)
    invite = InviteCode(
        code=code,
        created_by=admin.id,
        max_uses=request.max_uses,
    )
    db.add(invite)
    await db.commit()
    await db.refresh(invite)
    return invite


@router.get("/invite-codes", response_model=list[InviteCodeResponse])
async def list_invite_codes(admin: AdminUser, db: DB):
    result = await db.execute(
        select(InviteCode).where(InviteCode.created_by == admin.id).order_by(InviteCode.created_at.desc())
    )
    return result.scalars().all()
