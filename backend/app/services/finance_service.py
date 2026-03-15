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

        items: list[IncomeStatementItem] = []
        for row in data.get("output", []):
            stac_yymm = row.get("stac_yymm", "").strip()
            if not stac_yymm:
                continue
            items.append(
                IncomeStatementItem(
                    period=stac_yymm,
                    revenue=_safe_int(row.get("sale_account")) or None,
                    operating_profit=_safe_int(row.get("bsop_prti")) or None,
                    net_income=_safe_int(row.get("thtr_ntin")) or None,
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

        items: list[BalanceSheetItem] = []
        for row in data.get("output", []):
            stac_yymm = row.get("stac_yymm", "").strip()
            if not stac_yymm:
                continue
            items.append(
                BalanceSheetItem(
                    period=stac_yymm,
                    total_assets=_safe_int(row.get("total_aset")) or None,
                    total_liabilities=_safe_int(row.get("total_lblt")) or None,
                    total_equity=_safe_int(row.get("total_cptl")) or None,
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 3600)
        return items

    # ── 재무비율 ──────────────────────────────────────────

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

        items: list[FinancialRatioItem] = []
        for row in data.get("output", []):
            stac_yymm = row.get("stac_yymm", "").strip()
            if not stac_yymm:
                continue
            items.append(
                FinancialRatioItem(
                    period=stac_yymm,
                    roe=_safe_float(row.get("roe_val")) or None,
                    roa=_safe_float(row.get("roa_val")) or None,
                    per=_safe_float(row.get("per")) or None,
                    pbr=_safe_float(row.get("pbr")) or None,
                    eps=_safe_int(row.get("eps")) or None,
                    bps=_safe_int(row.get("bps")) or None,
                    debt_ratio=_safe_float(row.get("lblt_rate")) or None,
                    reserve_ratio=_safe_float(row.get("rsrv_rate")) or None,
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 3600)
        return items

    # ── 실적추정치 ────────────────────────────────────────

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
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": symbol,
            },
            db=db,
        )

        items: list[EstimateItem] = []
        for row in data.get("output", []):
            stac_yymm = row.get("stac_yymm", "").strip()
            if not stac_yymm:
                continue
            items.append(
                EstimateItem(
                    period=stac_yymm,
                    revenue_est=_safe_int(row.get("sale_account")) or None,
                    op_profit_est=_safe_int(row.get("bsop_prti")) or None,
                    net_income_est=_safe_int(row.get("thtr_ntin")) or None,
                    eps_est=_safe_int(row.get("eps")) or None,
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
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_COND_SCR_DIV_CODE": "16633",
                "FID_INPUT_ISCD": symbol,
                "FID_INPUT_DATE_1": date_from,
                "FID_INPUT_DATE_2": date_to,
            },
            db=db,
        )

        items: list[InvestOpinionItem] = []
        for row in data.get("output", []):
            date = row.get("stck_bsop_date", "").strip()
            if not date:
                continue
            items.append(
                InvestOpinionItem(
                    date=date,
                    firm=row.get("mbcr_name", "").strip(),
                    opinion=row.get("invt_opnn", "").strip(),
                    target_price=_safe_int(row.get("hts_goal_prc")) or None,
                    change=row.get("invt_opnn_cls_code", "").strip() or None,
                )
            )
        await cache_set(cache_key, [i.model_dump() for i in items], 1800)
        return items


finance_service = FinanceService()
