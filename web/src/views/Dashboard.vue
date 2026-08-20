<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { RouterLink } from "vue-router";
import { useScansStore } from "../stores/scans";

const store = useScansStore();
const stats = computed(() => {
  const total = store.scans.length;
  const running = store.scans.filter(s => s.status === "running").length;
  const completed = store.scans.filter(s => s.status === "completed").length;
  return { total, running, completed };
});

const sevColors: Record<string, string> = {
  critical: "#ff3366", high: "#ff6644", medium: "#ffaa00", low: "#4a9eff", info: "#6b7d99",
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
        { label: 'Avg Duration', value: '—', color: '#ffaa00' },
      ]" :key="i">
        <p class="text-xs text-txt-secondary uppercase tracking-wide">{{ card.label }}</p>
        <p class="text-3xl font-bold mt-2" :style="{ color: card.color }">{{ card.value }}</p>
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
              <span :class="['sev-badge', {
                running: 'sev-low', completed: 'sev-medium', failed: 'sev-critical',
                stopped: 'sev-info', pending: 'sev-info'
              }[scan.status]]">{{ scan.status }}</span>
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
