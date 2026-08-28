<script setup lang="ts">
import { reactive, ref } from "vue";

defineProps<{ tip: string }>();

const anchor = ref<HTMLElement | null>(null);
const bubble = ref<HTMLElement | null>(null);
const shown = ref(false);
const pos = reactive({ left: 0, top: 0 });

function show() {
  const a = anchor.value;
  const b = bubble.value;
  if (!a || !b) return;
  const r = a.getBoundingClientRect();
  const bw = b.offsetWidth;
  const bh = b.offsetHeight;
  const mainLeft = document.querySelector("main")?.getBoundingClientRect().left ?? 0;
  pos.left = Math.max(mainLeft + 8, Math.min(r.left + r.width / 2 - bw / 2, window.innerWidth - bw - 8));
  pos.top = r.top - bh - 8;
  if (pos.top < 8) pos.top = r.bottom + 8;
  pos.top = Math.max(8, Math.min(pos.top, window.innerHeight - bh - 8));
  shown.value = true;
}

function hide() {
  shown.value = false;
}
</script>

<template>
  <button
    ref="anchor"
    type="button"
    class="info-tip"
    aria-label="tooltip"
    @mouseenter="show"
    @mouseleave="hide"
    @focus="show"
    @blur="hide"
    @click.stop
  >?</button>
  <Teleport to="body">
    <span
      ref="bubble"
      class="info-tip-bubble"
      :class="{ visible: shown }"
      :style="{ left: pos.left + 'px', top: pos.top + 'px' }"
    >{{ tip }}</span>
  </Teleport>
</template>

<style>
.info-tip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  margin-left: 6px;
  flex-shrink: 0;
  border-radius: 9999px;
  border: 1px solid rgba(0, 240, 255, 0.3);
  color: #8b95a7;
  font-size: 10px;
  font-weight: 700;
  line-height: 1;
  cursor: help;
  vertical-align: middle;
  transition: all 0.15s;
}
.info-tip:hover,
.info-tip:focus-visible {
  border-color: rgba(0, 240, 255, 0.7);
  color: #00f0ff;
}
.info-tip-bubble {
  position: fixed;
  visibility: hidden;
  opacity: 0;
  max-width: 300px;
  background: #0d1520;
  border: 1px solid rgba(0, 240, 255, 0.3);
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12px;
  font-weight: 400;
  line-height: 1.5;
  color: #e0e6ed;
  text-align: left;
  white-space: normal;
  z-index: 9999;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
  pointer-events: none;
}
.info-tip-bubble.visible {
  visibility: visible;
  opacity: 1;
}
</style>
