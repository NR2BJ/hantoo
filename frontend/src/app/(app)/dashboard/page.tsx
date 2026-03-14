"use client";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">대시보드</h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard title="총 자산" value="--" />
        <SummaryCard title="일일 수익" value="--" />
        <SummaryCard title="보유 종목" value="--" />
        <SummaryCard title="예수금" value="--" />
      </div>

      {/* Market Indices */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <IndexCard name="KOSPI" value="--" change="--" />
        <IndexCard name="KOSDAQ" value="--" change="--" />
        <IndexCard name="S&P 500" value="--" change="--" />
        <IndexCard name="NASDAQ" value="--" change="--" />
      </div>

      {/* Holdings Table Placeholder */}
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
        <h3 className="text-lg font-medium mb-4">보유 종목</h3>
        <p className="text-[var(--muted-foreground)] text-sm">
          KIS 계좌를 등록하면 보유 종목이 표시됩니다.
        </p>
      </div>
    </div>
  );
}

function SummaryCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
      <p className="text-sm text-[var(--muted-foreground)]">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}

function IndexCard({
  name,
  value,
  change,
}: {
  name: string;
  value: string;
  change: string;
}) {
  return (
    <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4">
      <p className="text-sm text-[var(--muted-foreground)]">{name}</p>
      <p className="text-lg font-bold mt-1">{value}</p>
      <p className="text-sm text-[var(--muted-foreground)]">{change}</p>
    </div>
  );
}
