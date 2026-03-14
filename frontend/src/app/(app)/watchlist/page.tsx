"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  useWatchlists,
  useWatchlistQuotes,
  useCreateWatchlist,
  useDeleteWatchlist,
  useAddWatchlistItem,
  useRemoveWatchlistItem,
} from "@/hooks/use-watchlist";
import { useSearch } from "@/hooks/use-market";
import { getPriceColor, getPriceSign } from "@/types/market";

export default function WatchlistPage() {
  const router = useRouter();
  const { data: watchlists } = useWatchlists();
  const [activeWlId, setActiveWlId] = useState<string | null>(null);
  const [newName, setNewName] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [showSearch, setShowSearch] = useState(false);

  const createWl = useCreateWatchlist();
  const deleteWl = useDeleteWatchlist();
  const addItem = useAddWatchlistItem();
  const removeItem = useRemoveWatchlistItem();
  const { data: searchResults } = useSearch(searchQuery);

  // Auto-select first watchlist
  const selectedId = activeWlId ?? watchlists?.[0]?.id ?? null;
  const { data: wlWithQuotes } = useWatchlistQuotes(selectedId);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    const wl = await createWl.mutateAsync(newName.trim());
    setNewName("");
    setActiveWlId(wl.id);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">관심 종목</h2>
        <button
          onClick={() => setShowSearch(!showSearch)}
          className="px-3 py-1.5 text-sm rounded-lg bg-[var(--primary)] text-white hover:opacity-90"
        >
          {showSearch ? "닫기" : "종목 추가"}
        </button>
      </div>

      {/* Search to add */}
      {showSearch && selectedId && (
        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
          <input
            type="text"
            placeholder="추가할 종목 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
            autoFocus
          />
          {searchResults && searchResults.length > 0 && (
            <div className="mt-2 divide-y divide-[var(--border)] max-h-48 overflow-y-auto">
              {searchResults.map((r) => (
                <button
                  key={r.symbol}
                  onClick={() => {
                    addItem.mutate({
                      watchlistId: selectedId,
                      symbol: r.symbol,
                      market: r.market,
                    });
                    setSearchQuery("");
                    setShowSearch(false);
                  }}
                  className="w-full flex items-center justify-between py-2 px-1 hover:bg-[var(--secondary)] rounded text-left text-sm"
                >
                  <span>
                    {r.name} <span className="text-[var(--muted-foreground)]">{r.symbol}</span>
                  </span>
                  <span className="text-xs text-[var(--muted-foreground)]">{r.market}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Watchlist Tabs */}
      <div className="flex gap-2 items-center flex-wrap">
        {watchlists?.map((wl) => (
          <button
            key={wl.id}
            onClick={() => setActiveWlId(wl.id)}
            className={`px-3 py-1.5 text-sm rounded-lg ${
              selectedId === wl.id
                ? "bg-[var(--primary)] text-white"
                : "bg-[var(--secondary)] text-[var(--muted-foreground)] hover:bg-[var(--border)]"
            }`}
          >
            {wl.name} ({wl.items.length})
          </button>
        ))}
        {/* Create new */}
        <div className="flex gap-1">
          <input
            type="text"
            placeholder="새 목록..."
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            className="px-2 py-1 text-sm rounded-lg bg-[var(--input)] border border-[var(--border)] w-28 focus:outline-none focus:ring-1 focus:ring-[var(--ring)]"
          />
          <button
            onClick={handleCreate}
            disabled={!newName.trim()}
            className="px-2 py-1 text-sm rounded-lg bg-[var(--secondary)] hover:bg-[var(--border)] disabled:opacity-50"
          >
            +
          </button>
        </div>
      </div>

      {/* Watchlist Table */}
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)]">
        {wlWithQuotes && wlWithQuotes.items.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                  <th className="text-left p-3">종목</th>
                  <th className="text-right p-3">현재가</th>
                  <th className="text-right p-3">등락</th>
                  <th className="text-right p-3">등락률</th>
                  <th className="text-right p-3">거래량</th>
                  <th className="text-center p-3"></th>
                </tr>
              </thead>
              <tbody>
                {wlWithQuotes.items.map((item) => {
                  const q = item.quote;
                  const color = q ? getPriceColor(q.change_sign) : "";
                  return (
                    <tr
                      key={item.id}
                      className="border-b border-[var(--border)] hover:bg-[var(--secondary)] cursor-pointer"
                      onClick={() => router.push(`/market/${item.symbol}`)}
                    >
                      <td className="p-3">
                        <div className="font-medium">{q?.name ?? item.symbol}</div>
                        <div className="text-xs text-[var(--muted-foreground)]">
                          {item.symbol} · {item.market}
                        </div>
                      </td>
                      <td className={`text-right p-3 font-mono ${color}`}>
                        {q?.current_price.toLocaleString() ?? "--"}
                      </td>
                      <td className={`text-right p-3 font-mono ${color}`}>
                        {q ? `${getPriceSign(q.change)}${q.change.toLocaleString()}` : "--"}
                      </td>
                      <td className={`text-right p-3 font-mono ${color}`}>
                        {q ? `${getPriceSign(q.change)}${q.change_rate.toFixed(2)}%` : "--"}
                      </td>
                      <td className="text-right p-3 font-mono text-[var(--muted-foreground)]">
                        {q?.volume.toLocaleString() ?? "--"}
                      </td>
                      <td className="text-center p-3">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            removeItem.mutate({
                              watchlistId: selectedId!,
                              itemId: item.id,
                            });
                          }}
                          className="text-[var(--muted-foreground)] hover:text-[var(--destructive)] text-xs"
                        >
                          삭제
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-[var(--muted-foreground)]">
            {selectedId ? "종목을 추가해보세요" : "관심종목 목록을 만들어보세요"}
          </div>
        )}
      </div>

      {/* Delete watchlist */}
      {selectedId && (
        <button
          onClick={() => {
            if (confirm("이 관심종목 목록을 삭제하시겠습니까?")) {
              deleteWl.mutate(selectedId);
              setActiveWlId(null);
            }
          }}
          className="text-sm text-[var(--destructive)] hover:underline"
        >
          현재 목록 삭제
        </button>
      )}
    </div>
  );
}
