"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { useTradingStore } from "@/stores/trading-store";
import type { AccountBalance, Holding } from "@/types/market";

function useAccountId() {
  return useTradingStore((s) => s.activeAccountId);
}

export function useBalance() {
  const accountId = useAccountId();
  return useQuery<AccountBalance>({
    queryKey: ["balance", accountId],
    queryFn: () =>
      api.get(`/api/portfolio/balance`, {
        params: { account_id: accountId! },
      }),
    enabled: !!accountId,
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

export function useHoldings() {
  const accountId = useAccountId();
  return useQuery<Holding[]>({
    queryKey: ["holdings", accountId],
    queryFn: () =>
      api.get(`/api/portfolio/holdings`, {
        params: { account_id: accountId! },
      }),
    enabled: !!accountId,
    refetchInterval: 10000,
    staleTime: 5000,
  });
}
