<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useScansStore } from "../stores/scans";
import { CHECK_CATEGORIES, ALL_CHECKS, checkLabel, presetChecks, type PresetId } from "../constants/checks";
import { SECRET_PATTERNS, ALL_SECRET_PATTERNS } from "../constants/secrets";
import { api } from "../api/client";

const router = useRouter();
const store = useScansStore();

const targetUrl = ref("");
const scopeNl = ref("");
const threads = ref(5);
const depth = ref(2);
const formats = ref<string[]>(["html"]);
const authorized = ref(false);
const submitting = ref(false);

const enableRecon = ref(false);
const fullScan = ref(false);
const quickScan = ref(false);
const scanSubdomains = ref(false);

const secretsEnabled = ref(false);
const selectedPatterns = ref<string[]>([...ALL_SECRET_PATTERNS]);

function togglePattern(id: string) {
  const idx = selectedPatterns.value.indexOf(id);
  if (idx >= 0) selectedPatterns.value.splice(idx, 1);
  else selectedPatterns.value.push(id);
}

const scanModeOptions = [
  { id: "enable_recon", label: "Enable Reconnaissance", get: () => enableRecon.value, set: (v: boolean) => (enableRecon.value = v) },
  { id: "full_scan", label: "Full Scan", get: () => fullScan.value, set: (v: boolean) => (fullScan.value = v) },
  { id: "quick_scan", label: "Quick Scan", get: () => quickScan.value, set: (v: boolean) => (quickScan.value = v) },
  { id: "scan_subdomains", label: "Scan Subdomains", get: () => scanSubdomains.value, set: (v: boolean) => (scanSubdomains.value = v) },
];

const crawlTargets = ref<string[]>([]);
const ingesting = ref(false);

async function onSpecFile(e: Event) {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = "";
  if (!file) return;
  ingesting.value = true;
  try {
    const res = await api.scans.ingestOpenApi(file.name, await file.text());
    crawlTargets.value = res.targets;
  } catch (err: any) {
    alert("Failed to parse spec: " + err.message);
  } finally {
    ingesting.value = false;
  }
}

function applyTarget(t: string) {
  targetUrl.value = t;
}

function applyAllToScope() {
  if (!crawlTargets.value.length) return;
  if (!targetUrl.value) targetUrl.value = crawlTargets.value[0];
  scopeNl.value = "only " + crawlTargets.value.join(" ");
}

const allFormats = ["html", "pdf", "json", "sarif", "junit", "csv", "xlsx"];

function toggleFormat(fmt: string) {
  const idx = formats.value.indexOf(fmt);
  if (idx >= 0) formats.value.splice(idx, 1);
  else formats.value.push(fmt);
}

const selectedChecks = ref<string[]>([...ALL_CHECKS]);

function isCheckSelected(id: string) {
  return selectedChecks.value.includes(id);
}

function toggleCheck(id: string) {
  const idx = selectedChecks.value.indexOf(id);
  if (idx >= 0) selectedChecks.value.splice(idx, 1);
  else selectedChecks.value.push(id);
}

function selectAllChecks() {
  selectedChecks.value = [...ALL_CHECKS];
}

function clearAllChecks() {
  selectedChecks.value = [];
}

function applyPreset(preset: PresetId) {
  if (preset === "custom") return;
  selectedChecks.value = presetChecks(preset);
}

function categorySelectedCount(checks: string[]) {
  return checks.filter((c) => selectedChecks.value.includes(c)).length;
}

function detectPreset(): PresetId {
  const current = [...selectedChecks.value].sort();
  for (const p of ["quick", "full", "api_focus"] as PresetId[]) {
    if (JSON.stringify(current) === JSON.stringify([...presetChecks(p)].sort())) return p;
  }
  return "custom";
}

const activePreset = computed(detectPreset);
const selectedCount = computed(() => selectedChecks.value.length);
const totalCount = ALL_CHECKS.length;

const canSubmit = computed(
  () => Boolean(targetUrl.value) && authorized.value && selectedCount.value > 0 && !submitting.value,
);

