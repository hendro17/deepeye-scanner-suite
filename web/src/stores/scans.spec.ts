import { describe, it, expect, vi, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useScansStore } from "./scans";

function mockFetch(responses: any[]) {
  const fn = vi.fn();
  responses.forEach((r) => fn.mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(r) }));
  return fn;
}

describe("useScansStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.stubGlobal("fetch", mockFetch([]));
  });

  it("fetchScans populates scans", async () => {
    const mockScans = [{ id: 1, target: "http://example.com", status: "completed" }];
    vi.stubGlobal("fetch", mockFetch([mockScans]));

    const store = useScansStore();
    await store.fetchScans();
    expect(store.scans).toEqual(mockScans);
    expect(store.loading).toBe(false);
  });

  it("createScan calls API and refreshes list", async () => {
    const created = { id: 1, status: "pending" };
    const refreshed = [{ id: 1, target: "http://x.com", status: "pending" }];
    vi.stubGlobal("fetch", mockFetch([created, refreshed]));

    const store = useScansStore();
    const res = await store.createScan({ target_url: "http://x.com" });
    expect(res.id).toBe(1);
    expect(store.scans.length).toBe(1);
  });

  it("loading flag resets on error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network")));
    const store = useScansStore();
    await expect(store.fetchScans()).rejects.toThrow();
    expect(store.loading).toBe(false);
  });
});
