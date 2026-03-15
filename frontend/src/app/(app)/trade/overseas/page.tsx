"use client";

import { useState } from "react";
import { useOverseasSearch, useOverseasQuote } from "@/hooks/use-overseas-market";
import { useOverseasFilledOrders } from "@/hooks/use-overseas-orders";
import {
  formatUSD,
  getExchangeLabel,
  getUSPriceColor,
  getPriceSign,
} from "@/types/market";
import OverseasStockChart from "@/components/charts/overseas-stock-chart";
import OverseasOrderForm from "@/components/trading/overseas-order-form";

export default function OverseasTradePage() {
  const [symbol, setSymbol] = useState("");
  const [exchange, setExchange] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const { data: searchResults } = useOverseasSearch(searchQuery);
  const { data: quote } = useOverseasQuote(symbol, exchange);
  const { data: filledOrders } = useOverseasFilledOrders();

  const selectStock = (sym: string, exch: string) => {
    setSymbol(sym);
    setExchange(exch);
    setSearchQuery("");
  };

  return (
    <div className="space-y-4">
      {/* Header + Search */}
      <div className="flex items-center gap-4">
        <h2 className="text-2xl font-bold">해외주식 거래</h2>
        <div className="relative flex-1 max-w-md">
          <input
            type="text"
            placeholder="미국 종목 검색 (예: AAPL, TSLA, MSFT)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 text-sm rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
          />
          {searchResults && searchResults.length > 0 && searchQuery && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-[var(--card)] border border-[var(--border)] rounded-lg shadow-lg z-20 max-h-60 overflow-y-auto">
              {searchResults.map((r) => (
                <button
                  key={`${r.exchange}-${r.symbol}`}
                  onClick={() => selectStock(r.symbol, r.exchange)}
                  className="w-full flex items-center justify-between py-2 px-3 hover:bg-[var(--secondary)] text-left text-sm"
                >
                  <span>
                    <span className="font-medium">{r.symbol}</span>{" "}
                    <span className="text-[var(--muted-foreground)]">
                      {r.name}
                    </span>
                  </span>
                  <span className="text-xs px-1.5 py-0.5 rounded bg-[var(--secondary)] text-[var(--muted-foreground)]">
                    {getExchangeLabel(r.exchange)}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {symbol && exchange ? (
        <>
          {/* Quote Header */}
          {quote && (
            <div className="flex items-baseline gap-4 flex-wrap">
              <h3 className="text-xl font-bold">{quote.name}</h3>
              <span className="text-sm text-[var(--muted-foreground)]">
                {symbol}
              </span>
              <span className="text-xs px-1.5 py-0.5 rounded bg-[var(--secondary)] text-[var(--muted-foreground)]">
                {getExchangeLabel(exchange)}
              </span>
              <span
                className={`text-2xl font-bold ${getUSPriceColor(quote.change_sign)}`}
              >
                {formatUSD(quote.current_price)}
              </span>
              <span
                className={`text-sm ${getUSPriceColor(quote.change_sign)}`}
              >
                {getPriceSign(quote.change)}
                {quote.change.toFixed(2)} ({getPriceSign(quote.change)}
                {quote.change_rate.toFixed(2)}%)
              </span>
            </div>
          )}

          {/* Quote detail pills */}
          {quote && (
            <div className="flex gap-4 text-xs text-[var(--muted-foreground)]">
              <span>
                시가{" "}
                <span className="font-mono">{formatUSD(quote.open_price)}</span>
              </span>
              <span>
                고가{" "}
                <span className="font-mono text-green-500">
                  {formatUSD(quote.high_price)}
                </span>
              </span>
              <span>
                저가{" "}
                <span className="font-mono text-red-500">
                  {formatUSD(quote.low_price)}
                </span>
              </span>
              <span>
                전일{" "}
                <span className="font-mono">
                  {formatUSD(quote.prev_close)}
                </span>
              </span>
              <span>
                거래량{" "}
                <span className="font-mono">
                  {quote.volume.toLocaleString()}
                </span>
              </span>
            </div>
          )}

          {/* Main grid: Chart + OrderForm */}
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-4">
            {/* Left: Chart + Recent fills */}
            <div className="space-y-4">
              <OverseasStockChart symbol={symbol} exchange={exchange} />

              {/* Recent filled orders for this symbol */}
              {filledOrders &&
                filledOrders.filter((o) => o.symbol === symbol).length > 0 && (
                  <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-3">
                    <h4 className="text-sm font-medium text-[var(--muted-foreground)] mb-2">
                      최근 체결
                    </h4>
                    <div className="space-y-1 text-xs">
                      {filledOrders
                        .filter((o) => o.symbol === symbol)
                        .slice(0, 10)
                        .map((o) => (
                          <div
                            key={o.order_id}
                            className="flex items-center justify-between py-1"
                          >
                            <span
                              className={
                                o.side === "buy"
                                  ? "text-green-500"
                                  : "text-red-500"
                              }
                            >
                              {o.side === "buy" ? "매수" : "매도"}
                            </span>
                            <span className="font-mono">
                              {formatUSD(o.price)}
                            </span>
                            <span className="font-mono">{o.quantity}주</span>
                            <span className="text-[var(--muted-foreground)]">
                              {o.filled_time}
                            </span>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
            </div>

            {/* Right: Order Form */}
            <div>
              <OverseasOrderForm
                symbol={symbol}
                exchange={exchange}
                quote={quote ?? null}
              />
            </div>
          </div>
        </>
      ) : (
        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-12 text-center">
          <p className="text-lg text-[var(--muted-foreground)]">
            종목을 검색하여 선택하세요
          </p>
          <p className="text-sm text-[var(--muted-foreground)] mt-2">
            미국 주식: NASDAQ, NYSE, AMEX
          </p>
          <div className="flex justify-center gap-3 mt-4 text-xs text-[var(--muted-foreground)]">
            <button
              onClick={() => selectStock("AAPL", "NAS")}
              className="px-3 py-1.5 rounded-lg bg-[var(--secondary)] hover:bg-[var(--border)]"
            >
              AAPL
            </button>
            <button
              onClick={() => selectStock("TSLA", "NAS")}
              className="px-3 py-1.5 rounded-lg bg-[var(--secondary)] hover:bg-[var(--border)]"
            >
              TSLA
            </button>
            <button
              onClick={() => selectStock("MSFT", "NAS")}
              className="px-3 py-1.5 rounded-lg bg-[var(--secondary)] hover:bg-[var(--border)]"
            >
              MSFT
            </button>
            <button
              onClick={() => selectStock("AMZN", "NAS")}
              className="px-3 py-1.5 rounded-lg bg-[var(--secondary)] hover:bg-[var(--border)]"
            >
              AMZN
            </button>
            <button
              onClick={() => selectStock("NVDA", "NAS")}
              className="px-3 py-1.5 rounded-lg bg-[var(--secondary)] hover:bg-[var(--border)]"
            >
              NVDA
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
