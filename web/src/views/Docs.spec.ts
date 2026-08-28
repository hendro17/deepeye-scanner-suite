import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import Docs from "./Docs.vue";

describe("Docs.vue", () => {
  it("renders documentation component cleanly", () => {
    const wrapper = mount(Docs);
    expect(wrapper.text()).toContain("Pengantar");
    expect(wrapper.text()).toContain("Cara Memulai");
  });
});
