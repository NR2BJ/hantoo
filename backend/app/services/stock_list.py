"""Local stock list fetched from KRX for fast keyword search."""

import logging

import httpx

from app.services.cache import cache_get, cache_set
from app.schemas.market import SearchResult

logger = logging.getLogger(__name__)

CACHE_KEY = "kis:stocklist"
CACHE_TTL = 86400  # 24 hours

# KRX stock list sources
KRX_KOSPI_URL = "http://data.krx.co.kr/comm/bldAttend/getJsonData.cmd"
KRX_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
}


async def _fetch_krx_stocks(mkt_id: str) -> list[dict]:
    """Fetch stock list from KRX for a given market."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                KRX_KOSPI_URL,
                headers=KRX_HEADERS,
                data={
                    "bld": "dbms/MDC/STAT/standard/MDCSTAT01901",
                    "mktId": mkt_id,  # STK=KOSPI, KSQ=KOSDAQ
                    "share": "1",
                    "csvxls_isNo": "false",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("OutBlock_1", [])
    except Exception as e:
        logger.error("Failed to fetch KRX stock list (mkt=%s): %s", mkt_id, e)
        return []


async def load_stock_list() -> list[dict]:
    """Load stock list from cache or KRX."""
    cached = await cache_get(CACHE_KEY)
    if cached:
        return cached

    logger.info("Fetching stock list from KRX...")
    kospi = await _fetch_krx_stocks("STK")
    kosdaq = await _fetch_krx_stocks("KSQ")

    stocks = []
    for item in kospi:
        stocks.append({
            "symbol": item.get("ISU_SRT_CD", ""),
            "name": item.get("ISU_ABBRV", ""),
            "market": "KOSPI",
        })
    for item in kosdaq:
        stocks.append({
            "symbol": item.get("ISU_SRT_CD", ""),
            "name": item.get("ISU_ABBRV", ""),
            "market": "KOSDAQ",
        })

    if stocks:
        await cache_set(CACHE_KEY, stocks, CACHE_TTL)
        logger.info("Loaded %d stocks from KRX", len(stocks))
    else:
        logger.warning("No stocks loaded from KRX")

    return stocks


async def search_local(query: str) -> list[SearchResult]:
    """Search stocks locally by name or code."""
    stocks = await load_stock_list()
    query_lower = query.lower()

    results = []
    for s in stocks:
        if query_lower in s["name"].lower() or query_lower in s["symbol"].lower():
            results.append(SearchResult(
                symbol=s["symbol"],
                name=s["name"],
                market=s["market"],
            ))
        if len(results) >= 20:
            break

    return results
