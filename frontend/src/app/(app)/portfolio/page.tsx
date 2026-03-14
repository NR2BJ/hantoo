"use client";

export default function PortfolioPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">포트폴리오</h2>
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-6">
        <p className="text-[var(--muted-foreground)]">보유 종목, 수익률 차트, 자산 배분이 표시됩니다.</p>
      </div>
    </div>
  );
}
