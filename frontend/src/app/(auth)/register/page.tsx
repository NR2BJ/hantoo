"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api-client";
import Link from "next/link";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    username: "",
    display_name: "",
    password: "",
    password_confirm: "",
    invite_code: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (form.password !== form.password_confirm) {
      setError("비밀번호가 일치하지 않습니다");
      return;
    }

    setIsLoading(true);
    try {
      await api.post("/api/auth/register", {
        username: form.username,
        display_name: form.display_name,
        password: form.password,
        invite_code: form.invite_code,
      });
      router.push("/login");
    } catch (err: unknown) {
      const apiErr = err as { message?: string };
      setError(apiErr.message || "가입 실패");
    } finally {
      setIsLoading(false);
    }
  };

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  return (
    <div>
      <h1 className="text-3xl font-bold text-center mb-2">회원가입</h1>
      <p className="text-center text-[var(--muted-foreground)] mb-8">
        초대 코드가 필요합니다
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm mb-1">초대 코드</label>
          <input
            type="text"
            value={form.invite_code}
            onChange={(e) => update("invite_code", e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
            required
          />
        </div>

        <div>
          <label className="block text-sm mb-1">아이디</label>
          <input
            type="text"
            value={form.username}
            onChange={(e) => update("username", e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
            required
            minLength={3}
          />
        </div>

        <div>
          <label className="block text-sm mb-1">표시 이름</label>
          <input
            type="text"
            value={form.display_name}
            onChange={(e) => update("display_name", e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
            required
          />
        </div>

        <div>
          <label className="block text-sm mb-1">비밀번호</label>
          <input
            type="password"
            value={form.password}
            onChange={(e) => update("password", e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
            required
            minLength={8}
          />
        </div>

        <div>
          <label className="block text-sm mb-1">비밀번호 확인</label>
          <input
            type="password"
            value={form.password_confirm}
            onChange={(e) => update("password_confirm", e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
            required
          />
        </div>

        {error && (
          <p className="text-[var(--destructive)] text-sm">{error}</p>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2 rounded-lg bg-[var(--primary)] text-white font-medium hover:opacity-90 disabled:opacity-50"
        >
          {isLoading ? "가입 중..." : "가입하기"}
        </button>
      </form>

      <p className="text-center text-sm text-[var(--muted-foreground)] mt-4">
        이미 계정이 있으신가요?{" "}
        <Link href="/login" className="text-[var(--primary)] hover:underline">
          로그인
        </Link>
      </p>
    </div>
  );
}
