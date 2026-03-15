"""Phase 7 — 배당 / 뉴스 / 종목정보 / KSD 기업정보 서비스."""

import logging

from app.models.kis_account import KISAccount
from app.schemas.analysis import (
    DividendItem,
    DividendRankItem,
    NewsItem,
    StockInfoDetail,
)
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


class CorporateService:
    """Dividend, news, stock info, and KSD corporate events via KIS API."""

    # ── 배당정보 ──────────────────────────────────────────

    async def get_dividend(
        self,
        account: KISAccount,
        symbol: str,
        db,
    ) -> list[DividendItem]:
        cache_key = f"kis:corp:dividend:{symbol}"
        cached = await cache_get(cache_key)
        if cached:
            return [DividendItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/ksdinfo/dividend",
            tr_id="HHKDB669102C0",
            params={
                "COND_MRKT_DIV_CODE": "J",
                "INPUT_ISCD": symbol,
                "SHT_CD": symbol,
            },
            db=db,
        )

        items: list[DividendItem] = []
        for row in data.get("output", []):
            year = row.get("record_date", "")[:4]
            if not year:
                continue
            items.append(
                DividendItem(
                    year=year,
                    dps=_safe_int(row.get("per_sto_divi_amt")) or None,
                    div_rate=_safe_float(row.get("divi_rate")) or None,
                    ex_date=row.get("divi_pay_dt", "").strip() or None,
                    pay_date=row.get("divi_pay_dt", "").strip() or None,
                    record_date=row.get("record_date", "").strip() or None,
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 3600)
        return items

    # ── 배당수익률 랭킹 ──────────────────────────────────

    async def get_dividend_rate_ranking(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
    ) -> list[DividendRankItem]:
        cache_key = f"kis:corp:divrate:{market}"
        cached = await cache_get(cache_key)
        if cached:
            return [DividendRankItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/ranking/dividend-rate",
            tr_id="HHKDB13470100",
            params={
                "FID_COND_MRKT_DIV_CODE": market,
                "FID_COND_SCR_DIV_CODE": "13470",
                "FID_INPUT_ISCD": "0000",
                "FID_DIV_CLS_CODE": "0",
                "FID_INPUT_PRICE_1": "0",
                "FID_INPUT_PRICE_2": "0",
                "FID_VOL_CNT": "0",
                "FID_TRGT_CLS_CODE": "111111111",
                "FID_TRGT_EXLS_CLS_CODE": "000000",
            },
            db=db,
        )

        items: list[DividendRankItem] = []
        for idx, row in enumerate(data.get("output", []), 1):
            symbol = row.get("mksc_shrn_iscd", "").strip()
            name = row.get("hts_kor_isnm", "").strip()
            if not symbol or not name:
                continue
            items.append(
                DividendRankItem(
                    rank=idx,
                    symbol=symbol,
                    name=name,
                    div_rate=_safe_float(row.get("divi_rate")),
                    current_price=_safe_int(row.get("stck_prpr")),
                    dps=_safe_int(row.get("per_sto_divi_amt")) or None,
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 3600)
        return items

    # ── 뉴스 제목 ────────────────────────────────────────

    async def get_news(
        self,
        account: KISAccount,
        symbol: str,
        db,
    ) -> list[NewsItem]:
        cache_key = f"kis:corp:news:{symbol}"
        cached = await cache_get(cache_key)
        if cached:
            return [NewsItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/news-title",
            tr_id="FHKST01011800",
            params={
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": symbol,
                "FID_INPUT_DATE_1": "",
                "FID_INPUT_DATE_2": "",
                "FID_INPUT_HOUR_1": "",
            },
            db=db,
        )

        items: list[NewsItem] = []
        for row in data.get("output", []):
            title = row.get("data_dt", "").strip()  # 뉴스 제목
            if not title:
                # KIS field names vary — try common alternatives
                title = row.get("news_titl", row.get("titl", "")).strip()
            date = row.get("data_dt", row.get("cntt_date", "")).strip()
            time = row.get("data_tm", row.get("cntt_time", "")).strip()
            news_title = row.get("news_titl", row.get("titl", "")).strip()
            if not news_title:
                continue
            items.append(
                NewsItem(
                    date=date,
                    time=time,
                    title=news_title,
                    source=row.get("news_ofi_name", row.get("dprt_name", "")).strip() or None,
                    article_id=row.get("news_id", row.get("cntt_sn", "")).strip() or None,
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 60)
        return items

    # ── 종목 기본정보 ────────────────────────────────────

    async def get_stock_info(
        self,
        account: KISAccount,
        symbol: str,
        db,
    ) -> StockInfoDetail:
        cache_key = f"kis:corp:info:{symbol}"
        cached = await cache_get(cache_key)
        if cached:
            return StockInfoDetail(**cached)

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/search-info",
            tr_id="CTPF1604R",
            params={
                "PDNO": symbol,
                "PRDT_TYPE_CD": "300",  # 주식
            },
            db=db,
        )

        output = data.get("output", {})
        info = StockInfoDetail(
            symbol=symbol,
            name=output.get("prdt_abrv_name", "").strip(),
            market=output.get("rprs_mrkt_kor_name", "").strip(),
            sector=output.get("std_idst_clsf_cd_name", "").strip() or None,
            listing_date=output.get("lstg_dt", "").strip() or None,
            face_value=_safe_int(output.get("papr")) or None,
            shares_outstanding=_safe_int(output.get("lstg_stqt")) or None,
            capital=_safe_int(output.get("cpfn")) or None,
        )
        await cache_set(cache_key, info.model_dump(), 86400)
        return info


corporate_service = CorporateService()
