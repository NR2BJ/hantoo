"use client";

export default function OrdersPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">주문 내역</h2>
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-6">
        <p className="text-[var(--muted-foreground)]">주문 내역과 체결 내역이 표시됩니다.</p>
      </div>
    </div>
  );
}
