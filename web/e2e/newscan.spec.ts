import { test, expect } from "@playwright/test";
import type { Route } from "@playwright/test";
import { fulfillJson, stubApi } from "./api-stubs";

test.describe("new scan form", () => {
  test("submits recon toggles + preset checks and lands on the live view", async ({
    page,
  }) => {
    const createScanBodies: Array<Record<string, unknown>> = [];

    await stubApi(page, {
      "GET /api/scans": [],
      "POST /api/scans": async (route: Route) => {
        // Capture the exact request payload the app sent.
        createScanBodies.push(route.request().postDataJSON() as Record<string, unknown>);
        await fulfillJson(route, { id: 42, status: "pending" });
      },
      "POST /api/scans/42/start": { id: 42, status: "running" },
    });

    await page.goto("/#/scan/new");
    await expect(page.getByRole("heading", { name: "New Scan" })).toBeVisible();

    await page.getByLabel("Target URL").fill("https://example.com");

    // Recon & scan-mode switches are role="switch" buttons whose accessible
    // context is their row text.
    const toggle = (label: string) =>
      page.locator("li").filter({ hasText: label }).getByRole("switch");
    await toggle("Enable Reconnaissance").click();
    await toggle("Scan Subdomains").click();

    // Secrets scanner switch carries an explicit aria-label.
    await page.getByRole("switch", { name: "Enable secrets scanner" }).click();
    await expect(
      page.locator("li").filter({ hasText: "Enable Reconnaissance" }).getByRole("switch")
    ).toHaveAttribute("aria-checked", "true");

    // Pick the Quick Scan preset → exactly 10 checks selected.
    await page.getByLabel("Check presets").selectOption("quick");
    await expect(page.getByText(/of \d+ selected/)).toContainText("10 of");

    // Authorization checkbox gates the submit button.
    await page.getByRole("checkbox").check();
    await page.getByRole("button", { name: "Launch Scan" }).click();

    // Wait on the intercepted POST itself — condition, not clock.
    await expect.poll(() => createScanBodies.length).toBeGreaterThan(0);
    const body = createScanBodies[0];

    expect(body.target_url).toBe("https://example.com");
    expect(Array.isArray(body.checks)).toBe(true);
    expect((body.checks as unknown[]).length).toBeGreaterThan(0);
    expect(body.enable_recon).toBe(true);
    expect(body.scan_subdomains).toBe(true);
    expect(body.secrets_enabled).toBe(true);
    expect(body.formats).toContain("html"); // default report format

    // Successful creation navigates to the live console of scan #42.
    await expect(page.getByRole("heading", { name: "Scan #42" })).toBeVisible();
  });

  test("submit stays disabled without authorization or target", async ({ page }) => {
    await stubApi(page, { "GET /api/scans": [] });
    await page.goto("/#/scan/new");

    const launch = page.getByRole("button", { name: "Launch Scan" });
    await expect(launch).toBeDisabled();

    await page.getByLabel("Target URL").fill("https://example.com");
    await expect(launch).toBeDisabled(); // still unauthorized

    await page.getByRole("checkbox").check();
    await expect(launch).toBeEnabled();
  });
});
