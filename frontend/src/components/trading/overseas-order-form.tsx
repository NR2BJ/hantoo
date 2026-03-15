"use client";

import { useState, useEffect } from "react";
import {
  usePlaceOverseasOrder,
  useOverseasBuyable,
} from "@/hooks/use-overseas-orders";
import {
  formatUSD,
  getExchangeLabel,
  type OverseasQuote,
} from "@/types/market";

interface OverseasOrderFormProps {
  symbol: string;
  exchange: string;
  quote: OverseasQuote | null;
  externalPrice?: number;
}

export default function OverseasOrderForm({
  symbol,
  exchange,
  quote,
  externalPrice,
}: OverseasOrderFormProps) {
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [orderType, setOrderType] = useState<"limit" | "market">("limit");
  const [quantity, setQuantity] = useState("");
  const [price, setPrice] = useState("");
  const [showConfirm, setShowConfirm] = useState(false);

  const placeOrder = usePlaceOverseasOrder();
  const priceNum = parseFloat(price) || 0;
  const { data: buyable } = useOverseasBuyable(symbol, exchange, priceNum);

  // Sync external price
  useEffect(() => {
    if (externalPrice && externalPrice > 0) {
      setPrice(String(externalPrice));
    }
  }, [externalPrice]);

  // Set initial price from quote
  useEffect(() => {
    if (quote?.current_price && !price) {
      setPrice(String(quote.current_price));
    }
  }, [quote?.current_price]);

  const qtyNum = parseInt(quantity) || 0;
  const totalAmount = priceNum * qtyNum;

  const handleSubmit = () => {
    if (!symbol || qtyNum <= 0) return;
    if (orderType === "limit" && priceNum <= 0) return;
    setShowConfirm(true);
  };

  const confirmOrder = () => {
    placeOrder.mutate(
      {
        symbol,
        exchange,
        side,
        order_type: orderType,
        quantity: qtyNum,
        price: orderType === "limit" ? priceNum : undefined,
      },
      {
        onSuccess: () => {
          setQuantity("");
          setShowConfirm(false);
        },
        onError: () => {
          setShowConfirm(false);
        },
      },
    );
  };

  const setQtyPercent = (pct: number) => {
    if (!buyable || priceNum <= 0) return;
    if (side === "buy") {
      const maxQty = buyable.orderable_qty;
      setQuantity(String(Math.floor((maxQty * pct) / 100)));
    }
  };

  return (
    <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-[var(--muted-foreground)]">
          주문
        </h3>
        {exchange && (
          <span className="text-xs px-2 py-0.5 rounded bg-[var(--secondary)] text-[var(--muted-foreground)]">
            {getExchangeLabel(exchange)}
          </span>
        )}
      </div>

      {/* Buy / Sell tabs — US convention: green buy, red sell */}
      <div className="flex gap-1">
        <button
          onClick={() => setSide("buy")}
          className={`flex-1 py-2 text-sm font-medium rounded-lg ${
            side === "buy"
              ? "bg-green-500/20 text-green-500 border border-green-500/40"
              : "bg-[var(--secondary)] text-[var(--muted-foreground)]"
          }`}
        >
          매수
        </button>
        <button
          onClick={() => setSide("sell")}
          className={`flex-1 py-2 text-sm font-medium rounded-lg ${
            side === "sell"
              ? "bg-red-500/20 text-red-500 border border-red-500/40"
              : "bg-[var(--secondary)] text-[var(--muted-foreground)]"
          }`}
        >
          매도
        </button>
      </div>

      {/* Order type */}
      <div className="flex gap-2">
        <button
          onClick={() => setOrderType("limit")}
          className={`px-3 py-1 text-xs rounded ${
            orderType === "limit"
              ? "bg-[var(--primary)] text-white"
              : "bg-[var(--secondary)] text-[var(--muted-foreground)]"
          }`}
        >
          지정가
        </button>
        <button
          onClick={() => setOrderType("market")}
          className={`px-3 py-1 text-xs rounded ${
            orderType === "market"
              ? "bg-[var(--primary)] text-white"
              : "bg-[var(--secondary)] text-[var(--muted-foreground)]"
          }`}
        >
          시장가
        </button>
      </div>

      {/* Price input (limit only) — USD with 0.01 step */}
      {orderType === "limit" && (
        <div>
          <label className="text-xs text-[var(--muted-foreground)]">
            가격 (USD)
          </label>
          <div className="flex items-center gap-1 mt-1">
            <button
              onClick={() =>
                setPrice(String(Math.max(0, priceNum - 0.01).toFixed(2)))
              }
              className="w-8 h-8 rounded bg-[var(--secondary)] text-[var(--muted-foreground)] hover:bg-[var(--border)]"
            >
              -
            </button>
            <input
              type="number"
              step="0.01"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="flex-1 px-3 py-1.5 text-right font-mono text-sm rounded bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)]"
              placeholder="0.00"
            />
            <button
              onClick={() => setPrice(String((priceNum + 0.01).toFixed(2)))}
              className="w-8 h-8 rounded bg-[var(--secondary)] text-[var(--muted-foreground)] hover:bg-[var(--border)]"
            >
              +
            </button>
          </div>
        </div>
      )}

      {/* Quantity input */}
      <div>
        <label className="text-xs text-[var(--muted-foreground)]">수량</label>
        <input
          type="number"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          className="w-full mt-1 px-3 py-1.5 text-right font-mono text-sm rounded bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)]"
          placeholder="0"
        />
        {side === "buy" && (
          <div className="flex gap-1 mt-1">
            {[10, 25, 50, 100].map((pct) => (
              <button
                key={pct}
                onClick={() => setQtyPercent(pct)}
                className="flex-1 py-1 text-xs rounded bg-[var(--secondary)] text-[var(--muted-foreground)] hover:bg-[var(--border)]"
              >
                {pct}%
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Buyable info */}
      {side === "buy" && buyable && (
        <div className="text-xs text-[var(--muted-foreground)] space-y-0.5">
          <div className="flex justify-between">
            <span>주문가능</span>
            <span className="font-mono">
              {formatUSD(buyable.orderable_cash_foreign)}
            </span>
          </div>
          <div className="flex justify-between">
            <span>최대수량</span>
            <span className="font-mono">
              {buyable.orderable_qty.toLocaleString()}주
            </span>
          </div>
          <div className="flex justify-between">
            <span>환율</span>
            <span className="font-mono">
              {buyable.exchange_rate.toLocaleString()}원
            </span>
          </div>
        </div>
      )}

      {/* Total */}
      {qtyNum > 0 && priceNum > 0 && (
        <div className="flex justify-between text-sm font-medium">
          <span>총 주문금액</span>
          <span className="font-mono">{formatUSD(totalAmount)}</span>
        </div>
      )}

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={
          !symbol ||
          qtyNum <= 0 ||
          (orderType === "limit" && priceNum <= 0) ||
          placeOrder.isPending
        }
        className={`w-full py-2.5 rounded-lg font-medium text-white disabled:opacity-50 ${
          side === "buy"
            ? "bg-green-500 hover:bg-green-600"
            : "bg-red-500 hover:bg-red-600"
        }`}
      >
        {placeOrder.isPending
          ? "주문 중..."
          : side === "buy"
            ? "매수 주문"
            : "매도 주문"}
      </button>

      {placeOrder.isError && (
        <p className="text-xs text-red-500 text-center">
          {placeOrder.error?.message || "주문 실패"}
        </p>
      )}

      {/* Confirmation dialog */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-6 max-w-sm w-full mx-4 space-y-4">
            <h4 className="text-lg font-bold">해외주식 주문 확인</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-[var(--muted-foreground)]">종목</span>
                <span className="font-medium">
                  {quote?.name || symbol}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--muted-foreground)]">거래소</span>
                <span>{getExchangeLabel(exchange)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--muted-foreground)]">구분</span>
                <span
                  className={`font-medium ${side === "buy" ? "text-green-500" : "text-red-500"}`}
                >
                  {side === "buy" ? "매수" : "매도"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--muted-foreground)]">유형</span>
                <span>{orderType === "limit" ? "지정가" : "시장가"}</span>
              </div>
              {orderType === "limit" && (
                <div className="flex justify-between">
                  <span className="text-[var(--muted-foreground)]">가격</span>
                  <span className="font-mono">{formatUSD(priceNum)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-[var(--muted-foreground)]">수량</span>
                <span className="font-mono">
                  {qtyNum.toLocaleString()}주
                </span>
              </div>
              {totalAmount > 0 && (
                <div className="flex justify-between border-t border-[var(--border)] pt-2">
                  <span className="font-medium">총 금액</span>
                  <span className="font-mono font-medium">
                    {formatUSD(totalAmount)}
                  </span>
                </div>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowConfirm(false)}
                className="flex-1 py-2 rounded-lg bg-[var(--secondary)] text-[var(--muted-foreground)] hover:bg-[var(--border)]"
              >
                취소
              </button>
              <button
                onClick={confirmOrder}
                disabled={placeOrder.isPending}
                className={`flex-1 py-2 rounded-lg font-medium text-white ${
                  side === "buy"
                    ? "bg-green-500 hover:bg-green-600"
                    : "bg-red-500 hover:bg-red-600"
                }`}
              >
                {placeOrder.isPending ? "처리 중..." : "확인"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
