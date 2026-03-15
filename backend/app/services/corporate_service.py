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
        cache_key = f"kis:{account.environment}:corp:dividend:{symbol}"
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

        # 디버그
        logger.info("[dividend] response keys: %s", list(data.keys()))
        for key in ["output", "output1"]:
            val = data.get(key)
            if val and isinstance(val, list) and val:
                logger.info("[dividend] %s has %d rows, first row keys: %s", key, len(val), list(val[0].keys()))
                logger.info("[dividend] %s first row: %s", key, dict(val[0]))

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
    # COLUMN_MAPPING: rank, sht_cd, record_date, per_sto_divi_amt, divi_rate, divi_kind
    # Note: no stock name or current price documented — using fallbacks

    async def get_dividend_rate_ranking(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
    ) -> list[DividendRankItem]:
        cache_key = f"kis:{account.environment}:corp:divrate:{market}"
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

        # 디버그
        logger.info("[dividend_rate] response keys: %s", list(data.keys()))
        for key in ["output", "output1"]:
            val = data.get(key)
            if val and isinstance(val, list) and val:
                logger.info("[dividend_rate] %s has %d rows, first row keys: %s", key, len(val), list(val[0].keys()))
                logger.info("[dividend_rate] %s first row: %s", key, dict(val[0]))

        items: list[DividendRankItem] = []
        output = data.get("output1", data.get("output", []))
        if not isinstance(output, list):
            output = []

        for idx, row in enumerate(output, 1):
            # Try multiple field name patterns for symbol
            sym = (
                row.get("mksc_shrn_iscd", "").strip()
                or row.get("sht_cd", "").strip()
            )
            # Try multiple field name patterns for name
            name = (
                row.get("hts_kor_isnm", "").strip()
                or row.get("isin_name", "").strip()
                or row.get("prdt_abrv_name", "").strip()
            )
            if not sym:
                continue
            # If no name, use symbol as fallback
            if not name:
                name = sym

            items.append(
                DividendRankItem(
                    rank=_safe_int(row.get("rank", idx)),
                    symbol=sym,
                    name=name,
                    div_rate=_safe_float(row.get("divi_rate", row.get("sht_divi_rate", 0))),
                    current_price=_safe_int(
                        row.get("stck_prpr", row.get("thdt_clpr", 0))
                    ),
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
        cache_key = f"kis:{account.environment}:corp:news:{symbol}"
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

        # 디버그
        logger.info("[news] response keys: %s", list(data.keys()))
        for key in ["output", "output1"]:
            val = data.get(key)
            if val and isinstance(val, list) and val:
                logger.info("[news] %s has %d rows, first row keys: %s", key, len(val), list(val[0].keys()))

        items: list[NewsItem] = []
        output = data.get("output1", data.get("output", []))
        if isinstance(output, list):
            for row in output:
                title = row.get("hts_pbnt_titl_cntt", "").strip()
                if not title:
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
    # Primary: search-stock-info (CTPF1002R) — 91+ fields
    # Fallback: search-info (CTPF1604R) — 12 fields only
    # Reference: examples_llm/domestic_stock/search_stock_info/search_stock_info.py

    async def get_stock_info(
        self,
        account: KISAccount,
        symbol: str,
        db,
    ) -> StockInfoDetail:
        cache_key = f"kis:{account.environment}:corp:info:{symbol}"
        cached = await cache_get(cache_key)
        if cached:
            return StockInfoDetail(**cached)

        data: dict = {}
        # Try CTPF1002R (search-stock-info) first — has many more fields
        try:
            data = await kis_client.request(
                account,
                "GET",
                "/uapi/domestic-stock/v1/quotations/search-stock-info",
                tr_id="CTPF1002R",
                params={
                    "PRDT_TYPE_CD": "300",
                    "PDNO": symbol,
                },
                db=db,
            )
        except Exception as e:
            logger.warning("[stock_info] CTPF1002R failed for %s: %s, trying CTPF1604R", symbol, e)
            # Fallback to CTPF1604R
            try:
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
            except Exception as e2:
                logger.warning("[stock_info] CTPF1604R also failed for %s: %s — returning minimal info", symbol, e2)
                # VTS server may not support these APIs — return minimal data
                return StockInfoDetail(
                    symbol=symbol, name=symbol, market="", sector=None,
                    listing_date=None, face_value=None,
                    shares_outstanding=None, capital=None,
                )

        output = data.get("output", {})
        if isinstance(output, list) and len(output) > 0:
            output = output[0]
        elif isinstance(output, list):
            output = {}

        logger.info("[stock_info] keys for %s: %s", symbol, list(output.keys())[:30] if output else "empty")
        logger.info("[stock_info] sample data: %s", {k: output.get(k) for k in [
            "prdt_abrv_name", "prdt_name", "prdt_eng_name", "mket_id_cd",
            "lstg_stqt", "papr", "cpta", "std_idst_clsf_cd_name",
            "scts_mket_lstg_dt", "kosdaq_mket_lstg_dt",
            "rprs_mrkt_kor_name", "std_pdno", "cpfn",
            "idx_bztp_lcls_cd_name", "idx_bztp_mcls_cd_name",
        ] if k in (output or {})})

        # Build info from available fields
        name = (
            output.get("prdt_abrv_name", "")
            or output.get("prdt_name", "")
            or output.get("prdt_eng_name", "")
        )
        if isinstance(name, str):
            name = name.strip()

        # Market: CTPF1002R has mket_id_cd, CTPF1604R has rprs_mrkt_kor_name
        market_code = output.get("mket_id_cd", "").strip()
        market_name = output.get("rprs_mrkt_kor_name", "").strip()
        if market_code == "STK":
            market_str = "KOSPI"
        elif market_code == "KSQ":
            market_str = "KOSDAQ"
        elif market_name:
            market_str = market_name
        elif output.get("std_pdno", ""):
            market_str = output.get("std_pdno", "").strip()
        else:
            market_str = ""

        # Sector: multiple fallback fields
        sector = (
            output.get("idx_bztp_mcls_cd_name", "").strip()
            or output.get("idx_bztp_lcls_cd_name", "").strip()
            or output.get("std_idst_clsf_cd_name", "").strip()
        ) or None

        # Listing date: check multiple fields
        listing_date = (
            output.get("scts_mket_lstg_dt", "").strip()
            or output.get("kosdaq_mket_lstg_dt", "").strip()
            or output.get("lstg_dt", "").strip()
            or output.get("frst_erlm_dt", "").strip()
            or output.get("sale_strt_dt", "").strip()
        ) or None

        info = StockInfoDetail(
            symbol=symbol,
            name=name,
            market=market_str,
            sector=sector,
            listing_date=listing_date,
            face_value=_opt_int(output.get("papr")),
            shares_outstanding=_opt_int(output.get("lstg_stqt")),
            capital=_opt_int(output.get("cpta", output.get("cpfn"))),
        )
        await cache_set(cache_key, info.model_dump(), 86400)
        return info


corporate_service = CorporateService()
