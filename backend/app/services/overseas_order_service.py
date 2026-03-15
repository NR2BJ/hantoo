"""Overseas stock order service — place, modify, cancel orders via KIS API."""

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kis_account import KISAccount
from app.models.trade import Trade
from app.models.user import User
from app.schemas.overseas import (
    OverseasBuyableAmount,
    OverseasFilledOrder,
    OverseasOrderCreate,
    OverseasOrderModify,
    OverseasOrderResponse,
)
from app.services.cache import cache_get, cache_set
from app.services.kis_client import kis_client

logger = logging.getLogger(__name__)

# US market order type mapping (same as domestic)
ORD_DVSN_MAP = {
    "limit": "00",   # 지정가
    "market": "01",  # 시장가
}


def _tr_id(base: str, environment: str) -> str:
    """Swap T→V prefix for paper trading."""
    if environment == "paper":
        return "V" + base[1:]
    return base


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


def _trade_to_response(t: Trade, exchange: str = "") -> OverseasOrderResponse:
    return OverseasOrderResponse(
        id=str(t.id),
        account_id=str(t.account_id),
        symbol=t.symbol,
        exchange=exchange or t.market,
        side=t.side,
        order_type=t.order_type,
        quantity=int(t.quantity),
        price=float(t.price) if t.price else None,
        status=t.status,
        filled_quantity=int(t.filled_quantity),
        filled_price=float(t.filled_price) if t.filled_price else None,
        kis_order_id=t.kis_order_id,
        submitted_at=t.submitted_at,
        created_at=t.created_at,
    )


