"use client";

import { useEffect, useRef, useState } from "react";
import {
  createChart,
  type IChartApi,
  type ISeriesApi,
  ColorType,
} from "lightweight-charts";
import { useOverseasCandles } from "@/hooks/use-overseas-market";
import type { OverseasCandle } from "@/types/market";

interface OverseasStockChartProps {
  symbol: string;
  exchange: string;
  height?: number;
}

const PERIODS = [
  { label: "일", value: "D" },
  { label: "주", value: "W" },
  { label: "월", value: "M" },
] as const;

function formatCandles(candles: OverseasCandle[]) {
  return candles.map((c) => {
    const d = c.date;
    const time = `${d.slice(0, 4)}-${d.slice(4, 6)}-${d.slice(6, 8)}`;
    return {
      time,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close,
    };
  });
}

function formatVolumes(candles: OverseasCandle[]) {
  return candles.map((c) => {
    const d = c.date;
    const time = `${d.slice(0, 4)}-${d.slice(4, 6)}-${d.slice(6, 8)}`;
    // US convention: green = up, red = down
    const color =
      c.close >= c.open
        ? "rgba(34, 197, 94, 0.5)"
        : "rgba(239, 68, 68, 0.5)";
    return { time, value: c.volume, color };
  });
}

export default function OverseasStockChart({
  symbol,
  exchange,
  height = 400,
}: OverseasStockChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const [period, setPeriod] = useState<string>("D");

  const { data: candles } = useOverseasCandles(symbol, exchange, period);

  // Create chart
  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      height,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#9ca3af",
      },
      grid: {
        vertLines: { color: "rgba(107, 114, 128, 0.1)" },
        horzLines: { color: "rgba(107, 114, 128, 0.1)" },
      },
      crosshair: {
        mode: 0,
      },
      rightPriceScale: {
        borderColor: "rgba(107, 114, 128, 0.2)",
      },
      timeScale: {
        borderColor: "rgba(107, 114, 128, 0.2)",
        timeVisible: false,
      },
      localization: {
        priceFormatter: (price: number) =>
          `$${price.toFixed(2)}`,
      },
    });

    // US convention: green up, red down
    const candleSeries = chart.addCandlestickSeries({
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderUpColor: "#22c55e",
      borderDownColor: "#ef4444",
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
    });

    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });

    chart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };

    const observer = new ResizeObserver(handleResize);
    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, [height]);

  // Update data
  useEffect(() => {
    if (!candles || !candleSeriesRef.current || !volumeSeriesRef.current)
      return;

    const candleData = formatCandles(candles);
    const volumeData = formatVolumes(candles);

    candleSeriesRef.current.setData(candleData as any);
    volumeSeriesRef.current.setData(volumeData as any);

    chartRef.current?.timeScale().fitContent();
  }, [candles]);

  return (
    <div>
      <div className="flex gap-1 mb-2">
        {PERIODS.map((p) => (
          <button
            key={p.value}
            onClick={() => setPeriod(p.value)}
            className={`px-3 py-1 text-sm rounded ${
              period === p.value
                ? "bg-[var(--primary)] text-white"
                : "bg-[var(--secondary)] text-[var(--muted-foreground)] hover:bg-[var(--border)]"
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>
      <div ref={containerRef} className="w-full" />
    </div>
  );
}
