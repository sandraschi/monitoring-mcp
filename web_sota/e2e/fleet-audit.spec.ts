import { test, expect } from "@playwright/test";

const BE = "http://127.0.0.1:10851";
const FE = "http://127.0.0.1:10850";

test.describe("Fleet Audit", () => {
  test("Backend health", async ({ request }) => {
    const resp = await request.get(`${BE}/api/health`);
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe("ok");
    expect(body.server).toBe("monitoring-mcp");
  });

  test("Backend plain health", async ({ request }) => {
    const resp = await request.get(`${BE}/health`);
    expect(resp.status()).toBe(200);
  });

  test("Frontend loads", async ({ page }) => {
    await page.goto(FE, { timeout: 15000 });
    await page.waitForTimeout(3000);
    await expect(page.locator("#root")).toBeAttached();
    await expect(page.locator('[data-testid="dashboard"]')).toBeAttached();
  });

  test("No console errors", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });
    await page.goto(FE, { timeout: 15000 });
    await page.waitForTimeout(3000);
    expect(errors.length).toBe(0);
  });

  test("No 404s on navigation", async ({ page }) => {
    const routes: string[] = ["/", "/chat", "/tools", "/skills", "/apps", "/logging", "/api-docs", "/help", "/settings"];
    const failures: string[] = [];
    page.on("response", (resp) => {
      if (resp.status() === 404 && resp.url().startsWith(FE)) {
        failures.push(resp.url());
      }
    });
    for (const route of routes) {
      await page.goto(`${FE}${route}`, { timeout: 10000 });
      await page.waitForTimeout(500);
    }
    expect(failures).toEqual([]);
  });

  test("Dashboard KPIs visible", async ({ page }) => {
    await page.goto(FE, { timeout: 15000 });
    await page.waitForTimeout(3000);
    await expect(page.locator('[data-testid="kpi-server"]')).toBeAttached();
    await expect(page.locator('[data-testid="kpi-tools"]')).toBeAttached();
  });
});
