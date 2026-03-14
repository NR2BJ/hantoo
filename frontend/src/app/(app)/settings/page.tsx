"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";

interface Setting {
  key: string;
  value: string;
  is_secret: boolean;
  category: string;
  description: string;
  has_value: boolean;
}

const CATEGORY_LABELS: Record<string, string> = {
  general: "일반",
  security: "보안",
  kis: "KIS API",
  llm: "LLM (AI)",
};

const CATEGORY_ORDER = ["general", "security", "kis", "llm"];

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const isAdmin = user?.role === "admin";
  const [settings, setSettings] = useState<Setting[]>([]);
  const [editValues, setEditValues] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (isAdmin) {
      loadSettings();
    }
  }, [isAdmin]);

  const loadSettings = async () => {
    try {
      const data = await api.get<Setting[]>("/api/settings");
      setSettings(data);
      const initial: Record<string, string> = {};
      for (const s of data) {
        initial[s.key] = s.value;
      }
      setEditValues(initial);
    } catch {
      // Not admin or error
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      const updates = settings
        .filter((s) => editValues[s.key] !== s.value)
        .map((s) => ({ key: s.key, value: editValues[s.key] }));

      if (updates.length === 0) {
        setMessage("변경사항이 없습니다");
        setSaving(false);
        return;
      }

      await api.put("/api/settings", { settings: updates });
      setMessage(`${updates.length}개 설정이 저장되었습니다`);
      await loadSettings();
    } catch (err: unknown) {
      const apiErr = err as { message?: string };
      setMessage(`오류: ${apiErr.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (!isAdmin) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">설정</h2>
        <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-6">
          <p className="text-[var(--muted-foreground)]">
            앱 설정은 관리자만 변경할 수 있습니다.
          </p>
        </div>
      </div>
    );
  }

  const grouped = CATEGORY_ORDER.map((cat) => ({
    category: cat,
    label: CATEGORY_LABELS[cat] || cat,
    items: settings.filter((s) => s.category === cat),
  })).filter((g) => g.items.length > 0);

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">앱 설정</h2>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-4 py-2 rounded-lg bg-[var(--primary)] text-white text-sm font-medium hover:opacity-90 disabled:opacity-50"
        >
          {saving ? "저장 중..." : "저장"}
        </button>
      </div>

      {message && (
        <div className="px-4 py-2 rounded-lg bg-[var(--secondary)] text-sm">
          {message}
        </div>
      )}

      {grouped.map((group) => (
        <div
          key={group.category}
          className="bg-[var(--card)] rounded-lg border border-[var(--border)]"
        >
          <div className="px-4 py-3 border-b border-[var(--border)]">
            <h3 className="font-medium">{group.label}</h3>
          </div>
          <div className="divide-y divide-[var(--border)]">
            {group.items.map((setting) => (
              <div key={setting.key} className="px-4 py-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-mono text-[var(--muted-foreground)]">
                      {setting.key}
                    </p>
                    <p className="text-sm mt-0.5">{setting.description}</p>
                  </div>
                  <div className="w-72 flex-shrink-0">
                    {setting.key === "setup_completed" ? (
                      <span className="text-sm text-[var(--muted-foreground)]">
                        {setting.value}
                      </span>
                    ) : (
                      <input
                        type={setting.is_secret ? "password" : "text"}
                        value={editValues[setting.key] || ""}
                        onChange={(e) =>
                          setEditValues((prev) => ({
                            ...prev,
                            [setting.key]: e.target.value,
                          }))
                        }
                        placeholder={setting.is_secret && setting.has_value ? "변경하려면 새 값 입력" : ""}
                        className="w-full px-2 py-1.5 text-sm rounded bg-[var(--input)] border border-[var(--border)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)]"
                      />
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
