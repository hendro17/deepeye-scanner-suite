<script setup lang="ts">
import { ref, onMounted } from "vue";
import { api } from "../api/client";

const config = ref<any>({});
const providers = ref<any[]>([]);
const activeTab = ref("providers");
const saving = ref(false);
const savedMsg = ref("");

const providerNames = ["openai", "claude", "grok", "gemini", "ollama", "openrouter", "groq", "mistral", "litellm", "lmstudio", "orcarouter", "requesty"];

onMounted(async () => {
  const [cfgRes, provRes] = await Promise.all([api.config.get(), api.providers.status()]);
  config.value = cfgRes.config;
  providers.value = provRes;
});

async function save() {
  saving.value = true;
  try {
    await api.config.update(config.value);
    savedMsg.value = "Saved!";
    setTimeout(() => (savedMsg.value = ""), 2000);
  } finally {
    saving.value = false;
  }
}

async function updateCve() {
  await api.maintenance.updateCve();
  savedMsg.value = "CVE DB update started";
  setTimeout(() => (savedMsg.value = ""), 3000);
}

async function buildRag() {
  await api.maintenance.buildRag();
  savedMsg.value = "RAG index build started";
  setTimeout(() => (savedMsg.value = ""), 3000);
}
</script>

<template>
  <div class="p-8 max-w-3xl">
    <h1 class="text-2xl font-bold mb-1">Settings</h1>
    <p class="text-txt-secondary text-sm mb-8">Configure scanner and AI providers</p>

    <!-- Tabs -->
    <div class="flex gap-1 mb-6 border-b border-[rgba(0,240,255,0.08)] pb-px">
      <button v-for="tab in ['providers', 'scanner', 'maintenance']" :key="tab"
              @click="activeTab = tab"
              :class="['px-4 py-2 text-sm font-medium border-b-2 transition-all capitalize',
                activeTab === tab ? 'border-neon-cyan text-neon-cyan' : 'border-transparent text-txt-secondary hover:text-txt-primary']">
        {{ tab }}
      </button>
    </div>

    <!-- Providers tab -->
    <div v-if="activeTab === 'providers'" class="space-y-4">
      <div v-for="name in providerNames" :key="name" v-if="config.ai_providers">
        <div v-if="config.ai_providers[name]" class="glass p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-bold capitalize">{{ name }}</h3>
            <div class="flex items-center gap-2">
              <span v-if="config.ai_providers[name].enabled" class="sev-badge sev-low">Enabled</span>
              <span v-else class="sev-badge sev-info">Disabled</span>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-txt-secondary block mb-1">API Key</label>
              <input v-model="config.ai_providers[name].api_key" type="password"
                     class="input-field" placeholder="sk-..." />
            </div>
            <div>
              <label class="text-xs text-txt-secondary block mb-1">Model</label>
              <input v-model="config.ai_providers[name].model" type="text"
                     class="input-field" />
            </div>
            <div v-if="name === 'openai' || name === 'ollama' || name === 'openrouter'">
              <label class="text-xs text-txt-secondary block mb-1">Base URL <span class="text-txt-tertiary">(custom OpenAI-compatible)</span></label>
              <input v-model="config.ai_providers[name].base_url" type="text"
                     class="input-field" placeholder="https://your-api.com/v1" />
            </div>
            <div>
              <label class="text-xs text-txt-secondary block mb-1">Enabled</label>
              <label class="flex items-center gap-2 mt-2">
                <input v-model="config.ai_providers[name].enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
                <span class="text-sm">Active</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scanner tab -->
    <div v-if="activeTab === 'scanner' && config.scanner" class="space-y-4">
      <div class="glass p-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-xs text-txt-secondary block mb-1">Default Depth (1-10)</label>
            <input v-model.number="config.scanner.default_depth" type="number" min="1" max="10" class="input-field" />
          </div>
          <div>
            <label class="text-xs text-txt-secondary block mb-1">Default Threads (1-50)</label>
            <input v-model.number="config.scanner.default_threads" type="number" min="1" max="50" class="input-field" />
          </div>
          <div>
            <label class="text-xs text-txt-secondary block mb-1">AI Provider</label>
            <input v-model="config.scanner.ai_provider" type="text" class="input-field" />
          </div>
          <div>
            <label class="text-xs text-txt-secondary block mb-1">Proxy</label>
            <input v-model="config.scanner.proxy" type="text" class="input-field" placeholder="http://127.0.0.1:8080" />
          </div>
        </div>
      </div>
      <div class="glass p-4">
        <div class="grid grid-cols-3 gap-3">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.scanner.enable_recon" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Enable Recon</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.scanner.full_scan" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Full Scan</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.scanner.quick_scan" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Quick Scan</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Maintenance tab -->
    <div v-if="activeTab === 'maintenance'" class="space-y-4">
      <div class="glass p-4 flex items-center justify-between">
        <div>
          <h3 class="font-bold">Update CVE Database</h3>
          <p class="text-xs text-txt-secondary mt-1">Fetch latest CVEs from NVD</p>
        </div>
        <button @click="updateCve" class="neon-btn text-sm">Run</button>
      </div>
      <div class="glass p-4 flex items-center justify-between">
        <div>
          <h3 class="font-bold">Build RAG Index</h3>
          <p class="text-xs text-txt-secondary mt-1">Rebuild CVE RAG vector index</p>
        </div>
        <button @click="buildRag" class="neon-btn text-sm">Run</button>
      </div>
    </div>

    <!-- Save bar -->
    <div class="flex items-center gap-4 mt-6">
      <button @click="save" :disabled="saving" class="neon-btn">
        {{ saving ? "Saving..." : "Save Config" }}
      </button>
      <span v-if="savedMsg" class="text-neon-green text-sm">{{ savedMsg }}</span>
    </div>
  </div>
</template>
