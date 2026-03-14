"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { api } from "@/lib/api-client";
import Link from "next/link";

interface SetupStatus {
  setup_completed: boolean;
  app_name: string;
}

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [needs2FA, setNeeds2FA] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [appName, setAppName] = useState("Hantoo");

  useEffect(() => {
    api.get<SetupStatus>("/api/setup/status").then((status) => {
      if (!status.setup_completed) {
        router.push("/setup");
        return;
      }
      setAppName(status.app_name);
    }).catch(() => {});
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await login(username, password, totpCode || undefined);
      router.push("/dashboard");
    } catch (err: unknown) {
      const apiErr = err as { status?: number; message?: string };
      if (apiErr.message?.includes("2FA code required")) {
        setNeeds2FA(true);
      } else {
        setError(apiErr.message || "로그인 실패");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-center mb-2">{appName}</h1>
      <p className="text-center text-[var(--muted-foreground)] mb-8">
        KIS Trading Platform
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm mb-1">아이디</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
            required
          />
        </div>

        <div>
          <label className="block text-sm mb-1">비밀번호</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
            required
          />
        </div>

        {needs2FA && (
          <div>
            <label className="block text-sm mb-1">2FA 인증 코드</label>
            <input
              type="text"
              value={totpCode}
              onChange={(e) => setTotpCode(e.target.value)}
              placeholder="6자리 코드"
              maxLength={6}
              className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              autoFocus
            />
          </div>
        )}

        {error && (
          <p className="text-[var(--destructive)] text-sm">{error}</p>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2 rounded-lg bg-[var(--primary)] text-white font-medium hover:opacity-90 disabled:opacity-50"
        >
          {isLoading ? "로그인 중..." : "로그인"}
        </button>
      </form>

      <p className="text-center text-sm text-[var(--muted-foreground)] mt-4">
        계정이 없으신가요?{" "}
        <Link href="/register" className="text-[var(--primary)] hover:underline">
          초대코드로 가입
        </Link>
      </p>
    </div>
  );
}
