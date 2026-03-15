"""Trading order service — place, modify, cancel orders via KIS API."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kis_account import KISAccount
from app.models.trade import Trade
from app.models.user import User
from app.schemas.order import (
    BuyableAmount,
    FilledOrder,
    OrderCreate,
    OrderModify,
    OrderResponse,
    PendingOrder,
)
from app.services.kis_client import kis_client

logger = logging.getLogger(__name__)

# KIS order type mapping
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


def _trade_to_response(t: Trade) -> OrderResponse:
    return OrderResponse(
        id=str(t.id),
        account_id=str(t.account_id),
        symbol=t.symbol,
        side=t.side,
        order_type=t.order_type,
        quantity=int(t.quantity),
        price=int(t.price) if t.price else None,
        status=t.status,
        filled_quantity=int(t.filled_quantity),
        filled_price=int(t.filled_price) if t.filled_price else None,
        kis_order_id=t.kis_order_id,
        submitted_at=t.submitted_at,
        created_at=t.created_at,
    )


class OrderService:
    # ── Place Order ──
    async def place_order(
        self,
        account: KISAccount,
        user: User,
        req: OrderCreate,
        db: AsyncSession,
    ) -> OrderResponse:
        # Build KIS request body
        body = {
            "CANO": account.account_number,
            "ACNT_PRDT_CD": account.product_code,
            "PDNO": req.symbol,
            "ORD_DVSN": ORD_DVSN_MAP[req.order_type],
            "ORD_QTY": str(req.quantity),
            "ORD_UNPR": str(req.price or 0),
        }

        # Select tr_id based on side + environment
        if req.side == "buy":
            tr_id = _tr_id("TTTC0802U", account.environment)
        else:
            tr_id = _tr_id("TTTC0801U", account.environment)

        data = await kis_client.request(
            account,
            "POST",
            "/uapi/domestic-stock/v1/trading/order-cash",
            tr_id=tr_id,
            body=body,
            db=db,
            use_hashkey=True,
        )

        out = data.get("output", {})
        kis_order_id = out.get("ODNO", "")

        # Save to DB
        trade = Trade(
            account_id=account.id,
            user_id=user.id,
            symbol=req.symbol,
            market="KRX",
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
            "Order placed: %s %s %s qty=%d price=%s kis_odno=%s",
            req.side, req.symbol, req.order_type, req.quantity, req.price, kis_order_id,
        )

        return _trade_to_response(trade)

    # ── Modify Order ──
    async def modify_order(
        self,
        account: KISAccount,
        user: User,
        trade_id: str,
        req: OrderModify,
        db: AsyncSession,
    ) -> OrderResponse:
        # Lookup trade in DB
        trade = await db.get(Trade, trade_id)
        if not trade or str(trade.account_id) != str(account.id):
            raise ValueError("Order not found")
        if not trade.kis_order_id:
            raise ValueError("No KIS order ID for this trade")

        body = {
            "CANO": account.account_number,
            "ACNT_PRDT_CD": account.product_code,
            "KRX_FWDG_ORD_ORGNO": "",
            "ORGN_ODNO": trade.kis_order_id,
            "ORD_DVSN": "00",  # 정정은 지정가
            "RVSE_CNCL_DVSN_CD": "01",  # 01=정정
            "ORD_QTY": str(req.quantity),
            "ORD_UNPR": str(req.price),
            "QTY_ALL_ORD_YN": "N",
        }

        tr_id = _tr_id("TTTC0803U", account.environment)

        await kis_client.request(
            account,
            "POST",
            "/uapi/domestic-stock/v1/trading/order-rvsecncl",
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

        logger.info("Order modified: %s qty=%d price=%d", trade.kis_order_id, req.quantity, req.price)
        return _trade_to_response(trade)

    # ── Cancel Order ──
    async def cancel_order(
        self,
        account: KISAccount,
        user: User,
        trade_id: str,
        db: AsyncSession,
    ) -> OrderResponse:
        trade = await db.get(Trade, trade_id)
        if not trade or str(trade.account_id) != str(account.id):
            raise ValueError("Order not found")
        if not trade.kis_order_id:
            raise ValueError("No KIS order ID for this trade")

        body = {
            "CANO": account.account_number,
            "ACNT_PRDT_CD": account.product_code,
            "KRX_FWDG_ORD_ORGNO": "",
            "ORGN_ODNO": trade.kis_order_id,
            "ORD_DVSN": "00",
            "RVSE_CNCL_DVSN_CD": "02",  # 02=취소
            "ORD_QTY": "0",  # 0=전량취소
            "ORD_UNPR": "0",
            "QTY_ALL_ORD_YN": "Y",
        }

        tr_id = _tr_id("TTTC0803U", account.environment)

        await kis_client.request(
            account,
            "POST",
            "/uapi/domestic-stock/v1/trading/order-rvsecncl",
            tr_id=tr_id,
            body=body,
            db=db,
            use_hashkey=True,
        )

        trade.status = "cancelled"
        await db.commit()
        await db.refresh(trade)

        logger.info("Order cancelled: %s", trade.kis_order_id)
        return _trade_to_response(trade)

    # ── Pending Orders (from KIS API) ──
    async def get_pending_orders(
        self,
        account: KISAccount,
        db: AsyncSession,
    ) -> list[PendingOrder]:
        tr_id = _tr_id("TTTC8036R", account.environment)

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl",
            tr_id=tr_id,
            params={
                "CANO": account.account_number,
                "ACNT_PRDT_CD": account.product_code,
                "CTX_AREA_FK100": "",
                "CTX_AREA_NK100": "",
                "INQR_DVSN_1": "0",
                "INQR_DVSN_2": "0",
            },
            db=db,
        )

        orders = []
        for item in data.get("output", []):
            qty = _safe_int(item.get("psbl_qty"))
            if qty <= 0:
                continue

            side_code = item.get("sll_buy_dvsn_cd", "")
            side = "sell" if side_code == "01" else "buy"

            orders.append(PendingOrder(
                order_id=item.get("odno", ""),
                symbol=item.get("pdno", ""),
                name=item.get("prdt_name", ""),
                side=side,
                order_type="limit",
                quantity=_safe_int(item.get("ord_qty")),
                price=_safe_int(item.get("ord_unpr")),
                unfilled_qty=qty,
                order_time=item.get("ord_tmd", ""),
            ))

        return orders

    # ── Filled Orders (from KIS API) ──
    async def get_filled_orders(
        self,
        account: KISAccount,
        db: AsyncSession,
    ) -> list[FilledOrder]:
        tr_id = _tr_id("TTTC8001R", account.environment)

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/trading/inquire-daily-ccld",
            tr_id=tr_id,
            params={
                "CANO": account.account_number,
                "ACNT_PRDT_CD": account.product_code,
                "INQR_STRT_DT": "",  # empty = today
                "INQR_END_DT": "",
                "SLL_BUY_DVSN_CD": "00",  # 00=전체
                "INQR_DVSN": "00",
                "PDNO": "",
                "CCLD_DVSN": "01",  # 01=체결
                "ORD_GNO_BRNO": "",
                "ODNO": "",
                "INQR_DVSN_3": "00",
                "INQR_DVSN_1": "",
                "CTX_AREA_FK100": "",
                "CTX_AREA_NK100": "",
            },
            db=db,
        )

        orders = []
        for item in data.get("output1", []):
            filled_qty = _safe_int(item.get("tot_ccld_qty"))
            if filled_qty <= 0:
                continue

            side_code = item.get("sll_buy_dvsn_cd", "")
            side = "sell" if side_code == "01" else "buy"

            orders.append(FilledOrder(
                order_id=item.get("odno", ""),
                symbol=item.get("pdno", ""),
                name=item.get("prdt_name", ""),
                side=side,
                quantity=filled_qty,
                price=_safe_int(item.get("avg_prvs")),
                total_amount=_safe_int(item.get("tot_ccld_amt")),
                order_time=item.get("ord_tmd", ""),
                filled_time=item.get("ccld_tmd", item.get("ord_tmd", "")),
            ))

        return orders

    # ── Buyable Amount ──
    async def get_buyable_amount(
        self,
        account: KISAccount,
        symbol: str,
        price: int,
        db: AsyncSession,
    ) -> BuyableAmount:
        tr_id = _tr_id("TTTC8908R", account.environment)

        data = await kis_client.request(
            account,
            "GET",
            "/uapi/domestic-stock/v1/trading/inquire-psbl-order",
            tr_id=tr_id,
            params={
                "CANO": account.account_number,
                "ACNT_PRDT_CD": account.product_code,
                "PDNO": symbol,
                "ORD_UNPR": str(price),
                "ORD_DVSN": "00",
                "CMA_EVLU_AMT_ICLD_YN": "Y",
                "OVRS_ICLD_YN": "N",
            },
            db=db,
        )

        out = data.get("output", {})
        return BuyableAmount(
            orderable_cash=_safe_int(out.get("ord_psbl_cash")),
            orderable_qty=_safe_int(out.get("nrcvb_buy_qty")),
        )


order_service = OrderService()
