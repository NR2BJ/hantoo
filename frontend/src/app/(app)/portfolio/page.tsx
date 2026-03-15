"use client";

import { useRouter } from "next/navigation";
import { useBalance, useHoldings } from "@/hooks/use-portfolio";
import { getPriceColor } from "@/types/market";

export default function PortfolioPage() {
  const router = useRouter();
  const { data: balance } = useBalance();
  const { data: holdings } = useHoldings();

  // Calculate weight percentages for holdings
  const totalStockValue = holdings?.reduce((sum, h) => sum + h.value, 0) ?? 0;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">포트폴리오</h2>

      {/* Account Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard
          title="총 평가금액"
          value={balance ? `${balance.total_value.toLocaleString()}원` : "--"}
        />
        <SummaryCard
          title="총 손익"
          value={
            balance
              ? `${balance.total_pnl >= 0 ? "+" : ""}${balance.total_pnl.toLocaleString()}원`
              : "--"
          }
          sub={
            balance
              ? `${balance.total_pnl_rate >= 0 ? "+" : ""}${balance.total_pnl_rate.toFixed(2)}%`
              : undefined
          }
          color={
            balance
              ? balance.total_pnl > 0
                ? "text-red-500"
                : balance.total_pnl < 0
                  ? "text-blue-500"
                  : undefined
              : undefined
          }
        />
        <SummaryCard
          title="주식 평가"
          value={balance ? `${balance.stock_value.toLocaleString()}원` : "--"}
        />
        <SummaryCard
          title="예수금"
          value={balance ? `${balance.cash.toLocaleString()}원` : "--"}
        />
      </div>

      {/* Asset Allocation Bar */}
      {balance && balance.total_value > 0 && (
        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
          <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-3">
            자산 배분
          </h3>
          <div className="flex h-6 rounded-full overflow-hidden bg-[var(--secondary)]">
            {balance.stock_value > 0 && (
              <div
                className="bg-[var(--primary)] flex items-center justify-center text-xs text-white font-medium"
                style={{
                  width: `${((balance.stock_value / balance.total_value) * 100).toFixed(1)}%`,
                }}
              >
                {((balance.stock_value / balance.total_value) * 100).toFixed(1)}%
              </div>
            )}
            {balance.cash > 0 && (
              <div
                className="bg-emerald-500 flex items-center justify-center text-xs text-white font-medium"
                style={{
                  width: `${((balance.cash / balance.total_value) * 100).toFixed(1)}%`,
                }}
              >
                {((balance.cash / balance.total_value) * 100).toFixed(1)}%
              </div>
            )}
          </div>
          <div className="flex gap-4 mt-2 text-xs text-[var(--muted-foreground)]">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-[var(--primary)]" />
              주식
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              현금
            </span>
          </div>
        </div>
      )}

      {/* Holdings Detail Table */}
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)]">
        <div className="p-4 border-b border-[var(--border)]">
          <h3 className="text-lg font-medium">보유 종목</h3>
        </div>
        {holdings && holdings.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                  <th className="text-left p-3">종목</th>
                  <th className="text-right p-3">현재가</th>
                  <th className="text-right p-3">평균단가</th>
                  <th className="text-right p-3">수량</th>
                  <th className="text-right p-3">평가금액</th>
                  <th className="text-right p-3">손익</th>
                  <th className="text-right p-3">수익률</th>
                  <th className="text-right p-3">비중</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((h) => {
                  const pnlColor =
                    h.pnl > 0
                      ? "text-red-500"
                      : h.pnl < 0
                        ? "text-blue-500"
                        : "";
                  const weight =
                    totalStockValue > 0
                      ? ((h.value / totalStockValue) * 100).toFixed(1)
                      : "0.0";
                  return (
                    <tr
                      key={h.symbol}
                      className="border-b border-[var(--border)] hover:bg-[var(--secondary)] cursor-pointer"
                      onClick={() => router.push(`/market/${h.symbol}`)}
                    >
                      <td className="p-3">
                        <div className="font-medium">{h.name}</div>
                        <div className="text-xs text-[var(--muted-foreground)]">
                          {h.symbol}
                        </div>
                      </td>
                      <td className="text-right p-3 font-mono">
                        {h.current_price.toLocaleString()}
                      </td>
                      <td className="text-right p-3 font-mono">
                        {h.avg_price.toLocaleString()}
                      </td>
                      <td className="text-right p-3 font-mono">
                        {h.quantity.toLocaleString()}
                      </td>
                      <td className="text-right p-3 font-mono">
                        {h.value.toLocaleString()}
                      </td>
                      <td className={`text-right p-3 font-mono ${pnlColor}`}>
                        {h.pnl >= 0 ? "+" : ""}
                        {h.pnl.toLocaleString()}
                      </td>
                      <td className={`text-right p-3 font-mono ${pnlColor}`}>
                        {h.pnl_rate >= 0 ? "+" : ""}
                        {h.pnl_rate.toFixed(2)}%
                      </td>
                      <td className="text-right p-3">
                        <div className="flex items-center justify-end gap-2">
                          <div className="w-16 h-2 rounded-full bg-[var(--secondary)] overflow-hidden">
                            <div
                              className="h-full bg-[var(--primary)] rounded-full"
                              style={{ width: `${weight}%` }}
                            />
                          </div>
                          <span className="text-xs text-[var(--muted-foreground)] w-10 text-right">
                            {weight}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-[var(--muted-foreground)] text-sm">
            {balance
              ? "보유 종목이 없습니다"
              : "KIS 계좌를 선택하면 보유 종목이 표시됩니다"}
          </div>
        )}
      </div>
    </div>
  );
}

function SummaryCard({
  title,
  value,
  sub,
  color,
}: {
  title: string;
  value: string;
  sub?: string;
  color?: string;
}) {
  return (
    <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
      <p className="text-sm text-[var(--muted-foreground)]">{title}</p>
      <p className={`text-2xl font-bold mt-1 ${color ?? ""}`}>{value}</p>
      {sub && (
        <p
          className={`text-sm mt-0.5 ${color ?? "text-[var(--muted-foreground)]"}`}
        >
          {sub}
        </p>
      )}
    </div>
  );
}
