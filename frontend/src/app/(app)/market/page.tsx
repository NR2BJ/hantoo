"use client";

export default function MarketPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">시장 정보</h2>
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-6">
        <p className="text-[var(--muted-foreground)]">시장 개요, 업종별 동향, 거래량 순위가 표시됩니다.</p>
      </div>
    </div>
  );
}
