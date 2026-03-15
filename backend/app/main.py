import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import Base, async_session, engine
from app.services.redis_client import close_redis, init_redis
from app.services.settings_service import app_settings

# Configure app loggers to INFO so debug logs from services are visible
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

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

    from app.routers import (
        accounts, auth, corporate, finance, market, orders, overseas,
        portfolio, ranking, setup, watchlists,
    )

    app.include_router(setup.router, prefix="/api", tags=["Setup"])
    app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
    app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
    app.include_router(market.router, prefix="/api/market", tags=["Market"])
    app.include_router(watchlists.router, prefix="/api/watchlists", tags=["Watchlists"])
    app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
    app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
    app.include_router(overseas.router, prefix="/api/overseas", tags=["Overseas"])
    app.include_router(ranking.router, prefix="/api/ranking", tags=["Ranking"])
    app.include_router(finance.router, prefix="/api/finance", tags=["Finance"])
    app.include_router(corporate.router, prefix="/api/corporate", tags=["Corporate"])

    @app.get("/api/health")
    async def health():
        return {"status": "ok", "setup_completed": app_settings.setup_completed}

    @app.get("/api/debug/test-quote")
    async def debug_test_quote(symbol: str = "005930"):
        """Diagnostic: test KIS API quote call and return raw data or error details."""
        from app.database import async_session as _session
        from app.models.kis_account import KISAccount
        from app.services.kis_client import KISApiError, kis_client
        from sqlalchemy import select

        async with _session() as db:
            result = await db.execute(
                select(KISAccount).where(KISAccount.is_active == True).limit(1)  # noqa: E712
            )
            account = result.scalar_one_or_none()
            if not account:
                return {"error": "No active KIS account found"}

            try:
                data = await kis_client.request(
                    account, "GET",
                    "/uapi/domestic-stock/v1/quotations/inquire-price",
                    tr_id="FHKST01010100",
                    params={"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": symbol},
                    db=db,
                )
                out = data.get("output", {})
                return {
                    "status": "ok",
                    "rt_cd": data.get("rt_cd"),
                    "symbol": symbol,
                    "name": out.get("hts_kor_isnm"),
                    "price": out.get("stck_prpr"),
                    "volume": out.get("acml_vol"),
                    "raw_keys": list(out.keys())[:20],
                }
            except KISApiError as e:
                return {"status": "kis_error", "rt_cd": e.rt_cd, "msg_cd": e.msg_cd, "msg": e.msg}
            except Exception as e:
                return {"status": "exception", "type": type(e).__name__, "msg": str(e)}

    @app.post("/api/cache/flush")
    async def flush_cache(symbol: str = "", scope: str = ""):
        """Flush Redis cache. Optional: symbol=005930 or scope=ranking."""
        from app.services.redis_client import get_redis
        r = get_redis()
        if symbol:
            pattern = f"kis:*{symbol}*"
        elif scope:
            pattern = f"kis:*:{scope}:*"
        else:
            pattern = "kis:*"
        keys = [k async for k in r.scan_iter(pattern)]
        if keys:
            await r.delete(*keys)
        return {"flushed": len(keys), "pattern": pattern}

    return app
