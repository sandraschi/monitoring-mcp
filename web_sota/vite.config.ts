import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    allowedHosts: ['goliath'],
    port: 10850,
    strictPort: true,
    host: "127.0.0.1",
    proxy: {
      // Same-origin API: the frontend calls relative /api/* + /health, vite
      // forwards to the FastAPI backend. Absolute backend URLs are only used
      // inside the Tauri WebView (see src/lib/api.ts).
      "/api": { target: "http://127.0.0.1:10851", changeOrigin: true },
      "/health": { target: "http://127.0.0.1:10851", changeOrigin: true },
      "/docs": { target: "http://127.0.0.1:10851", changeOrigin: true },
      "/redoc": { target: "http://127.0.0.1:10851", changeOrigin: true },
      "/openapi.json": { target: "http://127.0.0.1:10851", changeOrigin: true },
    },
  }
});
