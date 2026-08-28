import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import InfoTip from "./InfoTip.vue";

describe("InfoTip.vue", () => {
  it("renders tooltip icon and handles mouse events", async () => {
    const wrapper = mount(InfoTip, {
      props: { tip: "Petunjuk" },
    });
    expect(wrapper.text()).toBe("?");
    const trigger = wrapper.find(".info-tip");
    await trigger.trigger("mouseenter");
    expect((wrapper.vm as any).shown).toBe(true);
    await trigger.trigger("mouseleave");
    expect((wrapper.vm as any).shown).toBe(false);
  });
});
