import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.config import settings
from app.database import async_session, engine
from app.models.user import User
from app.utils.security import hash_password

logger = logging.getLogger(__name__)


async def create_admin_user():
    """Create admin user on first startup if none exists."""
    async with async_session() as db:
        result = await db.execute(select(User).where(User.role == "admin"))
        if result.scalar_one_or_none() is None:
            admin = User(
                username=settings.ADMIN_USERNAME,
                display_name="Admin",
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                role="admin",
            )
            db.add(admin)
            await db.commit()
            logger.info("Admin user created: %s", settings.ADMIN_USERNAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Hantoo Trading Platform")
    await create_admin_user()
    yield
    # Shutdown
    await engine.dispose()
    logger.info("Hantoo shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Hantoo Trading API",
        description="KIS Open API Web Trading Platform",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.routers import accounts, auth

    app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
    app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    return app
