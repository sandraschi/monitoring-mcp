// API base: same-origin relative ("") everywhere, so browser tabs on any
// hostname (localhost, LAN name, Tailscale MagicDNS) hit the vite proxy.
// Absolute backend URL only inside the Tauri WebView (no vite proxy there).
// Override with window.__MONITORING_API_BASE when embedding.
declare global {
  interface Window {
    __MONITORING_API_BASE?: string;
  }
}

const isTauri =
  typeof window !== "undefined" &&
  ("__TAURI__" in window || "__TAURI_INTERNALS__" in window);

export const API_BASE =
  (typeof window !== "undefined" && window.__MONITORING_API_BASE) ||
  (isTauri ? "http://127.0.0.1:10851" : "");

/** Fetch JSON with status-aware errors. Never throws a raw SyntaxError on
 *  plain-text 500s — surfaces backend `error`/`detail` or the HTTP status. */
export async function apiJSON(path: string, init?: RequestInit): Promise<any> {
  const res = await fetch(`${API_BASE}${path}`, init);
  const text = await res.text();
  let data: any = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    throw new Error(`Backend ${res.status}: ${text.slice(0, 160) || res.statusText}`);
  }
  if (!res.ok) {
    throw new Error(data?.error || data?.detail || `Backend ${res.status}: ${text.slice(0, 160)}`);
  }
  if (data?.error && !res.ok) throw new Error(data.error);
  return data;
}
