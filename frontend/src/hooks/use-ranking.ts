"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { useTradingStore } from "@/stores/trading-store";
import type { RankItem, InvestorItem } from "@/types/market";

function useAccountId() {
  return useTradingStore((s) => s.activeAccountId);
}

export function useVolumeRank(market = "J") {
  const accountId = useAccountId();
  return useQuery<RankItem[]>({
    queryKey: ["ranking", "volume", market, accountId],
    queryFn: () =>
      api.get(`/api/ranking/volume`, {
        params: { account_id: accountId!, market },
      }),
    enabled: !!accountId,
    refetchInterval: 30000,
    refetchIntervalInBackground: false,
    staleTime: 10000,
  });
}

export function useFluctuation(market = "J", sort = "1") {
  const accountId = useAccountId();
  return useQuery<RankItem[]>({
    queryKey: ["ranking", "fluctuation", market, sort, accountId],
    queryFn: () =>
      api.get(`/api/ranking/fluctuation`, {
        params: { account_id: accountId!, market, sort },
      }),
    enabled: !!accountId,
    refetchInterval: 30000,
    refetchIntervalInBackground: false,
    staleTime: 10000,
  });
}

export function useMarketCapRank(market = "J") {
  const accountId = useAccountId();
  return useQuery<RankItem[]>({
    queryKey: ["ranking", "market-cap", market, accountId],
    queryFn: () =>
      api.get(`/api/ranking/market-cap`, {
        params: { account_id: accountId!, market },
      }),
    enabled: !!accountId,
    refetchInterval: 30000,
    refetchIntervalInBackground: false,
    staleTime: 10000,
  });
}

export function useTopInterest(market = "J") {
  const accountId = useAccountId();
  return useQuery<RankItem[]>({
    queryKey: ["ranking", "interest", market, accountId],
    queryFn: () =>
      api.get(`/api/ranking/interest`, {
        params: { account_id: accountId!, market },
      }),
    enabled: !!accountId,
    refetchInterval: 30000,
    refetchIntervalInBackground: false,
    staleTime: 10000,
  });
}

export function useNearHighLow(market = "J", sort = "1") {
  const accountId = useAccountId();
  return useQuery<RankItem[]>({
    queryKey: ["ranking", "highlow", market, sort, accountId],
    queryFn: () =>
      api.get(`/api/ranking/highlow`, {
        params: { account_id: accountId!, market, sort },
      }),
    enabled: !!accountId,
    refetchInterval: 30000,
    refetchIntervalInBackground: false,
    staleTime: 10000,
  });
}

export function useInvestor(symbol: string) {
  const accountId = useAccountId();
  return useQuery<InvestorItem[]>({
    queryKey: ["ranking", "investor", symbol, accountId],
    queryFn: () =>
      api.get(`/api/ranking/investor`, {
        params: { account_id: accountId!, symbol },
      }),
    enabled: !!accountId && !!symbol,
    refetchInterval: 30000,
    refetchIntervalInBackground: false,
    staleTime: 10000,
  });
}

export function useForeignInstitution(market = "J") {
  const accountId = useAccountId();
  return useQuery<RankItem[]>({
    queryKey: ["ranking", "foreign", market, accountId],
    queryFn: () =>
      api.get(`/api/ranking/foreign`, {
        params: { account_id: accountId!, market },
      }),
    enabled: !!accountId,
    refetchInterval: 30000,
    refetchIntervalInBackground: false,
    staleTime: 10000,
  });
}
