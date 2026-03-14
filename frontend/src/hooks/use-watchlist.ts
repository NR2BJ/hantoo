"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { useTradingStore } from "@/stores/trading-store";
import type { Watchlist } from "@/types/market";

export function useWatchlists() {
  return useQuery<Watchlist[]>({
    queryKey: ["watchlists"],
    queryFn: () => api.get("/api/watchlists"),
  });
}

export function useWatchlistQuotes(watchlistId: string | null) {
  const accountId = useTradingStore((s) => s.activeAccountId);
  return useQuery<Watchlist>({
    queryKey: ["watchlistQuotes", watchlistId, accountId],
    queryFn: () =>
      api.get(`/api/watchlists/${watchlistId}/quotes`, {
        params: { account_id: accountId! },
      }),
    enabled: !!watchlistId && !!accountId,
    refetchInterval: 5000,
    staleTime: 3000,
  });
}

export function useCreateWatchlist() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (name: string) =>
      api.post<Watchlist>("/api/watchlists", { name }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlists"] }),
  });
}

export function useRenameWatchlist() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, name }: { id: string; name: string }) =>
      api.put<Watchlist>(`/api/watchlists/${id}`, { name }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlists"] }),
  });
}

export function useDeleteWatchlist() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`/api/watchlists/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlists"] }),
  });
}

export function useAddWatchlistItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      watchlistId,
      symbol,
      market,
    }: {
      watchlistId: string;
      symbol: string;
      market: string;
    }) =>
      api.post(`/api/watchlists/${watchlistId}/items`, { symbol, market }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["watchlists"] });
      qc.invalidateQueries({ queryKey: ["watchlistQuotes"] });
    },
  });
}

export function useRemoveWatchlistItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      watchlistId,
      itemId,
    }: {
      watchlistId: string;
      itemId: string;
    }) => api.delete(`/api/watchlists/${watchlistId}/items/${itemId}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["watchlists"] });
      qc.invalidateQueries({ queryKey: ["watchlistQuotes"] });
    },
  });
}
