"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";

export default function SetupPage() {
  const router = useRouter();
  const fetchUser = useAuthStore((s) => s.fetchUser);
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    admin_username: "",
    admin_display_name: "",
    admin_password: "",
    admin_password_confirm: "",
    app_name: "Hantoo",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleNext = () => {
    if (step === 1) {
      if (!form.app_name.trim()) {
        setError("앱 이름을 입력하세요");
        return;
      }
      setError("");
      setStep(2);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (form.admin_password !== form.admin_password_confirm) {
      setError("비밀번호가 일치하지 않습니다");
      return;
    }

    if (form.admin_password.length < 8) {
      setError("비밀번호는 8자 이상이어야 합니다");
      return;
    }

    setIsLoading(true);
    try {
      await api.post("/api/setup/complete", {
        admin_username: form.admin_username,
        admin_display_name: form.admin_display_name,
        admin_password: form.admin_password,
        app_name: form.app_name,
      });
      await fetchUser();
      router.push("/dashboard");
    } catch (err: unknown) {
      const apiErr = err as { message?: string };
      setError(apiErr.message || "셋업 실패");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-3xl font-bold text-center mb-2">초기 설정</h1>
      <p className="text-center text-[var(--muted-foreground)] mb-8">
        Hantoo 트레이딩 플랫폼을 처음 설정합니다
      </p>

      {/* Step indicator */}
      <div className="flex items-center justify-center gap-2 mb-8">
        <StepDot active={step >= 1} label="1" />
        <div className="w-8 h-px bg-[var(--border)]" />
        <StepDot active={step >= 2} label="2" />
      </div>

      {step === 1 && (
        <div className="space-y-4">
          <h2 className="text-lg font-medium">앱 설정</h2>
          <p className="text-sm text-[var(--muted-foreground)]">
            보안 키(JWT, 암호화 키)는 자동으로 생성됩니다. 나중에 설정 페이지에서 변경할 수 있습니다.
          </p>

          <div>
            <label className="block text-sm mb-1">앱 이름</label>
            <input
              type="text"
              value={form.app_name}
              onChange={(e) => update("app_name", e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
            />
          </div>

          <div className="bg-[var(--secondary)] rounded-lg p-4 text-sm space-y-2">
            <p className="font-medium">자동 생성 항목:</p>
            <ul className="text-[var(--muted-foreground)] space-y-1 ml-4 list-disc">
              <li>JWT 서명 키 (토큰 인증용)</li>
              <li>AES-256 암호화 키 (KIS 자격증명 보호용)</li>
            </ul>
          </div>

          {error && <p className="text-[var(--destructive)] text-sm">{error}</p>}

          <button
            onClick={handleNext}
            className="w-full py-2 rounded-lg bg-[var(--primary)] text-white font-medium hover:opacity-90"
          >
            다음
          </button>
        </div>
      )}

      {step === 2 && (
        <form onSubmit={handleSubmit} className="space-y-4">
          <h2 className="text-lg font-medium">관리자 계정 생성</h2>

          <div>
            <label className="block text-sm mb-1">아이디</label>
            <input
              type="text"
              value={form.admin_username}
              onChange={(e) => update("admin_username", e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              required
              minLength={3}
            />
          </div>

          <div>
            <label className="block text-sm mb-1">표시 이름</label>
            <input
              type="text"
              value={form.admin_display_name}
              onChange={(e) => update("admin_display_name", e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-1">비밀번호</label>
            <input
              type="password"
              value={form.admin_password}
              onChange={(e) => update("admin_password", e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              required
              minLength={8}
            />
          </div>

          <div>
            <label className="block text-sm mb-1">비밀번호 확인</label>
            <input
              type="password"
              value={form.admin_password_confirm}
              onChange={(e) => update("admin_password_confirm", e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              required
            />
          </div>

          {error && <p className="text-[var(--destructive)] text-sm">{error}</p>}

          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="flex-1 py-2 rounded-lg border border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--secondary)]"
            >
              이전
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 py-2 rounded-lg bg-[var(--primary)] text-white font-medium hover:opacity-90 disabled:opacity-50"
            >
              {isLoading ? "설정 중..." : "설정 완료"}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

function StepDot({ active, label }: { active: boolean; label: string }) {
  return (
    <div
      className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
        active
          ? "bg-[var(--primary)] text-white"
          : "bg-[var(--secondary)] text-[var(--muted-foreground)]"
      }`}
    >
      {label}
    </div>
  );
}
