<script setup lang="ts">
import InfoTip from "../components/InfoTip.vue";
import { useProviderTest, type ProviderConfig } from "../composables/useProviderTest";

type AiProviderConfig = ProviderConfig & { enabled?: boolean };
type ProvidersConfig = Record<string, AiProviderConfig>;
type AppConfig = Record<string, unknown> & { ai_providers?: ProvidersConfig };
type ProviderStatus = { name: string; enabled?: boolean; configured?: boolean };

const props = defineProps<{ config: AppConfig; providers: ProviderStatus[] }>();

const { isKeyless, isConnected, testStatus, testProvider: runProviderTest } = useProviderTest();

function statusOf(name: string) {
  return props.providers.find((p) => p.name === name);
}

function testProvider(name: string) {
  const cfg = props.config.ai_providers?.[name];
  return runProviderTest(name, cfg);
}

const providerNames = ["openai", "claude", "grok", "gemini", "ollama", "openrouter", "groq", "mistral", "litellm", "lmstudio", "orcarouter"];
</script>

<template>
  <div class="space-y-4">
    <template v-for="name in providerNames" :key="name">
      <div v-if="config.ai_providers?.[name]" class="glass p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-bold capitalize">{{ name }}</h3>
          <div class="flex items-center gap-2 flex-wrap">
            <span v-if="config.ai_providers[name]?.enabled" class="sev-badge sev-low">Enabled</span>
            <span v-else class="sev-badge sev-info">Disabled</span>
            <span v-if="statusOf(name)?.configured" class="sev-badge sev-info">Configured</span>
            <span v-if="isConnected(name)" class="sev-badge sev-green">✓ Connected</span>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label :for="'api-key-' + name" class="text-xs text-txt-secondary block mb-1">API Key<InfoTip tip="Kunci rahasia dari provider. Didapat dari dashboard akun provider masing-masing. Disimpan terenkripsi di konfigurasi lokal." /></label>
            <input :id="'api-key-' + name" v-model="config.ai_providers[name]!.api_key" type="password"
                   class="input-field" placeholder="sk-..." />
          </div>
          <div>
            <label :for="'provider-model-' + name" class="text-xs text-txt-secondary block mb-1">Model<InfoTip tip="Nama model AI yang dipakai provider ini untuk analisis hasil scan, mis. gpt-4o, claude-3-5-sonnet, atau nama model lokal Ollama." /></label>
            <input :id="'provider-model-' + name" v-model="config.ai_providers[name]!.model" type="text"
                   class="input-field" />
          </div>
          <div v-if="name === 'openai' || name === 'ollama' || name === 'openrouter'">
            <label :for="'base-url-' + name" class="text-xs text-txt-secondary block mb-1">Base URL <span class="text-txt-tertiary">(custom OpenAI-compatible)</span><InfoTip tip="URL endpoint API khusus. Isi jika memakai server OpenAI-compatibel sendiri, Ollama lokal (http://localhost:11434/v1), atau OpenRouter (https://openrouter.ai/api/v1)." /></label>
            <input :id="'base-url-' + name" v-model="config.ai_providers[name]!.base_url" type="text"
                   class="input-field" placeholder="https://your-api.com/v1" />
          </div>
          <div>
            <label :for="'enabled-' + name" class="text-xs text-txt-secondary block mb-1">Enabled<InfoTip tip="Aktifkan provider ini agar ikut dipakai untuk analisis AI. Beberapa provider sekaligus = fallback otomatis saat salah satu gagal." /></label>
            <label class="flex items-center gap-2 mt-2">
              <input :id="'enabled-' + name" v-model="config.ai_providers[name]!.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
              <span class="text-sm">Active</span>
            </label>
          </div>
        </div>
        <div class="mt-3 flex items-center gap-3">
          <button type="button" :disabled="testStatus(name).running" @click="testProvider(name)" class="neon-btn text-sm">
            {{ testStatus(name).running ? "Testing…" : isKeyless(name) ? "Test Connection" : "Test API Key" }}
          </button>
          <span v-if="testStatus(name).result" :class="testStatus(name).result!.ok ? 'text-neon-green' : 'text-sev-critical'" class="text-sm">
            <template v-if="testStatus(name).result!.ok">✓ Connected · {{ testStatus(name).result!.message }} {{ testStatus(name).result!.ms }}ms</template>
            <template v-else>✗ {{ testStatus(name).result!.message }}</template>
          </span>
        </div>
      </div>
    </template>
  </div>
</template>
