<script setup lang="ts">
import { ref, onMounted } from "vue";
import { api } from "../api/client";

const config = ref<any>({});
const providers = ref<any[]>([]);
const templates = ref<any[]>([]);
const templatesLoaded = ref(false);
const activeTab = ref("providers");
const saving = ref(false);
const savedMsg = ref("");

const providerNames = ["openai", "claude", "grok", "gemini", "ollama", "openrouter", "groq", "mistral", "litellm", "lmstudio", "orcarouter"];

const impersonationTargets = ["chrome99", "chrome101", "chrome104", "chrome107", "chrome110", "chrome116", "chrome120", "edge99", "edge101", "safari15_3", "safari15_5", "safari17_0"];
const logLevels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];
const triageSeverities = ["critical", "high", "medium", "low"];
const complianceFrameworks = [
  { id: "pci_dss", name: "PCI-DSS", description: "Payment Card Industry Data Security Standard" },
  { id: "soc2", name: "SOC 2", description: "Service Organization Control 2" },
  { id: "iso_27001", name: "ISO 27001", description: "Information Security Management" },
];

function isFrameworkEnabled(id: string): boolean {
  const list = config.value.compliance?.frameworks;
  return Array.isArray(list) && list.includes(id);
}

function toggleFramework(id: string, ev: Event) {
  const checked = (ev.target as HTMLInputElement).checked;
  const list = config.value.compliance?.frameworks;
  if (!Array.isArray(list)) return;
  const idx = list.indexOf(id);
  if (checked && idx === -1) list.push(id);
  else if (!checked && idx !== -1) list.splice(idx, 1);
}

function addListItem(list: unknown) {
  if (Array.isArray(list)) list.push("");
}

function removeListItem(list: unknown, index: number) {
  if (Array.isArray(list)) list.splice(index, 1);
}

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

async function selectTab(tab: string) {
  activeTab.value = tab;
  if (tab === "templates" && !templatesLoaded.value) await loadTemplates();
}

async function loadTemplates() {
  try {
    templates.value = await api.templates.list();
  } catch {
    templates.value = [];
  } finally {
    templatesLoaded.value = true;
  }
}
</script>

