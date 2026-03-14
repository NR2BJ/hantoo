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
