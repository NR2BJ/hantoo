import logging

from app.models.kis_account import KISAccount
from app.schemas.market import (
    Candle,
    IndexQuote,
    Orderbook,
    OrderbookEntry,
    SearchResult,
    StockQuote,
    TradeRecord,
)
from app.services.cache import cache_get, cache_set
from app.services.kis_client import kis_client
from app.services.stock_list import search_stocks as search_stocks_naver

logger = logging.getLogger(__name__)

# Fallback index names (KIS API sometimes omits them)
INDEX_NAMES = {
    "0001": "코스피",
    "1001": "코스닥",
    "2001": "코스피200",
}


def _safe_int(val, default=0) -> int:
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def _safe_float(val, default=0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


class QuoteService:
    async def get_current_price(
        self, account: KISAccount, symbol: str, db
    ) -> StockQuote:
        cache_key = f"kis:quote:{symbol}"
        cached = await cache_get(cache_key)
        if cached:
            return StockQuote(**cached)

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/inquire-price",
            tr_id="FHKST01010100",
            params={
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": symbol,
            },
            db=db,
        )
        out = data.get("output", {})
        logger.info("KIS quote raw for %s: name=%s, price=%s, vol=%s",
                     symbol, out.get("hts_kor_isnm"), out.get("stck_prpr"), out.get("acml_vol"))

        quote = StockQuote(
            symbol=symbol,
            name=out.get("hts_kor_isnm", ""),
            current_price=_safe_int(out.get("stck_prpr")),
            change=_safe_int(out.get("prdy_vrss")),
            change_rate=_safe_float(out.get("prdy_ctrt")),
            change_sign=out.get("prdy_vrss_sign", "3"),
            open_price=_safe_int(out.get("stck_oprc")),
            high_price=_safe_int(out.get("stck_hgpr")),
            low_price=_safe_int(out.get("stck_lwpr")),
            volume=_safe_int(out.get("acml_vol")),
            trade_amount=_safe_int(out.get("acml_tr_pbmn")),
            prev_close=_safe_int(out.get("stck_sdpr")),
            market_cap=_safe_int(out.get("hts_avls")),
            per=_safe_float(out.get("per")) or None,
            pbr=_safe_float(out.get("pbr")) or None,
            eps=_safe_int(out.get("eps")) or None,
        )

        await cache_set(cache_key, quote.model_dump(), 5)
        return quote

    async def get_daily_candles(
        self, account: KISAccount, symbol: str, period: str, count: int, db
    ) -> list[Candle]:
        # period: D=일, W=주, M=월
        cache_key = f"kis:daily:{symbol}:{period}"
        cached = await cache_get(cache_key)
        if cached:
            return [Candle(**c) for c in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/inquire-daily-price",
            tr_id="FHKST01010400",
            params={
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": symbol,
                "FID_PERIOD_DIV_CODE": period,
                "FID_ORG_ADJ_PRC": "0",
            },
            db=db,
        )

        candles = []
        for item in data.get("output", [])[:count]:
            candles.append(
                Candle(
                    date=item.get("stck_bsop_date", ""),
                    open=_safe_int(item.get("stck_oprc")),
                    high=_safe_int(item.get("stck_hgpr")),
                    low=_safe_int(item.get("stck_lwpr")),
                    close=_safe_int(item.get("stck_clpr")),
                    volume=_safe_int(item.get("acml_vol")),
                )
            )

        # Reverse so oldest first
        candles.reverse()
        await cache_set(cache_key, [c.model_dump() for c in candles], 60)
        return candles

    async def get_minute_candles(
        self, account: KISAccount, symbol: str, interval: int, db
    ) -> list[Candle]:
        cache_key = f"kis:minute:{symbol}:{interval}"
        cached = await cache_get(cache_key)
        if cached:
            return [Candle(**c) for c in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice",
            tr_id="FHKST03010200",
            params={
                "FID_ETC_CLS_CODE": "",
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": symbol,
                "FID_INPUT_HOUR_1": "155000",
                "FID_PW_DATA_INCU_YN": "N",
            },
            db=db,
        )

        candles = []
        for item in data.get("output2", []):
            candles.append(
                Candle(
                    date=item.get("stck_bsop_date", "") + item.get("stck_cntg_hour", ""),
                    open=_safe_int(item.get("stck_oprc")),
                    high=_safe_int(item.get("stck_hgpr")),
                    low=_safe_int(item.get("stck_lwpr")),
                    close=_safe_int(item.get("stck_prpr")),
                    volume=_safe_int(item.get("cntg_vol")),
                )
            )

        candles.reverse()
        await cache_set(cache_key, [c.model_dump() for c in candles], 30)
        return candles

    async def get_orderbook(
        self, account: KISAccount, symbol: str, db
    ) -> Orderbook:
        cache_key = f"kis:orderbook:{symbol}"
        cached = await cache_get(cache_key)
        if cached:
            return Orderbook(**cached)

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn",
            tr_id="FHKST01010200",
            params={
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": symbol,
            },
            db=db,
        )
        out = data.get("output1", {})

        ask = []
        bid = []
        for i in range(1, 11):
            ask.append(
                OrderbookEntry(
                    price=_safe_int(out.get(f"askp{i}")),
                    volume=_safe_int(out.get(f"askp_rsqn{i}")),
                )
            )
            bid.append(
                OrderbookEntry(
                    price=_safe_int(out.get(f"bidp{i}")),
                    volume=_safe_int(out.get(f"bidp_rsqn{i}")),
                )
            )

        orderbook = Orderbook(
            symbol=symbol,
            ask=ask,
            bid=bid,
            total_ask_volume=_safe_int(out.get("total_askp_rsqn")),
            total_bid_volume=_safe_int(out.get("total_bidp_rsqn")),
        )

        await cache_set(cache_key, orderbook.model_dump(), 3)
        return orderbook

    async def get_trades(
        self, account: KISAccount, symbol: str, db
    ) -> list[TradeRecord]:
        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/inquire-ccnl",
            tr_id="FHKST01010300",
            params={
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": symbol,
            },
            db=db,
        )

        trades = []
        for item in data.get("output", [])[:50]:
            trades.append(
                TradeRecord(
                    time=item.get("stck_cntg_hour", ""),
                    price=_safe_int(item.get("stck_prpr")),
                    volume=_safe_int(item.get("cntg_vol")),
                    change=_safe_int(item.get("prdy_vrss")),
                )
            )
        return trades

    async def get_index_price(
        self, account: KISAccount, index_code: str, db
    ) -> IndexQuote:
        cache_key = f"kis:index:{index_code}"
        cached = await cache_get(cache_key)
        if cached:
            return IndexQuote(**cached)

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/inquire-index-price",
            tr_id="FHPUP02100000",
            params={
                "FID_COND_MRKT_DIV_CODE": "U",
                "FID_INPUT_ISCD": index_code,
            },
            db=db,
        )
        out = data.get("output", {})

        index = IndexQuote(
            code=index_code,
            name=out.get("hts_kor_isnm") or INDEX_NAMES.get(index_code, index_code),
            current=_safe_float(out.get("bstp_nmix_prpr")),
            change=_safe_float(out.get("bstp_nmix_prdy_vrss")),
            change_rate=_safe_float(out.get("bstp_nmix_prdy_ctrt")),
            change_sign=out.get("prdy_vrss_sign", "3"),
        )

        await cache_set(cache_key, index.model_dump(), 10)
        return index

    async def search_stocks(
        self, query: str
    ) -> list[SearchResult]:
        """Search stocks via Naver Finance autocomplete (no KIS API needed)."""
        return await search_stocks_naver(query)


quote_service = QuoteService()
