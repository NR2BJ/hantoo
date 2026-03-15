"""Stock search using Naver Finance autocomplete API.

This replaces the KRX-based approach which fails from certain networks.
Naver autocomplete is fast, always available, and returns KIS-compatible
6-digit stock codes with market info.
"""

import logging

import httpx

from app.services.cache import cache_get, cache_set
from app.schemas.market import SearchResult

logger = logging.getLogger(__name__)

NAVER_AC_URL = "https://ac.stock.naver.com/ac"
NAVER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# Map Naver typeCode to our market names
MARKET_MAP = {
    "KOSPI": "KOSPI",
    "KOSDAQ": "KOSDAQ",
    "KONEX": "KONEX",
}


async def search_stocks(query: str) -> list[SearchResult]:
    """Search stocks via Naver Finance autocomplete API."""
    if not query or len(query.strip()) < 1:
        return []

    # Check cache first (short TTL since autocomplete is fast)
    cache_key = f"kis:search:{query.strip().lower()}"
    cached = await cache_get(cache_key)
    if cached:
        return [SearchResult(**r) for r in cached]

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                NAVER_AC_URL,
                headers=NAVER_HEADERS,
                params={
                    "q": query.strip(),
                    "target": "stock",
                },
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.error("Naver autocomplete failed for query=%r: %s", query, e)
        return []

    results = []
    for item in data.get("items", []):
        # Only include Korean domestic stocks
        if item.get("nationCode") != "KOR":
            continue
        type_code = item.get("typeCode", "")
        market = MARKET_MAP.get(type_code)
        if not market:
            continue

        code = item.get("code", "").strip()
        name = item.get("name", "").strip()
        if not code or not name:
            continue

        results.append(SearchResult(
            symbol=code,
            name=name,
            market=market,
        ))
        if len(results) >= 20:
            break

    # Cache for 5 minutes
    if results:
        await cache_set(cache_key, [r.model_dump() for r in results], 300)

    return results
