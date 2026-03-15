"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";

const navItems = [
  { label: "대시보드", href: "/dashboard", icon: "📊" },
  { label: "국내주식", href: "/trade", icon: "📈" },
  { label: "해외주식", href: "/trade/overseas", icon: "🌐" },
  { label: "ETF", href: "/trade/etf", icon: "📦" },
  { label: "선물/옵션", href: "/trade/futures", icon: "⚡" },
  { label: "채권", href: "/trade/bonds", icon: "📜" },
  { label: "포트폴리오", href: "/portfolio", icon: "💼" },
  { label: "시장정보", href: "/market", icon: "🏛️" },
  { label: "관심종목", href: "/watchlist", icon: "⭐" },
  { label: "주문내역", href: "/orders", icon: "📋" },
  { label: "AI 어시스턴트", href: "/ai", icon: "🤖" },
  { label: "AI 전략", href: "/ai/strategies", icon: "🧠" },
  { label: "KIS 계좌", href: "/settings/accounts", icon: "🔑" },
  { label: "설정", href: "/settings", icon: "⚙️" },
];

const adminItems = [
  { label: "유저 관리", href: "/admin/users", icon: "👥" },
  { label: "공용 계좌", href: "/admin/shared-account", icon: "🏦" },
];

export function Sidebar() {
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);

  return (
    <aside className="w-56 bg-[var(--card)] border-r border-[var(--border)] flex flex-col">
      <div className="p-4 border-b border-[var(--border)]">
        <h1 className="text-xl font-bold">Hantoo</h1>
        <p className="text-xs text-[var(--muted-foreground)]">Trading Platform</p>
      </div>

      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors",
              pathname === item.href
                ? "bg-[var(--primary)] text-white"
                : "text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:bg-[var(--secondary)]"
            )}
          >
            <span>{item.icon}</span>
            {item.label}
          </Link>
        ))}

        {user?.role === "admin" && (
          <>
            <div className="pt-4 pb-1 px-3">
              <span className="text-xs font-medium text-[var(--muted-foreground)]">관리</span>
            </div>
            {adminItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors",
                  pathname === item.href
                    ? "bg-[var(--primary)] text-white"
                    : "text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:bg-[var(--secondary)]"
                )}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </>
        )}
      </nav>
    </aside>
  );
}
