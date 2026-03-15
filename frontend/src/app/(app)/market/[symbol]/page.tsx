"use client";

import { use, useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useQuote, useOrderbook, useTrades } from "@/hooks/use-market";
import {
  useIncomeStatement,
  useBalanceSheet,
  useFinancialRatio,
  useEstimate,
  useInvestOpinion,
  useDividend,
  useNews,
  useStockInfo,
} from "@/hooks/use-analysis";
import { useInvestor } from "@/hooks/use-ranking";
import { getPriceColor, getPriceSign } from "@/types/market";
import { api } from "@/lib/api-client";
import StockChart from "@/components/charts/stock-chart";

type Tab = "chart" | "finance" | "dividend" | "news" | "opinion" | "investor" | "info";

const tabs: { key: Tab; label: string }[] = [
  { key: "chart", label: "차트/호가" },
  { key: "finance", label: "재무제표" },
  { key: "dividend", label: "배당" },
  { key: "news", label: "뉴스" },
  { key: "opinion", label: "투자의견" },
  { key: "investor", label: "투자자동향" },
  { key: "info", label: "종목정보" },
];

export default function StockDetailPage({
  params,
}: {
  params: Promise<{ symbol: string }>;
}) {
  const { symbol } = use(params);
  const [activeTab, setActiveTab] = useState<Tab>("chart");
  const [refreshing, setRefreshing] = useState(false);
  const { data: quote } = useQuote(symbol);
  const queryClient = useQueryClient();

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await api.post("/api/cache/flush", undefined, { params: { symbol } });
      await queryClient.invalidateQueries({ predicate: (q) => {
        const key = q.queryKey;
        return key.some((k) => k === symbol);
      }});
    } finally {
      setRefreshing(false);
    }
  }, [symbol, queryClient]);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-baseline gap-3">
        <h2 className="text-2xl font-bold">{quote?.name || symbol}</h2>
        <span className="text-[var(--muted-foreground)]">{symbol}</span>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="ml-auto px-3 py-1 text-xs rounded border border-[var(--border)] hover:bg-[var(--secondary)] disabled:opacity-50 transition-colors"
        >
          {refreshing ? "갱신 중..." : "새로고침"}
        </button>
      </div>

      {/* Price */}
      {quote && (
        <div className="flex items-baseline gap-4">
          <span className={`text-3xl font-bold ${getPriceColor(quote.change_sign)}`}>
            {quote.current_price.toLocaleString()}원
          </span>
          <span className={`text-lg ${getPriceColor(quote.change_sign)}`}>
            {getPriceSign(quote.change)}{quote.change.toLocaleString()} ({getPriceSign(quote.change)}{quote.change_rate.toFixed(2)}%)
          </span>
        </div>
      )}

      {/* Stats */}
      {quote && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Stat label="시가" value={quote.open_price.toLocaleString()} />
          <Stat label="고가" value={quote.high_price.toLocaleString()} />
          <Stat label="저가" value={quote.low_price.toLocaleString()} />
          <Stat label="전일종가" value={quote.prev_close.toLocaleString()} />
          <Stat label="거래량" value={quote.volume.toLocaleString()} />
          <Stat label="시가총액" value={quote.market_cap ? `${(quote.market_cap / 100000000).toFixed(0)}억` : "--"} />
          <Stat label="PER" value={quote.per?.toFixed(2) ?? "--"} />
          <Stat label="PBR" value={quote.pbr?.toFixed(2) ?? "--"} />
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 border-b border-[var(--border)] overflow-x-auto">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`px-4 py-2 text-sm whitespace-nowrap border-b-2 transition-colors ${
              activeTab === t.key
                ? "border-[var(--primary)] text-[var(--foreground)] font-medium"
                : "border-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "chart" && <ChartTab symbol={symbol} />}
      {activeTab === "finance" && <FinanceTab symbol={symbol} />}
      {activeTab === "dividend" && <DividendTab symbol={symbol} />}
      {activeTab === "news" && <NewsTab symbol={symbol} />}
      {activeTab === "opinion" && <OpinionTab symbol={symbol} />}
      {activeTab === "investor" && <InvestorTab symbol={symbol} />}
      {activeTab === "info" && <InfoTab symbol={symbol} />}
    </div>
  );
}

/* ─── Chart / Orderbook / Trades (original content) ─── */

