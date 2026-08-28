import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { api } from "./client";

function mockFetchOnce(data: any, ok = true, status = 200) {
  const mock = vi.fn().mockResolvedValue({
    ok,
    status,
    text: () => Promise.resolve(ok ? "" : "error"),
    json: () => Promise.resolve(data),
  } as any);
  vi.stubGlobal("fetch", mock);
  return mock;
}

describe("api client", () => {
  beforeEach(() => vi.restoreAllMocks());
  afterEach(() => vi.unstubAllGlobals());

  it("request throws on !ok", async () => {
    mockFetchOnce(null, false, 500);
    await expect(api.health()).rejects.toThrow("API 500");
  });

  it("health calls /health", async () => {
    const mock = mockFetchOnce({ status: "ok" });
    const res = await api.health();
    expect(res.status).toBe("ok");
    expect(mock).toHaveBeenCalledWith("/api/health", expect.anything());
  });

  it("scans.list", async () => {
    mockFetchOnce([{ id: 1 }]);
    const res = await api.scans.list();
    expect(res[0].id).toBe(1);
  });

  it("scans.get", async () => {
    mockFetchOnce({ id: 5 });
    const res = await api.scans.get(5);
    expect(res.id).toBe(5);
  });

  it("scans.create", async () => {
    mockFetchOnce({ id: 1, status: "pending" });
    const res = await api.scans.create({ target_url: "http://x.com" });
    expect(res.id).toBe(1);
  });

  it("scans.start", async () => {
    mockFetchOnce({ status: "running", pid: 123 });
    const res = await api.scans.start(1);
    expect(res.status).toBe("running");
  });

  it("scans.stop", async () => {
    mockFetchOnce({ status: "stopped" });
    const res = await api.scans.stop(1);
    expect(res.status).toBe("stopped");
  });

  it("scans.findings", async () => {
    mockFetchOnce({ vulnerabilities: [], total: 0 });
    const res = await api.scans.findings(1);
    expect(res.total).toBe(0);
  });

  it("scans.streamUrl", () => {
    expect(api.scans.streamUrl(42)).toBe("/api/scans/42/stream");
  });

  it("config.get", async () => {
    mockFetchOnce({ config: {}, masked: true });
    const res = await api.config.get();
    expect(res.masked).toBe(true);
  });

  it("config.update", async () => {
    mockFetchOnce({ success: true });
    const res = await api.config.update({ a: 1 });
    expect(res.success).toBe(true);
  });

  it("providers.status", async () => {
    mockFetchOnce([{ name: "openai" }]);
    const res = await api.providers.status();
    expect(res[0].name).toBe("openai");
  });

  it("providers.test", async () => {
    mockFetchOnce({ success: true });
    const res = await api.providers.test("openai");
    expect(res.success).toBe(true);
  });

  it("providers.test sends config body", async () => {
    const mock = mockFetchOnce({ success: true });
    await api.providers.test("openai", { config: { api_key: "x" } });
    expect(mock).toHaveBeenCalledWith(
      "/api/providers/test/openai",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ config: { api_key: "x" } }),
      })
    );
  });

  it("providers.test defaults body to {}", async () => {
    const mock = mockFetchOnce({ success: true });
    await api.providers.test("grok");
    expect(mock).toHaveBeenCalledWith(
      "/api/providers/test/grok",
      expect.objectContaining({ method: "POST", body: "{}" })
    );
  });

  it("reports.list", async () => {
    mockFetchOnce([{ filename: "a.html" }]);
    const res = await api.reports.list();
    expect(res[0].filename).toBe("a.html");
  });

  it("reports.downloadUrl", () => {
    expect(api.reports.downloadUrl("a.html")).toBe("/api/reports/a.html");
  });

  it("maintenance.updateCve", async () => {
    mockFetchOnce({ status: "started", pid: 1 });
    const res = await api.maintenance.updateCve();
    expect(res.status).toBe("started");
  });

  it("maintenance.buildRag", async () => {
    mockFetchOnce({ status: "started", pid: 2 });
    const res = await api.maintenance.buildRag();
    expect(res.status).toBe("started");
  });

  it("scans.compare", async () => {
    const mock = mockFetchOnce({ diff: [] });
    const res = await api.scans.compare(1, 2);
    expect(res.diff).toEqual([]);
    expect(mock).toHaveBeenCalledWith(
      "/api/scans/compare",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ scan_id_a: 1, scan_id_b: 2 }),
      })
    );
  });

  it("scans.ingestOpenApi", async () => {
    const mock = mockFetchOnce({ targets: ["/a"], count: 1 });
    const res = await api.scans.ingestOpenApi("spec.json", '{"openapi":"3.0.0"}');
    expect(res.count).toBe(1);
    expect(mock).toHaveBeenCalledWith(
      "/api/scans/ingest-openapi",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ filename: "spec.json", content: '{"openapi":"3.0.0"}' }),
      })
    );
  });
});
