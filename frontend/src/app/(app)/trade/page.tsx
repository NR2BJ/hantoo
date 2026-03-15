"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSearch, useQuote, useOrderbook, useTrades } from "@/hooks/use-market";
import { usePendingOrders, useCancelOrder } from "@/hooks/use-orders";
import { getPriceColor, getPriceSign } from "@/types/market";
import StockChart from "@/components/charts/stock-chart";
import OrderForm from "@/components/trading/order-form";

export default function TradePage() {
  const [symbol, setSymbol] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [orderPrice, setOrderPrice] = useState<number>(0);

  const { data: searchResults } = useSearch(searchQuery);
  const { data: quote } = useQuote(symbol);
  const { data: orderbook } = useOrderbook(symbol);
  const { data: trades } = useTrades(symbol);
  const { data: pending } = usePendingOrders();
  const cancelOrder = useCancelOrder();

  const selectStock = (sym: string) => {
    setSymbol(sym);
    setSearchQuery("");
  };

  return (
    <div className="space-y-4">
      {/* Header + Search */}
      <div className="flex items-center gap-4">
        <h2 className="text-2xl font-bold">국내주식 거래</h2>
        <div className="relative flex-1 max-w-md">
          <input
            type="text"
            placeholder="종목 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 text-sm rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
          />
          {searchResults && searchResults.length > 0 && searchQuery && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-[var(--card)] border border-[var(--border)] rounded-lg shadow-lg z-20 max-h-60 overflow-y-auto">
              {searchResults.map((r) => (
                <button
                  key={r.symbol}
                  onClick={() => selectStock(r.symbol)}
                  className="w-full flex items-center justify-between py-2 px-3 hover:bg-[var(--secondary)] text-left text-sm"
                >
                  <span>
                    {r.name}{" "}
                    <span className="text-[var(--muted-foreground)]">{r.symbol}</span>
                  </span>
                  <span className="text-xs text-[var(--muted-foreground)]">{r.market}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {symbol ? (
        <>
          {/* Quote Header */}
          {quote && (
            <div className="flex items-baseline gap-4">
              <h3 className="text-xl font-bold">{quote.name}</h3>
              <span className="text-sm text-[var(--muted-foreground)]">{symbol}</span>
              <span className={`text-2xl font-bold ${getPriceColor(quote.change_sign)}`}>
                {quote.current_price.toLocaleString()}원
              </span>
              <span className={`text-sm ${getPriceColor(quote.change_sign)}`}>
                {getPriceSign(quote.change)}
                {quote.change.toLocaleString()} ({getPriceSign(quote.change)}
                {quote.change_rate.toFixed(2)}%)
              </span>
            </div>
          )}

          {/* Main grid: Chart + OrderForm */}
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-4">
            {/* Left: Chart + Orderbook + Trades */}
            <div className="space-y-4">
              {/* Chart */}
              <StockChart symbol={symbol} />

              {/* Orderbook + Recent trades */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Orderbook */}
                <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-3">
                  <h4 className="text-sm font-medium text-[var(--muted-foreground)] mb-2">호가</h4>
                  {orderbook ? (
                    <div className="space-y-0.5 text-xs font-mono">
                      {/* Ask (매도) — reversed so lowest ask is at bottom */}
                      {[...orderbook.ask].reverse().map((e, i) => (
                        <button
                          key={`ask-${i}`}
                          onClick={() => setOrderPrice(e.price)}
                          className="w-full flex justify-between py-0.5 px-1 hover:bg-blue-500/10 rounded text-blue-400"
                        >
                          <span>{e.volume.toLocaleString()}</span>
                          <span>{e.price.toLocaleString()}</span>
                        </button>
                      ))}
                      <div className="border-t border-[var(--border)] my-1" />
                      {/* Bid (매수) */}
                      {orderbook.bid.map((e, i) => (
                        <button
                          key={`bid-${i}`}
                          onClick={() => setOrderPrice(e.price)}
                          className="w-full flex justify-between py-0.5 px-1 hover:bg-red-500/10 rounded text-red-400"
                        >
                          <span>{e.price.toLocaleString()}</span>
                          <span>{e.volume.toLocaleString()}</span>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-[var(--muted-foreground)]">호가 데이터 없음</p>
                  )}
                </div>

                {/* Recent trades */}
                <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-3">
                  <h4 className="text-sm font-medium text-[var(--muted-foreground)] mb-2">체결</h4>
                  {trades && trades.length > 0 ? (
                    <div className="space-y-0.5 text-xs font-mono max-h-64 overflow-y-auto">
                      {trades.slice(0, 20).map((t, i) => (
                        <div key={i} className="flex justify-between py-0.5">
                          <span className="text-[var(--muted-foreground)]">
                            {t.time.slice(0, 2)}:{t.time.slice(2, 4)}:{t.time.slice(4, 6)}
                          </span>
                          <span>{t.price.toLocaleString()}</span>
                          <span className="text-[var(--muted-foreground)]">{t.volume}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-[var(--muted-foreground)]">체결 데이터 없음</p>
                  )}
                </div>
              </div>
            </div>

            {/* Right: Order Form */}
            <div className="space-y-4">
              <OrderForm symbol={symbol} quote={quote ?? null} externalPrice={orderPrice} />

              {/* Pending orders for this symbol */}
              {pending && pending.filter((o) => o.symbol === symbol).length > 0 && (
                <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-3">
                  <h4 className="text-sm font-medium text-[var(--muted-foreground)] mb-2">
                    미체결 주문
                  </h4>
                  <div className="space-y-1">
                    {pending
                      .filter((o) => o.symbol === symbol)
                      .map((o) => (
                        <div
                          key={o.order_id}
                          className="flex items-center justify-between text-xs py-1"
                        >
                          <span
                            className={
                              o.side === "buy" ? "text-red-500" : "text-blue-500"
                            }
                          >
                            {o.side === "buy" ? "매수" : "매도"}
                          </span>
                          <span className="font-mono">{o.price.toLocaleString()}</span>
                          <span className="font-mono">{o.unfilled_qty}주</span>
                          <button
                            onClick={() => {
                              // We'd need the DB trade_id, but KIS pending uses order_id
                              // For now, just show the cancel action
                            }}
                            className="text-[var(--destructive)] hover:underline"
                          >
                            취소
                          </button>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      ) : (
        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-12 text-center">
          <p className="text-lg text-[var(--muted-foreground)]">
            종목을 검색하여 선택하세요
          </p>
          <p className="text-sm text-[var(--muted-foreground)] mt-2">
            검색창에 종목명 또는 종목코드를 입력하세요
          </p>
        </div>
      )}
    </div>
  );
}
