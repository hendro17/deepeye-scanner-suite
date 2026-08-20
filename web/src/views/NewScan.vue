<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useScansStore } from "../stores/scans";

const router = useRouter();
const store = useScansStore();

const targetUrl = ref("");
const scopeNl = ref("");
const threads = ref(5);
const depth = ref(2);
const formats = ref<string[]>(["html"]);
const authorized = ref(false);
const submitting = ref(false);

const allFormats = ["html", "pdf", "json", "sarif", "junit", "csv", "xlsx"];

function toggleFormat(fmt: string) {
  const idx = formats.value.indexOf(fmt);
  if (idx >= 0) formats.value.splice(idx, 1);
  else formats.value.push(fmt);
}

const canSubmit = computed(() => targetUrl.value && authorized.value && !submitting.value);

async function submit() {
  submitting.value = true;
  try {
    const res = await store.createScan({
      target_url: targetUrl.value,
      scope_nl: scopeNl.value || undefined,
      threads: threads.value,
      depth: depth.value,
      formats: formats.value,
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
        <label class="text-sm font-medium block mb-2">Target URL</label>
        <input v-model="targetUrl" type="text" placeholder="https://example.com"
               class="input-field font-mono" />
      </div>

      <!-- Scope NL -->
      <div class="glass p-5">
        <label class="text-sm font-medium block mb-2">Natural Language Scope <span class="text-txt-tertiary">(optional)</span></label>
        <input v-model="scopeNl" type="text" placeholder="Focus on authentication and API endpoints"
               class="input-field" />
      </div>

      <!-- Sliders -->
      <div class="grid grid-cols-2 gap-4">
        <div class="glass p-5">
          <label class="text-sm font-medium block mb-2">Threads: <span class="text-neon-cyan">{{ threads }}</span></label>
          <input v-model.number="threads" type="range" min="1" max="50" class="w-full" />
        </div>
        <div class="glass p-5">
          <label class="text-sm font-medium block mb-2">Depth: <span class="text-neon-cyan">{{ depth }}</span></label>
          <input v-model.number="depth" type="range" min="1" max="10" class="w-full" />
        </div>
      </div>

      <!-- Formats -->
      <div class="glass p-5">
        <label class="text-sm font-medium block mb-3">Report Formats</label>
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