async function submit() {
  submitting.value = true;
  try {
    const res = await store.createScan({
      target_url: targetUrl.value,
      scope_nl: scopeNl.value || undefined,
      checks: selectedChecks.value,
      threads: threads.value,
      depth: depth.value,
      formats: formats.value,
      enable_recon: enableRecon.value,
      full_scan: fullScan.value,
      quick_scan: quickScan.value,
      scan_subdomains: scanSubdomains.value,
      secrets_enabled: secretsEnabled.value,
      secret_patterns: secretsEnabled.value ? selectedPatterns.value : undefined,
    });
    await store.startScan(res.id);
    router.push(`/scan/${res.id}/live`);
  } catch (e: any) {
    alert("Failed: " + e.message);
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="p-8 max-w-3xl">
    <h1 class="text-2xl font-bold mb-1">New Scan</h1>
    <p class="text-txt-secondary text-sm mb-8">Configure and launch a vulnerability scan</p>

    <div class="space-y-6">
      <!-- Target -->
      <div class="glass p-5">
        <label for="target-url" class="text-sm font-medium block mb-2">Target URL</label>
        <input id="target-url" v-model="targetUrl" type="text" placeholder="https://example.com"
               class="input-field font-mono" />
      </div>

      <!-- Scope NL -->
      <div class="glass p-5">
        <label for="scope-nl" class="text-sm font-medium block mb-2">Natural Language Scope <span class="text-txt-tertiary">(optional)</span></label>
        <input id="scope-nl" v-model="scopeNl" type="text" placeholder="Focus on authentication and API endpoints"
               class="input-field" />
      </div>

      <!-- OpenAPI Import -->
      <div class="glass p-5">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-1">
          <div>
            <label for="openapi-file" class="text-sm font-medium block cursor-pointer">Import OpenAPI Specification</label>
            <p class="text-xs text-txt-secondary mt-1">Load a .json or .yaml spec to seed crawl targets</p>
          </div>
          <input id="openapi-file" type="file" accept=".json,.yaml,.yml" :disabled="ingesting" @change="onSpecFile"
                 class="text-xs text-txt-secondary file:mr-3 file:rounded file:border-0 file:bg-[rgba(0,240,255,0.15)] file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-neon-cyan" />
        </div>
        <template v-if="crawlTargets.length">
          <p class="text-xs mt-3 mb-2"><span class="text-neon-cyan font-medium">{{ crawlTargets.length }}</span> crawl targets found</p>
          <div class="max-h-48 overflow-y-auto space-y-1.5 pr-1">
            <div v-for="t in crawlTargets" :key="t"
                 class="flex items-center justify-between gap-3 rounded border border-[rgba(0,240,255,0.12)] px-3 py-1.5">
              <code class="text-xs truncate font-mono">{{ t }}</code>
              <button type="button" @click="applyTarget(t)"
                      class="shrink-0 px-2 py-1 rounded text-[11px] font-medium border transition-all bg-[rgba(0,240,255,0.15)] text-neon-cyan border-[rgba(0,240,255,0.4)]">
                Use
              </button>
            </div>
          </div>
          <button type="button" @click="applyAllToScope"
                  class="mt-3 px-3 py-1.5 rounded text-xs font-medium border transition-all bg-[rgba(0,240,255,0.15)] text-neon-cyan border-[rgba(0,240,255,0.4)]">
            Apply all to target &amp; scope
          </button>
        </template>
      </div>

      <!-- Vulnerability Checks -->
      <div class="glass p-5">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wider text-txt-secondary">Vulnerability Checks</p>
            <p class="text-xs mt-1"><span class="text-neon-cyan font-medium">{{ selectedCount }}</span> of {{ totalCount }} selected</p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <select :value="activePreset" @change="applyPreset(($event.target as HTMLSelectElement).value as PresetId)"
                    aria-label="Check presets"
                    class="bg-transparent border border-[rgba(0,240,255,0.12)] hover:border-[rgba(0,240,255,0.25)] rounded px-2 py-1.5 text-xs font-medium text-txt-secondary transition-all">
              <option value="quick">Quick Scan</option>
              <option value="full">Full Scan</option>
              <option value="api_focus">API Focus</option>
              <option value="custom" disabled>Custom</option>
            </select>
            <button type="button" @click="selectAllChecks"
                    class="px-3 py-1.5 rounded text-xs font-medium border transition-all bg-[rgba(0,240,255,0.15)] text-neon-cyan border-[rgba(0,240,255,0.4)]">
              Select All
            </button>
            <button type="button" @click="clearAllChecks"
                    class="px-3 py-1.5 rounded text-xs font-medium border transition-all text-txt-secondary border-[rgba(0,240,255,0.12)] hover:border-[rgba(0,240,255,0.25)]">
              Clear
            </button>
          </div>
        </div>

        <div class="grid gap-3 [grid-template-columns:repeat(auto-fill,minmax(280px,1fr))]">
          <fieldset v-for="category in CHECK_CATEGORIES" :key="category.id" class="glass p-3 rounded-md border-0">
            <legend class="sr-only">{{ category.name }}</legend>
            <div class="flex items-center justify-between mb-2">
              <p class="text-[13px] font-semibold uppercase tracking-wide text-txt-secondary">{{ category.name }}</p>
              <span class="text-[11px] font-mono px-1.5 py-0.5 rounded border border-[rgba(0,240,255,0.12)] text-txt-secondary">
                {{ categorySelectedCount(category.checks) }}/{{ category.checks.length }}
              </span>
            </div>
            <ul class="space-y-2">
              <li v-for="checkId in category.checks" :key="checkId">
                <div class="flex items-center gap-2.5 cursor-pointer select-none" @click="toggleCheck(checkId)">
                  <button type="button" role="switch" :aria-checked="isCheckSelected(checkId)"
                          :aria-label="checkLabel(checkId)"
                          @click.stop="toggleCheck(checkId)"
                          class="relative shrink-0 w-10 h-[22px] rounded-full transition-colors duration-150 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neon-cyan"
                          :class="isCheckSelected(checkId) ? 'bg-[rgba(0,240,255,0.35)]' : 'bg-[rgba(255,255,255,0.08)]'">
                    <span aria-hidden="true"
                          class="absolute top-[2px] left-[2px] w-[18px] h-[18px] rounded-full transition-transform duration-150"
                          :class="isCheckSelected(checkId) ? 'translate-x-[18px] bg-neon-cyan' : 'translate-x-0 bg-txt-tertiary'"></span>
                  </button>
                  <span class="text-sm" :class="isCheckSelected(checkId) ? 'text-txt-primary' : 'text-txt-secondary'">{{ checkLabel(checkId) }}</span>
                </div>
              </li>
            </ul>
          </fieldset>
        </div>
      </div>

      <!-- Sliders -->
      <div class="grid grid-cols-2 gap-4">
        <div class="glass p-5">
          <label for="scan-threads" class="text-sm font-medium block mb-2">Threads: <span class="text-neon-cyan">{{ threads }}</span></label>
          <input id="scan-threads" v-model.number="threads" type="range" min="1" max="50" class="w-full" />
        </div>
        <div class="glass p-5">
          <label for="scan-depth" class="text-sm font-medium block mb-2">Depth: <span class="text-neon-cyan">{{ depth }}</span></label>
          <input id="scan-depth" v-model.number="depth" type="range" min="1" max="10" class="w-full" />
        </div>
      </div>

      <!-- Formats -->
      <div class="glass p-5">
        <p class="text-sm font-medium block mb-3">Report Formats</p>
        <div class="flex flex-wrap gap-2">
          <button v-for="fmt in allFormats" :key="fmt"
                  @click="toggleFormat(fmt)"
                  :class="['px-3 py-1.5 rounded text-xs font-medium border transition-all',
                    formats.includes(fmt)
                      ? 'bg-[rgba(0,240,255,0.15)] text-neon-cyan border-[rgba(0,240,255,0.4)]'
                      : 'text-txt-secondary border-[rgba(0,240,255,0.12)] hover:border-[rgba(0,240,255,0.25)]']">
            {{ fmt }}
          </button>
        </div>
      </div>

      <!-- Recon & Scan Mode -->
      <div class="glass p-5">
        <p class="text-sm font-medium block mb-3">Recon &amp; Scan Mode</p>
        <ul class="grid gap-2 sm:grid-cols-2">
          <li v-for="opt in scanModeOptions" :key="opt.id">
            <div class="flex items-center gap-2.5 cursor-pointer select-none" @click="opt.set(!opt.get())">
              <button type="button" role="switch" :aria-checked="opt.get()"
                      :aria-label="opt.label"
                      @click.stop="opt.set(!opt.get())"
                      class="relative shrink-0 w-10 h-[22px] rounded-full transition-colors duration-150 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neon-cyan"
                      :class="opt.get() ? 'bg-[rgba(0,240,255,0.35)]' : 'bg-[rgba(255,255,255,0.08)]'">
                <span aria-hidden="true"
                      class="absolute top-[2px] left-[2px] w-[18px] h-[18px] rounded-full transition-transform duration-150"
                      :class="opt.get() ? 'translate-x-[18px] bg-neon-cyan' : 'translate-x-0 bg-txt-tertiary'"></span>
              </button>
              <span class="text-sm" :class="opt.get() ? 'text-txt-primary' : 'text-txt-secondary'">{{ opt.label }}</span>
            </div>
          </li>
        </ul>
      </div>

      <!-- Secrets Scanner -->
      <div class="glass p-5">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p class="text-sm font-medium">Secrets Scanner</p>
            <p class="text-xs mt-1"><span class="text-neon-cyan font-medium">{{ selectedPatterns.length }}</span> of {{ SECRET_PATTERNS.length }} patterns selected</p>
          </div>
          <button type="button" role="switch" :aria-checked="secretsEnabled" aria-label="Enable secrets scanner"
                  @click="secretsEnabled = !secretsEnabled"
                  class="relative shrink-0 w-10 h-[22px] rounded-full transition-colors duration-150 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neon-cyan"
                  :class="secretsEnabled ? 'bg-[rgba(0,240,255,0.35)]' : 'bg-[rgba(255,255,255,0.08)]'">
            <span aria-hidden="true"
                  class="absolute top-[2px] left-[2px] w-[18px] h-[18px] rounded-full transition-transform duration-150"
                  :class="secretsEnabled ? 'translate-x-[18px] bg-neon-cyan' : 'translate-x-0 bg-txt-tertiary'"></span>
          </button>
        </div>

        <div v-if="secretsEnabled" class="flex flex-wrap gap-2 mt-4">
          <button v-for="p in SECRET_PATTERNS" :key="p.id" type="button" @click="togglePattern(p.id)"
                  :class="['px-3 py-1.5 rounded text-xs font-medium border transition-all',
                    selectedPatterns.includes(p.id)
                      ? 'bg-[rgba(0,240,255,0.15)] text-neon-cyan border-[rgba(0,240,255,0.4)]'
                      : 'text-txt-secondary border-[rgba(0,240,255,0.12)] hover:border-[rgba(0,240,255,0.25)]']">
            {{ p.label }}
          </button>
        </div>
      </div>

      <!-- Authorization -->
      <div class="glass p-5 border-[rgba(255,170,0,0.2)]">
        <label class="flex items-start gap-3 cursor-pointer">
          <input v-model="authorized" type="checkbox" class="mt-1 w-4 h-4 accent-[#00f0ff]" />
          <div>
            <p class="text-sm font-medium">I have explicit authorization to scan this target</p>
            <p class="text-xs text-txt-secondary mt-1">Unauthorized scanning is illegal and unethical. You are solely responsible.</p>
          </div>
        </label>
      </div>

      <button @click="submit" :disabled="!canSubmit" class="neon-btn w-full text-center">
        {{ submitting ? "Starting..." : "Launch Scan" }}
      </button>
    </div>
  </div>
</template>
