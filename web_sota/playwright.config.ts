import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60000,
  retries: 1,
  use: {
    baseURL: "http://localhost:10850",
    headless: true,
    screenshot: "only-on-failure",
  },
  webServer: [
    {
      command:
        "uv run uvicorn monitoring_mcp.server:app --host 127.0.0.1 --port 10851 --log-level warning",
      port: 10851,
      cwd: "../",
      timeout: 30000,
      reuseExistingServer: false,
    },
    {
      command: "npm run dev -- --port 10850 --host 127.0.0.1",
      port: 10850,
      timeout: 60000,
      reuseExistingServer: false,
    },
  ],
});
