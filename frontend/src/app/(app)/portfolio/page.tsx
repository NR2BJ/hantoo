"use client";

import { useRouter } from "next/navigation";
import { useBalance, useHoldings, useOverseasHoldings } from "@/hooks/use-portfolio";

const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: "$",
  HKD: "HK$",
  JPY: "¥",
  CNY: "¥",
  EUR: "€",
  GBP: "£",
};

function fmtCurrency(val: number, currency: string, decimals = 2): string {
  const sym = CURRENCY_SYMBOLS[currency] ?? currency + " ";
  return `${sym}${val.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`;
}

export default function PortfolioPage() {
  const router = useRouter();
  const { data: balance, error: balanceError } = useBalance();
  const { data: holdings } = useHoldings();
  const { data: overseasHoldings } = useOverseasHoldings();

  // Calculate weight percentages for holdings
  const totalStockValue = holdings?.reduce((sum, h) => sum + h.value, 0) ?? 0;

  const isUnsupportedAccount =
    balanceError && typeof balanceError === "object" && "message" in balanceError
      ? String((balanceError as { message?: string }).message).includes("금융상품")
      : false;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">포트폴리오</h2>

      {/* Unsupported account warning */}
      {isUnsupportedAccount && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 text-sm text-yellow-600">
          금융상품 계좌는 잔고 조회를 지원하지 않습니다. 위탁계좌(상품코드 01)를 선택해주세요.
        </div>
      )}

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
          title="주식 평가 (국내)"
          value={balance ? `${balance.stock_value.toLocaleString()}원` : "--"}
        />
        <SummaryCard
          title="예수금 (원화)"
          value={balance ? `${balance.cash.toLocaleString()}원` : "--"}
        />
      </div>

      {/* Foreign Currency Balances */}
      {balance && balance.foreign_balances.length > 0 && (
        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
          <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-3">
            외화 자산
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {balance.foreign_balances.map((fb) => (
              <div
                key={fb.currency}
                className="bg-[var(--secondary)] rounded-lg p-3"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium">{fb.currency}</span>
                  {fb.exchange_rate > 0 && (
                    <span className="text-xs text-[var(--muted-foreground)]">
                      환율 {fb.exchange_rate.toLocaleString()}원
                    </span>
                  )}
                </div>
                <div className="space-y-0.5 text-sm">
                  <div className="flex justify-between">
                    <span className="text-[var(--muted-foreground)]">예수금</span>
                    <span className="font-mono">
                      {fmtCurrency(fb.deposit, fb.currency)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[var(--muted-foreground)]">주식평가</span>
                    <span className="font-mono">
                      {fmtCurrency(fb.stock_value, fb.currency)}
                    </span>
                  </div>
                  <div className="flex justify-between font-medium pt-1 border-t border-[var(--border)]">
                    <span>합계</span>
                    <span className="font-mono">
                      {fmtCurrency(fb.total_value, fb.currency)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {balance.overseas_total_krw > 0 && (
            <p className="text-xs text-[var(--muted-foreground)] mt-2">
              해외주식 원화환산 합계: {balance.overseas_total_krw.toLocaleString()}원
            </p>
          )}
        </div>
      )}

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
            {balance.overseas_total_krw > 0 && (
              <div
                className="bg-amber-500 flex items-center justify-center text-xs text-white font-medium"
                style={{
                  width: `${((balance.overseas_total_krw / balance.total_value) * 100).toFixed(1)}%`,
                }}
              >
                {((balance.overseas_total_krw / balance.total_value) * 100).toFixed(1)}%
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
              국내주식
            </span>
            {balance.overseas_total_krw > 0 && (
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                해외주식
              </span>
            )}
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              현금
            </span>
          </div>
        </div>
      )}

      {/* Domestic Holdings Table */}
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)]">
        <div className="p-4 border-b border-[var(--border)]">
          <h3 className="text-lg font-medium">국내 보유 종목</h3>
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
              ? "국내 보유 종목이 없습니다"
              : "KIS 계좌를 선택하면 보유 종목이 표시됩니다"}
          </div>
        )}
      </div>

      {/* Overseas Holdings Table */}
      {overseasHoldings && overseasHoldings.length > 0 && (
        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)]">
          <div className="p-4 border-b border-[var(--border)]">
            <h3 className="text-lg font-medium">해외 보유 종목</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                  <th className="text-left p-3">종목</th>
                  <th className="text-center p-3">시장</th>
                  <th className="text-right p-3">현재가</th>
                  <th className="text-right p-3">평균단가</th>
                  <th className="text-right p-3">수량</th>
                  <th className="text-right p-3">평가금액</th>
                  <th className="text-right p-3">손익</th>
                  <th className="text-right p-3">수익률</th>
                  <th className="text-right p-3">환율</th>
                </tr>
              </thead>
              <tbody>
                {overseasHoldings.map((h) => {
                  const pnlColor =
                    h.pnl_foreign > 0
                      ? "text-red-500"
                      : h.pnl_foreign < 0
                        ? "text-blue-500"
                        : "";
                  return (
                    <tr
                      key={h.symbol}
                      className="border-b border-[var(--border)] hover:bg-[var(--secondary)]"
                    >
                      <td className="p-3">
                        <div className="font-medium">{h.name}</div>
                        <div className="text-xs text-[var(--muted-foreground)]">
                          {h.symbol}
                        </div>
                      </td>
                      <td className="text-center p-3 text-xs text-[var(--muted-foreground)]">
                        {h.market}
                      </td>
                      <td className="text-right p-3 font-mono">
                        {fmtCurrency(h.current_price, h.currency)}
                      </td>
                      <td className="text-right p-3 font-mono">
                        {fmtCurrency(h.avg_price, h.currency)}
                      </td>
                      <td className="text-right p-3 font-mono">
                        {h.quantity.toLocaleString()}
                      </td>
                      <td className="text-right p-3 font-mono">
                        {fmtCurrency(h.value_foreign, h.currency)}
                      </td>
                      <td className={`text-right p-3 font-mono ${pnlColor}`}>
                        {h.pnl_foreign >= 0 ? "+" : ""}
                        {fmtCurrency(h.pnl_foreign, h.currency)}
                      </td>
                      <td className={`text-right p-3 font-mono ${pnlColor}`}>
                        {h.pnl_rate >= 0 ? "+" : ""}
                        {h.pnl_rate.toFixed(2)}%
                      </td>
                      <td className="text-right p-3 font-mono text-xs text-[var(--muted-foreground)]">
                        {h.exchange_rate > 0
                          ? `₩${h.exchange_rate.toLocaleString()}`
                          : "--"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
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
