"use client";

import { use } from "react";
import { useQuote, useOrderbook, useTrades } from "@/hooks/use-market";
import { getPriceColor, getPriceSign } from "@/types/market";
import StockChart from "@/components/charts/stock-chart";

export default function StockDetailPage({
  params,
}: {
  params: Promise<{ symbol: string }>;
}) {
  const { symbol } = use(params);
  const { data: quote } = useQuote(symbol);
  const { data: orderbook } = useOrderbook(symbol);
  const { data: trades } = useTrades(symbol);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-baseline gap-3">
        <h2 className="text-2xl font-bold">
          {quote?.name ?? symbol}
        </h2>
        <span className="text-[var(--muted-foreground)]">{symbol}</span>
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

      {/* Chart */}
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
        <StockChart symbol={symbol} height={400} />
      </div>

      {/* Orderbook + Trades */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Orderbook */}
        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
          <h3 className="text-lg font-medium mb-3">호가</h3>
          {orderbook ? (
            <div className="space-y-1 text-sm font-mono">
              {/* Ask (매도) - reverse so highest is top */}
              {[...orderbook.ask].reverse().map((entry, i) => (
                <div key={`ask-${i}`} className="flex justify-between text-blue-500">
                  <span>{entry.volume.toLocaleString()}</span>
                  <span>{entry.price.toLocaleString()}</span>
                </div>
              ))}
              <div className="border-t border-[var(--border)] my-1" />
              {/* Bid (매수) */}
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
            <p className="text-[var(--muted-foreground)] text-sm">KIS 계좌를 선택하세요</p>
          )}
        </div>

        {/* Recent Trades */}
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
            <p className="text-[var(--muted-foreground)] text-sm">KIS 계좌를 선택하세요</p>
          )}
        </div>
      </div>
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
