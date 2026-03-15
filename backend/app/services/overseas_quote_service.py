"""Overseas stock quote service — price, candles, search via KIS API."""

import asyncio
import logging

from app.models.kis_account import KISAccount
from app.schemas.overseas import OverseasCandle, OverseasQuote, OverseasSearchResult
from app.services.cache import cache_get, cache_set
from app.services.kis_client import kis_client

logger = logging.getLogger(__name__)


def _safe_int(val, default=0) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _safe_float(val, default=0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


class OverseasQuoteService:
    # ── Current Price ──
    async def get_current_price(
        self,
        account: KISAccount,
        symbol: str,
        exchange: str,
        db,
    ) -> OverseasQuote:
        """해외주식 현재가 (HHDFS00000300)."""
        cache_key = f"kis:overseas:quote:{exchange}:{symbol}"
        cached = await cache_get(cache_key)
        if cached:
            return OverseasQuote(**cached)

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/overseas-price/v1/quotations/price",
            tr_id="HHDFS00000300",
            params={
                "AUTH": "",
                "EXCD": exchange,
                "SYMB": symbol,
            },
            db=db,
        )
        out = data.get("output", {})

        # Determine change_sign from diff value
        diff = _safe_float(out.get("diff"))
        if diff > 0:
            change_sign = "2"  # 상승
        elif diff < 0:
            change_sign = "5"  # 하락
        else:
            change_sign = "3"  # 보합

        # Override with explicit sign if present
        sign = out.get("sign", "")
        if sign:
            change_sign = sign

        quote = OverseasQuote(
            symbol=symbol,
            name=out.get("rsym", "").replace(f"{exchange}", "").strip()
            if not out.get("name")
            else out.get("name", ""),
            exchange=exchange,
            current_price=_safe_float(out.get("last")),
            change=_safe_float(out.get("diff")),
            change_rate=_safe_float(out.get("rate")),
            change_sign=change_sign,
            open_price=_safe_float(out.get("open")),
            high_price=_safe_float(out.get("high")),
            low_price=_safe_float(out.get("low")),
            volume=_safe_int(out.get("tvol")),
            prev_close=_safe_float(out.get("base")),
        )

        await cache_set(cache_key, quote.model_dump(), 5)
        return quote

    # ── Daily Candles ──
    async def get_daily_candles(
        self,
        account: KISAccount,
        symbol: str,
        exchange: str,
        period: str,
        count: int,
        db,
    ) -> list[OverseasCandle]:
        """해외주식 일봉/주봉/월봉 차트 (FHKST03030100)."""
        cache_key = f"kis:overseas:daily:{exchange}:{symbol}:{period}"
        cached = await cache_get(cache_key)
        if cached:
            return [OverseasCandle(**c) for c in cached]

        # Map exchange to FID_COND_MRKT_DIV_CODE
        # N = 뉴욕, X = AMEX, O = NASDAQ (... etc)
        market_div = _exchange_to_market_div(exchange)

        # Date range — get last 1 year
        from datetime import datetime, timedelta

        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/overseas-price/v1/quotations/inquire-daily-chartprice",
            tr_id="FHKST03030100",
            params={
                "FID_COND_MRKT_DIV_CODE": market_div,
                "FID_INPUT_ISCD": symbol,
                "FID_INPUT_DATE_1": start_date,
                "FID_INPUT_DATE_2": end_date,
                "FID_PERIOD_DIV_CODE": period,
            },
            db=db,
        )

        candles = []
        for item in data.get("output2", [])[:count]:
            close = _safe_float(item.get("clos")) or _safe_float(item.get("ovrs_nmix_prpr"))
            if close <= 0:
                continue
            candles.append(
                OverseasCandle(
                    date=item.get("stck_bsop_date", ""),
                    open=_safe_float(item.get("open")) or _safe_float(item.get("ovrs_nmix_oprc")),
                    high=_safe_float(item.get("high")) or _safe_float(item.get("ovrs_nmix_hgpr")),
                    low=_safe_float(item.get("low")) or _safe_float(item.get("ovrs_nmix_lwpr")),
                    close=close,
                    volume=_safe_int(item.get("acml_vol")),
                )
            )

        # Reverse so oldest first
        candles.reverse()
        await cache_set(cache_key, [c.model_dump() for c in candles], 60)
        return candles

    # ── Stock Search ──
    async def search_stocks(
        self,
        account: KISAccount,
        query: str,
        db,
    ) -> list[OverseasSearchResult]:
        """해외종목 검색 (HHDFS76410000) — NAS/NYS/AMS 3개 거래소 병렬 조회."""
        cache_key = f"kis:overseas:search:{query.upper()}"
        cached = await cache_get(cache_key)
        if cached:
            return [OverseasSearchResult(**r) for r in cached]

        exchanges = ["NAS", "NYS", "AMS"]

        async def _search_one(excd: str) -> list[OverseasSearchResult]:
            try:
                data = await kis_client.request(
                    account,
                    "GET",
                    "/uapi/overseas-price/v1/quotations/inquire-search",
                    tr_id="HHDFS76410000",
                    params={
                        "AUTH": "",
                        "EXCD": excd,
                        "CO_YN_PRCR": "",
                        "OS_YN_PRCR": "",
                        "FND_COND": query.upper(),
                    },
                    db=db,
                )
                results = []
                for item in data.get("output2", []):
                    sym = item.get("symb", "").strip()
                    name = item.get("name", "").strip()
                    if sym:
                        results.append(
                            OverseasSearchResult(
                                symbol=sym,
                                name=name,
                                exchange=excd,
                            )
                        )
                return results
            except Exception as e:
                logger.warning("Overseas search failed for %s: %s", excd, e)
                return []

        all_results = await asyncio.gather(*[_search_one(ex) for ex in exchanges])
        merged = []
        for results in all_results:
            merged.extend(results)

        # Sort by relevance: exact symbol > prefix > contains > rest
        q_upper = query.upper()

        def _relevance(r: OverseasSearchResult) -> tuple[int, str]:
            sym = r.symbol.upper()
            if sym == q_upper:
                return (0, sym)          # exact match
            if sym.startswith(q_upper):
                return (1, sym)          # prefix match
            if q_upper in sym:
                return (2, sym)          # symbol contains query
            if q_upper in r.name.upper():
                return (3, sym)          # name contains query
            return (4, sym)

        merged.sort(key=_relevance)
        merged = merged[:50]

        await cache_set(cache_key, [r.model_dump() for r in merged], 30)
        return merged


def _exchange_to_market_div(exchange: str) -> str:
    """Map exchange code to KIS FID_COND_MRKT_DIV_CODE."""
    mapping = {
        "NAS": "N",  # NASDAQ
        "NYS": "N",  # NYSE (also uses N for US)
        "AMS": "N",  # AMEX (also uses N for US)
    }
    return mapping.get(exchange, "N")


overseas_quote_service = OverseasQuoteService()
