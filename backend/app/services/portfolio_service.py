"""Portfolio service — account balance & holdings via KIS API."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kis_account import KISAccount
from app.schemas.portfolio import AccountBalance, Holding
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


def _tr_id(base: str, environment: str) -> str:
    if environment == "paper":
        return "V" + base[1:]
    return base


class PortfolioService:

    async def get_holdings(
        self,
        account: KISAccount,
        db: AsyncSession,
    ) -> list[Holding]:
        """Get list of holdings with live prices from KIS."""
        cache_key = f"kis:holdings:{account.id}"
        cached = await cache_get(cache_key)
        if cached:
            return [Holding(**h) for h in cached]

        tr_id = _tr_id("TTTC8434R", account.environment)

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/trading/inquire-balance",
            tr_id=tr_id,
            params={
                "CANO": account.account_number,
                "ACNT_PRDT_CD": account.product_code,
                "AFHR_FLPR_YN": "N",
                "OFL_YN": "",
                "INQR_DVSN": "02",
                "UNPR_DVSN": "01",
                "FUND_STTL_ICLD_YN": "N",
                "FNCG_AMT_AUTO_RDPT_YN": "N",
                "PRCS_DVSN": "01",
                "CTX_AREA_FK100": "",
                "CTX_AREA_NK100": "",
            },
            db=db,
        )

        holdings = []
        for item in data.get("output1", []):
            qty = _safe_int(item.get("hldg_qty"))
            if qty <= 0:
                continue

            holdings.append(Holding(
                symbol=item.get("pdno", ""),
                name=item.get("prdt_name", ""),
                quantity=qty,
                avg_price=_safe_int(item.get("pchs_avg_pric")),
                current_price=_safe_int(item.get("prpr")),
                value=_safe_int(item.get("evlu_amt")),
                pnl=_safe_int(item.get("evlu_pfls_amt")),
                pnl_rate=_safe_float(item.get("evlu_pfls_rt")),
            ))

        await cache_set(cache_key, [h.model_dump() for h in holdings], 10)
        return holdings

    async def get_balance(
        self,
        account: KISAccount,
        db: AsyncSession,
    ) -> AccountBalance:
        """Get account balance summary from KIS."""
        cache_key = f"kis:balance:{account.id}"
        cached = await cache_get(cache_key)
        if cached:
            return AccountBalance(**cached)

        tr_id = _tr_id("TTTC8434R", account.environment)

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/trading/inquire-balance",
            tr_id=tr_id,
            params={
                "CANO": account.account_number,
                "ACNT_PRDT_CD": account.product_code,
                "AFHR_FLPR_YN": "N",
                "OFL_YN": "",
                "INQR_DVSN": "02",
                "UNPR_DVSN": "01",
                "FUND_STTL_ICLD_YN": "N",
                "FNCG_AMT_AUTO_RDPT_YN": "N",
                "PRCS_DVSN": "01",
                "CTX_AREA_FK100": "",
                "CTX_AREA_NK100": "",
            },
            db=db,
        )

        # output2 is a list with one summary item
        summary = data.get("output2", [{}])
        if isinstance(summary, list) and summary:
            out = summary[0]
        else:
            out = summary if isinstance(summary, dict) else {}

        # Count holdings from output1
        holding_count = sum(
            1 for item in data.get("output1", [])
            if _safe_int(item.get("hldg_qty")) > 0
        )

        stock_value = _safe_int(out.get("evlu_amt_smtl_amt"))
        cash = _safe_int(out.get("dnca_tot_amt"))
        total_value = _safe_int(out.get("tot_evlu_amt")) or (stock_value + cash)
        total_pnl = _safe_int(out.get("evlu_pfls_smtl_amt"))

        # Calculate P&L rate
        purchase_total = _safe_int(out.get("pchs_amt_smtl_amt"))
        if purchase_total > 0:
            total_pnl_rate = round((total_pnl / purchase_total) * 100, 2)
        else:
            total_pnl_rate = 0.0

        balance = AccountBalance(
            total_value=total_value,
            cash=cash,
            stock_value=stock_value,
            total_pnl=total_pnl,
            total_pnl_rate=total_pnl_rate,
            holding_count=holding_count,
        )

        await cache_set(cache_key, balance.model_dump(), 10)
        return balance


portfolio_service = PortfolioService()
