"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { useTradingStore } from "@/stores/trading-store";
import type {
  IncomeStatementItem,
  BalanceSheetItem,
  FinancialRatioItem,
  EstimateItem,
  InvestOpinionItem,
  DividendItem,
  DividendRankItem,
  NewsItem,
  StockInfoDetail,
} from "@/types/market";

function useAccountId() {
  return useTradingStore((s) => s.activeAccountId);
}

// ── 재무제표 ──

export function useIncomeStatement(symbol: string, period = "A") {
  const accountId = useAccountId();
  return useQuery<IncomeStatementItem[]>({
    queryKey: ["finance", "income", symbol, period, accountId],
    queryFn: () =>
      api.get("/api/finance/income-statement", {
        params: { account_id: accountId!, symbol, period },
      }),
    enabled: !!accountId && !!symbol,
    staleTime: 300_000, // 5min
  });
}

export function useBalanceSheet(symbol: string, period = "A") {
  const accountId = useAccountId();
  return useQuery<BalanceSheetItem[]>({
    queryKey: ["finance", "balance", symbol, period, accountId],
    queryFn: () =>
      api.get("/api/finance/balance-sheet", {
        params: { account_id: accountId!, symbol, period },
      }),
    enabled: !!accountId && !!symbol,
    staleTime: 300_000,
  });
}

export function useFinancialRatio(symbol: string, period = "A") {
  const accountId = useAccountId();
  return useQuery<FinancialRatioItem[]>({
    queryKey: ["finance", "ratio", symbol, period, accountId],
    queryFn: () =>
      api.get("/api/finance/financial-ratio", {
        params: { account_id: accountId!, symbol, period },
      }),
    enabled: !!accountId && !!symbol,
    staleTime: 300_000,
  });
}

// ── 실적추정 / 투자의견 ──

export function useEstimate(symbol: string) {
  const accountId = useAccountId();
  return useQuery<EstimateItem[]>({
    queryKey: ["finance", "estimate", symbol, accountId],
    queryFn: () =>
      api.get("/api/finance/estimate", {
        params: { account_id: accountId!, symbol },
      }),
    enabled: !!accountId && !!symbol,
    staleTime: 300_000,
  });
}

export function useInvestOpinion(symbol: string) {
  const accountId = useAccountId();
  return useQuery<InvestOpinionItem[]>({
    queryKey: ["finance", "opinion", symbol, accountId],
    queryFn: () =>
      api.get("/api/finance/opinion", {
        params: { account_id: accountId!, symbol },
      }),
    enabled: !!accountId && !!symbol,
    staleTime: 300_000,
  });
}

// ── 배당 ──

export function useDividend(symbol: string) {
  const accountId = useAccountId();
  return useQuery<DividendItem[]>({
    queryKey: ["corporate", "dividend", symbol, accountId],
    queryFn: () =>
      api.get("/api/corporate/dividend", {
        params: { account_id: accountId!, symbol },
      }),
    enabled: !!accountId && !!symbol,
    staleTime: 300_000,
  });
}

export function useDividendRateRanking(market = "J") {
  const accountId = useAccountId();
  return useQuery<DividendRankItem[]>({
    queryKey: ["corporate", "dividend-rate", market, accountId],
    queryFn: () =>
      api.get("/api/corporate/dividend-rate", {
        params: { account_id: accountId!, market },
      }),
    enabled: !!accountId,
    staleTime: 300_000,
  });
}

// ── 뉴스 ──

export function useNews(symbol: string) {
  const accountId = useAccountId();
  return useQuery<NewsItem[]>({
    queryKey: ["corporate", "news", symbol, accountId],
    queryFn: () =>
      api.get("/api/corporate/news", {
        params: { account_id: accountId!, symbol },
      }),
    enabled: !!accountId && !!symbol,
    refetchInterval: 60_000, // 1분
    staleTime: 30_000,
  });
}

// ── 종목 기본정보 ──

export function useStockInfo(symbol: string) {
  const accountId = useAccountId();
  return useQuery<StockInfoDetail>({
    queryKey: ["corporate", "stock-info", symbol, accountId],
    queryFn: () =>
      api.get("/api/corporate/stock-info", {
        params: { account_id: accountId!, symbol },
      }),
    enabled: !!accountId && !!symbol,
    staleTime: 86_400_000, // 24h
  });
}
