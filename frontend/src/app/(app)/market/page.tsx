"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useIndices, useSearch } from "@/hooks/use-market";
import { getPriceColor, getPriceSign } from "@/types/market";

export default function MarketPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const { data: indices } = useIndices();
  const { data: results, isLoading: searching } = useSearch(query);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">시장 정보</h2>

      {/* Market Indices */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {indices?.map((idx) => (
          <div
            key={idx.code}
            className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4"
          >
            <p className="text-sm text-[var(--muted-foreground)]">{idx.name}</p>
            <p className="text-xl font-bold mt-1">{idx.current.toFixed(2)}</p>
            <p className={`text-sm ${getPriceColor(idx.change_sign)}`}>
              {getPriceSign(idx.change)}{idx.change.toFixed(2)} ({getPriceSign(idx.change)}{idx.change_rate.toFixed(2)}%)
            </p>
          </div>
        )) ?? (
          <>
            {["KOSPI", "KOSDAQ", "KOSPI200"].map((name) => (
              <div
                key={name}
                className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4"
              >
                <p className="text-sm text-[var(--muted-foreground)]">{name}</p>
                <p className="text-xl font-bold mt-1 text-[var(--muted-foreground)]">
                  KIS 계좌를 선택하세요
                </p>
              </div>
            ))}
          </>
        )}
      </div>

      {/* Stock Search */}
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
        <h3 className="text-lg font-medium mb-3">종목 검색</h3>
        <input
          type="text"
          placeholder="종목명 또는 종목코드 입력..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
        />

        {query.length > 0 && (
          <div className="mt-3">
            {searching ? (
              <p className="text-sm text-[var(--muted-foreground)]">검색 중...</p>
            ) : results && results.length > 0 ? (
              <div className="divide-y divide-[var(--border)]">
                {results.map((r) => (
                  <button
                    key={r.symbol}
                    onClick={() => router.push(`/market/${r.symbol}`)}
                    className="w-full flex items-center justify-between py-2 px-1 hover:bg-[var(--secondary)] rounded text-left"
                  >
                    <div>
                      <span className="font-medium">{r.name}</span>
                      <span className="text-sm text-[var(--muted-foreground)] ml-2">
                        {r.symbol}
                      </span>
                    </div>
                    <span className="text-xs px-2 py-0.5 rounded bg-[var(--secondary)] text-[var(--muted-foreground)]">
                      {r.market}
                    </span>
                  </button>
                ))}
              </div>
            ) : (
              <p className="text-sm text-[var(--muted-foreground)]">검색 결과가 없습니다</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
