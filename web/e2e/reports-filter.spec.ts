import { test, expect } from "@playwright/test";
import { stubApi } from "./api-stubs";

const reports = [
  { filename: "scan_report.html", format: "html", size: 20480, created_at: "2026-08-26T09:15:00Z" },
  { filename: "scan_report.pdf", format: "pdf", size: 409600, created_at: "2026-08-26T09:16:00Z" },
  { filename: "findings.json", format: "json", size: 1024, created_at: "2026-08-26T09:17:00Z" },
  { filename: "results.sarif", format: "sarif", size: 512000, created_at: "2026-08-26T09:18:00Z" },
];

test.describe("reports filter", () => {
  test("seeds mixed-format artifacts and filters the list by format", async ({ page }) => {
    await stubApi(page, { "GET /api/reports": reports });
    await page.goto("/#/scan/9/reports");

    await expect(page.getByRole("heading", { name: "Reports" })).toBeVisible();

    // "All" (default): every seeded artifact is listed.
    for (const r of reports) {
      await expect(page.getByText(r.filename)).toBeVisible();
    }

    const filter = page.getByLabel("Filter by report format");

    await filter.selectOption("html");
    await expect(page.getByText("scan_report.html")).toBeVisible();
    await expect(page.getByText("scan_report.pdf")).toHaveCount(0);
    await expect(page.getByText("findings.json")).toHaveCount(0);
    await expect(page.getByText("results.sarif")).toHaveCount(0);

    await filter.selectOption("pdf");
    await expect(page.getByText("scan_report.pdf")).toBeVisible();
    await expect(page.getByText("scan_report.html")).toHaveCount(0);

    await filter.selectOption("sarif");
    await expect(page.getByText("results.sarif")).toBeVisible();
    await expect(page.getByText("scan_report.pdf")).toHaveCount(0);

    // Back to all: everything returns.
    await filter.selectOption("all");
    await expect(page.getByText("findings.json")).toBeVisible();
    await expect(page.getByText("results.sarif")).toBeVisible();
  });

  test("shows the per-format empty state when nothing matches", async ({ page }) => {
    await stubApi(page, {
      "GET /api/reports": [reports[2]], // only a .json artifact
    });
    await page.goto("/#/scan/9/reports");

    const filter = page.getByLabel("Filter by report format");
    await filter.selectOption("xlsx");
    await expect(page.getByText("No XLSX artifacts found.")).toBeVisible();
  });
});
