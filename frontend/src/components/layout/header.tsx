"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/auth-store";
import { useTradingStore } from "@/stores/trading-store";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api-client";

interface KISAccount {
  id: string;
  label: string;
  account_type: string;
  environment: string;
  account_number: string;
  has_valid_token: boolean;
}

export function Header() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const activeAccountId = useTradingStore((s) => s.activeAccountId);
  const setActiveAccount = useTradingStore((s) => s.setActiveAccount);
  const router = useRouter();

  const { data: accounts } = useQuery<KISAccount[]>({
    queryKey: ["accounts"],
    queryFn: () => api.get("/api/accounts/"),
  });

  // Auto-select first account if none selected
  useEffect(() => {
    if (!activeAccountId && accounts && accounts.length > 0) {
      setActiveAccount(accounts[0].id);
    }
  }, [activeAccountId, accounts, setActiveAccount]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  return (
    <header className="h-14 border-b border-[var(--border)] bg-[var(--card)] flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        {accounts && accounts.length > 0 ? (
          <select
            value={activeAccountId || ""}
            onChange={(e) => setActiveAccount(e.target.value || null)}
            className="text-sm px-2 py-1 rounded bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)]"
          >
            {accounts.map((acc) => (
              <option key={acc.id} value={acc.id}>
                {acc.label} ({acc.account_number}) {acc.environment === "paper" ? "[모의]" : ""}
              </option>
            ))}
          </select>
        ) : (
          <button
            onClick={() => router.push("/settings/accounts")}
            className="text-sm text-[var(--primary)] hover:underline"
          >
            KIS 계좌를 등록하세요
          </button>
        )}
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
