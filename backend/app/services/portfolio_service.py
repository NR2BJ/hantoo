"""Portfolio service — account balance & holdings via KIS API."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kis_account import KISAccount
from app.schemas.portfolio import (
    AccountBalance,
    ForeignCurrencyBalance,
    Holding,
    OverseasHolding,
)
from app.services.cache import cache_get, cache_set
from app.services.kis_client import KISApiError, kis_client

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

    async def _get_holdings_account_overview(
        self,
        account: KISAccount,
        db: AsyncSession,
    ) -> list[Holding]:
        """Get holdings for non-brokerage accounts via CTRP6548R output1."""
        tr_id = _tr_id("CTRP6548R", account.environment)

        try:
            data = await kis_client.request(
                account,
                "GET",
                "/uapi/domestic-stock/v1/trading/inquire-account-balance",
                tr_id=tr_id,
                params={
                    "CANO": account.account_number,
                    "ACNT_PRDT_CD": account.product_code,
                    "INQR_DVSN_1": "",
                    "BSPR_BF_DT_APLY_YN": "",
                },
                db=db,
            )
        except Exception as e:
            logger.warning("CTRP6548R holdings query failed: %s", e)
            return []

        holdings = []
        for item in data.get("output1", []):
            qty = _safe_int(item.get("hldg_qty", item.get("cblc_qty13", 0)))
            if qty <= 0:
                continue

            holdings.append(Holding(
                symbol=item.get("pdno", ""),
                name=item.get("prdt_name", ""),
                quantity=qty,
                avg_price=_safe_int(item.get("pchs_avg_pric")),
                current_price=_safe_int(item.get("prpr", item.get("bstp_nmix_prpr", 0))),
                value=_safe_int(item.get("evlu_amt")),
                pnl=_safe_int(item.get("evlu_pfls_amt")),
                pnl_rate=_safe_float(item.get("evlu_pfls_rt")),
            ))

        return holdings

    async def get_holdings(
        self,
        account: KISAccount,
        db: AsyncSession,
    ) -> list[Holding]:
        """Get list of domestic holdings with live prices from KIS."""
        cache_key = f"kis:holdings:{account.id}"
        cached = await cache_get(cache_key)
        if cached:
            return [Holding(**h) for h in cached]

        # Non-brokerage accounts use CTRP6548R
        if account.product_code != "01":
            holdings = await self._get_holdings_account_overview(account, db)
            await cache_set(cache_key, [h.model_dump() for h in holdings], 10)
            return holdings

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

    async def get_overseas_holdings(
        self,
        account: KISAccount,
        db: AsyncSession,
    ) -> list[OverseasHolding]:
        """Get overseas stock holdings from KIS (CTRP6504R).

        Tries for all account types — gracefully returns [] on failure.
        """
        cache_key = f"kis:overseas_holdings:{account.id}"
        cached = await cache_get(cache_key)
        if cached:
            return [OverseasHolding(**h) for h in cached]

        tr_id = _tr_id("CTRP6504R", account.environment)

        try:
            data = await kis_client.request(
                account,
                "GET",
                "/uapi/overseas-stock/v1/trading/inquire-present-balance",
                tr_id=tr_id,
                params={
                    "CANO": account.account_number,
                    "ACNT_PRDT_CD": account.product_code,
                    "WCRC_FRCR_DVSN_CD": "02",  # 외화 기준
                    "NATN_CD": "840",  # USA
                    "TR_MKET_CD": "00",  # 전체
                    "INQR_DVSN_CD": "00",
                },
                db=db,
            )
        except KISApiError as e:
            logger.warning("Overseas balance query failed: %s", e.msg)
            return []
        except Exception as e:
            logger.warning("Overseas balance query error: %s", e)
            return []

        holdings = []
        for item in data.get("output1", []):
            qty = _safe_int(item.get("cblc_qty13"))
            if qty <= 0:
                continue

            holdings.append(OverseasHolding(
                symbol=item.get("pdno", ""),
                name=item.get("prdt_name", ""),
                market=item.get("tr_mket_name", ""),
                currency=item.get("buy_crcy_cd", "USD"),
                quantity=qty,
                avg_price=_safe_float(item.get("pchs_avg_pric")),
                current_price=_safe_float(item.get("ovrs_now_pric1")),
                value_foreign=_safe_float(item.get("frcr_evlu_amt2")),
                pnl_foreign=_safe_float(item.get("evlu_pfls_amt2")),
                pnl_rate=_safe_float(item.get("evlu_pfls_rt1")),
                exchange_rate=_safe_float(item.get("bass_exrt")),
            ))

        await cache_set(cache_key, [h.model_dump() for h in holdings], 10)
        return holdings

    async def _get_overseas_foreign_balances(
        self,
        account: KISAccount,
        db: AsyncSession,
    ) -> tuple[list[ForeignCurrencyBalance], int]:
        """Get foreign currency balances and total overseas KRW value.

        Returns (foreign_balances, overseas_total_krw).
        Tries for all account types — gracefully returns ([], 0) on failure.
        """
        cache_key = f"kis:overseas_balance:{account.id}"
        cached = await cache_get(cache_key)
        if cached:
            return (
                [ForeignCurrencyBalance(**fb) for fb in cached["foreign_balances"]],
                cached["overseas_total_krw"],
            )

        tr_id = _tr_id("CTRP6504R", account.environment)

        try:
            data = await kis_client.request(
                account,
                "GET",
                "/uapi/overseas-stock/v1/trading/inquire-present-balance",
                tr_id=tr_id,
                params={
                    "CANO": account.account_number,
                    "ACNT_PRDT_CD": account.product_code,
                    "WCRC_FRCR_DVSN_CD": "02",  # 외화 기준
                    "NATN_CD": "840",  # USA
                    "TR_MKET_CD": "00",
                    "INQR_DVSN_CD": "00",
                },
                db=db,
            )
        except (KISApiError, Exception) as e:
            logger.warning("Overseas balance query failed: %s", e)
            return [], 0

        # output2: per-currency summary — only include currencies with actual balances
        foreign_balances = []
        output2 = data.get("output2", [])
        if isinstance(output2, list):
            for item in output2:
                crcy = item.get("crcy_cd", "").strip()
                if not crcy:
                    continue
                deposit = _safe_float(item.get("frcr_dncl_amt_2", item.get("frcr_dncl_amt")))
                stock_val = _safe_float(item.get("frcr_evlu_amt2"))
                total_val = deposit + stock_val
                # Skip currencies with zero balance
                if total_val <= 0:
                    continue
                foreign_balances.append(ForeignCurrencyBalance(
                    currency=crcy,
                    deposit=deposit,
                    stock_value=stock_val,
                    total_value=total_val,
                    exchange_rate=0.0,  # filled from output1 if available
                ))

        # Try to get exchange rate from output1 holdings
        for item in data.get("output1", []):
            exrt = _safe_float(item.get("bass_exrt"))
            crcy = item.get("buy_crcy_cd", "").strip()
            if exrt > 0 and crcy:
                for fb in foreign_balances:
                    if fb.currency == crcy and fb.exchange_rate == 0.0:
                        fb.exchange_rate = exrt

        # output3: grand total (KRW converted) — only trust if we have actual foreign balances
        overseas_total_krw = 0
        if foreign_balances:
            output3 = data.get("output3", {})
            if isinstance(output3, list) and output3:
                output3 = output3[0]
            overseas_total_krw = _safe_int(output3.get("tot_asst_amt")) if isinstance(output3, dict) else 0

        result = {
            "foreign_balances": [fb.model_dump() for fb in foreign_balances],
            "overseas_total_krw": overseas_total_krw,
        }
        await cache_set(cache_key, result, 10)
        return foreign_balances, overseas_total_krw

    async def _get_balance_brokerage(
        self,
        account: KISAccount,
        db: AsyncSession,
    ) -> AccountBalance:
        """Get balance for brokerage accounts (product_code='01') via TTTC8434R."""
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

        # Get overseas foreign currency balances (best effort)
        foreign_balances = []
        overseas_total_krw = 0
        try:
            foreign_balances, overseas_total_krw = await self._get_overseas_foreign_balances(account, db)
        except Exception as e:
            logger.warning("Failed to get overseas balance: %s", e)

        return AccountBalance(
            total_value=total_value,
            cash=cash,
            stock_value=stock_value,
            total_pnl=total_pnl,
            total_pnl_rate=total_pnl_rate,
            holding_count=holding_count,
            foreign_balances=foreign_balances,
            overseas_total_krw=overseas_total_krw,
        )

    async def _get_balance_account_overview(
        self,
        account: KISAccount,
        db: AsyncSession,
    ) -> AccountBalance:
        """Get balance for non-brokerage accounts via CTRP6548R (투자계좌 자산현황).

        This is the universal account balance API that works with various
        product codes (금융상품, 연금 등). Maps to HTS screen [0891].
        """
        tr_id = _tr_id("CTRP6548R", account.environment)

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/trading/inquire-account-balance",
            tr_id=tr_id,
            params={
                "CANO": account.account_number,
                "ACNT_PRDT_CD": account.product_code,
                "INQR_DVSN_1": "",
                "BSPR_BF_DT_APLY_YN": "",
            },
            db=db,
        )

        # output1: per-holding items
        holdings_data = data.get("output1", [])
        holding_count = len(holdings_data)

        # output2: summary (list with one item, or dict)
        summary = data.get("output2", [{}])
        if isinstance(summary, list) and summary:
            out = summary[0]
        else:
            out = summary if isinstance(summary, dict) else {}

        # Try various field names that CTRP6548R may return
        # 총평가금액
        total_value = (
            _safe_int(out.get("tot_evlu_amt"))
            or _safe_int(out.get("scts_evlu_amt"))  # 유가증권평가금액
            or _safe_int(out.get("tot_asst_amt"))
        )
        # 예수금
        cash = (
            _safe_int(out.get("dnca_tot_amt"))
            or _safe_int(out.get("prvs_rcdl_excc_amt"))  # 가수도정산예상금액
            or _safe_int(out.get("nass_amt"))  # 순자산금액
        )
        # 주식/상품 평가금액
        stock_value = (
            _safe_int(out.get("evlu_amt_smtl_amt"))
            or _safe_int(out.get("scts_evlu_amt"))
        )
        # 총손익
        total_pnl = (
            _safe_int(out.get("evlu_pfls_smtl_amt"))
            or _safe_int(out.get("evlu_pfls_amt"))
        )

        if total_value == 0:
            total_value = stock_value + cash

        purchase_total = _safe_int(out.get("pchs_amt_smtl_amt"))
        if purchase_total > 0:
            total_pnl_rate = round((total_pnl / purchase_total) * 100, 2)
        else:
            total_pnl_rate = 0.0

        # Get overseas foreign currency balances (best effort)
        foreign_balances = []
        overseas_total_krw = 0
        try:
            foreign_balances, overseas_total_krw = await self._get_overseas_foreign_balances(account, db)
        except Exception as e:
            logger.warning("Failed to get overseas balance for account_overview: %s", e)

        return AccountBalance(
            total_value=total_value,
            cash=cash,
            stock_value=stock_value,
            total_pnl=total_pnl,
            total_pnl_rate=total_pnl_rate,
            holding_count=holding_count,
            foreign_balances=foreign_balances,
            overseas_total_krw=overseas_total_krw,
        )

    async def get_balance(
        self,
        account: KISAccount,
        db: AsyncSession,
    ) -> AccountBalance:
        """Get account balance summary from KIS.

        Uses TTTC8434R for brokerage accounts (01),
        falls back to CTRP6548R for other account types (금융상품 등).
        """
        cache_key = f"kis:balance:{account.id}"
        cached = await cache_get(cache_key)
        if cached:
            return AccountBalance(**cached)

        if account.product_code == "01":
            balance = await self._get_balance_brokerage(account, db)
        else:
            # Try CTRP6548R for non-brokerage accounts
            try:
                balance = await self._get_balance_account_overview(account, db)
            except KISApiError as e:
                logger.warning(
                    "CTRP6548R failed for product_code=%s: %s",
                    account.product_code, e.msg,
                )
                raise KISApiError(
                    rt_cd="9",
                    msg_cd="NOT_SUPPORTED",
                    msg=(
                        f"계좌(상품코드: {account.product_code}) 잔고 조회에 실패했습니다. "
                        f"KIS 응답: {e.msg}"
                    ),
                )

        await cache_set(cache_key, balance.model_dump(), 10)
        return balance


portfolio_service = PortfolioService()
