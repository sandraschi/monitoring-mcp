import { useCallback, useEffect } from "react";
import { API_BASE } from "@/lib/api";
import { useZoom } from "@/lib/use-zoom";
import { useAppStore } from "@/lib/store";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

interface AppLayoutProps {
  children: React.ReactNode;
}

async function checkBackendHealth() {
  try {
    const r = await fetch(`${API_BASE}/api/health`);
    if (!r.ok) return { ok: false, error: `HTTP ${r.status}` };
    const data = await r.json();
    return { ok: true, version: data.version, tool_count: data.tool_count };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : "Network error" };
  }
}

export function AppLayout({ children }: AppLayoutProps) {
  useZoom();
  const { sidebarCollapsed, setSidebarCollapsed, setBackendOk, setBackendVersion, setToolCount } = useAppStore();

  const refresh = useCallback(async () => {
    const h = await checkBackendHealth();
    setBackendOk(h.ok);
    if (h.ok && "version" in h) {
      setBackendVersion((h as any).version || "");
      setToolCount((h as any).tool_count || 0);
    }
  }, [setBackendOk, setBackendVersion, setToolCount]);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 10000);
    return () => clearInterval(interval);
  }, [refresh]);

  useEffect(() => {
    let unlisten: (() => void) | undefined;
    (async () => {
      try {
        const { listen } = await import("@tauri-apps/api/event");
        unlisten = await listen<string>("backend-status", (event) => {
          if (event.payload === "ready") {
            refresh();
          } else if (typeof event.payload === "string" && event.payload.startsWith("error:")) {
            setBackendOk(false);
          }
        });
      } catch {
        /* not in Tauri — HTTP polling handles it */
      }
    })();
    return () => { if (unlisten) unlisten(); };
  }, [refresh, setBackendOk]);

  return (
    <div className="flex min-h-screen flex-col bg-slate-950 text-slate-50 font-sans selection:bg-emerald-500/30">
      <div className="flex flex-1 overflow-hidden">
        <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-6 scroll-smooth">
            <div className="mx-auto max-w-7xl animate-in fade-in duration-500">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
