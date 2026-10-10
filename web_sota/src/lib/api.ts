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
