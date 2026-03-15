"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { useTradingStore } from "@/stores/trading-store";
import type {
  OrderCreate,
  OrderModify,
  OrderResponse,
  PendingOrder,
  FilledOrder,
  BuyableAmount,
} from "@/types/market";

function useAccountId() {
  return useTradingStore((s) => s.activeAccountId);
}

export function usePlaceOrder() {
  const accountId = useAccountId();
  const qc = useQueryClient();

  return useMutation<OrderResponse, Error, OrderCreate>({
    mutationFn: (order) =>
      api.post(`/api/orders`, order, {
        params: { account_id: accountId! },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["pendingOrders"] });
      qc.invalidateQueries({ queryKey: ["filledOrders"] });
    },
  });
}

export function useModifyOrder() {
  const accountId = useAccountId();
  const qc = useQueryClient();

  return useMutation<OrderResponse, Error, { tradeId: string; data: OrderModify }>({
    mutationFn: ({ tradeId, data }) =>
      api.put(`/api/orders/${tradeId}`, data, {
        params: { account_id: accountId! },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["pendingOrders"] });
    },
  });
}

export function useCancelOrder() {
  const accountId = useAccountId();
  const qc = useQueryClient();

  return useMutation<OrderResponse, Error, string>({
    mutationFn: (tradeId) =>
      api.delete(`/api/orders/${tradeId}`, {
        params: { account_id: accountId! },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["pendingOrders"] });
    },
  });
}

export function usePendingOrders() {
  const accountId = useAccountId();
  return useQuery<PendingOrder[]>({
    queryKey: ["pendingOrders", accountId],
    queryFn: () =>
      api.get(`/api/orders/pending`, {
        params: { account_id: accountId! },
      }),
    enabled: !!accountId,
    refetchInterval: 5000,
    staleTime: 3000,
  });
}

export function useFilledOrders() {
  const accountId = useAccountId();
  return useQuery<FilledOrder[]>({
    queryKey: ["filledOrders", accountId],
    queryFn: () =>
      api.get(`/api/orders/filled`, {
        params: { account_id: accountId! },
      }),
    enabled: !!accountId,
    staleTime: 10000,
  });
}

export function useBuyableAmount(symbol: string, price: number) {
  const accountId = useAccountId();
  return useQuery<BuyableAmount>({
    queryKey: ["buyable", symbol, price, accountId],
    queryFn: () =>
      api.get(`/api/orders/buyable`, {
        params: {
          symbol,
          price: String(price),
          account_id: accountId!,
        },
      }),
    enabled: !!accountId && !!symbol && price > 0,
    staleTime: 5000,
  });
}
