"""Overseas stock master list — download & cache KIS .cod files for text search."""

import asyncio
import csv
import io
import logging
import zipfile

import httpx

from app.services.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

# KIS master file download URL pattern
_BASE_URL = "https://new.real.download.dws.co.kr/common/master"
# US markets only (NASDAQ, NYSE, AMEX)
_MARKETS = {
    "nas": "NAS",  # NASDAQ
    "nys": "NYS",  # NYSE
    "ams": "AMS",  # AMEX
}

# Column indices in the .cod tab-separated file (0-based)
_COL_SYMBOL = 4        # Symbol
_COL_KR_NAME = 6       # Korea name
_COL_EN_NAME = 7       # English name
_COL_SEC_TYPE = 8       # Security type (1:Index, 2:Stock, 3:ETP, 4:Warrant)

# Cache key & TTL — master list rarely changes, cache for 24h
_CACHE_KEY = "kis:overseas:master_list"
_CACHE_TTL = 86400  # 24 hours


async def _download_and_parse(market_code: str, exchange: str) -> list[dict]:
    """Download one market's .cod.zip, parse, return list of stock dicts."""
    url = f"{_BASE_URL}/{market_code}mst.cod.zip"
    items = []

    try:
        async with httpx.AsyncClient(verify=False, timeout=30) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            # There should be exactly one .cod file inside
            cod_names = [n for n in zf.namelist() if n.endswith(".cod")]
            if not cod_names:
                logger.warning("No .cod file in %s", url)
                return []

            raw = zf.read(cod_names[0])
            text = raw.decode("cp949", errors="replace")

        reader = csv.reader(io.StringIO(text), delimiter="\t")
        for row in reader:
            if len(row) <= _COL_EN_NAME:
                continue
            symbol = row[_COL_SYMBOL].strip()
            kr_name = row[_COL_KR_NAME].strip()
            en_name = row[_COL_EN_NAME].strip()
            sec_type = row[_COL_SEC_TYPE].strip() if len(row) > _COL_SEC_TYPE else ""

            if not symbol:
                continue
            # Skip indices (type 1), keep stocks (2), ETF/ETP (3), etc.
            if sec_type == "1":
                continue

            items.append({
                "symbol": symbol,
                "name": kr_name or en_name,
                "en_name": en_name,
                "exchange": exchange,
            })

        logger.info("Loaded %d stocks from %s (%s)", len(items), market_code, exchange)
    except Exception as e:
        logger.error("Failed to download master list for %s: %s", market_code, e)

    return items


async def get_master_list() -> list[dict]:
    """Get the full overseas master stock list (cached 24h in Redis)."""
    cached = await cache_get(_CACHE_KEY)
    if cached:
        return cached

    # Download all markets in parallel
    tasks = [_download_and_parse(code, excd) for code, excd in _MARKETS.items()]
    results = await asyncio.gather(*tasks)

    master = []
    for items in results:
        master.extend(items)

    logger.info("Total overseas master list: %d stocks", len(master))
    await cache_set(_CACHE_KEY, master, _CACHE_TTL)
    return master


async def search_master(query: str, limit: int = 30) -> list[dict]:
    """Search master list by symbol/name, returning most relevant results."""
    master = await get_master_list()
    q = query.upper()

    exact = []
    prefix = []
    contains_sym = []
    contains_name = []

    for item in master:
        sym = item["symbol"].upper()
        name_upper = item["name"].upper()
        en_upper = item.get("en_name", "").upper()

        if sym == q:
            exact.append(item)
        elif sym.startswith(q):
            prefix.append(item)
        elif q in sym:
            contains_sym.append(item)
        elif q in name_upper or q in en_upper:
            contains_name.append(item)

    # Sort each group alphabetically by symbol
    prefix.sort(key=lambda x: x["symbol"])
    contains_sym.sort(key=lambda x: x["symbol"])
    contains_name.sort(key=lambda x: x["symbol"])

    results = exact + prefix + contains_sym + contains_name
    return results[:limit]
