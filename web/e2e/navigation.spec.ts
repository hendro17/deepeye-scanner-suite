import { test, expect } from "@playwright/test";
import { stubApi } from "./api-stubs";

test.describe("sidebar navigation", () => {
  test("sidebar links navigate between the main routes", async ({ page }) => {
    await stubApi(page, { "GET /api/scans": [] });
    await page.goto("/#/");

    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();

    // Scope to the sidebar <nav>: the Dashboard also has a "+ New Scan" link
    // in its Recent Scans card that would otherwise collide on "New Scan".
    const navLink = (name: string) =>
      page.locator("nav").getByRole("link", { name, exact: true });

    await navLink("New Scan").click();
    await expect(page.getByRole("heading", { name: "New Scan" })).toBeVisible();
    await expect(page).toHaveURL(/#\/scan\/new$/);

    await navLink("Compare Scans").click();
    await expect(page.getByRole("heading", { name: "Compare Scans" })).toBeVisible();

    await navLink("Settings").click();
    await expect(page.getByRole("heading", { name: "Settings" })).toBeVisible();

    await navLink("Dashboard").click();
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
    await expect(page).toHaveURL(/#\/$/);
  });

  test("per-scan reports route renders its headline", async ({ page }) => {
    await stubApi(page, { "GET /api/reports": [] });
    await page.goto("/#/scan/7/reports");

    await expect(page.getByRole("heading", { name: "Reports" })).toBeVisible();
    await expect(page.getByText("Scan #7 artifacts")).toBeVisible();
  });
});
