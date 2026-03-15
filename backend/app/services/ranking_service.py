"""Ranking & market info service — volume rank, fluctuation, market cap, etc."""

import logging

from app.models.kis_account import KISAccount
from app.schemas.market import InvestorItem, RankItem
from app.services.cache import cache_get, cache_set
from app.services.kis_client import kis_client

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _parse_rank_items(output: list[dict]) -> list[RankItem]:
    """Parse KIS ranking output into RankItem list."""
    items: list[RankItem] = []
    for row in output:
        symbol = row.get("mksc_shrn_iscd", "").strip()
        name = row.get("hts_kor_isnm", "").strip()
        if not symbol or not name:
            continue
        items.append(
            RankItem(
                rank=_safe_int(row.get("data_rank", 0)),
                symbol=symbol,
                name=name,
                current_price=_safe_int(row.get("stck_prpr")),
                change=_safe_int(row.get("prdy_vrss")),
                change_rate=_safe_float(row.get("prdy_ctrt")),
                change_sign=row.get("prdy_vrss_sign", "3"),
                volume=_safe_int(row.get("acml_vol")),
                trade_amount=_safe_int(row.get("acml_tr_pbmn")),
            )
        )
    return items


# ---------------------------------------------------------------------------
# Investor name mapping
# ---------------------------------------------------------------------------

