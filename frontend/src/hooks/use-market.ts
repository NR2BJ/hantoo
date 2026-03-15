"use client";

import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { api } from "@/lib/api-client";
import { useTradingStore } from "@/stores/trading-store";
import type {
  StockQuote,
  Candle,
  Orderbook,
  TradeRecord,
  IndexQuote,
  SearchResult,
} from "@/types/market";

function useAccountId() {
  return useTradingStore((s) => s.activeAccountId);
}

export function useQuote(symbol: string) {
  const accountId = useAccountId();
  return useQuery<StockQuote>({
    queryKey: ["quote", symbol, accountId],
    queryFn: () =>
      api.get(`/api/market/quote`, {
        params: { symbol, account_id: accountId! },
      }),
    enabled: !!symbol && !!accountId,
    refetchInterval: 5000,
    staleTime: 3000,
  });
}

export function useCandles(symbol: string, period = "D", count = 100) {
  const accountId = useAccountId();
  return useQuery<Candle[]>({
    queryKey: ["candles", symbol, period, count, accountId],
    queryFn: () =>
      api.get(`/api/market/candles`, {
        params: {
          symbol,
          period,
          count: String(count),
          account_id: accountId!,
        },
      }),
    enabled: !!symbol && !!accountId,
    staleTime: 30000,
  });
}

export function useMinuteCandles(symbol: string, interval = 1) {
  const accountId = useAccountId();
  return useQuery<Candle[]>({
    queryKey: ["minuteCandles", symbol, interval, accountId],
    queryFn: () =>
      api.get(`/api/market/candles/minute`, {
        params: {
          symbol,
          interval: String(interval),
          account_id: accountId!,
        },
      }),
    enabled: !!symbol && !!accountId,
    staleTime: 15000,
  });
}

export function useOrderbook(symbol: string) {
  const accountId = useAccountId();
  return useQuery<Orderbook>({
    queryKey: ["orderbook", symbol, accountId],
    queryFn: () =>
      api.get(`/api/market/orderbook`, {
        params: { symbol, account_id: accountId! },
      }),
    enabled: !!symbol && !!accountId,
    refetchInterval: 3000,
    staleTime: 2000,
  });
}

export function useTrades(symbol: string) {
  const accountId = useAccountId();
  return useQuery<TradeRecord[]>({
    queryKey: ["trades", symbol, accountId],
    queryFn: () =>
      api.get(`/api/market/trades`, {
        params: { symbol, account_id: accountId! },
      }),
    enabled: !!symbol && !!accountId,
    refetchInterval: 5000,
    staleTime: 3000,
  });
}

export function useIndices() {
  const accountId = useAccountId();
  return useQuery<IndexQuote[]>({
    queryKey: ["indices", accountId],
    queryFn: () =>
      api.get(`/api/market/indices`, {
        params: { account_id: accountId! },
      }),
    enabled: !!accountId,
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

export function useSearch(query: string) {
  const [debouncedQuery, setDebouncedQuery] = useState(query);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  return useQuery<SearchResult[]>({
    queryKey: ["search", debouncedQuery],
    queryFn: () =>
      api.get(`/api/market/search`, {
        params: { q: debouncedQuery },
      }),
    enabled: debouncedQuery.length >= 1,
    staleTime: 60000,
  });
}
