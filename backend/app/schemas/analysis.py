"""Phase 7 — 종목 분석 스키마 (재무/기업/뉴스/ETF)."""

from pydantic import BaseModel


# ── 재무제표 ──────────────────────────────────────────────


class IncomeStatementItem(BaseModel):
    """손익계산서 항목."""

    period: str  # YYYYMM (e.g., 202412)
    revenue: int | None = None  # 매출액
    operating_profit: int | None = None  # 영업이익
    net_income: int | None = None  # 당기순이익
    eps: int | None = None  # 주당순이익


class BalanceSheetItem(BaseModel):
    """재무상태표 항목."""

    period: str
    total_assets: int | None = None  # 자산총계
    total_liabilities: int | None = None  # 부채총계
    total_equity: int | None = None  # 자본총계


class FinancialRatioItem(BaseModel):
    """재무비율 항목."""

    period: str
    roe: float | None = None  # 자기자본이익률
    roa: float | None = None  # 총자산이익률
    per: float | None = None
    pbr: float | None = None
    eps: int | None = None
    bps: int | None = None  # 주당순자산
    debt_ratio: float | None = None  # 부채비율
    reserve_ratio: float | None = None  # 유보율


# ── 실적추정 / 투자의견 ──────────────────────────────────


class EstimateItem(BaseModel):
    """실적추정치 항목."""

    period: str  # YYYYMM
    revenue_est: int | None = None  # 매출액 추정
    op_profit_est: int | None = None  # 영업이익 추정
    net_income_est: int | None = None  # 순이익 추정
    eps_est: int | None = None  # EPS 추정


class InvestOpinionItem(BaseModel):
    """투자의견/컨센서스 항목."""

    date: str  # YYYYMMDD
    firm: str  # 증권사명
    opinion: str  # 매수/중립/매도 등
    target_price: int | None = None
    change: str | None = None  # 상향/하향/유지


# ── 배당 ─────────────────────────────────────────────────


class DividendItem(BaseModel):
    """배당정보 항목."""

    year: str  # YYYY
    dps: int | None = None  # 주당배당금
    div_rate: float | None = None  # 배당수익률(%)
    ex_date: str | None = None  # 배당락일
    pay_date: str | None = None  # 지급일
    record_date: str | None = None  # 기준일


class DividendRankItem(BaseModel):
    """배당수익률 랭킹 항목."""

    rank: int
    symbol: str
    name: str
    div_rate: float  # 배당수익률(%)
    current_price: int
    dps: int | None = None


# ── 뉴스 ─────────────────────────────────────────────────


class NewsItem(BaseModel):
    """뉴스 제목 항목."""

    date: str  # YYYYMMDD
    time: str  # HHMMSS
    title: str
    source: str | None = None  # 기사 출처
    article_id: str | None = None  # 기사 식별자


# ── 종목 기본정보 ────────────────────────────────────────


class StockInfoDetail(BaseModel):
    """종목 기본정보 (search-info)."""

    symbol: str
    name: str
    market: str  # KOSPI / KOSDAQ
    sector: str | None = None  # 업종
    listing_date: str | None = None  # 상장일
    face_value: int | None = None  # 액면가
    shares_outstanding: int | None = None  # 상장주수
    capital: int | None = None  # 자본금
