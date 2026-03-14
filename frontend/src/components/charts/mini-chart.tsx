"use client";

import { useEffect, useRef } from "react";
import { createChart, type IChartApi, ColorType } from "lightweight-charts";

interface MiniChartProps {
  data: { time: string; value: number }[];
  color?: string;
  width?: number;
  height?: number;
}

export default function MiniChart({
  data,
  color = "#9ca3af",
  width = 120,
  height = 40,
}: MiniChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;

    const chart = createChart(containerRef.current, {
      width,
      height,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "transparent",
      },
      grid: {
        vertLines: { visible: false },
        horzLines: { visible: false },
      },
      rightPriceScale: { visible: false },
      timeScale: { visible: false },
      crosshair: { mode: 0 },
      handleScroll: false,
      handleScale: false,
    });

    const series = chart.addLineSeries({
      color,
      lineWidth: 1,
      priceLineVisible: false,
      lastValueVisible: false,
      crosshairMarkerVisible: false,
    });

    series.setData(data as any);
    chart.timeScale().fitContent();
    chartRef.current = chart;

    return () => {
      chart.remove();
      chartRef.current = null;
    };
  }, [data, color, width, height]);

  return <div ref={containerRef} />;
}
