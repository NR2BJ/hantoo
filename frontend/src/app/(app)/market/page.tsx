"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useIndices, useSearch } from "@/hooks/use-market";
import { api } from "@/lib/api-client";
import {
  useVolumeRank,
  useFluctuation,
  useMarketCapRank,
  useTopInterest,
  useNearHighLow,
  useForeignInstitution,
} from "@/hooks/use-ranking";
import { useDividendRateRanking } from "@/hooks/use-analysis";
import { getPriceColor, getPriceSign } from "@/types/market";
import type { RankItem } from "@/types/market";

type RankTab = "volume" | "updown" | "marketcap" | "interest" | "highlow" | "foreign" | "dividend";

const rankTabs: { key: RankTab; label: string }[] = [
  { key: "volume", label: "거래량" },
  { key: "updown", label: "등락률" },
  { key: "marketcap", label: "시가총액" },
  { key: "interest", label: "관심종목" },
  { key: "highlow", label: "52주 신고/저" },
  { key: "foreign", label: "외인/기관" },
  { key: "dividend", label: "배당률" },
];

export default function MarketPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [query, setQuery] = useState("");
  const [market, setMarket] = useState<"J" | "Q">("J");
  const [rankTab, setRankTab] = useState<RankTab>("volume");
  const [refreshing, setRefreshing] = useState(false);
  const { data: indices } = useIndices();
  const { data: results, isLoading: searching } = useSearch(query);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await api.post("/api/cache/flush", undefined, { params: { scope: "ranking" } });
      await queryClient.invalidateQueries({ predicate: (q) => {
        const key = q.queryKey;
        return key[0] === "ranking" || key[0] === "corporate" || key[0] === "indices";
      }});
    } finally {
      setRefreshing(false);
    }
  }, [queryClient]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">시장 정보</h2>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="px-3 py-1 text-xs rounded border border-[var(--border)] hover:bg-[var(--secondary)] disabled:opacity-50 transition-colors"
        >
          {refreshing ? "갱신 중..." : "새로고침"}
        </button>
      </div>

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

      {/* Rankings */}
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-medium">순위</h3>
          <div className="flex gap-2">
            <button
              onClick={() => setMarket("J")}
              className={`px-3 py-1 text-xs rounded ${market === "J" ? "bg-[var(--primary)] text-white" : "bg-[var(--secondary)]"}`}
            >
              코스피
            </button>
            <button
              onClick={() => setMarket("Q")}
              className={`px-3 py-1 text-xs rounded ${market === "Q" ? "bg-[var(--primary)] text-white" : "bg-[var(--secondary)]"}`}
            >
              코스닥
            </button>
          </div>
        </div>

        {/* Rank Tabs */}
        <div className="flex gap-1 border-b border-[var(--border)] overflow-x-auto mb-3">
          {rankTabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setRankTab(t.key)}
              className={`px-3 py-1.5 text-xs whitespace-nowrap border-b-2 transition-colors ${
                rankTab === t.key
                  ? "border-[var(--primary)] text-[var(--foreground)] font-medium"
                  : "border-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {rankTab === "volume" && <VolumeRankSection market={market} />}
        {rankTab === "updown" && <FluctuationSection market={market} />}
        {rankTab === "marketcap" && <MarketCapSection market={market} />}
        {rankTab === "interest" && <InterestSection market={market} />}
        {rankTab === "highlow" && <HighLowSection market={market} />}
        {rankTab === "foreign" && <ForeignSection market={market} />}
        {rankTab === "dividend" && <DividendRankSection market={market} />}
      </div>
    </div>
  );
}

/* ─── Ranking Sections ─── */

function VolumeRankSection({ market }: { market: string }) {
  const { data, isLoading, error } = useVolumeRank(market);
  return <RankTable data={data} loading={isLoading} error={error} label="거래량 순위" />;
}

function FluctuationSection({ market }: { market: string }) {
  const [sort, setSort] = useState("1"); // 1=상승, 2=하락
  const { data, isLoading, error } = useFluctuation(market, sort);
  return (
    <div>
      <div className="flex gap-2 mb-2">
        <button onClick={() => setSort("1")} className={`px-2 py-0.5 text-xs rounded ${sort === "1" ? "bg-red-500 text-white" : "bg-[var(--secondary)]"}`}>상승</button>
        <button onClick={() => setSort("2")} className={`px-2 py-0.5 text-xs rounded ${sort === "2" ? "bg-blue-500 text-white" : "bg-[var(--secondary)]"}`}>하락</button>
      </div>
      <RankTable data={data} loading={isLoading} error={error} label="등락률 순위" />
    </div>
  );
}

function MarketCapSection({ market }: { market: string }) {
  const { data, isLoading, error } = useMarketCapRank(market);
  return <RankTable data={data} loading={isLoading} error={error} label="시가총액 순위" />;
}

function InterestSection({ market }: { market: string }) {
  const { data, isLoading, error } = useTopInterest(market);
  return <RankTable data={data} loading={isLoading} error={error} label="관심종목 순위" />;
}

function HighLowSection({ market }: { market: string }) {
  const [sort, setSort] = useState("1");
  const { data, isLoading, error } = useNearHighLow(market, sort);
  return (
    <div>
      <div className="flex gap-2 mb-2">
        <button onClick={() => setSort("1")} className={`px-2 py-0.5 text-xs rounded ${sort === "1" ? "bg-red-500 text-white" : "bg-[var(--secondary)]"}`}>신고가</button>
        <button onClick={() => setSort("2")} className={`px-2 py-0.5 text-xs rounded ${sort === "2" ? "bg-blue-500 text-white" : "bg-[var(--secondary)]"}`}>신저가</button>
      </div>
      <RankTable data={data} loading={isLoading} error={error} label="52주 신고/저가" />
    </div>
  );
}

function ForeignSection({ market }: { market: string }) {
  const { data, isLoading, error } = useForeignInstitution(market);
  return <RankTable data={data} loading={isLoading} error={error} label="외인/기관 순매수" />;
}

function DividendRankSection({ market }: { market: string }) {
  const { data, isLoading, error } = useDividendRateRanking(market);
  const router = useRouter();

  if (isLoading) return <p className="text-sm text-[var(--muted-foreground)]">로딩 중...</p>;
  if (error) return <p className="text-sm text-red-500">오류: {(error as Error).message}</p>;
  if (!data || data.length === 0) return <p className="text-sm text-[var(--muted-foreground)]">데이터 없음</p>;

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="text-[var(--muted-foreground)] border-b border-[var(--border)]">
          <th className="text-left py-1 w-8">#</th>
          <th className="text-left py-1">종목</th>
          <th className="text-right py-1">현재가</th>
          <th className="text-right py-1">배당률</th>
          <th className="text-right py-1">배당금</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr
            key={row.symbol}
            className="border-b border-[var(--border)] cursor-pointer hover:bg-[var(--secondary)]"
            onClick={() => router.push(`/market/${row.symbol}`)}
          >
            <td className="py-1 text-[var(--muted-foreground)]">{row.rank}</td>
            <td className="py-1">
              <span className="font-medium">{row.name}</span>
              <span className="text-xs text-[var(--muted-foreground)] ml-1">{row.symbol}</span>
            </td>
            <td className="text-right">{row.current_price.toLocaleString()}</td>
            <td className="text-right text-green-500">{row.div_rate.toFixed(2)}%</td>
            <td className="text-right">{row.dps?.toLocaleString() ?? "-"}원</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/* ─── Shared RankTable ─── */

function RankTable({
  data,
  loading,
  error,
  label,
}: {
  data: RankItem[] | undefined;
  loading: boolean;
  error: Error | null;
  label: string;
}) {
  const router = useRouter();

  if (loading) return <p className="text-sm text-[var(--muted-foreground)]">로딩 중...</p>;
  if (error) return <p className="text-sm text-red-500">오류: {error.message}</p>;
  if (!data || data.length === 0) return <p className="text-sm text-[var(--muted-foreground)]">{label}: 데이터 없음</p>;

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="text-[var(--muted-foreground)] border-b border-[var(--border)]">
          <th className="text-left py-1 w-8">#</th>
          <th className="text-left py-1">종목</th>
          <th className="text-right py-1">현재가</th>
          <th className="text-right py-1">등락률</th>
          <th className="text-right py-1">거래량</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr
            key={row.symbol}
            className="border-b border-[var(--border)] cursor-pointer hover:bg-[var(--secondary)]"
            onClick={() => router.push(`/market/${row.symbol}`)}
          >
            <td className="py-1 text-[var(--muted-foreground)]">{row.rank}</td>
            <td className="py-1">
              <span className="font-medium">{row.name}</span>
              <span className="text-xs text-[var(--muted-foreground)] ml-1">{row.symbol}</span>
            </td>
            <td className="text-right">{row.current_price.toLocaleString()}</td>
            <td className={`text-right ${getPriceColor(row.change_sign)}`}>
              {getPriceSign(row.change)}{row.change_rate.toFixed(2)}%
            </td>
            <td className="text-right">{row.volume.toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
