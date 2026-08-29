<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { api } from "../api/client";

type ScanRecord = Record<string, unknown> & { id: number; status: string; target?: string };
type CompareResult = Record<string, unknown> & {
  new_count: number; resolved_count: number; persisting_count: number;
  new_vulnerabilities: Record<string, unknown>[];
  resolved_vulnerabilities: Record<string, unknown>[];
  severity_changes: Array<Record<string, unknown> & { type: string; url: string; parameter?: string; severity_a: string; severity_b: string }>;
};

const scans = ref<ScanRecord[]>([]);
const loadingScans = ref(true);
const scanIdA = ref<number | "">("");
const scanIdB = ref<number | "">("");
const comparing = ref(false);
const error = ref("");
const result = ref<CompareResult | null>(null);
const expandedSection = ref<string>("new");

const selectable = computed(() =>
  scans.value.filter(s => s.status === "completed" || s.status === "stopped")
);

const canCompare = computed(() =>
  scanIdA.value !== "" && scanIdB.value !== "" && scanIdA.value !== scanIdB.value
);

const sections = computed(() => {
  if (!result.value) return [];
  const r = result.value;
  return [
    { key: "new", label: "New", count: r.new_count, items: r.new_vulnerabilities },
    { key: "resolved", label: "Resolved", count: r.resolved_count, items: r.resolved_vulnerabilities },
    { key: "persisting", label: "Persisting", count: r.persisting_count, items: null as unknown as Record<string, unknown>[] | null },
  ];
});

onMounted(async () => {
  try {
    scans.value = await api.scans.list() as ScanRecord[];
  } finally {
    loadingScans.value = false;
  }
});

async function compare() {
  if (!canCompare.value) return;
  comparing.value = true;
  error.value = "";
  result.value = null;
  try {
    result.value = await api.scans.compare(Number(scanIdA.value), Number(scanIdB.value)) as CompareResult;
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : String(err) || "Comparison failed.";
  } finally {
    comparing.value = false;
  }
}
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-1">Compare Scans</h1>
    <p class="text-txt-secondary text-sm mb-8">Diff findings between two completed scans</p>

    <div class="glass p-5 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
        <div>
          <label for="scan-a" class="text-xs text-txt-secondary uppercase tracking-wide">Baseline (Scan A)</label>
          <select id="scan-a" v-model.number="scanIdA" class="input-field mt-1">
            <option disabled value="">Select scan...</option>
            <option v-for="s in selectable" :key="s.id" :value="s.id">#{{ s.id }} · {{ s.target }}</option>
          </select>
        </div>
        <div>
          <label for="scan-b" class="text-xs text-txt-secondary uppercase tracking-wide">Current (Scan B)</label>
          <select id="scan-b" v-model.number="scanIdB" class="input-field mt-1">
            <option disabled value="">Select scan...</option>
            <option v-for="s in selectable" :key="s.id" :value="s.id">#{{ s.id }} · {{ s.target }}</option>
          </select>
        </div>
        <button @click="compare" :disabled="!canCompare || comparing" class="neon-btn h-[42px]">
          {{ comparing ? "Comparing..." : "Compare" }}
        </button>
      </div>
      <p v-if="loadingScans" class="text-txt-secondary text-xs mt-3">Loading scans...</p>
      <p v-else-if="selectable.length === 0" class="text-txt-secondary text-xs mt-3">
        No completed scans yet. Run a scan first.
      </p>
    </div>

    <div v-if="error" class="sev-badge sev-critical mb-6">{{ error }}</div>

    <template v-if="result">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div v-for="(card, i) in [
          { label: 'New', value: result.new_count, color: '#ff5c85' },
          { label: 'Resolved', value: result.resolved_count, color: '#00ff88' },
          { label: 'Persisting', value: result.persisting_count, color: '#ffaa00' },
          { label: 'Severity Changes', value: result.severity_changes.length, color: '#00f0ff' },
        ]" :key="i" class="glass p-5">
          <p class="text-xs text-txt-secondary uppercase tracking-wide">{{ card.label }}</p>
          <p class="text-3xl font-bold mt-2" :style="{ color: card.color }">{{ card.value }}</p>
        </div>
      </div>

      <div v-if="result.severity_changes.length > 0" class="glass p-5 mb-6">
        <h2 class="font-bold mb-3">Severity Changes</h2>
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-txt-secondary border-b border-[rgba(0,240,255,0.08)]">
              <th class="pb-2 font-medium">Type</th>
              <th class="pb-2 font-medium">URL</th>
              <th class="pb-2 font-medium">Parameter</th>
              <th class="pb-2 font-medium">Change</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(c, i) in result.severity_changes" :key="i"
                class="border-b border-[rgba(255,255,255,0.03)]">
              <td class="py-2 font-mono text-xs">{{ c.type }}</td>
              <td class="py-2 truncate max-w-md text-txt-secondary">{{ c.url }}</td>
              <td class="py-2 font-mono text-xs">{{ (c.parameter as string) || "—" }}</td>
              <td class="py-2">
                <span :class="['sev-badge', `sev-${String(c.severity_a)}`]">{{ c.severity_a }}</span>
                →
                <span :class="['sev-badge', `sev-${String(c.severity_b)}`]">{{ c.severity_b }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-for="section in sections" :key="section.key" class="glass p-5 mb-6">
        <button @click="expandedSection = expandedSection === section.key ? '' : section.key"
                class="flex items-center gap-3 w-full text-left">
          <h2 class="font-bold">
            {{ section.label }}
            <span :class="['sev-badge ml-2',
              section.key === 'new' ? 'sev-critical' : section.key === 'resolved' ? 'sev-low' : 'sev-medium']">
              {{ section.count }}
            </span>
          </h2>
          <span class="ml-auto text-txt-tertiary text-xs">
            {{ expandedSection === section.key ? "▲" : "▼" }}
          </span>
        </button>

        <div v-if="expandedSection === section.key" class="mt-4">
          <div v-if="!section.items || section.items.length === 0"
               class="text-txt-secondary text-sm py-4 text-center">No {{ section.label.toLowerCase() }} findings.</div>
          <table v-else class="w-full text-sm">
            <thead>
              <tr class="text-left text-txt-secondary border-b border-[rgba(0,240,255,0.08)]">
                <th class="pb-2 font-medium">Severity</th>
                <th class="pb-2 font-medium">Type</th>
                <th class="pb-2 font-medium">URL</th>
                <th class="pb-2 font-medium">Parameter</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(f, i) in section.items" :key="i"
                  class="border-b border-[rgba(255,255,255,0.03)] hover:bg-[rgba(0,240,255,0.03)] transition-colors">
                <td class="py-2"><span :class="['sev-badge', `sev-${String((f as Record<string, unknown>).severity)}`]">{{ (f as Record<string, unknown>).severity }}</span></td>
                <td class="py-2 font-mono text-xs">{{ (f as Record<string, unknown>).type }}</td>
                <td class="py-2 truncate max-w-md text-txt-secondary">{{ (f as Record<string, unknown>).url }}</td>
                <td class="py-2 font-mono text-xs">{{ ((f as Record<string, unknown>).parameter as string) || "—" }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
