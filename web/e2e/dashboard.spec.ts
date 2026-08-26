import { test, expect } from "@playwright/test";
import { stubApi } from "./api-stubs";

test.describe("dashboard", () => {
  test("renders stat cards, charts and recent scans from the scans store fetch", async ({
    page,
  }) => {
    const today = new Date().toISOString().slice(0, 10);
    const scans = [
      {
        id: 1,
        target: "https://example.com",
        status: "completed",
        created_at: `${today}T09:15:00`,
        severity_counts: { critical: 2, high: 3, medium: 4, low: 1, info: 0 },
      },
      {
        id: 2,
        target: "https://api.example.com",
        status: "running",
        created_at: `${today}T11:30:00`,
        severity_counts: { critical: 0, high: 1, medium: 2, low: 0, info: 5 },
      },
    ];

    await stubApi(page, { "GET /api/scans": scans });
    await page.goto("/#/");

    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();

    // Stat cards reflect the stubbed store state (2 scans, 1 running, 1 completed).
    const statCard = (label: string) =>
      page.locator(".glass.glass-hover").filter({ hasText: label });
    await expect(statCard("Total Scans").locator("p.text-3xl")).toHaveText("2");
    await expect(statCard("Running").locator("p.text-3xl")).toHaveText("1");
    await expect(statCard("Completed").locator("p.text-3xl")).toHaveText("1");
    await expect(statCard("Avg Duration")).toBeVisible();

    // Both ApexCharts mount (donut + bar) and render an <svg>.
    const canvases = page.locator(".apexcharts-canvas");
    await expect(canvases).toHaveCount(2);
    await expect(page.locator(".apexcharts-canvas svg").first()).toBeVisible();
    await expect(page.getByRole("heading", { name: "Severity Distribution" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Scan History (7 Days)" })).toBeVisible();

    // Recent scans table lists the stubbed scans.
    await expect(page.getByRole("row", { name: /example\.com/ }).first()).toBeVisible();
    await expect(page.getByRole("row", { name: /api\.example\.com/ })).toBeVisible();
  });

  test("shows the empty state when no scans exist", async ({ page }) => {
    await stubApi(page, { "GET /api/scans": [] });
    await page.goto("/#/");

    await expect(
      page.getByText("No scans yet. Start your first scan.")
    ).toBeVisible();
  });
});
