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
        return int(float(val))
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
# Service
# ---------------------------------------------------------------------------

class RankingService:
    """Ranking & market info queries via KIS API."""

    # ---- 거래량 순위 ----
    # Valid market codes: J, NX, UN, W (Q not supported)
    async def get_volume_rank(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
    ) -> list[RankItem]:
        if market not in ("J", "NX", "UN", "W"):
            logger.info("volume-rank: market=%s not supported, returning empty", market)
            return []
        cache_key = f"kis:{account.environment}:ranking:volume:{market}"
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
    # Docs say J, W, Q valid but Q returns error in practice
    async def get_fluctuation(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
        sort: str = "1",  # 1=상승, 2=하락
    ) -> list[RankItem]:
        if market not in ("J", "W"):
            logger.info("fluctuation: market=%s not supported, returning empty", market)
            return []
        cache_key = f"kis:{account.environment}:ranking:fluctuation:{market}:{sort}"
        cached = await cache_get(cache_key)
        if cached:
            return [RankItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/ranking/fluctuation",
            tr_id="FHPST01700000",
            params={
                "fid_cond_mrkt_div_code": market,
                "fid_cond_scr_div_code": "20170",
                "fid_input_iscd": "0000",
                "fid_rank_sort_cls_code": sort,
                "fid_input_cnt_1": "0",
                "fid_prc_cls_code": "0",
                "fid_input_price_1": "0",
                "fid_input_price_2": "0",
                "fid_vol_cnt": "0",
                "fid_trgt_cls_code": "111111111",
                "fid_trgt_exls_cls_code": "0000000000",
                "fid_div_cls_code": "0",
                "fid_rsfl_rate1": "",
                "fid_rsfl_rate2": "",
            },
            db=db,
        )
        items = _parse_rank_items(data.get("output", []))
        await cache_set(cache_key, [i.model_dump() for i in items], 10)
        return items

    # ---- 시가총액 순위 ----
    # Valid market codes: J only
    async def get_market_cap(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
    ) -> list[RankItem]:
        if market != "J":
            logger.info("market-cap: market=%s not supported (J only), returning empty", market)
            return []
        cache_key = f"kis:{account.environment}:ranking:marketcap:{market}"
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
    # Valid market codes: J only
    async def get_top_interest(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
    ) -> list[RankItem]:
        if market != "J":
            logger.info("top-interest: market=%s not supported (J only), returning empty", market)
            return []
        cache_key = f"kis:{account.environment}:ranking:interest:{market}"
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
    # Valid market codes: J only
    async def get_near_highlow(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
        sort: str = "1",  # 1=신고가, 2=신저가
    ) -> list[RankItem]:
        if market != "J":
            logger.info("near-highlow: market=%s not supported (J only), returning empty", market)
            return []
        cache_key = f"kis:{account.environment}:ranking:highlow:{market}:{sort}"
        cached = await cache_get(cache_key)
        if cached:
            return [RankItem(**item) for item in cached]

        # Map frontend sort to KIS fid_prc_cls_code: 1→"0" (신고), 2→"1" (신저)
        prc_cls_code = "0" if sort == "1" else "1"

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/ranking/near-new-highlow",
            tr_id="FHPST01870000",
            params={
                "fid_cond_mrkt_div_code": market,
                "fid_cond_scr_div_code": "20187",
                "fid_input_iscd": "0000",
                "fid_prc_cls_code": prc_cls_code,
                "fid_div_cls_code": "0",
                "fid_trgt_cls_code": "0",
                "fid_trgt_exls_cls_code": "0",
                "fid_input_cnt_1": "0",
                "fid_input_cnt_2": "100",
                "fid_aply_rang_vol": "0",
                "fid_aply_rang_prc_1": "0",
                "fid_aply_rang_prc_2": "0",
            },
            db=db,
        )
        items = _parse_rank_items(data.get("output", []))
        await cache_set(cache_key, [i.model_dump() for i in items], 10)
        return items

    # ---- 종목별 투자자 매매동향 ----
    # FHKST01010900: 날짜별 시계열 — 한 행에 개인/외인/기관 데이터가 모두 포함
    # Reference: examples_llm/domestic_stock/inquire_investor/inquire_investor.py
    async def get_investor(
        self,
        account: KISAccount,
        symbol: str,
        db,
    ) -> list[InvestorItem]:
        cache_key = f"kis:{account.environment}:investor:{symbol}"
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

        output = data.get("output", [])
        if not output:
            return []

        # 가장 최근 날짜 데이터를 개인/외인/기관 3행으로 변환
        row = output[0]
        logger.info("Investor data keys for %s: %s", symbol, list(row.keys())[:20])

        items: list[InvestorItem] = [
            InvestorItem(
                investor="개인",
                buy_volume=_safe_int(row.get("prsn_shnu_vol", 0)),
                sell_volume=_safe_int(row.get("prsn_seln_vol", 0)),
                net_volume=_safe_int(row.get("prsn_ntby_qty", 0)),
                buy_amount=_safe_int(row.get("prsn_shnu_tr_pbmn", 0)),
                sell_amount=_safe_int(row.get("prsn_seln_tr_pbmn", 0)),
                net_amount=_safe_int(row.get("prsn_ntby_tr_pbmn", 0)),
            ),
            InvestorItem(
                investor="외국인",
                buy_volume=_safe_int(row.get("frgn_shnu_vol", 0)),
                sell_volume=_safe_int(row.get("frgn_seln_vol", 0)),
                net_volume=_safe_int(row.get("frgn_ntby_qty", 0)),
                buy_amount=_safe_int(row.get("frgn_shnu_tr_pbmn", 0)),
                sell_amount=_safe_int(row.get("frgn_seln_tr_pbmn", 0)),
                net_amount=_safe_int(row.get("frgn_ntby_tr_pbmn", 0)),
            ),
            InvestorItem(
                investor="기관",
                buy_volume=_safe_int(row.get("orgn_shnu_vol", 0)),
                sell_volume=_safe_int(row.get("orgn_seln_vol", 0)),
                net_volume=_safe_int(row.get("orgn_ntby_qty", 0)),
                buy_amount=_safe_int(row.get("orgn_shnu_tr_pbmn", 0)),
                sell_amount=_safe_int(row.get("orgn_seln_tr_pbmn", 0)),
                net_amount=_safe_int(row.get("orgn_ntby_tr_pbmn", 0)),
            ),
        ]

        await cache_set(cache_key, [i.model_dump() for i in items], 10)
        return items

    # ---- 외국인/기관 순매수 종목 ----
    # Reference: examples_llm/domestic_stock/foreign_institution_total/foreign_institution_total.py
    # FID_COND_MRKT_DIV_CODE should be "V" (not "J")
    async def get_foreign_institution(
        self,
        account: KISAccount,
        db,
        *,
        market: str = "J",
    ) -> list[RankItem]:
        cache_key = f"kis:{account.environment}:ranking:foreign:{market}"
        cached = await cache_get(cache_key)
        if cached:
            return [RankItem(**item) for item in cached]

        # Map market code: J→V (전체), Q→Q is not valid for this API
        # The API uses V for all markets
        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/foreign-institution-total",
            tr_id="FHPTJ04400000",
            params={
                "FID_COND_MRKT_DIV_CODE": "V",
                "FID_COND_SCR_DIV_CODE": "16449",
                "FID_INPUT_ISCD": "0000" if market == "J" else "1001",
                "FID_DIV_CLS_CODE": "0",
                "FID_RANK_SORT_CLS_CODE": "0",  # 0=순매수상위, 1=순매도상위
                "FID_ETC_CLS_CODE": "0",  # 0=전체, 1=외국인, 2=기관계
            },
            db=db,
        )
        items = _parse_rank_items(data.get("output", []))
        await cache_set(cache_key, [i.model_dump() for i in items], 10)
        return items


ranking_service = RankingService()