<template>
  <div class="p-8 max-w-3xl">
    <h1 class="text-2xl font-bold mb-1">Settings</h1>
    <p class="text-txt-secondary text-sm mb-8">Configure scanner and AI providers</p>

    <!-- Tabs -->
    <div class="flex flex-wrap gap-1 mb-6 border-b border-[rgba(0,240,255,0.08)] pb-px">
      <button v-for="tab in ['providers', 'scanner', 'notifications', 'proxy', 'compliance', 'advanced', 'templates', 'maintenance']" :key="tab"
              @click="selectTab(tab)"
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
              <label :for="'api-key-' + name" class="text-xs text-txt-secondary block mb-1">API Key</label>
              <input :id="'api-key-' + name" v-model="config.ai_providers[name].api_key" type="password"
                     class="input-field" placeholder="sk-..." />
            </div>
            <div>
              <label :for="'provider-model-' + name" class="text-xs text-txt-secondary block mb-1">Model</label>
              <input :id="'provider-model-' + name" v-model="config.ai_providers[name].model" type="text"
                     class="input-field" />
            </div>
            <div v-if="name === 'openai' || name === 'ollama' || name === 'openrouter'">
              <label :for="'base-url-' + name" class="text-xs text-txt-secondary block mb-1">Base URL <span class="text-txt-tertiary">(custom OpenAI-compatible)</span></label>
              <input :id="'base-url-' + name" v-model="config.ai_providers[name].base_url" type="text"
                     class="input-field" placeholder="https://your-api.com/v1" />
            </div>
            <div>
              <label :for="'enabled-' + name" class="text-xs text-txt-secondary block mb-1">Enabled</label>
              <label class="flex items-center gap-2 mt-2">
                <input :id="'enabled-' + name" v-model="config.ai_providers[name].enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
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
            <label for="default-depth" class="text-xs text-txt-secondary block mb-1">Default Depth (1-10)</label>
            <input id="default-depth" v-model.number="config.scanner.default_depth" type="number" min="1" max="10" class="input-field" />
          </div>
          <div>
            <label for="default-threads" class="text-xs text-txt-secondary block mb-1">Default Threads (1-50)</label>
            <input id="default-threads" v-model.number="config.scanner.default_threads" type="number" min="1" max="50" class="input-field" />
          </div>
          <div>
            <label for="ai-provider" class="text-xs text-txt-secondary block mb-1">AI Provider</label>
            <input id="ai-provider" v-model="config.scanner.ai_provider" type="text" class="input-field" />
          </div>
          <div>
            <label for="proxy" class="text-xs text-txt-secondary block mb-1">Proxy</label>
            <input id="proxy" v-model="config.scanner.proxy" type="text" class="input-field" placeholder="http://127.0.0.1:8080" />
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

    <!-- Notifications tab -->
    <div v-if="activeTab === 'notifications' && config.notifications" class="space-y-4">
      <div class="glass p-4 grid grid-cols-2 gap-3">
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="config.notifications.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Notifications</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="config.notifications.notify_on_critical" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Notify on Critical Findings</span>
        </label>
      </div>
      <div class="glass p-4">
        <h3 class="font-bold mb-3">Email</h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.notifications.email.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Email Notifications</span>
        </label>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="smtp-server" class="text-xs text-txt-secondary block mb-1">SMTP Server</label>
            <input id="smtp-server" v-model="config.notifications.email.smtp_server" type="text" class="input-field" placeholder="smtp.gmail.com" />
          </div>
          <div>
            <label for="smtp-port" class="text-xs text-txt-secondary block mb-1">Port</label>
            <input id="smtp-port" v-model.number="config.notifications.email.smtp_port" type="number" class="input-field" placeholder="587" />
          </div>
          <div>
            <label for="email-username" class="text-xs text-txt-secondary block mb-1">Username</label>
            <input id="email-username" v-model="config.notifications.email.username" type="text" class="input-field" placeholder="your@email.com" />
          </div>
          <div>
            <label for="email-password" class="text-xs text-txt-secondary block mb-1">Password</label>
            <input id="email-password" v-model="config.notifications.email.password" type="password" class="input-field" />
          </div>
          <div>
            <label for="from-address" class="text-xs text-txt-secondary block mb-1">From Address</label>
            <input id="from-address" v-model="config.notifications.email.from_address" type="text" class="input-field" placeholder="deep-eye@company.com" />
          </div>
        </div>
        <div class="mt-3">
          <label for="email-to-address-0" class="text-xs text-txt-secondary block mb-1">To Addresses</label>
          <div v-for="(addr, i) in config.notifications.email.to_addresses" :key="i" class="flex items-center gap-2 mb-2">
            <input :id="'email-to-address-' + i" :aria-label="'To Address ' + (i + 1)" v-model="config.notifications.email.to_addresses[i]" type="text" class="input-field" placeholder="security@company.com" />
            <button type="button" @click="removeListItem(config.notifications.email.to_addresses, i)"
                    :aria-label="'Remove To Address ' + (i + 1)"
                    class="px-2 py-1 text-sev-critical hover:text-sev-high transition-colors">&times;</button>
          </div>
          <button type="button" @click="addListItem(config.notifications.email.to_addresses)" class="text-neon-cyan text-xs mt-1 hover:underline">+ Add Recipient</button>
        </div>
      </div>
      <div class="glass p-4">
        <h3 class="font-bold mb-3">Slack</h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.notifications.slack.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Slack Notifications</span>
        </label>
        <div class="grid grid-cols-2 gap-3">
          <div class="col-span-2">
            <label for="slack-webhook" class="text-xs text-txt-secondary block mb-1">Webhook URL</label>
            <input id="slack-webhook" v-model="config.notifications.slack.webhook_url" type="text" class="input-field font-mono" placeholder="https://hooks.slack.com/..." />
          </div>
          <div>
            <label for="slack-channel" class="text-xs text-txt-secondary block mb-1">Channel</label>
            <input id="slack-channel" v-model="config.notifications.slack.channel" type="text" class="input-field" placeholder="#security-alerts" />
          </div>
          <div>
            <label for="slack-username" class="text-xs text-txt-secondary block mb-1">Bot Name</label>
            <input id="slack-username" v-model="config.notifications.slack.username" type="text" class="input-field" placeholder="Deep Eye Scanner" />
          </div>
          <div>
            <label for="slack-icon" class="text-xs text-txt-secondary block mb-1">Icon</label>
            <input id="slack-icon" v-model="config.notifications.slack.icon_emoji" type="text" class="input-field font-mono" placeholder=":shield:" />
          </div>
        </div>
      </div>
      <div class="glass p-4">
        <h3 class="font-bold mb-3">Discord</h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.notifications.discord.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Discord Notifications</span>
        </label>
        <div class="grid grid-cols-2 gap-3">
          <div class="col-span-2">
            <label for="discord-webhook" class="text-xs text-txt-secondary block mb-1">Webhook URL</label>
            <input id="discord-webhook" v-model="config.notifications.discord.webhook_url" type="text" class="input-field font-mono" placeholder="https://discord.com/api/webhooks/..." />
          </div>
          <div>
            <label for="discord-username" class="text-xs text-txt-secondary block mb-1">Bot Name</label>
            <input id="discord-username" v-model="config.notifications.discord.username" type="text" class="input-field" placeholder="Deep Eye Scanner" />
          </div>
          <div>
            <label for="discord-avatar" class="text-xs text-txt-secondary block mb-1">Avatar URL</label>
            <input id="discord-avatar" v-model="config.notifications.discord.avatar_url" type="text" class="input-field" placeholder="https://..." />
          </div>
        </div>
      </div>
    </div>

    <!-- Proxy tab -->
    <div v-if="activeTab === 'proxy' && config.intercepting_proxy" class="space-y-4">
      <div class="glass p-4">
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="config.intercepting_proxy.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Intercepting Proxy (mitmweb)</span>
        </label>
      </div>
      <div class="glass p-4">
        <h3 class="font-bold mb-3">Proxy Configuration</h3>
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label for="proxy-bind-host" class="text-xs text-txt-secondary block mb-1">Bind Host</label>
            <input id="proxy-bind-host" v-model="config.intercepting_proxy.bind_host" type="text" class="input-field font-mono" placeholder="127.0.0.1" />
          </div>
          <div>
            <label for="proxy-port" class="text-xs text-txt-secondary block mb-1">Proxy Port</label>
            <input id="proxy-port" v-model.number="config.intercepting_proxy.proxy_port" type="number" class="input-field" placeholder="8080" />
          </div>
          <div>
            <label for="mitmweb-port" class="text-xs text-txt-secondary block mb-1">Web UI Port</label>
            <input id="mitmweb-port" v-model.number="config.intercepting_proxy.mitmweb_port" type="number" class="input-field" placeholder="8081" />
          </div>
        </div>
        <label class="flex items-center gap-2 cursor-pointer mt-3">
          <input v-model="config.intercepting_proxy.required" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Required (abort scan if mitmweb is missing)</span>
        </label>
      </div>
      <div v-if="config.proxy" class="glass p-4">
        <h3 class="font-bold mb-3">Scanner Proxy</h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.proxy.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable HTTP Proxy</span>
        </label>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="http-proxy" class="text-xs text-txt-secondary block mb-1">HTTP Proxy</label>
            <input id="http-proxy" v-model="config.proxy.http" type="text" class="input-field font-mono" placeholder="http://127.0.0.1:8080" />
          </div>
          <div>
            <label for="https-proxy" class="text-xs text-txt-secondary block mb-1">HTTPS Proxy</label>
            <input id="https-proxy" v-model="config.proxy.https" type="text" class="input-field font-mono" placeholder="http://127.0.0.1:8080" />
          </div>
        </div>
      </div>
      <div v-if="config.tls_evasion" class="glass p-4">
        <h3 class="font-bold mb-3">TLS Evasion</h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.tls_evasion.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable TLS Fingerprint Evasion (curl_cffi)</span>
        </label>
        <div class="max-w-xs">
          <label for="tls-impersonate" class="text-xs text-txt-secondary block mb-1">Impersonate</label>
          <select id="tls-impersonate" v-model="config.tls_evasion.impersonate" class="input-field">
            <option v-for="target in impersonationTargets" :key="target" :value="target">{{ target }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Compliance tab -->
    <div v-if="activeTab === 'compliance' && config.compliance" class="space-y-4">
      <div class="glass p-4">
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="config.compliance.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Compliance Mapping</span>
        </label>
        <p class="text-xs text-txt-tertiary mt-1">Tag findings with controls from the selected frameworks</p>
      </div>
      <div class="glass p-4">
        <h3 class="font-bold mb-3">Frameworks</h3>
        <div class="space-y-2">
          <label v-for="fw in complianceFrameworks" :key="fw.id" class="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" class="w-4 h-4 accent-[#00f0ff]" :checked="isFrameworkEnabled(fw.id)" @change="toggleFramework(fw.id, $event)" />
            <span class="text-sm">{{ fw.name }} <span class="text-txt-tertiary">({{ fw.description }})</span></span>
          </label>
        </div>
      </div>
    </div>

    <!-- Advanced tab -->
    <div v-if="activeTab === 'advanced' && config.advanced" class="space-y-4">
      <div class="glass p-4">
        <h3 class="font-bold mb-3">Browser Automation</h3>
        <div class="grid grid-cols-3 gap-3 mb-3">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.advanced.enable_javascript_rendering" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">JavaScript Rendering (Playwright)</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.advanced.screenshot_enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Screenshot Capture</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.advanced.enable_browser_use_ai" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Browser Use AI</span>
          </label>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label for="browser-timeout" class="text-xs text-txt-secondary block mb-1">Browser Timeout (s)</label>
            <input id="browser-timeout" v-model.number="config.advanced.browser_timeout" type="number" class="input-field" />
          </div>
          <div>
            <label for="page-timeout" class="text-xs text-txt-secondary block mb-1">Page Timeout (s)</label>
            <input id="page-timeout" v-model.number="config.advanced.browser_page_timeout" type="number" class="input-field" />
          </div>
          <div>
            <label for="nav-timeout" class="text-xs text-txt-secondary block mb-1">Navigation Timeout (s)</label>
            <input id="nav-timeout" v-model.number="config.advanced.browser_navigation_timeout" type="number" class="input-field" />
          </div>
        </div>
      </div>
      <div class="glass p-4">
        <h3 class="font-bold mb-3">Stealth &amp; Anti-Detection</h3>
        <div class="grid grid-cols-3 gap-3 items-end">
          <label class="flex items-center gap-2 cursor-pointer pb-2">
            <input v-model="config.advanced.ua_rotation" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">User-Agent Rotation</span>
          </label>
          <div>
            <label for="jitter-min" class="text-xs text-txt-secondary block mb-1">Jitter Min (s)</label>
            <input id="jitter-min" v-model.number="config.advanced.jitter_min" type="number" step="0.1" min="0" class="input-field" />
          </div>
          <div>
            <label for="jitter-max" class="text-xs text-txt-secondary block mb-1">Jitter Max (s)</label>
            <input id="jitter-max" v-model.number="config.advanced.jitter_max" type="number" step="0.1" min="0" class="input-field" />
          </div>
        </div>
        <div class="mt-3">
          <label for="proxy-pool-0" class="text-xs text-txt-secondary block mb-1">Proxy Pool</label>
          <div v-for="(entry, i) in config.advanced.proxy_pool" :key="i" class="flex items-center gap-2 mb-2">
            <input :id="'proxy-pool-' + i" :aria-label="'Proxy Pool ' + (i + 1)" v-model="config.advanced.proxy_pool[i]" type="text" class="input-field font-mono" placeholder="http://proxy1:8080" />
            <button type="button" @click="removeListItem(config.advanced.proxy_pool, i)"
                    :aria-label="'Remove Proxy ' + (i + 1)"
                    class="px-2 py-1 text-sev-critical hover:text-sev-high transition-colors">&times;</button>
          </div>
          <button type="button" @click="addListItem(config.advanced.proxy_pool)" class="text-neon-cyan text-xs mt-1 hover:underline">+ Add Proxy</button>
        </div>
      </div>
      <div class="glass p-4">
        <h3 class="font-bold mb-3">URL Filtering</h3>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="exclude-ext-0" class="text-xs text-txt-secondary block mb-1">Exclude Extensions</label>
            <div v-for="(ext, i) in config.advanced.exclude_extensions" :key="i" class="flex items-center gap-2 mb-2">
              <input :id="'exclude-ext-' + i" :aria-label="'Exclude Extension ' + (i + 1)" v-model="config.advanced.exclude_extensions[i]" type="text" class="input-field font-mono" placeholder=".jpg" />
              <button type="button" @click="removeListItem(config.advanced.exclude_extensions, i)"
                      :aria-label="'Remove Exclude Extension ' + (i + 1)"
                      class="px-2 py-1 text-sev-critical hover:text-sev-high transition-colors">&times;</button>
            </div>
            <button type="button" @click="addListItem(config.advanced.exclude_extensions)" class="text-neon-cyan text-xs mt-1 hover:underline">+ Add Extension</button>
          </div>
          <div>
            <label for="exclude-pattern-0" class="text-xs text-txt-secondary block mb-1">Exclude Patterns</label>
            <div v-for="(pattern, i) in config.advanced.exclude_patterns" :key="i" class="flex items-center gap-2 mb-2">
              <input :id="'exclude-pattern-' + i" :aria-label="'Exclude Pattern ' + (i + 1)" v-model="config.advanced.exclude_patterns[i]" type="text" class="input-field font-mono" placeholder="/logout" />
              <button type="button" @click="removeListItem(config.advanced.exclude_patterns, i)"
                      :aria-label="'Remove Exclude Pattern ' + (i + 1)"
                      class="px-2 py-1 text-sev-critical hover:text-sev-high transition-colors">&times;</button>
            </div>
            <button type="button" @click="addListItem(config.advanced.exclude_patterns)" class="text-neon-cyan text-xs mt-1 hover:underline">+ Add Pattern</button>
          </div>
        </div>
        <div class="mt-3 max-w-xs">
          <label for="max-response-size" class="text-xs text-txt-secondary block mb-1">Max Response Size (bytes)</label>
          <input id="max-response-size" v-model.number="config.advanced.max_response_size" type="number" class="input-field" />
        </div>
      </div>
      <div v-if="config.ai_triage" class="glass p-4">
        <h3 class="font-bold mb-3">AI Triage &amp; FP Reduction</h3>
        <div class="grid grid-cols-2 gap-3 mb-3">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.ai_triage.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Enable AI Auto-Triage</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.ai_triage.drop_false_positives" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Drop False Positives</span>
          </label>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="drop-threshold" class="text-xs text-txt-secondary block mb-1">Drop Threshold</label>
            <input id="drop-threshold" v-model.number="config.ai_triage.drop_threshold" type="number" step="0.05" min="0" max="1" class="input-field" />
          </div>
          <div>
            <label for="min-severity" class="text-xs text-txt-secondary block mb-1">Min Severity</label>
            <select id="min-severity" v-model="config.ai_triage.min_severity" class="input-field">
              <option v-for="sev in triageSeverities" :key="sev" :value="sev" class="capitalize">{{ sev }}</option>
            </select>
          </div>
        </div>
      </div>
      <div v-if="config.rag" class="glass p-4">
        <h3 class="font-bold mb-3">RAG (CVE Retrieval-Augmented Generation)</h3>
        <div class="grid grid-cols-2 gap-3 mb-3">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.rag.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Enable RAG</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.rag.auto_rebuild" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Auto-Rebuild on CVE DB Update</span>
          </label>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div class="col-span-3 sm:col-span-1">
            <label for="rag-index-path" class="text-xs text-txt-secondary block mb-1">Index Path</label>
            <input id="rag-index-path" v-model="config.rag.index_path" type="text" class="input-field font-mono" placeholder="data/cve_rag_index.pkl" />
          </div>
          <div>
            <label for="rag-top-k" class="text-xs text-txt-secondary block mb-1">Top K</label>
            <input id="rag-top-k" v-model.number="config.rag.top_k" type="number" min="1" class="input-field" />
          </div>
          <div>
            <label for="rag-min-score" class="text-xs text-txt-secondary block mb-1">Min Score</label>
            <input id="rag-min-score" v-model.number="config.rag.min_score" type="number" step="0.01" min="0" max="1" class="input-field" />
          </div>
        </div>
      </div>
      <div v-if="config.rate_limiting" class="glass p-4">
        <h3 class="font-bold mb-3">Rate Limiting</h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.rate_limiting.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Rate Limiting</span>
        </label>
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label for="requests-per-second" class="text-xs text-txt-secondary block mb-1">Requests/sec</label>
            <input id="requests-per-second" v-model.number="config.rate_limiting.requests_per_second" type="number" min="1" class="input-field" />
          </div>
          <div>
            <label for="burst-size" class="text-xs text-txt-secondary block mb-1">Burst Size</label>
            <input id="burst-size" v-model.number="config.rate_limiting.burst_size" type="number" min="1" class="input-field" />
          </div>
          <div>
            <label for="delay-on-error" class="text-xs text-txt-secondary block mb-1">Delay on Error (s)</label>
            <input id="delay-on-error" v-model.number="config.rate_limiting.delay_on_error" type="number" min="0" class="input-field" />
          </div>
        </div>
      </div>
      <div v-if="config.logging" class="glass p-4">
        <h3 class="font-bold mb-3">Logging</h3>
        <div class="grid grid-cols-3 gap-3 mb-3">
          <div>
            <label for="log-level" class="text-xs text-txt-secondary block mb-1">Level</label>
            <select id="log-level" v-model="config.logging.level" class="input-field">
              <option v-for="level in logLevels" :key="level" :value="level">{{ level }}</option>
            </select>
          </div>
          <div>
            <label for="log-file" class="text-xs text-txt-secondary block mb-1">Log File</label>
            <input id="log-file" v-model="config.logging.log_file" type="text" class="input-field font-mono" placeholder="logs/deep_eye.log" />
          </div>
          <label class="flex items-center gap-2 cursor-pointer pb-2">
            <input v-model="config.logging.log_to_file" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Log to File</span>
          </label>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="log-max-size" class="text-xs text-txt-secondary block mb-1">Max File Size (bytes)</label>
            <input id="log-max-size" v-model.number="config.logging.max_file_size" type="number" min="0" class="input-field" />
          </div>
          <div>
            <label for="log-backups" class="text-xs text-txt-secondary block mb-1">Backup Count</label>
            <input id="log-backups" v-model.number="config.logging.backup_count" type="number" min="0" class="input-field" />
          </div>
        </div>
      </div>
      <div v-if="config.database" class="glass p-4">
        <h3 class="font-bold mb-3">Database</h3>
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label for="db-type" class="text-xs text-txt-secondary block mb-1">Type</label>
            <input id="db-type" :value="config.database.type" type="text" disabled class="input-field opacity-60" />
          </div>
          <div>
            <label for="db-path" class="text-xs text-txt-secondary block mb-1">Path</label>
            <input id="db-path" v-model="config.database.path" type="text" class="input-field font-mono" placeholder="data/deep_eye.db" />
          </div>
          <div>
            <label for="db-cleanup" class="text-xs text-txt-secondary block mb-1">Auto-Cleanup After (days)</label>
            <input id="db-cleanup" v-model.number="config.database.auto_cleanup_days" type="number" min="0" class="input-field" />
          </div>
        </div>
      </div>
      <div v-if="config.login_replay" class="glass p-4">
        <h3 class="font-bold mb-3">Auth Macros &amp; Login Replay</h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.login_replay.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Login Replay</span>
        </label>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="login-macro-path" class="text-xs text-txt-secondary block mb-1">Macro Path</label>
            <input id="login-macro-path" v-model="config.login_replay.macro_path" type="text" class="input-field font-mono" placeholder="config/login_macro.json" />
          </div>
          <div>
            <label for="login-recheck-interval" class="text-xs text-txt-secondary block mb-1">Recheck Interval (s)</label>
            <input id="login-recheck-interval" v-model.number="config.login_replay.recheck_interval_seconds" type="number" min="0" class="input-field" placeholder="600" />
          </div>
        </div>
        <label class="flex items-center gap-2 cursor-pointer mt-3">
          <input v-model="config.login_replay.abort_on_fail" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Abort Scan on Login Failure</span>
        </label>
      </div>
      <div v-if="config.bug_bounty" class="glass p-4">
        <h3 class="font-bold mb-3">Bug Bounty</h3>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="bounty-format" class="text-xs text-txt-secondary block mb-1">Format</label>
            <select id="bounty-format" v-model="config.bug_bounty.format" class="input-field">
              <option value="hackerone">HackerOne</option>
              <option value="bugcrowd">Bugcrowd</option>
              <option value="generic">Generic</option>
            </select>
          </div>
          <div>
            <label for="bounty-output-directory" class="text-xs text-txt-secondary block mb-1">Output Directory</label>
            <input id="bounty-output-directory" v-model="config.bug_bounty.output_directory" type="text" class="input-field font-mono" placeholder="reports/bounty" />
          </div>
        </div>
      </div>
    </div>

    <!-- Templates tab -->
    <div v-if="activeTab === 'templates'" class="space-y-4">
      <div class="glass p-4 flex items-center justify-between">
        <div>
          <h3 class="font-bold">Scan Templates</h3>
          <p class="text-xs text-txt-secondary mt-1">YAML detection templates shipped with the engine</p>
        </div>
        <span class="sev-badge sev-info">{{ templates.length }} templates</span>
      </div>
      <div v-for="tpl in templates" :key="tpl.path" class="glass p-4 flex items-start justify-between gap-4">
        <div class="min-w-0">
          <h4 class="font-bold truncate">{{ tpl.name }}</h4>
          <p class="text-xs text-txt-tertiary font-mono mt-0.5 break-all">{{ tpl.path }}</p>
        </div>
        <div class="flex gap-1 flex-wrap justify-end shrink-0">
          <span v-for="tag in tpl.tags" :key="tag" class="sev-badge sev-info">{{ tag }}</span>
          <span v-if="!tpl.tags || !tpl.tags.length" class="sev-badge sev-info">untagged</span>
        </div>
      </div>
      <div v-if="templatesLoaded && !templates.length" class="glass p-6 text-center text-txt-secondary text-sm">
        No templates found
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