_INVESTOR_NAMES = {
    "1": "개인",
    "2": "외국인",
    "3": "기관계",
    "4": "금융투자",
    "5": "보험",
    "6": "투신",
    "7": "사모",
    "8": "은행",
    "9": "기타금융",
    "10": "연기금",
    "11": "기타법인",
    "12": "기타외국인",
}


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class RankingService:
    """Ranking & market info queries via KIS API."""

    # ---- 거래량 순위 ----
    async def get_volume_rank(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
    ) -> list[RankItem]:
        cache_key = f"kis:ranking:volume:{market}"
        cached = await cache_get(cache_key)
        if cached:
            return [RankItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/volume-rank",
            tr_id="FHPST01710000",
            params={
                "FID_COND_MRKT_DIV_CODE": market,
                "FID_COND_SCR_DIV_CODE": "20171",
                "FID_INPUT_ISCD": "0000",
                "FID_DIV_CLS_CODE": "0",
                "FID_BLNG_CLS_CODE": "0",
                "FID_TRGT_CLS_CODE": "111111111",
                "FID_TRGT_EXLS_CLS_CODE": "000000",
                "FID_INPUT_PRICE_1": "0",
                "FID_INPUT_PRICE_2": "0",
                "FID_VOL_CNT": "0",
                "FID_INPUT_DATE_1": "",
            },
            db=db,
        )
        items = _parse_rank_items(data.get("output", []))
        await cache_set(cache_key, [i.model_dump() for i in items], 10)
        return items

    # ---- 등락률 순위 ----
    async def get_fluctuation(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
        sort: str = "1",  # 1=상승, 2=하락
    ) -> list[RankItem]:
        cache_key = f"kis:ranking:fluctuation:{market}:{sort}"
        cached = await cache_get(cache_key)
        if cached:
            return [RankItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/ranking/fluctuation",
            tr_id="FHPST01700000",
            params={
                "FID_COND_MRKT_DIV_CODE": market,
                "FID_COND_SCR_DIV_CODE": "20170",
                "FID_INPUT_ISCD": "0000",
                "FID_RANK_SORT_CLS_CODE": sort,
                "FID_DIV_CLS_CODE": "0",
                "FID_TRGT_CLS_CODE": "111111111",
                "FID_TRGT_EXLS_CLS_CODE": "000000",
                "FID_INPUT_PRICE_1": "0",
                "FID_INPUT_PRICE_2": "0",
                "FID_VOL_CNT": "0",
                "FID_INPUT_DATE_1": "",
                "FID_RSFL_RATE1": "",
                "FID_RSFL_RATE2": "",
            },
            db=db,
        )
        items = _parse_rank_items(data.get("output", []))
        await cache_set(cache_key, [i.model_dump() for i in items], 10)
        return items

    # ---- 시가총액 순위 ----
    async def get_market_cap(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
    ) -> list[RankItem]:
        cache_key = f"kis:ranking:marketcap:{market}"
        cached = await cache_get(cache_key)
        if cached:
            return [RankItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/ranking/market-cap",
            tr_id="FHPST01740000",
            params={
                "FID_COND_MRKT_DIV_CODE": market,
                "FID_COND_SCR_DIV_CODE": "20174",
                "FID_INPUT_ISCD": "0000",
                "FID_DIV_CLS_CODE": "0",
                "FID_TRGT_CLS_CODE": "111111111",
                "FID_TRGT_EXLS_CLS_CODE": "000000",
                "FID_INPUT_PRICE_1": "0",
                "FID_INPUT_PRICE_2": "0",
                "FID_VOL_CNT": "0",
            },
            db=db,
        )
        items = _parse_rank_items(data.get("output", []))
        await cache_set(cache_key, [i.model_dump() for i in items], 10)
        return items

    # ---- 인기종목 (관심도) ----
    async def get_top_interest(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
    ) -> list[RankItem]:
        cache_key = f"kis:ranking:interest:{market}"
        cached = await cache_get(cache_key)
        if cached:
            return [RankItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/ranking/top-interest-stock",
            tr_id="FHPST01800000",
            params={
                "FID_COND_MRKT_DIV_CODE": market,
                "FID_COND_SCR_DIV_CODE": "20180",
                "FID_INPUT_ISCD": "0000",
                "FID_INPUT_ISCD_2": "000000",
                "FID_DIV_CLS_CODE": "0",
                "FID_TRGT_CLS_CODE": "0",
                "FID_TRGT_EXLS_CLS_CODE": "0",
                "FID_INPUT_PRICE_1": "0",
                "FID_INPUT_PRICE_2": "0",
                "FID_VOL_CNT": "0",
                "FID_INPUT_CNT_1": "1",
            },
            db=db,
        )
        items = _parse_rank_items(data.get("output", []))
        await cache_set(cache_key, [i.model_dump() for i in items], 10)
        return items

    # ---- 신고가/신저가 근접 ----
    async def get_near_highlow(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
        sort: str = "1",  # 1=신고가, 2=신저가
    ) -> list[RankItem]:
        cache_key = f"kis:ranking:highlow:{market}:{sort}"
        cached = await cache_get(cache_key)
        if cached:
            return [RankItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/ranking/near-new-highlow",
            tr_id="FHPST01870000",
            params={
                "FID_COND_MRKT_DIV_CODE": market,
                "FID_COND_SCR_DIV_CODE": "20187",
                "FID_INPUT_ISCD": "0000",
                "FID_RANK_SORT_CLS_CODE": sort,
                "FID_DIV_CLS_CODE": "0",
                "FID_TRGT_CLS_CODE": "111111111",
                "FID_TRGT_EXLS_CLS_CODE": "000000",
                "FID_INPUT_PRICE_1": "0",
                "FID_INPUT_PRICE_2": "0",
                "FID_VOL_CNT": "0",
            },
            db=db,
        )
        items = _parse_rank_items(data.get("output", []))
        await cache_set(cache_key, [i.model_dump() for i in items], 10)
        return items

    # ---- 종목별 투자자 매매동향 ----
    async def get_investor(
        self,
        account: KISAccount,
        symbol: str,
        db,
    ) -> list[InvestorItem]:
        cache_key = f"kis:investor:{symbol}"
        cached = await cache_get(cache_key)
        if cached:
            return [InvestorItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/inquire-investor",
            tr_id="FHKST01010900",
            params={
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": symbol,
            },
            db=db,
        )

        items: list[InvestorItem] = []
        for row in data.get("output", []):
            # 투자자 구분 코드 → 이름
            investor_cd = row.get("invr_cd", "")
            investor_name = _INVESTOR_NAMES.get(investor_cd, f"기타({investor_cd})")
            items.append(
                InvestorItem(
                    investor=investor_name,
                    buy_volume=_safe_int(row.get("prsn_ntby_qty", row.get("total_seln_qty", 0))),
                    sell_volume=_safe_int(row.get("total_seln_qty", 0)),
                    net_volume=_safe_int(row.get("prsn_ntby_qty", 0)),
                    buy_amount=_safe_int(row.get("total_shnu_amt", 0)),
                    sell_amount=_safe_int(row.get("total_seln_amt", 0)),
                    net_amount=_safe_int(row.get("prsn_ntby_amt", 0)),
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 10)
        return items

    # ---- 외국인/기관 순매수 종목 ----
    async def get_foreign_institution(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
    ) -> list[RankItem]:
        cache_key = f"kis:ranking:foreign:{market}"
        cached = await cache_get(cache_key)
        if cached:
            return [RankItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/foreign-institution-total",
            tr_id="FHPTJ04400000",
            params={
                "FID_COND_MRKT_DIV_CODE": market,
                "FID_COND_SCR_DIV_CODE": "16449",
                "FID_INPUT_ISCD": "0000",
                "FID_DIV_CLS_CODE": "0",
                "FID_RANK_SORT_CLS_CODE": "0",  # 0=외국인순매수, 1=기관순매수
                "FID_ETC_CLS_CODE": "0",
            },
            db=db,
        )
        items = _parse_rank_items(data.get("output", []))
        await cache_set(cache_key, [i.model_dump() for i in items], 10)
        return items


ranking_service = RankingService()
