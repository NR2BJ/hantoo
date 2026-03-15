"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";

interface KISAccount {
  id: string;
  label: string;
  account_type: string;
  environment: string;
  account_number: string;
  product_code: string;
  hts_id: string | null;
  is_active: boolean;
  has_valid_token: boolean;
}

export default function AccountsSettingsPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    label: "",
    account_type: "personal",
    environment: "prod",
    app_key: "",
    app_secret: "",
    account_number: "",
    product_code: "01",
    hts_id: "",
  });

  const { data: accounts } = useQuery<KISAccount[]>({
    queryKey: ["accounts"],
    queryFn: () => api.get("/api/accounts/"),
  });

  const createAccount = useMutation({
    mutationFn: (data: typeof form) =>
      api.post("/api/accounts/", {
        ...data,
        hts_id: data.hts_id || null,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      setShowForm(false);
      setForm({
        label: "",
        account_type: "personal",
        environment: "prod",
        app_key: "",
        app_secret: "",
        account_number: "",
        product_code: "01",
        hts_id: "",
      });
    },
  });

  const deleteAccount = useMutation({
    mutationFn: (id: string) => api.delete(`/api/accounts/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["accounts"] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">KIS 계좌 관리</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 text-sm rounded-lg bg-[var(--primary)] text-white hover:opacity-90"
        >
          {showForm ? "취소" : "계좌 추가"}
        </button>
      </div>

      {/* Create Form */}
      {showForm && (
        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-6 space-y-4">
          <h3 className="text-lg font-medium">새 KIS 계좌 등록</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-[var(--muted-foreground)] mb-1">
                별칭
              </label>
              <input
                type="text"
                placeholder="예: 내 실전 계좌"
                value={form.label}
                onChange={(e) => setForm({ ...form, label: e.target.value })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              />
            </div>
            <div>
              <label className="block text-sm text-[var(--muted-foreground)] mb-1">
                계좌 유형
              </label>
              <select
                value={form.account_type}
                onChange={(e) => setForm({ ...form, account_type: e.target.value })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              >
                <option value="personal">개인</option>
                <option value="shared">공용</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-[var(--muted-foreground)] mb-1">
                환경
              </label>
              <select
                value={form.environment}
                onChange={(e) => setForm({ ...form, environment: e.target.value })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              >
                <option value="prod">실전투자</option>
                <option value="paper">모의투자</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-[var(--muted-foreground)] mb-1">
                계좌번호
              </label>
              <input
                type="text"
                placeholder="12345678"
                value={form.account_number}
                onChange={(e) => setForm({ ...form, account_number: e.target.value })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              />
            </div>
            <div>
              <label className="block text-sm text-[var(--muted-foreground)] mb-1">
                App Key
              </label>
              <input
                type="password"
                value={form.app_key}
                onChange={(e) => setForm({ ...form, app_key: e.target.value })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              />
            </div>
            <div>
              <label className="block text-sm text-[var(--muted-foreground)] mb-1">
                App Secret
              </label>
              <input
                type="password"
                value={form.app_secret}
                onChange={(e) => setForm({ ...form, app_secret: e.target.value })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              />
            </div>
            <div>
              <label className="block text-sm text-[var(--muted-foreground)] mb-1">
                상품코드
              </label>
              <input
                type="text"
                value={form.product_code}
                onChange={(e) => setForm({ ...form, product_code: e.target.value })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              />
            </div>
            <div>
              <label className="block text-sm text-[var(--muted-foreground)] mb-1">
                HTS ID (선택)
              </label>
              <input
                type="text"
                value={form.hts_id}
                onChange={(e) => setForm({ ...form, hts_id: e.target.value })}
                className="w-full px-3 py-2 rounded-lg bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)]"
              />
            </div>
          </div>

          <div className="text-sm text-[var(--muted-foreground)]">
            App Key와 App Secret은 한국투자증권 개발자센터에서 발급받을 수 있습니다.
            암호화되어 저장됩니다.
          </div>

          <button
            onClick={() => createAccount.mutate(form)}
            disabled={!form.label || !form.app_key || !form.app_secret || !form.account_number || createAccount.isPending}
            className="px-4 py-2 text-sm rounded-lg bg-[var(--primary)] text-white hover:opacity-90 disabled:opacity-50"
          >
            {createAccount.isPending ? "등록 중..." : "등록"}
          </button>
          {createAccount.isError && (
            <p className="text-sm text-red-500">등록 실패: {(createAccount.error as Error).message}</p>
          )}
        </div>
      )}

      {/* Account List */}
      <div className="space-y-3">
        {accounts && accounts.length > 0 ? (
          accounts.map((acc) => (
            <div
              key={acc.id}
              className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-4 flex items-center justify-between"
            >
              <div>
                <div className="font-medium">{acc.label}</div>
                <div className="text-sm text-[var(--muted-foreground)] space-x-3">
                  <span>{acc.account_number}</span>
                  <span>{acc.environment === "prod" ? "실전" : "모의"}</span>
                  <span>{acc.account_type === "personal" ? "개인" : "공용"}</span>
                  <span className={acc.has_valid_token ? "text-green-500" : "text-yellow-500"}>
                    {acc.has_valid_token ? "토큰 유효" : "토큰 없음"}
                  </span>
                </div>
              </div>
              <button
                onClick={() => {
                  if (confirm(`"${acc.label}" 계좌를 삭제하시겠습니까?`)) {
                    deleteAccount.mutate(acc.id);
                  }
                }}
                className="text-sm text-[var(--destructive)] hover:underline"
              >
                삭제
              </button>
            </div>
          ))
        ) : (
          <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-8 text-center text-[var(--muted-foreground)]">
            등록된 KIS 계좌가 없습니다. 계좌를 추가하세요.
          </div>
        )}
      </div>
    </div>
  );
}
