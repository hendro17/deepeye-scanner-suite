import { describe, it, expect } from "vitest";
import router from "./index";

describe("router", () => {
  it("has expected routes", () => {
    const routes = router.getRoutes().map(r => r.path);
    expect(routes).toContain("/");
    expect(routes).toContain("/scan/new");
    expect(routes).toContain("/scan/:id/live");
    expect(routes).toContain("/scan/:id/findings");
    expect(routes).toContain("/settings");
  });

  it("resolves dashboard", async () => {
    const res = router.resolve("/");
    expect(res.name).toBe("dashboard");
  });

  it("resolves new-scan", async () => {
    const res = router.resolve("/scan/new");
    expect(res.name).toBe("new-scan");
  });
});
