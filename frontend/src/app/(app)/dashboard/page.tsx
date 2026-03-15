"use client";

import { useRouter } from "next/navigation";
import { useIndices } from "@/hooks/use-market";
import { useBalance, useHoldings } from "@/hooks/use-portfolio";
import { getPriceColor, getPriceSign } from "@/types/market";

export default function DashboardPage() {
  const router = useRouter();
  const { data: indices } = useIndices();
  const { data: balance } = useBalance();
  const { data: holdings } = useHoldings();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">대시보드</h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard
          title="총 자산"
          value={balance ? `${balance.total_value.toLocaleString()}원` : "--"}
        />
        <SummaryCard
          title="총 손익"
          value={
            balance
              ? `${balance.total_pnl >= 0 ? "+" : ""}${balance.total_pnl.toLocaleString()}원`
              : "--"
          }
          sub={balance ? `${balance.total_pnl_rate >= 0 ? "+" : ""}${balance.total_pnl_rate.toFixed(2)}%` : undefined}
          color={balance ? (balance.total_pnl > 0 ? "text-red-500" : balance.total_pnl < 0 ? "text-blue-500" : undefined) : undefined}
        />
        <SummaryCard
          title="보유 종목"
          value={balance ? `${balance.holding_count}종목` : "--"}
        />
        <SummaryCard
          title="예수금"
          value={balance ? `${balance.cash.toLocaleString()}원` : "--"}
        />
      </div>

      {/* Market Indices */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {indices ? (
          indices.map((idx) => (
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
          ))
        ) : (
          <>
            {["KOSPI", "KOSDAQ", "KOSPI200"].map((name) => (
              <div
                key={name}
                className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4"
              >
                <p className="text-sm text-[var(--muted-foreground)]">{name}</p>
                <p className="text-lg font-bold mt-1 text-[var(--muted-foreground)]">--</p>
                <p className="text-sm text-[var(--muted-foreground)]">
                  KIS 계좌를 선택하세요
                </p>
              </div>
            ))}
          </>
        )}
      </div>

      {/* Holdings Table */}
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
                  <th className="text-right p-3">수량</th>
                  <th className="text-right p-3">평가금액</th>
                  <th className="text-right p-3">손익</th>
                  <th className="text-right p-3">수익률</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((h) => {
                  const pnlColor = h.pnl > 0 ? "text-red-500" : h.pnl < 0 ? "text-blue-500" : "";
                  return (
                    <tr
                      key={h.symbol}
                      className="border-b border-[var(--border)] hover:bg-[var(--secondary)] cursor-pointer"
                      onClick={() => router.push(`/market/${h.symbol}`)}
                    >
                      <td className="p-3">
                        <div className="font-medium">{h.name}</div>
                        <div className="text-xs text-[var(--muted-foreground)]">{h.symbol}</div>
                      </td>
                      <td className="text-right p-3 font-mono">{h.current_price.toLocaleString()}</td>
                      <td className="text-right p-3 font-mono">{h.quantity.toLocaleString()}</td>
                      <td className="text-right p-3 font-mono">{h.value.toLocaleString()}</td>
                      <td className={`text-right p-3 font-mono ${pnlColor}`}>
                        {h.pnl >= 0 ? "+" : ""}{h.pnl.toLocaleString()}
                      </td>
                      <td className={`text-right p-3 font-mono ${pnlColor}`}>
                        {h.pnl_rate >= 0 ? "+" : ""}{h.pnl_rate.toFixed(2)}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-[var(--muted-foreground)] text-sm">
            {balance ? "보유 종목이 없습니다" : "KIS 계좌를 선택하면 보유 종목이 표시됩니다"}
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
      {sub && <p className={`text-sm mt-0.5 ${color ?? "text-[var(--muted-foreground)]"}`}>{sub}</p>}
    </div>
  );
}
