import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import router from "./router";
import App from "./App.vue";

describe("App.vue", () => {
  it("mounts with router and pinia", async () => {
    const { vi } = await import("vitest");
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve([]) } as any);
    vi.stubGlobal("fetch", fetchMock);
    const pinia = createPinia();
    const wrapper = mount(App, {
      global: {
        plugins: [pinia, router],
      },
    });
    // wait for async onMounted in Dashboard etc
    await new Promise((r) => setTimeout(r, 50));
    expect(wrapper.text()).toContain("DeepEye");
    expect(wrapper.text()).toContain("Scanner Suite");
    expect(wrapper.find("main").exists()).toBe(true);
    vi.unstubAllGlobals();
  });
});
