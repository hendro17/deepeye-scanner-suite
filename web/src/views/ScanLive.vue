<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { api } from "../api/client";

const route = useRoute();
const scanId = Number(route.params.id);
const logs = ref<{ line: string; timestamp: string }[]>([]);
const status = ref("connecting");
const consoleEl = ref<HTMLElement | null>(null);
let es: EventSource | null = null;

function logClass(line: string): string {
  if (line.includes("[CRITICAL]") || line.includes("[ERROR]")) return "#ff3366";
  if (line.includes("[WARN]")) return "#ffaa00";
  if (line.includes("[INFO]")) return "#00f0ff";
  return "#00ff88";
}

async function autoScroll() {
  await nextTick();
  if (consoleEl.value) consoleEl.value.scrollTop = consoleEl.value.scrollHeight;
}

onMounted(() => {
  es = new EventSource(api.scans.streamUrl(scanId));

  es.addEventListener("log", (e: MessageEvent) => {
    const data = JSON.parse(e.data) as { line: string; timestamp: string };
    logs.value.push(data);
    if (logs.value.length > 10000) logs.value.shift();
    void autoScroll();
  });

  es.addEventListener("done", (e: MessageEvent) => {
    const data = JSON.parse(e.data) as { exit_code: number };
    logs.value.push({ line: `[SCAN COMPLETE] exit code: ${data.exit_code}`, timestamp: new Date().toISOString() });
    status.value = data.exit_code === 0 ? "completed" : "failed";
    es?.close();
    void autoScroll();
  });

  es.onerror = () => {
    if (status.value === "connecting") {
      status.value = "error";
      es?.close();
    }
  };
});

onUnmounted(() => es?.close());

async function stopScan() {
  await api.scans.stop(scanId);
  status.value = "stopped";
  es?.close();
}
</script>

<template>
  <div class="p-8 h-full flex flex-col">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h1 class="text-2xl font-bold">Scan #{{ scanId }}</h1>
        <p class="text-txt-secondary text-sm">Live console</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <div :class="['w-2 h-2 rounded-full',
            status === 'running' ? 'bg-neon-green animate-pulse-glow' :
            status === 'completed' ? 'bg-neon-green' :
            status === 'failed' ? 'bg-sev-critical' :
            status === 'stopped' ? 'bg-sev-info' : 'bg-sev-info']"></div>
          <span class="text-sm capitalize">{{ status }}</span>
        </div>
        <button v-if="status === 'running'" @click="stopScan"
                class="px-3 py-1.5 rounded text-xs font-medium border border-[rgba(255,51,102,0.3)] text-sev-critical hover:bg-[rgba(255,51,102,0.1)] transition-all">
          Stop
        </button>
        <RouterLink v-if="status !== 'running'" :to="`/scan/${scanId}/findings`"
                    class="neon-btn text-xs">View Findings</RouterLink>
      </div>
    </div>

    <div ref="consoleEl" class="terminal flex-1 p-4 rounded-lg overflow-y-auto">
      <div v-if="logs.length === 0" class="text-txt-tertiary">Waiting for output...</div>
      <div v-for="(log, i) in logs" :key="i" class="whitespace-pre-wrap break-all">
        <span :style="{ color: logClass(log.line) }">{{ log.line }}</span>
      </div>
    </div>
  </div>
</template>
