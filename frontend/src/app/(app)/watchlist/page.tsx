"use client";

export default function WatchlistPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">관심 종목</h2>
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-6">
        <p className="text-[var(--muted-foreground)]">관심 종목 목록과 실시간 시세가 표시됩니다.</p>
      </div>
    </div>
  );
}
