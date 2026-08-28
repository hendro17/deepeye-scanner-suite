<script setup lang="ts">
import { onMounted, computed } from "vue";
import { RouterLink } from "vue-router";
import VueApexCharts from "vue3-apexcharts";
import type { ApexOptions } from "apexcharts";
import { useScansStore } from "../stores/scans";

const store = useScansStore();
function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

const stats = computed(() => {
  const total = store.scans.length;
  const running = store.scans.filter(s => s.status === "running").length;
  const completed = store.scans.filter(s => s.status === "completed").length;
  const durations = store.scans
    .filter(s => s.status === "completed" && s.started_at && s.ended_at)
    .map(s => (new Date(s.ended_at).getTime() - new Date(s.started_at).getTime()) / 1000)
    .filter(d => d >= 0);
  const avgDuration = durations.length
    ? formatDuration(durations.reduce((a, b) => a + b, 0) / durations.length)
    : "—";
  return { total, running, completed, avgDuration };
});

const sevColors: Record<string, string> = {
  critical: "#ff3366", high: "#ff6644", medium: "#ffaa00", low: "#4a9eff", info: "#6b7d99",
};

const statusBadge: Record<string, string> = {
  running: "sev-low", completed: "sev-medium", failed: "sev-critical",
  stopped: "sev-info", pending: "sev-info",
};

const chartsReady = typeof window !== "undefined" && "ResizeObserver" in window;

const severitySeries = computed(() => {
  const counts = [0, 0, 0, 0, 0];
  for (const scan of store.scans) {
    const sc = scan.severity_counts;
    if (!sc) continue;
    counts[0] += sc.critical ?? 0;
    counts[1] += sc.high ?? 0;
    counts[2] += sc.medium ?? 0;
    counts[3] += sc.low ?? 0;
    counts[4] += sc.info ?? 0;
  }
  return counts;
});

const severityDonutOptions: ApexOptions = {
  chart: { type: "donut", background: "transparent", foreColor: "#8b95a7", fontFamily: "inherit" },
  labels: ["Critical", "High", "Medium", "Low", "Info"],
  colors: ["#ff3366", "#ff6644", "#ffaa00", "#4a9eff", "#6b7d99"],
  stroke: { width: 0 },
  legend: {
    position: "right",
    fontSize: "13px",
    labels: { colors: "#8b95a7" },
    markers: { size: 8 },
  },
  dataLabels: { enabled: false },
  plotOptions: {
    pie: {
      donut: {
        size: "72%",
        labels: {
          show: true,
          name: { color: "#8b95a7", fontSize: "13px" },
          value: { color: "#e0e6ed", fontSize: "24px", fontWeight: 700 },
          total: { show: true, label: "Findings", color: "#8b95a7", fontSize: "11px" },
        },
      },
    },
  },
  tooltip: { theme: "dark" },
};

function lastSevenDays() {
  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const keys: string[] = [];
  const labels: string[] = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    keys.push(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`);
    labels.push(dayNames[d.getDay()]);
  }
  return { keys, labels };
}

const historyDays = lastSevenDays();

const historySeries = computed(() => {
  const data = new Array(7).fill(0);
  for (const scan of store.scans) {
    const idx = historyDays.keys.indexOf(String(scan.created_at ?? "").slice(0, 10));
    if (idx === -1) continue;
    const sc = scan.severity_counts ?? {};
    data[idx] += (sc.critical ?? 0) + (sc.high ?? 0) + (sc.medium ?? 0) + (sc.low ?? 0) + (sc.info ?? 0);
  }
  return [{ name: "Vulnerabilities", data }];
});

const scanHistoryOptions: ApexOptions = {
  chart: { type: "bar", background: "transparent", foreColor: "#8b95a7", toolbar: { show: false }, fontFamily: "inherit" },
  colors: ["#00f0ff"],
  plotOptions: { bar: { borderRadius: 4, columnWidth: "60%" } },
  grid: { borderColor: "rgba(255, 255, 255, 0.05)" },
  xaxis: {
    categories: historyDays.labels,
    axisBorder: { show: false },
    axisTicks: { show: false },
    labels: { style: { colors: "#8b95a7" } },
  },
  yaxis: { labels: { style: { colors: "#8b95a7" } } },
  dataLabels: { enabled: false },
  tooltip: { theme: "dark" },
};

onMounted(() => store.fetchScans());
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-1">Dashboard</h1>
    <p class="text-txt-secondary text-sm mb-8">Security operations overview</p>

    <!-- Stat cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="glass glass-hover p-5" v-for="(card, i) in [
        { label: 'Total Scans', value: stats.total, color: '#00f0ff' },
        { label: 'Running', value: stats.running, color: '#00ff88' },
        { label: 'Completed', value: stats.completed, color: '#4a9eff' },
        { label: 'Avg Duration', value: stats.avgDuration, color: '#ffaa00' },
      ]" :key="i">
        <p class="text-xs text-txt-secondary uppercase tracking-wide">{{ card.label }}</p>
        <p class="text-3xl font-bold mt-2" :style="{ color: card.color }">{{ card.value }}</p>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-[8fr_4fr] gap-4 mb-8">
      <div class="glass p-5 min-h-[280px]">
        <h2 class="font-bold mb-2">Severity Distribution</h2>
        <VueApexCharts v-if="chartsReady" type="donut" height="240" :options="severityDonutOptions" :series="severitySeries" />
      </div>
      <div class="glass p-5 min-h-[280px]">
        <h2 class="font-bold mb-2">Scan History (7 Days)</h2>
        <VueApexCharts v-if="chartsReady" type="bar" height="240" :options="scanHistoryOptions" :series="historySeries" />
      </div>
    </div>

    <!-- Recent scans -->
    <div class="glass p-5">
      <div class="flex items-center justify-between mb-4">
        <h2 class="font-bold">Recent Scans</h2>
        <RouterLink to="/scan/new" class="neon-btn text-sm">+ New Scan</RouterLink>
      </div>

      <div v-if="store.loading" class="text-txt-secondary text-sm py-8 text-center">Loading...</div>
      <div v-else-if="store.scans.length === 0" class="text-txt-secondary text-sm py-8 text-center">
        No scans yet. Start your first scan.
      </div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="text-left text-txt-secondary border-b border-[rgba(0,240,255,0.08)]">
            <th class="pb-2 font-medium">ID</th>
            <th class="pb-2 font-medium">Target</th>
            <th class="pb-2 font-medium">Status</th>
            <th class="pb-2 font-medium">Created</th>
            <th class="pb-2 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="scan in store.scans.slice(0, 10)" :key="scan.id"
              class="border-b border-[rgba(255,255,255,0.03)] hover:bg-[rgba(0,240,255,0.03)] transition-colors">
            <td class="py-2 font-mono text-neon-cyan">#{{ scan.id }}</td>
            <td class="py-2 truncate max-w-xs">{{ scan.target }}</td>
            <td class="py-2">
              <span :class="['sev-badge', statusBadge[scan.status]]">{{ scan.status }}</span>
            </td>
            <td class="py-2 text-txt-secondary">{{ scan.created_at?.slice(0, 19) }}</td>
            <td class="py-2">
              <RouterLink :to="`/scan/${scan.id}/findings`" class="text-neon-cyan hover:underline text-xs">View</RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
