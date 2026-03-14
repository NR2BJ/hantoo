"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface TradingState {
  activeAccountId: string | null;
  setActiveAccount: (id: string | null) => void;
}

export const useTradingStore = create<TradingState>()(
  persist(
    (set) => ({
      activeAccountId: null,
      setActiveAccount: (id) => set({ activeAccountId: id }),
    }),
    { name: "hantoo-trading" }
  )
);
