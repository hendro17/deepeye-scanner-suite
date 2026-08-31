<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api/client";

const route = useRoute();
const scanId = Number(route.params.id);
type ReportFile = Record<string, unknown> & { filename: string; format: string; size: number; created_at?: string };
const reports = ref<ReportFile[]>([]);
const loading = ref(true);

const formatColors: Record<string, string> = {
  html: "#00f0ff", pdf: "#ff3366", json: "#00ff88", sarif: "#ffaa00",
  junit: "#4a9eff", csv: "#6b7d99", xlsx: "#00ff88",
};

const FORMAT_OPTIONS = ["all", "html", "pdf", "json", "sarif", "junit", "csv", "xlsx"] as const;
const selectedFormat = ref<string>("all");

const filteredReports = computed(() => {
  if (selectedFormat.value === "all") return reports.value;
  return reports.value.filter((r) => extOf(r.filename) === selectedFormat.value);
});

function extOf(filename: string): string {
  const idx = filename.lastIndexOf(".");
  return idx >= 0 ? filename.slice(idx + 1).toLowerCase() : "";
}

onMounted(async () => {
  try {
    reports.value = await api.reports.list() as ReportFile[];
  } finally {
    loading.value = false;
  }
});

function fmtSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(1)} MB`;
}
</script>

<template>
  <div class="p-8">
    <div class="flex flex-wrap items-center justify-between gap-3 mb-8">
      <div>
        <h1 class="text-2xl font-bold mb-1">Reports</h1>
        <p class="text-txt-secondary text-sm">Scan #{{ scanId }} artifacts</p>
      </div>
      <select v-model="selectedFormat" aria-label="Filter by report format"
              class="bg-transparent border border-[rgba(0,240,255,0.12)] hover:border-[rgba(0,240,255,0.25)] rounded px-2 py-1.5 text-xs font-medium text-txt-secondary transition-all">
        <option v-for="f in FORMAT_OPTIONS" :key="f" :value="f">{{ f === "all" ? "All" : f }}</option>
      </select>
    </div>

    <div v-if="loading" class="text-txt-secondary py-8 text-center">Loading...</div>
    <div v-else-if="reports.length === 0" class="glass p-8 text-center text-txt-secondary">
      No report files found. Reports appear here after a scan completes.
    </div>
    <div v-else-if="filteredReports.length === 0" class="glass p-8 text-center text-txt-secondary">
      No {{ selectedFormat.toUpperCase() }} artifacts found.
    </div>
    <div v-else class="space-y-3">
      <div v-for="r in filteredReports" :key="r.filename"
           class="glass glass-hover p-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <span class="sev-badge" :style="{ color: formatColors[r.format] || '#6b7d99', borderColor: formatColors[r.format] || '#6b7d99' }">
            {{ r.format }}
          </span>
          <div>
            <p class="font-mono text-sm">{{ r.filename }}</p>
            <p class="text-xs text-txt-secondary">{{ fmtSize(r.size) }} · {{ r.created_at?.slice(0, 19) }}</p>
          </div>
        </div>
        <a :href="api.reports.downloadUrl(r.filename)" download
           class="neon-btn text-xs">Download</a>
      </div>
    </div>
  </div>
</template>
