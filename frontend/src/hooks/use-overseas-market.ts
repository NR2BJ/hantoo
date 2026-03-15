"use client";

import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { api } from "@/lib/api-client";
import { useTradingStore } from "@/stores/trading-store";
import type {
  OverseasQuote,
  OverseasCandle,
  OverseasSearchResult,
} from "@/types/market";

function useAccountId() {
  return useTradingStore((s) => s.activeAccountId);
}

export function useOverseasQuote(symbol: string, exchange: string) {
  const accountId = useAccountId();
  return useQuery<OverseasQuote>({
    queryKey: ["overseasQuote", symbol, exchange, accountId],
    queryFn: () =>
      api.get(`/api/overseas/quote`, {
        params: { symbol, exchange, account_id: accountId! },
      }),
    enabled: !!symbol && !!exchange && !!accountId,
    refetchInterval: 5000,
    staleTime: 3000,
  });
}

export function useOverseasCandles(
  symbol: string,
  exchange: string,
  period = "D",
  count = 100,
) {
  const accountId = useAccountId();
  return useQuery<OverseasCandle[]>({
    queryKey: ["overseasCandles", symbol, exchange, period, count, accountId],
    queryFn: () =>
      api.get(`/api/overseas/candles`, {
        params: {
          symbol,
          exchange,
          period,
          count: String(count),
          account_id: accountId!,
        },
      }),
    enabled: !!symbol && !!exchange && !!accountId,
    staleTime: 30000,
  });
}

export function useOverseasSearch(query: string) {
  const accountId = useAccountId();
  const [debouncedQuery, setDebouncedQuery] = useState(query);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  return useQuery<OverseasSearchResult[]>({
    queryKey: ["overseasSearch", debouncedQuery, accountId],
    queryFn: () =>
      api.get(`/api/overseas/search`, {
        params: { q: debouncedQuery, account_id: accountId! },
      }),
    enabled: debouncedQuery.length >= 1 && !!accountId,
    staleTime: 60000,
  });
}
