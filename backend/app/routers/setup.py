"""Setup wizard and settings management routes.

/api/setup/* - First-run setup (no auth required, only works before setup is complete)
/api/settings/* - Admin-only settings management
"""

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.database import get_db
from app.dependencies import DB, AdminUser
from app.models.user import User
from app.services.settings_service import app_settings
from app.utils.security import create_access_token, hash_password

router = APIRouter()


# ── Setup Wizard ──────────────────────────────────────────────


class SetupStatusResponse(BaseModel):
    setup_completed: bool
    app_name: str


class SetupRequest(BaseModel):
    """First-run setup: create admin account."""

    admin_username: str = Field(min_length=3, max_length=50)
    admin_display_name: str = Field(min_length=1, max_length=100)
    admin_password: str = Field(min_length=8)
    app_name: str = Field(default="Hantoo", max_length=100)


@router.get("/setup/status", response_model=SetupStatusResponse)
async def get_setup_status():
    """Check if initial setup has been completed. No auth required."""
    return SetupStatusResponse(
        setup_completed=app_settings.setup_completed,
        app_name=app_settings.get("app_name", "Hantoo"),
    )


@router.post("/setup/complete")
async def complete_setup(request: SetupRequest, response: Response, db: DB):
    """Complete first-run setup. Creates admin account. Only works once."""
    if app_settings.setup_completed:
        raise HTTPException(status_code=400, detail="Setup already completed")

    # Check no users exist (safety)
    result = await db.execute(select(User).limit(1))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Users already exist")

    # Create admin user
    admin = User(
        username=request.admin_username,
        display_name=request.admin_display_name,
        password_hash=hash_password(request.admin_password),
        role="admin",
    )
    db.add(admin)

    # Update app settings
    await app_settings.set("app_name", request.app_name, db)
    await app_settings.set("setup_completed", "true", db)

    await db.commit()
    await db.refresh(admin)

    # Auto-login the new admin
    token = create_access_token(data={"sub": str(admin.id), "role": admin.role})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # TODO: set True when behind HTTPS reverse proxy
        samesite="lax",
        max_age=86400,
    )

    return {"message": "Setup completed", "admin_username": admin.username}


# ── Settings Management (Admin only) ──────────────────────────


class SettingUpdate(BaseModel):
    key: str
    value: str


class SettingsBulkUpdate(BaseModel):
    settings: list[SettingUpdate]


@router.get("/settings", tags=["Settings"])
async def get_all_settings(admin: AdminUser, db: DB):
    """Get all app settings (secrets are masked)."""
    return await app_settings.get_all_for_ui(db)


@router.put("/settings", tags=["Settings"])
async def update_settings(request: SettingsBulkUpdate, admin: AdminUser, db: DB):
    """Update one or more settings."""
    updated = []
    for s in request.settings:
        # Don't allow overwriting secrets with the masked placeholder
        if s.value == "••••••••":
            continue
        await app_settings.set(s.key, s.value, db)
        updated.append(s.key)

    return {"message": f"Updated {len(updated)} settings", "updated_keys": updated}


@router.put("/settings/{key}", tags=["Settings"])
async def update_single_setting(key: str, request: SettingUpdate, admin: AdminUser, db: DB):
    """Update a single setting."""
    if request.value == "••••••••":
        raise HTTPException(status_code=400, detail="Cannot set masked value")
    await app_settings.set(key, request.value, db)
    return {"message": f"Updated {key}"}
