"use client";

import { useAuthStore } from "@/stores/auth-store";
import { useTradingStore } from "@/stores/trading-store";
import { useRouter } from "next/navigation";

export function Header() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const activeAccountId = useTradingStore((s) => s.activeAccountId);
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  return (
    <header className="h-14 border-b border-[var(--border)] bg-[var(--card)] flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        {/* Account selector will be added when accounts are loaded */}
        <span className="text-sm text-[var(--muted-foreground)]">
          {activeAccountId ? `계좌: ${activeAccountId.slice(0, 8)}...` : "계좌를 선택하세요"}
        </span>
      </div>

      <div className="flex items-center gap-4">
        <span className="text-sm">{user?.display_name}</span>
        <button
          onClick={handleLogout}
          className="text-sm text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
        >
          로그아웃
        </button>
      </div>
    </header>
  );
}
