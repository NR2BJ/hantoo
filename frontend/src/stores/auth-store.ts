"use client";

import { create } from "zustand";
import { api } from "@/lib/api-client";

interface User {
  id: string;
  username: string;
  display_name: string;
  role: string;
  is_active: boolean;
  totp_enabled: boolean;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string, totpCode?: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (username, password, totpCode) => {
    await api.post("/api/auth/login", {
      username,
      password,
      totp_code: totpCode || null,
    });
    const user = await api.get<User>("/api/auth/me");
    set({ user, isAuthenticated: true, isLoading: false });
  },

  logout: async () => {
    await api.post("/api/auth/logout");
    set({ user: null, isAuthenticated: false });
  },

  fetchUser: async () => {
    try {
      const user = await api.get<User>("/api/auth/me");
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