class OverseasOrderService:
    # ── Place Order ──
    async def place_order(
        self,
        account: KISAccount,
        user: User,
        req: OverseasOrderCreate,
        db: AsyncSession,
    ) -> OverseasOrderResponse:
        body = {
            "CANO": account.account_number,
            "ACNT_PRDT_CD": account.product_code,
            "OVRS_EXCG_CD": req.exchange,
            "PDNO": req.symbol,
            "ORD_DVSN": ORD_DVSN_MAP[req.order_type],
            "ORD_QTY": str(req.quantity),
            "OVRS_ORD_UNPR": str(req.price or 0),
            "ORD_SVR_DVSN_CD": "0",
        }

        if req.side == "buy":
            tr_id = _tr_id("TTTT1002U", account.environment)
        else:
            tr_id = _tr_id("TTTT1006U", account.environment)

        data = await kis_client.request(
            account,
            "POST",
            "/uapi/overseas-stock/v1/trading/order",
            tr_id=tr_id,
            body=body,
            db=db,
            use_hashkey=True,
        )

        out = data.get("output", {})
        kis_order_id = out.get("ODNO", "")

        trade = Trade(
            account_id=account.id,
            user_id=user.id,
            symbol=req.symbol,
            market=req.exchange,  # NAS, NYS, AMS
            side=req.side,
            order_type=req.order_type,
            quantity=req.quantity,
            price=req.price,
            status="pending",
            filled_quantity=0,
            kis_order_id=kis_order_id,
            submitted_at=datetime.now(timezone.utc),
        )
        db.add(trade)
        await db.commit()
        await db.refresh(trade)

        logger.info(
            "Overseas order placed: %s %s %s %s qty=%d price=%s kis_odno=%s",
            req.side, req.exchange, req.symbol, req.order_type,
            req.quantity, req.price, kis_order_id,
        )

        return _trade_to_response(trade, req.exchange)

    # ── Modify Order ──
    async def modify_order(
        self,
        account: KISAccount,
        user: User,
        trade_id: str,
        req: OverseasOrderModify,
        db: AsyncSession,
    ) -> OverseasOrderResponse:
        trade = await db.get(Trade, trade_id)
        if not trade or str(trade.account_id) != str(account.id):
            raise ValueError("Order not found")
        if not trade.kis_order_id:
            raise ValueError("No KIS order ID for this trade")

        body = {
            "CANO": account.account_number,
            "ACNT_PRDT_CD": account.product_code,
            "OVRS_EXCG_CD": trade.market,
            "PDNO": trade.symbol,
            "ORGN_ODNO": trade.kis_order_id,
            "RVSE_CNCL_DVSN_CD": "01",  # 01=정정
            "ORD_QTY": str(req.quantity),
            "OVRS_ORD_UNPR": str(req.price),
            "ORD_SVR_DVSN_CD": "0",
        }

        tr_id = _tr_id("TTTT1004U", account.environment)

        await kis_client.request(
            account,
            "POST",
            "/uapi/overseas-stock/v1/trading/order-rvsecncl",
            tr_id=tr_id,
            body=body,
            db=db,
            use_hashkey=True,
        )

        trade.quantity = req.quantity
        trade.price = req.price
        trade.status = "modified"
        await db.commit()
        await db.refresh(trade)

        logger.info("Overseas order modified: %s qty=%d price=%s", trade.kis_order_id, req.quantity, req.price)
        return _trade_to_response(trade)

    # ── Cancel Order ──
    async def cancel_order(
        self,
        account: KISAccount,
        user: User,
        trade_id: str,
        db: AsyncSession,
    ) -> OverseasOrderResponse:
        trade = await db.get(Trade, trade_id)
        if not trade or str(trade.account_id) != str(account.id):
            raise ValueError("Order not found")
        if not trade.kis_order_id:
            raise ValueError("No KIS order ID for this trade")

        body = {
            "CANO": account.account_number,
            "ACNT_PRDT_CD": account.product_code,
            "OVRS_EXCG_CD": trade.market,
            "PDNO": trade.symbol,
            "ORGN_ODNO": trade.kis_order_id,
            "RVSE_CNCL_DVSN_CD": "02",  # 02=취소
            "ORD_QTY": "0",
            "OVRS_ORD_UNPR": "0",
            "ORD_SVR_DVSN_CD": "0",
        }

        tr_id = _tr_id("TTTT1004U", account.environment)

        await kis_client.request(
            account,
            "POST",
            "/uapi/overseas-stock/v1/trading/order-rvsecncl",
            tr_id=tr_id,
            body=body,
            db=db,
            use_hashkey=True,
        )

        trade.status = "cancelled"
        await db.commit()
        await db.refresh(trade)

        logger.info("Overseas order cancelled: %s", trade.kis_order_id)
        return _trade_to_response(trade)

    # ── Filled Orders ──
    async def get_filled_orders(
        self,
        account: KISAccount,
        db: AsyncSession,
    ) -> list[OverseasFilledOrder]:
        tr_id = _tr_id("TTTS3035R", account.environment)

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/overseas-stock/v1/trading/inquire-ccnl",
            tr_id=tr_id,
            params={
                "CANO": account.account_number,
                "ACNT_PRDT_CD": account.product_code,
                "PDNO": "",
                "ORD_STRT_DT": "",  # empty = today
                "ORD_END_DT": "",
                "SLL_BUY_DVSN_CD": "00",  # 00=전체
                "CCLD_NCCS_DVSN": "00",
                "OVRS_EXCG_CD": "",  # all exchanges
                "SORT_SQN": "DS",
                "ORD_DT": "",
                "ORD_GNO_BRNO": "",
                "ODNO": "",
                "CTX_AREA_FK200": "",
                "CTX_AREA_NK200": "",
            },
            db=db,
        )

        orders = []
        for item in data.get("output", []):
            filled_qty = _safe_int(item.get("ft_ccld_qty"))
            if filled_qty <= 0:
                continue

            side_code = item.get("sll_buy_dvsn_cd", "")
            side = "sell" if side_code == "01" else "buy"

            orders.append(OverseasFilledOrder(
                order_id=item.get("odno", ""),
                symbol=item.get("pdno", ""),
                name=item.get("prdt_name", item.get("pdno", "")),
                exchange=item.get("ovrs_excg_cd", ""),
                side=side,
                quantity=filled_qty,
                price=_safe_float(item.get("ft_ccld_unpr3")),
                total_amount=_safe_float(item.get("ft_ccld_amt3")),
                order_time=item.get("ord_tmd", ""),
                filled_time=item.get("ccld_tmd", item.get("ord_tmd", "")),
            ))

        return orders

    # ── Buyable Amount ──
    async def get_buyable_amount(
        self,
        account: KISAccount,
        symbol: str,
        exchange: str,
        price: float,
        db: AsyncSession,
    ) -> OverseasBuyableAmount:
        """해외주식 매수가능금액 — CTRP6504R output2 USD 잔고 기반 계산."""
        from app.services.kis_client import KISApiError

        cache_key = f"kis:overseas_balance:{account.id}"
        cached = await cache_get(cache_key)

        usd_deposit = 0.0
        exchange_rate = 1300.0  # 기본 환율

        if cached:
            # 캐시에서 외화 잔고 정보 가져오기
            usd_deposit = cached.get("usd_deposit", 0.0)
            exchange_rate = cached.get("exchange_rate", 1300.0)
        else:
            try:
                tr_id = _tr_id("CTRP6504R", account.environment)
                data = await kis_client.request(
                    account,
                    "GET",
                    "/uapi/overseas-stock/v1/trading/inquire-present-balance",
                    tr_id=tr_id,
                    params={
                        "CANO": account.account_number,
                        "ACNT_PRDT_CD": account.product_code,
                        "WCRC_FRCR_DVSN_CD": "02",
                        "NATN_CD": "840",
                        "TR_MKET_CD": "00",
                        "INQR_DVSN_CD": "00",
                    },
                    db=db,
                )

                # output2: 통화별 잔고
                for cur_item in data.get("output2", []):
                    if cur_item.get("crcy_cd") == "USD":
                        usd_deposit = _safe_float(cur_item.get("frcr_dncl_amt_2"))
                        exchange_rate = _safe_float(cur_item.get("bass_exrt")) or 1300.0
                        break

                await cache_set(
                    cache_key,
                    {"usd_deposit": usd_deposit, "exchange_rate": exchange_rate},
                    10,
                )
            except (KISApiError, Exception) as e:
                logger.warning("Failed to get overseas balance: %s", e)

        orderable_qty = int(usd_deposit / price) if price > 0 else 0

        return OverseasBuyableAmount(
            orderable_cash_foreign=usd_deposit,
            orderable_qty=orderable_qty,
            exchange_rate=exchange_rate,
        )


overseas_order_service = OverseasOrderService()
