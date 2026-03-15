"""Phase 7 — 배당 / 뉴스 / 종목정보 / KSD 기업정보 서비스."""

import logging
from datetime import datetime, timedelta

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


def _opt_int(val) -> int | None:
    """Convert to int, returning None only if raw value is empty/missing."""
    if val is None or (isinstance(val, str) and val.strip() == ""):
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _opt_float(val) -> float | None:
    """Convert to float, returning None only if raw value is empty/missing."""
    if val is None or (isinstance(val, str) and val.strip() == ""):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


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

        # 최근 5년 배당 조회
        now = datetime.now()
        t_dt = now.strftime("%Y%m%d")
        f_dt = (now - timedelta(days=365 * 5)).strftime("%Y%m%d")

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/ksdinfo/dividend",
            tr_id="HHKDB669102C0",
            params={
                "CTS": "",
                "GB1": "0",
                "F_DT": f_dt,
                "T_DT": t_dt,
                "SHT_CD": symbol,
                "HIGH_GB": "",
            },
            db=db,
        )

        items: list[DividendItem] = []
        # output1 (not output)
        for row in data.get("output1", data.get("output", [])):
            record_date = row.get("record_date", "").strip()
            if not record_date:
                continue
            year = record_date[:4]
            items.append(
                DividendItem(
                    year=year,
                    dps=_opt_int(row.get("per_sto_divi_amt")),
                    div_rate=_opt_float(row.get("divi_rate")),
                    ex_date=row.get("record_date", "").strip() or None,
                    pay_date=row.get("divi_pay_dt", "").strip() or None,
                    record_date=row.get("record_date", "").strip() or None,
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 3600)
        return items

    # ── 배당수익률 랭킹 ──────────────────────────────────
    # Reference: examples_llm/domestic_stock/dividend_rate/dividend_rate.py
    # Uses completely different params: CTS_AREA, GB1, UPJONG, GB2, GB3, F_DT, T_DT, GB4

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

        # Map market code to GB1: J→0 (전체), Q→3 (코스닥)
        gb1 = "0" if market == "J" else "3"

        # 최근 1년 배당 기준
        now = datetime.now()
        t_dt = now.strftime("%Y%m%d")
        f_dt = (now - timedelta(days=365)).strftime("%Y%m%d")

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/ranking/dividend-rate",
            tr_id="HHKDB13470100",
            params={
                "CTS_AREA": "",
                "GB1": gb1,
                "UPJONG": "0001",  # 전체
                "GB2": "0",  # 0=전체
                "GB3": "2",  # 2=현금배당
                "F_DT": f_dt,
                "T_DT": t_dt,
                "GB4": "0",  # 0=전체
            },
            db=db,
        )

        items: list[DividendRankItem] = []
        for idx, row in enumerate(data.get("output1", data.get("output", [])), 1):
            sym = row.get("mksc_shrn_iscd", row.get("sht_cd", "")).strip()
            name = row.get("hts_kor_isnm", row.get("isin_name", "")).strip()
            if not sym or not name:
                continue
            items.append(
                DividendRankItem(
                    rank=idx,
                    symbol=sym,
                    name=name,
                    div_rate=_safe_float(row.get("divi_rate", row.get("sht_divi_rate", 0))),
                    current_price=_safe_int(row.get("stck_prpr", row.get("thdt_clpr", 0))),
                    dps=_opt_int(row.get("per_sto_divi_amt")),
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 3600)
        return items

    # ── 뉴스 제목 ────────────────────────────────────────
    # Reference: examples_llm/domestic_stock/news_title/news_title.py

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
                "FID_NEWS_OFER_ENTP_CODE": "",
                "FID_COND_MRKT_CLS_CODE": "",
                "FID_INPUT_ISCD": symbol,
                "FID_TITL_CNTT": "",
                "FID_INPUT_DATE_1": "",
                "FID_INPUT_HOUR_1": "",
                "FID_RANK_SORT_CLS_CODE": "",
                "FID_INPUT_SRNO": "",
            },
            db=db,
        )

        items: list[NewsItem] = []
        # output1 (not output)
        output = data.get("output1", data.get("output", []))
        if isinstance(output, list):
            for row in output:
                title = row.get("hts_pbnt_titl_cntt", "").strip()
                if not title:
                    # fallback field names
                    title = row.get("news_titl", row.get("titl", "")).strip()
                if not title:
                    continue
                date = row.get("data_dt", "").strip()
                time = row.get("data_tm", "").strip()
                items.append(
                    NewsItem(
                        date=date,
                        time=time,
                        title=title,
                        source=row.get("dorg", row.get("news_ofi_name", "")).strip() or None,
                        article_id=row.get("cntt_usiq_srno", row.get("news_id", "")).strip() or None,
                    )
                )
        await cache_set(cache_key, [i.model_dump() for i in items], 60)
        return items

    # ── 종목 기본정보 ────────────────────────────────────
    # Reference: examples_llm/domestic_stock/search_info/search_info.py
    # Uses lowercase params: pdno, prdt_type_cd

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
                "PRDT_TYPE_CD": "300",
            },
            db=db,
        )

        output = data.get("output", {})
        if isinstance(output, list) and len(output) > 0:
            output = output[0]
        elif isinstance(output, list):
            output = {}

        logger.info("Stock info keys for %s: %s", symbol, list(output.keys())[:20] if output else "empty")

        # 필드명은 KIS 응답에 따라 다양할 수 있음 — 여러 후보 시도
        info = StockInfoDetail(
            symbol=symbol,
            name=(
                output.get("prdt_abrv_name", "")
                or output.get("prdt_name", "")
                or output.get("prdt_eng_name", "")
            ).strip(),
            market=(
                output.get("rprs_mrkt_kor_name", "")
                or output.get("std_pdno", "")
            ).strip(),
            sector=output.get("std_idst_clsf_cd_name", "").strip() or None,
            listing_date=(
                output.get("lstg_dt", "")
                or output.get("scts_mket_lstg_dt", "")
                or output.get("frst_erlm_dt", "")
                or output.get("sale_strt_dt", "")
            ).strip() or None,
            face_value=_opt_int(output.get("papr")),
            shares_outstanding=_opt_int(output.get("lstg_stqt")),
            capital=_opt_int(output.get("cpfn")),
        )
        await cache_set(cache_key, info.model_dump(), 86400)
        return info


corporate_service = CorporateService()