function ChartTab({ symbol }: { symbol: string }) {
  const { data: orderbook } = useOrderbook(symbol);
  const { data: trades } = useTrades(symbol);

  return (
    <div className="space-y-4">
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
        <StockChart symbol={symbol} height={400} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
          <h3 className="text-lg font-medium mb-3">호가</h3>
          {orderbook ? (
            <div className="space-y-1 text-sm font-mono">
              {[...orderbook.ask].reverse().map((entry, i) => (
                <div key={`ask-${i}`} className="flex justify-between text-blue-500">
                  <span>{entry.volume.toLocaleString()}</span>
                  <span>{entry.price.toLocaleString()}</span>
                </div>
              ))}
              <div className="border-t border-[var(--border)] my-1" />
              {orderbook.bid.map((entry, i) => (
                <div key={`bid-${i}`} className="flex justify-between text-red-500">
                  <span>{entry.price.toLocaleString()}</span>
                  <span>{entry.volume.toLocaleString()}</span>
                </div>
              ))}
              <div className="flex justify-between text-xs text-[var(--muted-foreground)] mt-2 pt-2 border-t border-[var(--border)]">
                <span>총 매도: {orderbook.total_ask_volume.toLocaleString()}</span>
                <span>총 매수: {orderbook.total_bid_volume.toLocaleString()}</span>
              </div>
            </div>
          ) : (
            <p className="text-[var(--muted-foreground)] text-sm">로딩 중...</p>
          )}
        </div>

        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
          <h3 className="text-lg font-medium mb-3">체결</h3>
          {trades && trades.length > 0 ? (
            <div className="space-y-1 text-sm font-mono max-h-[400px] overflow-y-auto">
              <div className="flex justify-between text-xs text-[var(--muted-foreground)] mb-1">
                <span>시간</span>
                <span>가격</span>
                <span>수량</span>
              </div>
              {trades.map((t, i) => {
                const timeStr = t.time.length >= 6
                  ? `${t.time.slice(0, 2)}:${t.time.slice(2, 4)}:${t.time.slice(4, 6)}`
                  : t.time;
                const color = t.change > 0 ? "text-red-500" : t.change < 0 ? "text-blue-500" : "";
                return (
                  <div key={i} className={`flex justify-between ${color}`}>
                    <span>{timeStr}</span>
                    <span>{t.price.toLocaleString()}</span>
                    <span>{t.volume.toLocaleString()}</span>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-[var(--muted-foreground)] text-sm">체결 데이터 없음 (장 마감 시 비어있을 수 있음)</p>
          )}
        </div>
      </div>
    </div>
  );
}

/* ─── Finance Tab ─── */

function FinanceTab({ symbol }: { symbol: string }) {
  const [period, setPeriod] = useState<"A" | "Q">("A");
  const { data: income, isLoading: incLoading, error: incError } = useIncomeStatement(symbol, period);
  const { data: balance, isLoading: balLoading, error: balError } = useBalanceSheet(symbol, period);
  const { data: ratio, isLoading: ratLoading, error: ratError } = useFinancialRatio(symbol, period);
  const { data: estimate, isLoading: estLoading, error: estError } = useEstimate(symbol);

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <button
          onClick={() => setPeriod("A")}
          className={`px-3 py-1 text-sm rounded ${period === "A" ? "bg-[var(--primary)] text-white" : "bg-[var(--secondary)]"}`}
        >
          연간
        </button>
        <button
          onClick={() => setPeriod("Q")}
          className={`px-3 py-1 text-sm rounded ${period === "Q" ? "bg-[var(--primary)] text-white" : "bg-[var(--secondary)]"}`}
        >
          분기
        </button>
      </div>

      {/* Income Statement */}
      <DataSection title="손익계산서" loading={incLoading} error={incError}>
        {income && income.length > 0 ? (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[var(--muted-foreground)] border-b border-[var(--border)]">
                <th className="text-left py-1">기간</th>
                <th className="text-right py-1">매출액</th>
                <th className="text-right py-1">영업이익</th>
                <th className="text-right py-1">순이익</th>
                <th className="text-right py-1">EPS</th>
              </tr>
            </thead>
            <tbody>
              {income.map((row) => (
                <tr key={row.period} className="border-b border-[var(--border)]">
                  <td className="py-1">{row.period}</td>
                  <td className="text-right">{fmt(row.revenue)}</td>
                  <td className="text-right">{fmt(row.operating_profit)}</td>
                  <td className="text-right">{fmt(row.net_income)}</td>
                  <td className="text-right">{fmt(row.eps)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-sm text-[var(--muted-foreground)]">데이터 없음</p>
        )}
      </DataSection>

      {/* Balance Sheet */}
      <DataSection title="재무상태표" loading={balLoading} error={balError}>
        {balance && balance.length > 0 ? (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[var(--muted-foreground)] border-b border-[var(--border)]">
                <th className="text-left py-1">기간</th>
                <th className="text-right py-1">총자산</th>
                <th className="text-right py-1">총부채</th>
                <th className="text-right py-1">총자본</th>
              </tr>
            </thead>
            <tbody>
              {balance.map((row) => (
                <tr key={row.period} className="border-b border-[var(--border)]">
                  <td className="py-1">{row.period}</td>
                  <td className="text-right">{fmt(row.total_assets)}</td>
                  <td className="text-right">{fmt(row.total_liabilities)}</td>
                  <td className="text-right">{fmt(row.total_equity)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-sm text-[var(--muted-foreground)]">데이터 없음</p>
        )}
      </DataSection>

      {/* Financial Ratio */}
      <DataSection title="재무비율" loading={ratLoading} error={ratError}>
        {ratio && ratio.length > 0 ? (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[var(--muted-foreground)] border-b border-[var(--border)]">
                <th className="text-left py-1">기간</th>
                <th className="text-right py-1">ROE</th>
                <th className="text-right py-1">ROA</th>
                <th className="text-right py-1">PER</th>
                <th className="text-right py-1">PBR</th>
                <th className="text-right py-1">부채비율</th>
              </tr>
            </thead>
            <tbody>
              {ratio.map((row) => (
                <tr key={row.period} className="border-b border-[var(--border)]">
                  <td className="py-1">{row.period}</td>
                  <td className="text-right">{row.roe?.toFixed(2) ?? "-"}</td>
                  <td className="text-right">{row.roa?.toFixed(2) ?? "-"}</td>
                  <td className="text-right">{row.per?.toFixed(2) ?? "-"}</td>
                  <td className="text-right">{row.pbr?.toFixed(2) ?? "-"}</td>
                  <td className="text-right">{row.debt_ratio?.toFixed(2) ?? "-"}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-sm text-[var(--muted-foreground)]">데이터 없음</p>
        )}
      </DataSection>

      {/* Estimates */}
      <DataSection title="실적추정" loading={estLoading} error={estError}>
        {estimate && estimate.length > 0 ? (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[var(--muted-foreground)] border-b border-[var(--border)]">
                <th className="text-left py-1">기간</th>
                <th className="text-right py-1">매출추정</th>
                <th className="text-right py-1">영업이익추정</th>
                <th className="text-right py-1">순이익추정</th>
                <th className="text-right py-1">EPS추정</th>
              </tr>
            </thead>
            <tbody>
              {estimate.map((row) => (
                <tr key={row.period} className="border-b border-[var(--border)]">
                  <td className="py-1">{row.period}</td>
                  <td className="text-right">{fmt(row.revenue_est)}</td>
                  <td className="text-right">{fmt(row.op_profit_est)}</td>
                  <td className="text-right">{fmt(row.net_income_est)}</td>
                  <td className="text-right">{fmt(row.eps_est)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-sm text-[var(--muted-foreground)]">데이터 없음</p>
        )}
      </DataSection>
    </div>
  );
}

/* ─── Dividend Tab ─── */

function DividendTab({ symbol }: { symbol: string }) {
  const { data: dividend, isLoading, error } = useDividend(symbol);

  return (
    <DataSection title="배당 이력" loading={isLoading} error={error}>
      {dividend && dividend.length > 0 ? (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-[var(--muted-foreground)] border-b border-[var(--border)]">
              <th className="text-left py-1">연도</th>
              <th className="text-right py-1">주당배당금</th>
              <th className="text-right py-1">배당률</th>
              <th className="text-right py-1">배당락일</th>
              <th className="text-right py-1">지급일</th>
            </tr>
          </thead>
          <tbody>
            {dividend.map((row) => (
              <tr key={row.year} className="border-b border-[var(--border)]">
                <td className="py-1">{row.year}</td>
                <td className="text-right">{row.dps?.toLocaleString() ?? "-"}원</td>
                <td className="text-right">{row.div_rate?.toFixed(2) ?? "-"}%</td>
                <td className="text-right">{row.ex_date ?? "-"}</td>
                <td className="text-right">{row.pay_date ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="text-sm text-[var(--muted-foreground)]">배당 데이터 없음</p>
      )}
    </DataSection>
  );
}

/* ─── News Tab ─── */

function NewsTab({ symbol }: { symbol: string }) {
  const { data: news, isLoading, error } = useNews(symbol);

  return (
    <DataSection title="관련 뉴스" loading={isLoading} error={error}>
      {news && news.length > 0 ? (
        <div className="space-y-2">
          {news.map((item, i) => (
            <div key={i} className="py-2 border-b border-[var(--border)]">
              <p className="font-medium text-sm">{item.title}</p>
              <div className="flex gap-3 text-xs text-[var(--muted-foreground)] mt-1">
                <span>{item.date} {item.time}</span>
                {item.source && <span>{item.source}</span>}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-[var(--muted-foreground)]">뉴스 없음</p>
      )}
    </DataSection>
  );
}

/* ─── Opinion Tab ─── */

function OpinionTab({ symbol }: { symbol: string }) {
  const { data: opinions, isLoading, error } = useInvestOpinion(symbol);

  return (
    <DataSection title="투자의견" loading={isLoading} error={error}>
      {opinions && opinions.length > 0 ? (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-[var(--muted-foreground)] border-b border-[var(--border)]">
              <th className="text-left py-1">날짜</th>
              <th className="text-left py-1">증권사</th>
              <th className="text-left py-1">의견</th>
              <th className="text-right py-1">목표가</th>
              <th className="text-right py-1">변동</th>
            </tr>
          </thead>
          <tbody>
            {opinions.map((row, i) => (
              <tr key={i} className="border-b border-[var(--border)]">
                <td className="py-1">{row.date}</td>
                <td>{row.firm}</td>
                <td>{row.opinion}</td>
                <td className="text-right">{row.target_price?.toLocaleString() ?? "-"}원</td>
                <td className="text-right">{row.change ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="text-sm text-[var(--muted-foreground)]">투자의견 없음</p>
      )}
    </DataSection>
  );
}

/* ─── Investor Tab ─── */

function InvestorTab({ symbol }: { symbol: string }) {
  const { data: investors, isLoading, error } = useInvestor(symbol);

  return (
    <DataSection title="투자자별 매매동향" loading={isLoading} error={error}>
      {investors && investors.length > 0 ? (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-[var(--muted-foreground)] border-b border-[var(--border)]">
              <th className="text-left py-1">투자자</th>
              <th className="text-right py-1">매수량</th>
              <th className="text-right py-1">매도량</th>
              <th className="text-right py-1">순매수량</th>
              <th className="text-right py-1">순매수금액</th>
            </tr>
          </thead>
          <tbody>
            {investors.map((row, i) => (
              <tr key={i} className="border-b border-[var(--border)]">
                <td className="py-1">{row.investor}</td>
                <td className="text-right">{row.buy_volume.toLocaleString()}</td>
                <td className="text-right">{row.sell_volume.toLocaleString()}</td>
                <td className={`text-right ${row.net_volume > 0 ? "text-red-500" : row.net_volume < 0 ? "text-blue-500" : ""}`}>
                  {row.net_volume.toLocaleString()}
                </td>
                <td className={`text-right ${row.net_amount > 0 ? "text-red-500" : row.net_amount < 0 ? "text-blue-500" : ""}`}>
                  {(row.net_amount / 1000000).toFixed(0)}백만
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="text-sm text-[var(--muted-foreground)]">투자자 동향 없음</p>
      )}
    </DataSection>
  );
}

/* ─── Info Tab ─── */

function InfoTab({ symbol }: { symbol: string }) {
  const { data: info, isLoading, error } = useStockInfo(symbol);

  return (
    <DataSection title="종목 기본정보" loading={isLoading} error={error}>
      {info ? (
        <div className="grid grid-cols-2 gap-3">
          <InfoRow label="종목코드" value={info.symbol} />
          <InfoRow label="종목명" value={info.name} />
          <InfoRow label="시장" value={info.market} />
          <InfoRow label="업종" value={info.sector ?? "-"} />
          <InfoRow label="상장일" value={info.listing_date ?? "-"} />
          <InfoRow label="액면가" value={info.face_value ? `${info.face_value.toLocaleString()}원` : "-"} />
          <InfoRow label="발행주식수" value={info.shares_outstanding?.toLocaleString() ?? "-"} />
          <InfoRow label="자본금" value={info.capital ? `${(info.capital / 100000000).toFixed(0)}억원` : "-"} />
        </div>
      ) : (
        <p className="text-sm text-[var(--muted-foreground)]">종목정보 없음</p>
      )}
    </DataSection>
  );
}

/* ─── Shared Components ─── */

function DataSection({
  title,
  loading,
  error,
  children,
}: {
  title: string;
  loading: boolean;
  error: Error | null;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
      <h3 className="text-lg font-medium mb-3">{title}</h3>
      {loading ? (
        <p className="text-sm text-[var(--muted-foreground)]">로딩 중...</p>
      ) : error ? (
        <p className="text-sm text-red-500">오류: {error.message}</p>
      ) : (
        children
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-3">
      <p className="text-xs text-[var(--muted-foreground)]">{label}</p>
      <p className="font-medium">{value}</p>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="py-1">
      <span className="text-xs text-[var(--muted-foreground)]">{label}</span>
      <p className="font-medium">{value}</p>
    </div>
  );
}

function fmt(v: number | null | undefined): string {
  if (v == null) return "-";
  if (Math.abs(v) >= 100000000) return `${(v / 100000000).toFixed(0)}억`;
  if (Math.abs(v) >= 10000) return `${(v / 10000).toFixed(0)}만`;
  return v.toLocaleString();
}
