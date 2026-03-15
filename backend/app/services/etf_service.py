"""Phase 7 — ETF/ETN 전용 서비스 (스텁 — tr_id 미확인)."""

import logging

logger = logging.getLogger(__name__)


class EtfService:
    """ETF/ETN specific queries via KIS API.

    All methods are stubs — tr_ids not yet confirmed from KIS docs.
    """

    async def get_etf_price(self, account, symbol: str, db):
        raise NotImplementedError("ETF inquire_price: tr_id 미확인")

    async def get_component_stocks(self, account, symbol: str, db):
        raise NotImplementedError("ETF inquire_component_stock_price: tr_id 미확인")

    async def get_nav_trend(self, account, symbol: str, db):
        raise NotImplementedError("ETF etf_nav_trend: tr_id 미확인")

    async def get_nav_comparison_trend(self, account, symbol: str, db):
        raise NotImplementedError("ETF nav_comparison_trend: tr_id 미확인")

    async def get_nav_comparison_daily(self, account, symbol: str, db):
        raise NotImplementedError("ETF nav_comparison_daily_trend: tr_id 미확인")

    async def get_nav_comparison_time(self, account, symbol: str, db):
        raise NotImplementedError("ETF nav_comparison_time_trend: tr_id 미확인")


etf_service = EtfService()
