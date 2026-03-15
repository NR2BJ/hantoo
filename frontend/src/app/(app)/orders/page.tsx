"use client";

import { useState } from "react";
import { usePendingOrders, useFilledOrders, useCancelOrder } from "@/hooks/use-orders";

export default function OrdersPage() {
  const [tab, setTab] = useState<"pending" | "filled">("pending");
  const { data: pending, isLoading: loadingPending } = usePendingOrders();
  const { data: filled, isLoading: loadingFilled } = useFilledOrders();
  const cancelOrder = useCancelOrder();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">주문 내역</h2>

      {/* Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setTab("pending")}
          className={`px-4 py-2 text-sm rounded-lg ${
            tab === "pending"
              ? "bg-[var(--primary)] text-white"
              : "bg-[var(--secondary)] text-[var(--muted-foreground)] hover:bg-[var(--border)]"
          }`}
        >
          미체결 {pending ? `(${pending.length})` : ""}
        </button>
        <button
          onClick={() => setTab("filled")}
          className={`px-4 py-2 text-sm rounded-lg ${
            tab === "filled"
              ? "bg-[var(--primary)] text-white"
              : "bg-[var(--secondary)] text-[var(--muted-foreground)] hover:bg-[var(--border)]"
          }`}
        >
          체결 내역 {filled ? `(${filled.length})` : ""}
        </button>
      </div>

      {/* Pending Orders */}
      {tab === "pending" && (
        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)]">
          {loadingPending ? (
            <div className="p-8 text-center text-[var(--muted-foreground)]">로딩 중...</div>
          ) : pending && pending.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                    <th className="text-left p-3">종목</th>
                    <th className="text-center p-3">구분</th>
                    <th className="text-right p-3">주문가격</th>
                    <th className="text-right p-3">주문수량</th>
                    <th className="text-right p-3">미체결</th>
                    <th className="text-center p-3">주문시간</th>
                    <th className="text-center p-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {pending.map((o) => (
                    <tr key={o.order_id} className="border-b border-[var(--border)] hover:bg-[var(--secondary)]">
                      <td className="p-3">
                        <div className="font-medium">{o.name}</div>
                        <div className="text-xs text-[var(--muted-foreground)]">{o.symbol}</div>
                      </td>
                      <td className={`text-center p-3 font-medium ${
                        o.side === "buy" ? "text-red-500" : "text-blue-500"
                      }`}>
                        {o.side === "buy" ? "매수" : "매도"}
                      </td>
                      <td className="text-right p-3 font-mono">{o.price.toLocaleString()}</td>
                      <td className="text-right p-3 font-mono">{o.quantity.toLocaleString()}</td>
                      <td className="text-right p-3 font-mono">{o.unfilled_qty.toLocaleString()}</td>
                      <td className="text-center p-3 text-[var(--muted-foreground)]">
                        {o.order_time.slice(0, 2)}:{o.order_time.slice(2, 4)}:{o.order_time.slice(4, 6)}
                      </td>
                      <td className="text-center p-3">
                        <button
                          onClick={() => {
                            // KIS pending orders use order_id, not DB trade_id
                            // For cancellation via KIS, we'd need to map this
                            // For now, show a visual indicator
                            if (confirm(`${o.name} ${o.side === "buy" ? "매수" : "매도"} 주문을 취소하시겠습니까?`)) {
                              // TODO: cancel via KIS order_id mapping
                            }
                          }}
                          className="text-xs text-[var(--destructive)] hover:underline"
                        >
                          취소
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center text-[var(--muted-foreground)]">
              미체결 주문이 없습니다
            </div>
          )}
        </div>
      )}

      {/* Filled Orders */}
      {tab === "filled" && (
        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)]">
          {loadingFilled ? (
            <div className="p-8 text-center text-[var(--muted-foreground)]">로딩 중...</div>
          ) : filled && filled.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                    <th className="text-left p-3">종목</th>
                    <th className="text-center p-3">구분</th>
                    <th className="text-right p-3">체결가격</th>
                    <th className="text-right p-3">체결수량</th>
                    <th className="text-right p-3">체결금액</th>
                    <th className="text-center p-3">체결시간</th>
                  </tr>
                </thead>
                <tbody>
                  {filled.map((o, i) => (
                    <tr key={`${o.order_id}-${i}`} className="border-b border-[var(--border)] hover:bg-[var(--secondary)]">
                      <td className="p-3">
                        <div className="font-medium">{o.name}</div>
                        <div className="text-xs text-[var(--muted-foreground)]">{o.symbol}</div>
                      </td>
                      <td className={`text-center p-3 font-medium ${
                        o.side === "buy" ? "text-red-500" : "text-blue-500"
                      }`}>
                        {o.side === "buy" ? "매수" : "매도"}
                      </td>
                      <td className="text-right p-3 font-mono">{o.price.toLocaleString()}</td>
                      <td className="text-right p-3 font-mono">{o.quantity.toLocaleString()}</td>
                      <td className="text-right p-3 font-mono">{o.total_amount.toLocaleString()}</td>
                      <td className="text-center p-3 text-[var(--muted-foreground)]">
                        {o.filled_time
                          ? `${o.filled_time.slice(0, 2)}:${o.filled_time.slice(2, 4)}:${o.filled_time.slice(4, 6)}`
                          : "--"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center text-[var(--muted-foreground)]">
              오늘 체결된 주문이 없습니다
            </div>
          )}
        </div>
      )}
    </div>
  );
}
