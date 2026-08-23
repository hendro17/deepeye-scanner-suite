<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { api } from "../api/client";

const route = useRoute();
const scanId = Number(route.params.id);
const findings = ref<any[]>([]);
const loading = ref(true);
const search = ref("");
const severityFilter = ref("");
const expanded = ref<number | null>(null);

const filtered = computed(() =>
  findings.value.filter(f => {
    if (severityFilter.value && f.severity !== severityFilter.value) return false;
    if (search.value && !`${f.type} ${f.url} ${f.payload || ""}`.toLowerCase().includes(search.value.toLowerCase())) return false;
    return true;
  })
);

const severityCounts = computed(() => {
  const counts: Record<string, number> = {};
  for (const f of findings.value) counts[f.severity] = (counts[f.severity] || 0) + 1;
  return counts;
});

onMounted(async () => {
  try {
    const res = await api.scans.findings(scanId);
    findings.value = res.vulnerabilities || [];
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="p-8">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold">Findings</h1>
        <p class="text-txt-secondary text-sm">Scan #{{ scanId }} · {{ findings.length }} vulnerabilities</p>
      </div>
      <RouterLink :to="`/scan/${scanId}/reports`" class="text-neon-cyan text-sm hover:underline">Reports →</RouterLink>
    </div>

    <!-- Severity badges -->
    <div class="flex gap-2 mb-4" v-if="!loading">
      <button v-for="sev in ['critical', 'high', 'medium', 'low', 'info']" :key="sev"
              @click="severityFilter = severityFilter === sev ? '' : sev"
              :class="['sev-badge', `sev-${sev}`, { 'opacity-40': severityFilter && severityFilter !== sev }]">
        {{ sev }} · {{ severityCounts[sev] || 0 }}
      </button>
    </div>

    <!-- Search -->
    <template v-if="!loading">
      <label for="findings-search" class="sr-only">Search findings</label>
      <input id="findings-search" v-model="search" type="text" placeholder="Search findings..."
             class="input-field mb-4" />
    </template>

    <div v-if="loading" class="text-txt-secondary py-8 text-center">Loading findings...</div>
    <div v-else-if="filtered.length === 0" class="text-txt-secondary py-8 text-center">No findings match filters.</div>
    <table v-else class="w-full text-sm">
      <thead>
        <tr class="text-left text-txt-secondary border-b border-[rgba(0,240,255,0.08)]">
          <th class="pb-2 font-medium">Severity</th>
          <th class="pb-2 font-medium">Type</th>
          <th class="pb-2 font-medium">URL</th>
          <th class="pb-2 font-medium"></th>
        </tr>
      </thead>
      <tbody>
        <template v-for="(f, i) in filtered" :key="i">
          <tr @click="expanded = expanded === i ? null : i"
              class="border-b border-[rgba(255,255,255,0.03)] cursor-pointer hover:bg-[rgba(0,240,255,0.03)] transition-colors">
            <td class="py-2"><span :class="['sev-badge', `sev-${f.severity}`]">{{ f.severity }}</span></td>
            <td class="py-2 font-mono text-xs">{{ f.type }}</td>
            <td class="py-2 truncate max-w-md text-txt-secondary">{{ f.url }}</td>
            <td class="py-2 text-txt-tertiary text-xs">{{ expanded === i ? "▲" : "▼" }}</td>
          </tr>
          <tr v-if="expanded === i">
            <td colspan="4" class="py-3 px-4 bg-[rgba(10,14,26,0.5)]">
              <div class="space-y-2 text-xs font-mono">
                <div v-if="f.parameter"><span class="text-txt-secondary">Parameter:</span> {{ f.parameter }}</div>
                <div v-if="f.payload"><span class="text-txt-secondary">Payload:</span> <span class="text-sev-medium">{{ f.payload }}</span></div>
                <div v-if="f.evidence"><span class="text-txt-secondary">Evidence:</span> {{ f.evidence }}</div>
                <div v-if="f.remediation"><span class="text-neon-green">Remediation:</span> {{ f.remediation }}</div>
                <div v-if="f.ai_evidence_summary"><span class="text-neon-cyan">AI Summary:</span> {{ f.ai_evidence_summary }}</div>
                <div v-if="f.cve_references?.length"><span class="text-txt-secondary">CVEs:</span> {{ f.cve_references.join(", ") }}</div>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>
