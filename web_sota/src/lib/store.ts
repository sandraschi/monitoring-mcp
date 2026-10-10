import { create } from "zustand";

interface AppState {
  sidebarCollapsed: boolean;
  backendOk: boolean | null;
  backendVersion: string;
  toolCount: number;
  setSidebarCollapsed: (v: boolean) => void;
  setBackendOk: (v: boolean | null) => void;
  setBackendVersion: (v: string) => void;
  setToolCount: (v: number) => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarCollapsed: localStorage.getItem("sidebar-collapsed") === "true",
  backendOk: null,
  backendVersion: "",
  toolCount: 0,
  setSidebarCollapsed: (v) => {
    localStorage.setItem("sidebar-collapsed", String(v));
    set({ sidebarCollapsed: v });
  },
  setBackendOk: (v) => set({ backendOk: v }),
  setBackendVersion: (v) => set({ backendVersion: v }),
  setToolCount: (v) => set({ toolCount: v }),
}));
