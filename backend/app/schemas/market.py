from pydantic import BaseModel, Field


class StockQuote(BaseModel):
    symbol: str
    name: str
    current_price: int
    change: int
    change_rate: float
    change_sign: str  # 1=상한, 2=상승, 3=보합, 4=하한, 5=하락
    open_price: int
    high_price: int
    low_price: int
    volume: int
    trade_amount: int
    prev_close: int
    market_cap: int = 0
    per: float | None = None
    pbr: float | None = None
    eps: int | None = None


class Candle(BaseModel):
    date: str  # YYYYMMDD or YYYYMMDDHHMM
    open: int
    high: int
    low: int
    close: int
    volume: int


class OrderbookEntry(BaseModel):
    price: int
    volume: int


class Orderbook(BaseModel):
    symbol: str
    ask: list[OrderbookEntry]  # 매도호가 (10단계, 1호가가 index 0)
    bid: list[OrderbookEntry]  # 매수호가 (10단계, 1호가가 index 0)
    total_ask_volume: int
    total_bid_volume: int


class TradeRecord(BaseModel):
    time: str
    price: int
    volume: int
    change: int


class IndexQuote(BaseModel):
    code: str
    name: str
    current: float
    change: float
    change_rate: float
    change_sign: str


class SearchResult(BaseModel):
    symbol: str
    name: str
    market: str  # KOSPI / KOSDAQ


class RankItem(BaseModel):
    """공통 랭킹 항목 — 거래량/등락률/시총/인기 등 동일 구조."""

    rank: int
    symbol: str
    name: str
    current_price: int
    change: int  # 전일대비
    change_rate: float  # 전일대비율(%)
    change_sign: str  # 1=상한 2=상승 3=보합 4=하한 5=하락
    volume: int  # 누적거래량
    trade_amount: int  # 누적거래대금


class InvestorItem(BaseModel):
    """투자자별 매매동향 항목."""

    investor: str  # 개인, 외국인, 기관계 등
    buy_volume: int
    sell_volume: int
    net_volume: int  # 순매수량
    buy_amount: int  # 매수금액 (백만원)
    sell_amount: int  # 매도금액 (백만원)
    net_amount: int  # 순매수금액 (백만원)
