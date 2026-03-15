"""Pydantic schemas for portfolio (balance & holdings)."""

from pydantic import BaseModel


class ForeignCurrencyBalance(BaseModel):
    currency: str            # 통화코드 (USD, HKD, JPY 등)
    deposit: float           # 외화예수금
    stock_value: float       # 외화평가금액
    total_value: float       # 외화총자산
    exchange_rate: float     # 기준환율


class AccountBalance(BaseModel):
    total_value: int         # 총평가금액 (원화)
    cash: int                # 예수금(D+2) (원화)
    stock_value: int         # 주식평가금액 (원화)
    total_pnl: int           # 총평가손익 (원화)
    total_pnl_rate: float    # 총수익률(%)
    holding_count: int       # 보유종목수
    # 해외주식 외화 잔고
    foreign_balances: list[ForeignCurrencyBalance] = []
    overseas_total_krw: int = 0  # 해외주식 총평가 (원화환산)


class Holding(BaseModel):
    symbol: str
    name: str
    quantity: int            # 보유수량
    avg_price: int           # 평균매입가
    current_price: int       # 현재가
    value: int               # 평가금액
    pnl: int                 # 평가손익
    pnl_rate: float          # 수익률(%)


class OverseasHolding(BaseModel):
    symbol: str
    name: str
    market: str              # 거래시장명 (NASDAQ, NYSE 등)
    currency: str            # 통화코드 (USD 등)
    quantity: int            # 보유수량
    avg_price: float         # 평균매입가 (외화)
    current_price: float     # 현재가 (외화)
    value_foreign: float     # 평가금액 (외화)
    pnl_foreign: float       # 평가손익 (외화)
    pnl_rate: float          # 수익률(%)
    exchange_rate: float     # 기준환율
