import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import Base, async_session, engine
from app.services.redis_client import close_redis, init_redis
from app.services.settings_service import app_settings

logger = logging.getLogger(__name__)


async def init_db():
    """Create tables if they don't exist (for first run before alembic)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def init_settings():
    """Initialize settings from DB (seed defaults + load into memory cache)."""
    async with async_session() as db:
        await app_settings.initialize(db)
    logger.info("Settings initialized (setup_completed=%s)", app_settings.setup_completed)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Hantoo Trading Platform")
    await init_db()
    await init_redis()
    await init_settings()
    yield
    await close_redis()
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
        allow_origin_regex=r"https?://.*",  # credentials=True requires explicit origins, regex matches all
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.routers import accounts, auth, market, orders, portfolio, setup, watchlists

    app.include_router(setup.router, prefix="/api", tags=["Setup"])
    app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
    app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
    app.include_router(market.router, prefix="/api/market", tags=["Market"])
    app.include_router(watchlists.router, prefix="/api/watchlists", tags=["Watchlists"])
    app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
    app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])

    @app.get("/api/health")
    async def health():
        return {"status": "ok", "setup_completed": app_settings.setup_completed}

    return app
