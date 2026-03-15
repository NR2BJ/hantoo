"""Pydantic schemas for portfolio (balance & holdings)."""

from pydantic import BaseModel


class AccountBalance(BaseModel):
    total_value: int         # 총평가금액
    cash: int                # 예수금(D+2)
    stock_value: int         # 주식평가금액
    total_pnl: int           # 총평가손익
    total_pnl_rate: float    # 총수익률(%)
    holding_count: int       # 보유종목수


class Holding(BaseModel):
    symbol: str
    name: str
    quantity: int            # 보유수량
    avg_price: int           # 평균매입가
    current_price: int       # 현재가
    value: int               # 평가금액
    pnl: int                 # 평가손익
    pnl_rate: float          # 수익률(%)
