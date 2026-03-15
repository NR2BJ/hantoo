"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { useTradingStore } from "@/stores/trading-store";
import type {
  OverseasOrderCreate,
  OverseasOrderModify,
  OverseasOrderResponse,
  OverseasFilledOrder,
  OverseasBuyableAmount,
} from "@/types/market";

function useAccountId() {
  return useTradingStore((s) => s.activeAccountId);
}

export function usePlaceOverseasOrder() {
  const accountId = useAccountId();
  const qc = useQueryClient();

  return useMutation<OverseasOrderResponse, Error, OverseasOrderCreate>({
    mutationFn: (order) =>
      api.post(`/api/overseas/orders`, order, {
        params: { account_id: accountId! },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["overseasFilledOrders"] });
    },
  });
}

export function useModifyOverseasOrder() {
  const accountId = useAccountId();
  const qc = useQueryClient();

  return useMutation<
    OverseasOrderResponse,
    Error,
    { tradeId: string; data: OverseasOrderModify }
  >({
    mutationFn: ({ tradeId, data }) =>
      api.put(`/api/overseas/orders/${tradeId}`, data, {
        params: { account_id: accountId! },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["overseasFilledOrders"] });
    },
  });
}

export function useCancelOverseasOrder() {
  const accountId = useAccountId();
  const qc = useQueryClient();

  return useMutation<OverseasOrderResponse, Error, string>({
    mutationFn: (tradeId) =>
      api.delete(`/api/overseas/orders/${tradeId}`, {
        params: { account_id: accountId! },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["overseasFilledOrders"] });
    },
  });
}

export function useOverseasFilledOrders() {
  const accountId = useAccountId();
  return useQuery<OverseasFilledOrder[]>({
    queryKey: ["overseasFilledOrders", accountId],
    queryFn: () =>
      api.get(`/api/overseas/orders/filled`, {
        params: { account_id: accountId! },
      }),
    enabled: !!accountId,
    staleTime: 10000,
  });
}

export function useOverseasBuyable(
  symbol: string,
  exchange: string,
  price: number,
) {
  const accountId = useAccountId();
  return useQuery<OverseasBuyableAmount>({
    queryKey: ["overseasBuyable", symbol, exchange, price, accountId],
    queryFn: () =>
      api.get(`/api/overseas/orders/buyable`, {
        params: {
          symbol,
          exchange,
          price: String(price),
          account_id: accountId!,
        },
      }),
    enabled: !!accountId && !!symbol && !!exchange && price > 0,
    staleTime: 5000,
  });
}
