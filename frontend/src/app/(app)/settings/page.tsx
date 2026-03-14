"use client";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">설정</h2>
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-6">
        <p className="text-[var(--muted-foreground)]">프로필, KIS 계좌 관리, 2FA 설정, 알림 설정</p>
      </div>
    </div>
  );
}
