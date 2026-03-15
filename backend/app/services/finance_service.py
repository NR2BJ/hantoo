"""Phase 7 — 재무제표 / 실적추정 / 투자의견 서비스."""

import logging
from datetime import datetime, timedelta

from app.models.kis_account import KISAccount
from app.schemas.analysis import (
    BalanceSheetItem,
    EstimateItem,
    FinancialRatioItem,
    IncomeStatementItem,
    InvestOpinionItem,
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


# 투자의견 코드 → 한글 매핑
_OPINION_CODE_MAP = {
    "1": "강력매수",
    "2": "매수",
    "3": "중립",
    "4": "매도",
    "5": "강력매도",
}


def _opinion_change(cur_code: str, prev_code: str) -> str:
    """Compare opinion codes to determine change direction."""
    if not cur_code or not prev_code:
        return "신규"
    try:
        c, p = int(cur_code), int(prev_code)
        if c < p:
            return "상향"
        elif c > p:
            return "하향"
        return "유지"
    except (ValueError, TypeError):
        return "유지"


class FinanceService:
    """Financial statements, estimates, and investment opinions via KIS API."""

    # ── 손익계산서 ────────────────────────────────────────

    async def get_income_statement(
        self,
        account: KISAccount,
        symbol: str,
        db,
        *,
        period: str = "A",  # A=연간, Q=분기
    ) -> list[IncomeStatementItem]:
        cache_key = f"kis:finance:income:{symbol}:{period}"
        cached = await cache_get(cache_key)
        if cached:
            return [IncomeStatementItem(**item) for item in cached]

        # KIS: FID_DIV_CLS_CODE "0"=연간, "1"=분기
        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/finance/income-statement",
            tr_id="FHKST66430200",
            params={
                "FID_DIV_CLS_CODE": "0" if period == "A" else "1",
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": symbol,
            },
            db=db,
        )

        # 디버그: 응답 구조 로깅
        logger.info("[income_statement] response keys: %s", list(data.keys()))
        output = data.get("output", [])
        if output:
            logger.info("[income_statement] first row keys: %s", list(output[0].keys()) if isinstance(output, list) and output else "empty")
            logger.info("[income_statement] first row sample: %s", {k: v for k, v in (output[0].items() if isinstance(output, list) and output else [])})

        items: list[IncomeStatementItem] = []
        for row in output:
            stac_yymm = row.get("stac_yymm", "").strip()
            if not stac_yymm:
                continue
            items.append(
                IncomeStatementItem(
                    period=stac_yymm,
                    revenue=_opt_int(row.get("sale_account")),
                    operating_profit=_opt_int(row.get("bsop_prti")),
                    net_income=_opt_int(row.get("thtr_ntin")),
                    eps=None,  # EPS는 재무비율 API에서 제공
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 3600)
        return items

    # ── 재무상태표 ────────────────────────────────────────

    async def get_balance_sheet(
        self,
        account: KISAccount,
        symbol: str,
        db,
        *,
        period: str = "A",
    ) -> list[BalanceSheetItem]:
        cache_key = f"kis:finance:balance:{symbol}:{period}"
        cached = await cache_get(cache_key)
        if cached:
            return [BalanceSheetItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/finance/balance-sheet",
            tr_id="FHKST66430100",
            params={
                "FID_DIV_CLS_CODE": "0" if period == "A" else "1",
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": symbol,
            },
            db=db,
        )

        # 디버그
        logger.info("[balance_sheet] response keys: %s", list(data.keys()))
        output = data.get("output", [])
        if output:
            logger.info("[balance_sheet] first row keys: %s", list(output[0].keys()) if isinstance(output, list) and output else "empty")

        items: list[BalanceSheetItem] = []
        for row in output:
            stac_yymm = row.get("stac_yymm", "").strip()
            if not stac_yymm:
                continue
            items.append(
                BalanceSheetItem(
                    period=stac_yymm,
                    total_assets=_opt_int(row.get("total_aset")),
                    total_liabilities=_opt_int(row.get("total_lblt")),
                    total_equity=_opt_int(row.get("total_cptl")),
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 3600)
        return items

    # ── 재무비율 ──────────────────────────────────────────
    # Note: KIS financial-ratio API provides: stac_yymm, grs, bsop_prfi_inrt,
    # ntin_inrt, roe_val, eps, sps, bps, rsrv_rate, lblt_rate
    # PER/PBR/ROA are NOT in this API (they're in the stock quote).

    async def get_financial_ratio(
        self,
        account: KISAccount,
        symbol: str,
        db,
        *,
        period: str = "A",
    ) -> list[FinancialRatioItem]:
        cache_key = f"kis:finance:ratio:{symbol}:{period}"
        cached = await cache_get(cache_key)
        if cached:
            return [FinancialRatioItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/finance/financial-ratio",
            tr_id="FHKST66430300",
            params={
                "FID_DIV_CLS_CODE": "0" if period == "A" else "1",
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": symbol,
            },
            db=db,
        )

        # 디버그
        logger.info("[financial_ratio] response keys: %s", list(data.keys()))
        output = data.get("output", [])
        if output:
            logger.info("[financial_ratio] first row keys: %s", list(output[0].keys()) if isinstance(output, list) and output else "empty")
            logger.info("[financial_ratio] first row data: %s", dict(output[0]) if isinstance(output, list) and output else {})

        items: list[FinancialRatioItem] = []
        for row in output:
            stac_yymm = row.get("stac_yymm", "").strip()
            if not stac_yymm:
                continue
            items.append(
                FinancialRatioItem(
                    period=stac_yymm,
                    roe=_opt_float(row.get("roe_val")),
                    # roa_val, per, pbr are NOT documented in this API
                    # Try anyway in case API returns extra fields
                    roa=_opt_float(row.get("roa_val")),
                    per=_opt_float(row.get("per")),
                    pbr=_opt_float(row.get("pbr")),
                    eps=_opt_int(row.get("eps")),
                    bps=_opt_int(row.get("bps")),
                    debt_ratio=_opt_float(row.get("lblt_rate")),
                    reserve_ratio=_opt_float(row.get("rsrv_rate")),
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 3600)
        return items

    # ── 실적추정치 ────────────────────────────────────────
    # Reference: examples_llm/domestic_stock/estimate_perform/estimate_perform.py
    # Returns output1~output4 with generic fields: sht_cd, item_kor_nm, dt, data1~data5
    # NOT the same fields as income-statement.

    async def get_estimate(
        self,
        account: KISAccount,
        symbol: str,
        db,
    ) -> list[EstimateItem]:
        cache_key = f"kis:finance:estimate:{symbol}"
        cached = await cache_get(cache_key)
        if cached:
            return [EstimateItem(**item) for item in cached]

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/estimate-perform",
            tr_id="HHKST668300C0",
            params={
                "SHT_CD": symbol,
            },
            db=db,
        )

        # 디버그: 실제 응답 구조 파악
        logger.info("[estimate] response keys: %s", list(data.keys()))
        for key in ["output", "output1", "output2", "output3", "output4"]:
            val = data.get(key)
            if val:
                if isinstance(val, list) and val:
                    logger.info("[estimate] %s has %d rows, first row keys: %s", key, len(val), list(val[0].keys()))
                    logger.info("[estimate] %s first row data: %s", key, dict(val[0]))
                elif isinstance(val, dict):
                    logger.info("[estimate] %s is dict with keys: %s", key, list(val.keys()))

        items: list[EstimateItem] = []

        # output1을 먼저 시도 — 이 API는 output1~4를 반환
        output = data.get("output1", data.get("output", []))
        if not isinstance(output, list):
            output = [output] if output else []

        for row in output:
            # 두 가지 필드 형식 시도:
            # Format A (income-statement style): stac_yymm, sale_account, bsop_prti, thtr_ntin
            # Format B (estimate-perform style): dt, data1~data5
            period = (
                row.get("stac_yymm", "").strip()
                or row.get("dt", "").strip()
            )
            if not period:
                continue

            # Format A 시도
            revenue = _opt_int(row.get("sale_account"))
            op_profit = _opt_int(row.get("bsop_prti"))
            net_income = _opt_int(row.get("thtr_ntin"))
            eps = _opt_int(row.get("eps"))

            # Format B fallback (data1~data5 순서는 API 마다 다를 수 있음)
            if revenue is None and op_profit is None and net_income is None:
                revenue = _opt_int(row.get("data1"))
                op_profit = _opt_int(row.get("data2"))
                net_income = _opt_int(row.get("data3"))
                eps = _opt_int(row.get("data4"))

            items.append(
                EstimateItem(
                    period=period,
                    revenue_est=revenue,
                    op_profit_est=op_profit,
                    net_income_est=net_income,
                    eps_est=eps,
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 1800)
        return items

    # ── 투자의견 / 컨센서스 ───────────────────────────────

    async def get_invest_opinion(
        self,
        account: KISAccount,
        symbol: str,
        db,
    ) -> list[InvestOpinionItem]:
        cache_key = f"kis:finance:opinion:{symbol}"
        cached = await cache_get(cache_key)
        if cached:
            return [InvestOpinionItem(**item) for item in cached]

        # 최근 6개월 투자의견 조회
        now = datetime.now()
        date_to = now.strftime("%Y%m%d")
        date_from = (now - timedelta(days=180)).strftime("%Y%m%d")

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/quotations/invest-opinion",
            tr_id="FHKST663300C0",
            params={
                "fid_cond_mrkt_div_code": "J",
                "fid_cond_scr_div_code": "16633",
                "fid_input_iscd": symbol,
                "fid_input_date_1": date_from,
                "fid_input_date_2": date_to,
            },
            db=db,
        )

        # 디버그
        logger.info("[invest_opinion] response keys: %s", list(data.keys()))
        output = data.get("output", [])
        if output:
            logger.info("[invest_opinion] first row keys: %s", list(output[0].keys()) if isinstance(output, list) and output else "empty")
            logger.info("[invest_opinion] first row: %s", dict(output[0]) if isinstance(output, list) and output else {})

        items: list[InvestOpinionItem] = []
        for row in output:
            date = row.get("stck_bsop_date", "").strip()
            if not date:
                continue
            # 투자의견 코드를 한글로 변환
            cur_code = row.get("invt_opnn_cls_code", "").strip()
            prev_code = row.get("rgbf_invt_opnn_cls_code", "").strip()
            opinion_text = _OPINION_CODE_MAP.get(cur_code, "")
            if not opinion_text:
                opinion_text = row.get("invt_opnn", "").strip()
            items.append(
                InvestOpinionItem(
                    date=date,
                    firm=row.get("mbcr_name", "").strip(),
                    opinion=opinion_text,
                    target_price=_opt_int(row.get("hts_goal_prc")),
                    change=_opinion_change(cur_code, prev_code),
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 1800)
        return items


finance_service = FinanceService()
