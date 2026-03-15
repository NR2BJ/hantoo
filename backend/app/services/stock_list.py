"""Local stock list fetched from KRX for fast keyword search."""

import csv
import io
import logging

import httpx

from app.services.cache import cache_get, cache_set
from app.schemas.market import SearchResult

logger = logging.getLogger(__name__)

CACHE_KEY = "kis:stocklist"
CACHE_TTL = 86400  # 24 hours

KRX_OTP_URL = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
KRX_DOWN_URL = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
KRX_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiSub/mdiSub01/mdiSub01BySec.cmd",
}


async def _fetch_krx_csv(mkt_id: str) -> list[dict]:
    """Fetch stock list CSV from KRX using OTP method."""
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            # Step 1: Get OTP
            otp_resp = await client.post(
                KRX_OTP_URL,
                headers=KRX_HEADERS,
                data={
                    "locale": "ko_KR",
                    "mktId": mkt_id,
                    "share": "1",
                    "csvxls_isNo": "false",
                    "name": "fileDown",
                    "url": "dbms/MDC/STAT/standard/MDCSTAT01901",
                },
            )
            otp_resp.raise_for_status()
            otp = otp_resp.text.strip()

            # Step 2: Download CSV
            csv_resp = await client.post(
                KRX_DOWN_URL,
                headers=KRX_HEADERS,
                data={"code": otp},
            )
            csv_resp.raise_for_status()

            # Parse CSV
            content = csv_resp.content.decode("euc-kr", errors="replace")
            reader = csv.DictReader(io.StringIO(content))
            rows = list(reader)
            return rows
    except Exception as e:
        logger.error("Failed to fetch KRX stock list (mkt=%s): %s", mkt_id, e)
        return []


async def load_stock_list() -> list[dict]:
    """Load stock list from cache or KRX."""
    cached = await cache_get(CACHE_KEY)
    if cached:
        return cached

    logger.info("Fetching stock list from KRX...")
    kospi = await _fetch_krx_csv("STK")
    kosdaq = await _fetch_krx_csv("KSQ")

    stocks = []
    for item in kospi:
        code = item.get("종목코드", "").strip()
        name = item.get("종목명", "").strip()
        if code and name:
            stocks.append({"symbol": code, "name": name, "market": "KOSPI"})
    for item in kosdaq:
        code = item.get("종목코드", "").strip()
        name = item.get("종목명", "").strip()
        if code and name:
            stocks.append({"symbol": code, "name": name, "market": "KOSDAQ"})

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
