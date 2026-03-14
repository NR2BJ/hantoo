"use client";

export default function AdminUsersPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">유저 관리</h2>
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-6">
        <p className="text-[var(--muted-foreground)]">유저 목록, 초대 코드 관리, 권한 설정을 합니다.</p>
      </div>
    </div>
  );
}
