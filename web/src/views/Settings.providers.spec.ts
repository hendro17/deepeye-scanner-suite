import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import Settings from "./Settings.vue";

vi.mock("../api/client", () => ({
  api: {
    config: { get: vi.fn() },
    providers: { status: vi.fn(), test: vi.fn() },
    templates: { list: vi.fn() },
    maintenance: { updateCve: vi.fn(), buildRag: vi.fn() },
  },
}));

import { api } from "../api/client";

const baseConfig = {
  ai_providers: {
    openai: {
      api_key: "sk-test-123",
      model: "gpt-4o",
      base_url: "https://api.openai.com/v1",
      enabled: true,
    },
    ollama: {
      api_key: "",
      model: "llama3",
      base_url: "http://localhost:11434/v1",
      enabled: true,
    },
  },
};

describe("Settings.vue providers test button", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.mocked(api.config.get).mockResolvedValue({
      config: JSON.parse(JSON.stringify(baseConfig)),
      masked: false,
    } as any);
    vi.mocked(api.providers.status).mockResolvedValue([]);
    vi.mocked(api.providers.test).mockReset();
    vi.mocked(api.providers.test).mockResolvedValue({
      provider: "openai",
      success: true,
      message: "ok",
      latency_ms: 120,
    });
  });

  function mountSettings() {
    return mount(Settings, { global: { stubs: { InfoTip: true } } });
  }

  function testButton(wrapper: ReturnType<typeof mountSettings>, label: string) {
    const btn = wrapper.findAll("button").find((b) => b.text() === label);
    expect(btn, `button "${label}" not found`).toBeTruthy();
    return btn!;
  }

  it("shows Test Connection label for keyless ollama", async () => {
    const wrapper = mountSettings();
    await flushPromises();
    expect(testButton(wrapper, "Test Connection")).toBeDefined();
    expect(wrapper.findAll("button").some((b) => b.text() === "Test API Key")).toBe(true);
  });

  it("sends current provider values on Test API Key click", async () => {
    const wrapper = mountSettings();
    await flushPromises();
    await testButton(wrapper, "Test API Key").trigger("click");
    await flushPromises();
    expect(api.providers.test).toHaveBeenCalledWith("openai", {
      config: {
        api_key: "sk-test-123",
        base_url: "https://api.openai.com/v1",
        model: "gpt-4o",
      },
    });
    expect(wrapper.text()).toContain("✓ Connected · ok 120ms");
  });

  it("keyless provider sends base_url + model only, no api_key", async () => {
    vi.mocked(api.providers.test).mockResolvedValue({
      provider: "ollama",
      success: true,
      message: "connected",
      latency_ms: 8,
    });
    const wrapper = mountSettings();
    await flushPromises();
    await testButton(wrapper, "Test Connection").trigger("click");
    await flushPromises();
    expect(api.providers.test).toHaveBeenCalledWith("ollama", {
      config: { base_url: "http://localhost:11434/v1", model: "llama3" },
    });
    expect(wrapper.text()).toContain("✓ Connected · connected 8ms");
  });

  it("shows red message when request throws", async () => {
    vi.mocked(api.providers.test).mockRejectedValue(new Error("API 500: boom"));
    const wrapper = mountSettings();
    await flushPromises();
    await testButton(wrapper, "Test API Key").trigger("click");
    await flushPromises();
    expect(wrapper.text()).toContain("✗ API 500: boom");
  });

  it("shows Configured badge from provider status even before a test", async () => {
    vi.mocked(api.providers.status).mockResolvedValue([
      { name: "openai", enabled: true, configured: true, model: "gpt-4o", base_url: "" },
      { name: "ollama", enabled: true, configured: false, model: "llama3", base_url: "" },
    ]);
    const wrapper = mountSettings();
    await flushPromises();
    expect(wrapper.text()).toContain("Configured");
    expect(wrapper.text()).not.toContain("✓ Connected");
  });

  it("gains Connected badge only after a successful test", async () => {
    vi.mocked(api.providers.status).mockResolvedValue([
      { name: "openai", enabled: true, configured: true, model: "gpt-4o", base_url: "" },
    ]);
    const wrapper = mountSettings();
    await flushPromises();
    expect(wrapper.text()).toContain("Configured");
    expect(wrapper.text()).not.toContain("✓ Connected");
    await testButton(wrapper, "Test API Key").trigger("click");
    await flushPromises();
    expect(wrapper.text()).toContain("Configured");
    expect(wrapper.text()).toContain("✓ Connected");
  });

  it("persists Connected badge after a successful test", async () => {
    const wrapper = mountSettings();
    await flushPromises();
    await testButton(wrapper, "Test API Key").trigger("click");
    await flushPromises();
    expect(wrapper.findAll(".sev-green").length).toBeGreaterThanOrEqual(1);
    expect(JSON.parse(localStorage.getItem("deepeye:providers-connected") ?? "{}").openai.ok).toBe(true);
  });
});