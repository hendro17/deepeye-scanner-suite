<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { api } from "../api/client";
import InfoTip from "../components/InfoTip.vue";
import SettingsProviders from "./SettingsProviders.vue";
import SettingsTemplates from "./SettingsTemplates.vue";

const TAB_TIPS: Record<string, string> = {
  providers: "Konfigurasi 11 provider AI: API key, model, dan pengaktifan masing-masing.",
  scanner: "Nilai bawaan untuk scan baru: kedalaman, thread, AI provider, proxy, recon/full/quick/subdomain.",
  notifications: "Kirim notifikasi hasil scan lewat email, Slack, dan Discord.",
  proxy: "Proxy intercepting (mitmweb), proxy HTTP scanner, dan penyamaran TLS fingerprint.",
  compliance: "Tandai temuan dengan kontrol standar kepatuhan (PCI-DSS, SOC 2, ISO 27001).",
  advanced: "Opsi lanjutan: browser automation, stealth, filter URL, AI triage, RAG, rate limit, logging, database, login replay, bug bounty.",
  templates: "Daftar template deteksi YAML bawaan engine.",
  maintenance: "Perawatan: update database CVE dari NVD dan rebuild indeks RAG.",
};

type ProviderStatus = { name: string; enabled?: boolean; configured?: boolean };

type AppConfig = Record<string, unknown> & {
  scanner: Record<string, unknown> & { default_depth?: number; default_threads?: number; ai_provider?: string; proxy?: string; enable_recon?: boolean; full_scan?: boolean; quick_scan?: boolean; scan_subdomains?: boolean };
  notifications: Record<string, unknown> & {
    enabled?: boolean; notify_on_critical?: boolean;
    email: Record<string, unknown> & { enabled?: boolean; smtp_server?: string; smtp_port?: number; username?: string; password?: string; from_address?: string; to_addresses: string[] };
    slack: Record<string, unknown> & { enabled?: boolean; webhook_url?: string; channel?: string; username?: string; icon_emoji?: string };
    discord: Record<string, unknown> & { enabled?: boolean; webhook_url?: string; username?: string; avatar_url?: string };
  };
  intercepting_proxy: Record<string, unknown> & { enabled?: boolean; bind_host?: string; proxy_port?: number; mitmweb_port?: number; required?: boolean };
  proxy: Record<string, unknown> & { enabled?: boolean; http?: string; https?: string };
  tls_evasion: Record<string, unknown> & { enabled?: boolean; impersonate?: string };
  compliance: Record<string, unknown> & { enabled?: boolean; frameworks?: string[] };
  advanced: Record<string, unknown> & { enable_javascript_rendering?: boolean; screenshot_enabled?: boolean; enable_browser_use_ai?: boolean; browser_timeout?: number; browser_page_timeout?: number; browser_navigation_timeout?: number; ua_rotation?: boolean; jitter_min?: number; jitter_max?: number; proxy_pool: string[]; exclude_extensions: string[]; exclude_patterns: string[]; max_response_size?: number };
  ai_triage: Record<string, unknown> & { enabled?: boolean; drop_false_positives?: boolean; drop_threshold?: number; min_severity?: string };
  rag: Record<string, unknown> & { enabled?: boolean; auto_rebuild?: boolean; index_path?: string; top_k?: number; min_score?: number };
  rate_limiting: Record<string, unknown> & { enabled?: boolean; requests_per_second?: number; burst_size?: number; delay_on_error?: number };
  logging: Record<string, unknown> & { level?: string; log_file?: string; log_to_file?: boolean; max_file_size?: number; backup_count?: number };
  database: Record<string, unknown> & { type?: string; path?: string; auto_cleanup_days?: number };
  login_replay: Record<string, unknown> & { enabled?: boolean; macro_path?: string; recheck_interval_seconds?: number; abort_on_fail?: boolean };
  bug_bounty: Record<string, unknown> & { format?: string; output_directory?: string };
  ai_providers: Record<string, Record<string, unknown>>;
  templates: Record<string, unknown>;
};

const config = ref<AppConfig>({} as AppConfig);
const providers = ref<ProviderStatus[]>([]);
const activeTab = ref("providers");
const saving = ref(false);
const savedMsg = ref("");

const providerNames = ["openai", "claude", "grok", "gemini", "ollama", "openrouter", "groq", "mistral", "litellm", "lmstudio", "orcarouter"];

const aiProviderOptions = computed(() => {
  const enabledSet = new Set(providers.value.filter((p) => p.enabled).map((p) => p.name));
  return providerNames.map((n) => ({ name: n, active: enabledSet.has(n) }));
});

const activeAiProviderCount = computed(() => aiProviderOptions.value.filter((o) => o.active).length);

type ScannerProxyCfg = Record<string, Record<string, unknown> & { enabled?: boolean; proxy_port?: number; bind_host?: string; http?: string; https?: string; proxy_pool?: string[]; proxy?: string }>;

function appendInterceptingProxy(cfg: ScannerProxyCfg, opts: { label: string; value: string }[]): void {
  const ip = cfg.intercepting_proxy as Record<string, unknown> | undefined;
  if (!ip || typeof ip.enabled !== "boolean" || !ip.enabled) return;
  if (typeof ip.proxy_port !== "number" || !ip.proxy_port) return;
  const host = typeof ip.bind_host === "string" && ip.bind_host ? ip.bind_host : "127.0.0.1";
  const url = `http://${host}:${String(ip.proxy_port)}`;
  opts.push({ label: `Intercepting (mitmweb) — ${url}`, value: url });
}

function appendHttpProxies(cfg: ScannerProxyCfg, opts: { label: string; value: string }[]): void {
  const px = cfg.proxy as Record<string, unknown> | undefined;
  if (!px || !px.enabled) return;
  if (typeof px.http === "string" && px.http) opts.push({ label: `HTTP Proxy — ${px.http}`, value: px.http });
  if (typeof px.https === "string" && px.https && px.https !== px.http) opts.push({ label: `HTTPS Proxy — ${px.https}`, value: String(px.https) });
}

function appendProxyPool(cfg: ScannerProxyCfg, opts: { label: string; value: string }[]): void {
  const advanced = cfg.advanced as Record<string, unknown> | undefined;
  const pool: string[] = Array.isArray(advanced?.proxy_pool) ? (advanced.proxy_pool as string[]) : [];
  pool.forEach((p: string, i: number) => {
    if (!p || opts.some((o) => o.value === p)) return;
    opts.push({ label: `Pool #${i + 1} — ${p}`, value: p });
  });
}

function appendCustomProxy(cfg: ScannerProxyCfg, opts: { label: string; value: string }[]): void {
  const scanner = cfg.scanner as Record<string, unknown> | undefined;
  const cur = typeof scanner?.proxy === "string" ? scanner.proxy : "";
  if (!cur || opts.some((o) => o.value === cur)) return;
  opts.push({ label: `Custom — ${cur}`, value: cur });
}

const scannerProxyOptions = computed(() => {
  const opts: { label: string; value: string }[] = [{ label: "Direct — tanpa proxy", value: "" }];
  const cfg = config.value as ScannerProxyCfg;
  appendInterceptingProxy(cfg, opts);
  appendHttpProxies(cfg, opts);
  appendProxyPool(cfg, opts);
  appendCustomProxy(cfg, opts);
  return opts;
});

const impersonationTargets = ["chrome99", "chrome101", "chrome104", "chrome107", "chrome110", "chrome116", "chrome120", "edge99", "edge101", "safari15_3", "safari15_5", "safari17_0"];
const logLevels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];
const triageSeverities = ["critical", "high", "medium", "low"];
const complianceFrameworks = [
  { id: "pci_dss", name: "PCI-DSS", description: "Payment Card Industry Data Security Standard" },
  { id: "soc2", name: "SOC 2", description: "Service Organization Control 2" },
  { id: "iso_27001", name: "ISO 27001", description: "Information Security Management" },
];

function isFrameworkEnabled(id: string): boolean {
  const compliance = config.value.compliance as Record<string, unknown> | undefined;
  const list = compliance?.frameworks;
  return Array.isArray(list) && (list as string[]).includes(id);
}

function toggleFramework(id: string, ev: Event) {
  const checked = (ev.target as HTMLInputElement).checked;
  const compliance = config.value.compliance as Record<string, unknown> | undefined;
  const list = compliance?.frameworks as string[] | undefined;
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

function isMaskedValue(v: unknown): boolean {
  if (typeof v !== "string" || !v) return false;
  return v.includes("•") || v.includes("…") || v.includes("***");
}

function _sanitizeEntry(obj: Record<string, unknown>, key: string, value: unknown): void {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    sanitizeMaskedSecrets(value);
    return;
  }
  if (typeof value === "string" && isMaskedValue(value)) {
    obj[key] = "";
  }
}

function sanitizeMaskedSecrets(obj: unknown): void {
  if (!obj || typeof obj !== "object") return;
  const record = obj as Record<string, unknown>;
  for (const [k, v] of Object.entries(record)) {
    _sanitizeEntry(record, k, v);
  }
}

onMounted(async () => {
  const [cfgRes, provRes] = await Promise.all([api.config.get(), api.providers.status()]);
  sanitizeMaskedSecrets(cfgRes.config);
  config.value = cfgRes.config as AppConfig;
  providers.value = provRes as ProviderStatus[];
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

function selectTab(tab: string) {
  activeTab.value = tab;
}
</script>

<template>
  <div class="p-8 max-w-3xl">
    <h1 class="text-2xl font-bold mb-1">Settings</h1>
    <p class="text-txt-secondary text-sm mb-8">Configure scanner and AI providers</p>

    <!-- Tabs -->
    <div class="flex flex-wrap gap-1 mb-6 border-b border-[rgba(0,240,255,0.08)] pb-px">
      <button v-for="tab in ['providers', 'proxy', 'scanner', 'notifications', 'compliance', 'advanced', 'templates', 'maintenance']" :key="tab"
              @click="selectTab(tab)"
               :class="['px-4 py-2 text-sm font-medium border-b-2 transition-all capitalize inline-flex items-center',
                 activeTab === tab ? 'border-neon-cyan text-neon-cyan' : 'border-transparent text-txt-secondary hover:text-txt-primary']">
        {{ tab }}<InfoTip :tip="TAB_TIPS[tab]" />
      </button>
    </div>

    <!-- Providers tab -->
    <SettingsProviders v-if="activeTab === 'providers'" :config="config" :providers="providers" />

    <!-- Scanner tab -->
    <div v-if="activeTab === 'scanner' && config.scanner" class="space-y-4">
      <div class="glass p-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="default-depth" class="text-xs text-txt-secondary block mb-1">Default Depth (1-10)<InfoTip tip="Nilai bawaan kedalaman crawl untuk scan baru. Bisa diatur ulang per scan di halaman New Scan." /></label>
            <input id="default-depth" v-model.number="config.scanner.default_depth" type="number" min="1" max="10" class="input-field" />
          </div>
          <div>
            <label for="default-threads" class="text-xs text-txt-secondary block mb-1">Default Threads (1-50)<InfoTip tip="Nilai bawaan jumlah permintaan paralel untuk scan baru." /></label>
            <input id="default-threads" v-model.number="config.scanner.default_threads" type="number" min="1" max="50" class="input-field" />
          </div>
          <div>
            <label for="ai-provider" class="text-xs text-txt-secondary block mb-1">AI Provider<InfoTip tip="Pilih provider AI utama untuk analisis. Hanya provider berstatus Aktif di tab Providers yang direkomendasikan; scanner butuh provider aktif untuk jalan." /></label>
            <select id="ai-provider" v-model="config.scanner.ai_provider" class="input-field">
              <option value="" disabled>Pilih provider…</option>
              <option v-for="opt in aiProviderOptions" :key="opt.name" :value="opt.name">
                {{ opt.name }}{{ opt.active ? " — Aktif" : " — Nonaktif" }}
              </option>
            </select>
            <p v-if="providers.length && activeAiProviderCount === 0" class="text-xs text-amber-400 mt-1">Tidak ada provider aktif — aktifkan di tab Providers.</p>
            <p v-else-if="config.scanner?.ai_provider && !aiProviderOptions.find((o) => o.name === config.scanner.ai_provider)?.active" class="text-xs text-amber-400 mt-1">Provider terpilih sedang nonaktif — scanner mungkin tidak jalan.</p>
          </div>
          <div>
            <label for="proxy" class="text-xs text-txt-secondary block mb-1">Proxy<InfoTip tip="Pilih proxy untuk scan ini. Daftar diambil dari Settings → Proxy (single source). Atur proxy di tab Proxy dulu." /></label>
            <select id="proxy" v-model="config.scanner.proxy" class="input-field">
              <option v-for="opt in scannerProxyOptions" :key="opt.value || '__direct'" :value="opt.value">{{ opt.label }}</option>
            </select>
            <p v-if="scannerProxyOptions.length <= 1" class="text-xs text-txt-tertiary mt-1">Belum ada proxy — atur di tab Proxy atau gunakan Direct.</p>
          </div>
        </div>
      </div>
      <div class="glass p-4">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.scanner.enable_recon" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Enable Recon<InfoTip tip="Default OFF. Centang untuk aktifkan fase pengumpulan informasi (subdomain, teknologi) sebelum scan utama." /></span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.scanner.full_scan" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Full Scan<InfoTip tip="Default untuk scan menyeluruh: semua fitur aktif, durasi paling lama." /></span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.scanner.quick_scan" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Quick Scan<InfoTip tip="Default untuk scan cepat: hanya pengujian paling umum." /></span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.scanner.scan_subdomains" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Scan Subdomains<InfoTip tip="Ikut menguji subdomain target (mis. api.domain.com). Experimental — lebih lama & agresif." /></span>
          </label>
        </div>
      </div>
    </div>

    <!-- Notifications tab -->
    <div v-if="activeTab === 'notifications' && config.notifications" class="space-y-4">
      <div class="glass p-4 grid grid-cols-2 gap-3">
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="config.notifications.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Notifications<InfoTip tip="Master switch: aktifkan agar pemberitahuan hasil scan dikirim ke channel yang dipilih (email/Slack/Discord)." /></span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="config.notifications.notify_on_critical" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Notify on Critical Findings<InfoTip tip="Kirim notifikasi segera hanya saat ada temuan level Critical — tanpa menunggu scan selesai." /></span>
        </label>
      </div>
      <div class="glass p-4">
        <h3 class="font-bold mb-3">Email<InfoTip tip="Pengiriman notifikasi via SMTP. Isi server SMTP (mis. smtp.gmail.com), kredensial pengirim, dan daftar penerima." /></h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.notifications.email.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Email Notifications<InfoTip tip="Kirim laporan/notifikasi lewat email via server SMTP." /></span>
        </label>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="smtp-server" class="text-xs text-txt-secondary block mb-1">SMTP Server<InfoTip tip="Alamat server pengirim email. Contoh: smtp.gmail.com, smtp.office365.com." /></label>
            <input id="smtp-server" v-model="config.notifications.email.smtp_server" type="text" class="input-field" placeholder="smtp.gmail.com" />
          </div>
          <div>
            <label for="smtp-port" class="text-xs text-txt-secondary block mb-1">Port<InfoTip tip="Port server SMTP. Umumnya 587 (TLS) atau 465 (SSL)." /></label>
            <input id="smtp-port" v-model.number="config.notifications.email.smtp_port" type="number" class="input-field" placeholder="587" />
          </div>
          <div>
            <label for="email-username" class="text-xs text-txt-secondary block mb-1">Username<InfoTip tip="Nama akun untuk login ke server SMTP, biasanya alamat email." /></label>
            <input id="email-username" v-model="config.notifications.email.username" type="text" class="input-field" placeholder="your@email.com" />
          </div>
          <div>
            <label for="email-password" class="text-xs text-txt-secondary block mb-1">Password<InfoTip tip="Password atau app password SMTP. Untuk Gmail gunakan app password, bukan password utama." /></label>
            <input id="email-password" v-model="config.notifications.email.password" type="password" class="input-field" />
          </div>
          <div>
            <label for="from-address" class="text-xs text-txt-secondary block mb-1">From Address<InfoTip tip="Alamat pengirim yang tampil di email notifikasi." /></label>
            <input id="from-address" v-model="config.notifications.email.from_address" type="text" class="input-field" placeholder="deep-eye@company.com" />
          </div>
        </div>
        <div class="mt-3">
          <label for="email-to-address-0" class="text-xs text-txt-secondary block mb-1">To Addresses<InfoTip tip="Daftar penerima notifikasi. Tekan '+ Add Recipient' untuk menambah." /></label>
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
        <h3 class="font-bold mb-3">Slack<InfoTip tip="Kirim notifikasi ke channel Slack lewat webhook. Buat webhook di api.slack.com > Incoming Webhooks." /></h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.notifications.slack.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Slack Notifications<InfoTip tip="Aktifkan pengiriman notifikasi ke Slack." /></span>
        </label>
        <div class="grid grid-cols-2 gap-3">
          <div class="col-span-2">
            <label for="slack-webhook" class="text-xs text-txt-secondary block mb-1">Webhook URL<InfoTip tip="URL webhook dari Slack (dimulai https://hooks.slack.com/...). Notifikasi dikirim POST ke URL ini." /></label>
            <input id="slack-webhook" v-model="config.notifications.slack.webhook_url" type="text" class="input-field font-mono" placeholder="https://hooks.slack.com/..." />
          </div>
          <div>
            <label for="slack-channel" class="text-xs text-txt-secondary block mb-1">Channel<InfoTip tip="Channel tujuan notifikasi, mis. #security-alerts." /></label>
            <input id="slack-channel" v-model="config.notifications.slack.channel" type="text" class="input-field" placeholder="#security-alerts" />
          </div>
          <div>
            <label for="slack-username" class="text-xs text-txt-secondary block mb-1">Bot Name<InfoTip tip="Nama pengirim yang tampil di pesan Slack." /></label>
            <input id="slack-username" v-model="config.notifications.slack.username" type="text" class="input-field" placeholder="Deep Eye Scanner" />
          </div>
          <div>
            <label for="slack-icon" class="text-xs text-txt-secondary block mb-1">Icon<InfoTip tip="Emoji ikon pengirim, mis. :shield:." /></label>
            <input id="slack-icon" v-model="config.notifications.slack.icon_emoji" type="text" class="input-field font-mono" placeholder=":shield:" />
          </div>
        </div>
      </div>
      <div class="glass p-4">
        <h3 class="font-bold mb-3">Discord<InfoTip tip="Kirim notifikasi ke channel Discord lewat webhook. Buat webhook di Server Settings > Integrations > Webhooks." /></h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.notifications.discord.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Discord Notifications<InfoTip tip="Aktifkan pengiriman notifikasi ke Discord." /></span>
        </label>
        <div class="grid grid-cols-2 gap-3">
          <div class="col-span-2">
            <label for="discord-webhook" class="text-xs text-txt-secondary block mb-1">Webhook URL<InfoTip tip="URL webhook dari Discord (dimulai https://discord.com/api/webhooks/...)." /></label>
            <input id="discord-webhook" v-model="config.notifications.discord.webhook_url" type="text" class="input-field font-mono" placeholder="https://discord.com/api/webhooks/..." />
          </div>
          <div>
            <label for="discord-username" class="text-xs text-txt-secondary block mb-1">Bot Name<InfoTip tip="Nama pengirim yang tampil di pesan Discord." /></label>
            <input id="discord-username" v-model="config.notifications.discord.username" type="text" class="input-field" placeholder="Deep Eye Scanner" />
          </div>
          <div>
            <label for="discord-avatar" class="text-xs text-txt-secondary block mb-1">Avatar URL<InfoTip tip="URL gambar avatar pengirim di pesan Discord." /></label>
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
          <span class="text-sm">Enable Intercepting Proxy (mitmweb)<InfoTip tip="Jalankan mitmweb untuk melihat dan merekam seluruh traffic scanner secara real-time. Wajib ada jika dipakai untuk debugging request." /></span>
        </label>
      </div>
      <div class="glass p-4">
        <h3 class="font-bold mb-3">Proxy Configuration<InfoTip tip="Alamat dan port layanan mitmweb. Proxy Port dipakai scanner; Web UI Port untuk membuka tampilan mitmweb di browser." /></h3>
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label for="proxy-bind-host" class="text-xs text-txt-secondary block mb-1">Bind Host<InfoTip tip="Alamat IP yang didengarkan mitmweb. Biarkan 127.0.0.1 agar hanya bisa diakses dari komputer ini." /></label>
            <input id="proxy-bind-host" v-model="config.intercepting_proxy.bind_host" type="text" class="input-field font-mono" placeholder="127.0.0.1" />
          </div>
          <div>
            <label for="proxy-port" class="text-xs text-txt-secondary block mb-1">Proxy Port<InfoTip tip="Port proxy yang dipakai scanner untuk mengirim request. Default 8080." /></label>
            <input id="proxy-port" v-model.number="config.intercepting_proxy.proxy_port" type="number" class="input-field" placeholder="8080" />
          </div>
          <div>
            <label for="mitmweb-port" class="text-xs text-txt-secondary block mb-1">Web UI Port<InfoTip tip="Port untuk membuka tampilan web mitmweb di browser. Default 8081." /></label>
            <input id="mitmweb-port" v-model.number="config.intercepting_proxy.mitmweb_port" type="number" class="input-field" placeholder="8081" />
          </div>
        </div>
        <label class="flex items-center gap-2 cursor-pointer mt-3">
          <input v-model="config.intercepting_proxy.required" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Required (abort scan if mitmweb is missing)<InfoTip tip="Jika aktif, scan langsung dibatalkan saat mitmweb tidak tersedia — mencegah scan jalan tanpa pengawasan traffic." /></span>
        </label>
      </div>
      <div v-if="config.proxy" class="glass p-4">
        <h3 class="font-bold mb-3">Scanner Proxy<InfoTip tip="Arahkan semua request scanner lewat proxy HTTP biasa (mis. Burp Suite, perusahaan, atau ISP)." /></h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.proxy.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable HTTP Proxy<InfoTip tip="Aktifkan proxy untuk seluruh request scanner." /></span>
        </label>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="http-proxy" class="text-xs text-txt-secondary block mb-1">HTTP Proxy<InfoTip tip="Alamat proxy untuk request http://, format http://host:port." /></label>
            <input id="http-proxy" v-model="config.proxy.http" type="text" class="input-field font-mono" placeholder="http://127.0.0.1:8080" />
          </div>
          <div>
            <label for="https-proxy" class="text-xs text-txt-secondary block mb-1">HTTPS Proxy<InfoTip tip="Alamat proxy untuk request https://, format http://host:port." /></label>
            <input id="https-proxy" v-model="config.proxy.https" type="text" class="input-field font-mono" placeholder="http://127.0.0.1:8080" />
          </div>
        </div>
      </div>
      <div v-if="config.tls_evasion" class="glass p-4">
        <h3 class="font-bold mb-3">TLS Evasion<InfoTip tip="Samarkan sidik jari (fingerprint) TLS scanner agar terlihat seperti browser asli, untuk melewati WAF yang memblokir tool otomatis." /></h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.tls_evasion.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable TLS Fingerprint Evasion (curl_cffi)<InfoTip tip="Gunakan library curl_cffi untuk meniru handshake TLS browser nyata." /></span>
        </label>
        <div class="max-w-xs">
          <label for="tls-impersonate" class="text-xs text-txt-secondary block mb-1">Impersonate<InfoTip tip="Browser yang ditiru sidik jari TLS-nya, mis. chrome120 atau safari17_0. Pilih yang paling umum dipakai pengunjung target." /></label>
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
          <span class="text-sm">Enable Compliance Mapping<InfoTip tip="Tambahkan tag kontrol kepatuhan pada setiap temuan sehingga laporan mendukung audit." /></span>
        </label>
        <p class="text-xs text-txt-tertiary mt-1">Tag findings with controls from the selected frameworks</p>
      </div>
      <div class="glass p-4">
        <h3 class="font-bold mb-3">Frameworks<InfoTip tip="Standar yang dipakai untuk menandai temuan. Centang sesuai kebutuhan organisasi." /></h3>
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
        <h3 class="font-bold mb-3">Browser Automation<InfoTip tip="Pengaturan browser headless (Playwright) untuk merender halaman JavaScript dinamis dan mengambil bukti visual." /></h3>
        <div class="grid grid-cols-3 gap-3 mb-3">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.advanced.enable_javascript_rendering" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">JavaScript Rendering (Playwright)<InfoTip tip="Jalankan JavaScript halaman di browser headless agar konten dinamis (SPA) ikut teruji. Lebih lambat tapi lebih lengkap." /></span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.advanced.screenshot_enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Screenshot Capture<InfoTip tip="Simpan screenshot setiap halaman sebagai bukti visual temuan." /></span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.advanced.enable_browser_use_ai" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Browser Use AI<InfoTip tip="Biarkan AI mengendalikan browser secara otonom untuk eksplorasi interaksi kompleks (klik, isi form)." /></span>
          </label>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label for="browser-timeout" class="text-xs text-txt-secondary block mb-1">Browser Timeout (s)<InfoTip tip="Batas waktu total operasi browser (detik) sebelum dibatalkan." /></label>
            <input id="browser-timeout" v-model.number="config.advanced.browser_timeout" type="number" class="input-field" />
          </div>
          <div>
            <label for="page-timeout" class="text-xs text-txt-secondary block mb-1">Page Timeout (s)<InfoTip tip="Batas waktu memuat satu halaman (detik)." /></label>
            <input id="page-timeout" v-model.number="config.advanced.browser_page_timeout" type="number" class="input-field" />
          </div>
          <div>
            <label for="nav-timeout" class="text-xs text-txt-secondary block mb-1">Navigation Timeout (s)<InfoTip tip="Batas waktu perpindahan antar halaman (detik)." /></label>
            <input id="nav-timeout" v-model.number="config.advanced.browser_navigation_timeout" type="number" class="input-field" />
          </div>
        </div>
      </div>
      <div class="glass p-4">
        <h3 class="font-bold mb-3">Stealth &amp; Anti-Detection<InfoTip tip="Teknik agar scanner tidak mudah dideteksi/diblokir WAF atau rate limiter." /></h3>
        <div class="grid grid-cols-3 gap-3 items-end">
          <label class="flex items-center gap-2 cursor-pointer pb-2">
            <input v-model="config.advanced.ua_rotation" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">User-Agent Rotation<InfoTip tip="Ganti-ganti identitas browser (User-Agent) pada tiap request agar traffic tidak berpola." /></span>
          </label>
          <div>
            <label for="jitter-min" class="text-xs text-txt-secondary block mb-1">Jitter Min (s)<InfoTip tip="Jeda acak minimum antar request (detik). Menyamarkan pola mesin." /></label>
            <input id="jitter-min" v-model.number="config.advanced.jitter_min" type="number" step="0.1" min="0" class="input-field" />
          </div>
          <div>
            <label for="jitter-max" class="text-xs text-txt-secondary block mb-1">Jitter Max (s)<InfoTip tip="Jeda acak maksimum antar request (detik). Setiap request menunggu acak antara Min dan Max." /></label>
            <input id="jitter-max" v-model.number="config.advanced.jitter_max" type="number" step="0.1" min="0" class="input-field" />
          </div>
        </div>
        <div class="mt-3">
          <label for="proxy-pool-0" class="text-xs text-txt-secondary block mb-1">Proxy Pool<InfoTip tip="Daftar proxy yang dipakai bergantian untuk membagi beban dan menghindari pemblokiran IP." /></label>
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
        <h3 class="font-bold mb-3">URL Filtering<InfoTip tip="Batasi halaman yang dikunjungi crawler agar tidak membuang waktu atau memicu aksi berbahaya (mis. logout)." /></h3>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="exclude-ext-0" class="text-xs text-txt-secondary block mb-1">Exclude Extensions<InfoTip tip="Ekstensi file yang dilewati crawler, mis. .jpg, .png, .pdf — bukan halaman web sehingga tidak perlu diuji." /></label>
            <div v-for="(ext, i) in config.advanced.exclude_extensions" :key="i" class="flex items-center gap-2 mb-2">
              <input :id="'exclude-ext-' + i" :aria-label="'Exclude Extension ' + (i + 1)" v-model="config.advanced.exclude_extensions[i]" type="text" class="input-field font-mono" placeholder=".jpg" />
              <button type="button" @click="removeListItem(config.advanced.exclude_extensions, i)"
                      :aria-label="'Remove Exclude Extension ' + (i + 1)"
                      class="px-2 py-1 text-sev-critical hover:text-sev-high transition-colors">&times;</button>
            </div>
            <button type="button" @click="addListItem(config.advanced.exclude_extensions)" class="text-neon-cyan text-xs mt-1 hover:underline">+ Add Extension</button>
          </div>
          <div>
            <label for="exclude-pattern-0" class="text-xs text-txt-secondary block mb-1">Exclude Patterns<InfoTip tip="Pola URL yang dilewati, mis. /logout, /delete-account — hindari aksi yang mengubah data atau mengeluarkan sesi." /></label>
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
          <label for="max-response-size" class="text-xs text-txt-secondary block mb-1">Max Response Size (bytes)<InfoTip tip="Respons lebih besar dari nilai ini dipotong/diabaikan untuk menghemat memori dan waktu." /></label>
          <input id="max-response-size" v-model.number="config.advanced.max_response_size" type="number" class="input-field" />
        </div>
      </div>
      <div v-if="config.ai_triage" class="glass p-4">
        <h3 class="font-bold mb-3">AI Triage &amp; FP Reduction<InfoTip tip="AI memilah temuan untuk membuang false positive (peringatan palsu) sehingga hasil lebih bisa dipercaya." /></h3>
        <div class="grid grid-cols-2 gap-3 mb-3">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.ai_triage.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Enable AI Auto-Triage<InfoTip tip="AI menilai setiap temuan secara otomatis: mana yang nyata, mana yang false positive." /></span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.ai_triage.drop_false_positives" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Drop False Positives<InfoTip tip="Buang otomatis temuan yang dinilai AI sebagai false positive, jadi tidak muncul di hasil akhir." /></span>
          </label>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="drop-threshold" class="text-xs text-txt-secondary block mb-1">Drop Threshold<InfoTip tip="Batas keyakinan AI (0-1). Temuan dengan skor di bawah nilai ini dianggap false positive dan dibuang. Semakin tinggi, semakin ketat." /></label>
            <input id="drop-threshold" v-model.number="config.ai_triage.drop_threshold" type="number" step="0.05" min="0" max="1" class="input-field" />
          </div>
          <div>
            <label for="min-severity" class="text-xs text-txt-secondary block mb-1">Min Severity<InfoTip tip="Temuan di bawah level ini diabaikan triage. Pilih low agar semua diproses, atau medium/high agar fokus ke yang serius." /></label>
            <select id="min-severity" v-model="config.ai_triage.min_severity" class="input-field">
              <option v-for="sev in triageSeverities" :key="sev" :value="sev" class="capitalize">{{ sev }}</option>
            </select>
          </div>
        </div>
      </div>
      <div v-if="config.rag" class="glass p-4">
        <h3 class="font-bold mb-3">RAG (CVE Retrieval-Augmented Generation)<InfoTip tip="AI mencari data CVE (daftar kerentanan publik) yang relevan dengan temuan, lalu melampirkannya sebagai referensi." /></h3>
        <div class="grid grid-cols-2 gap-3 mb-3">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.rag.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Enable RAG<InfoTip tip="Aktifkan pencarian CVE otomatis untuk memperkaya temuan dengan referensi CVE." /></span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="config.rag.auto_rebuild" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Auto-Rebuild on CVE DB Update<InfoTip tip="Indeks vektor RAG dibangun ulang otomatis setiap kali database CVE di-update." /></span>
          </label>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div class="col-span-3 sm:col-span-1">
            <label for="rag-index-path" class="text-xs text-txt-secondary block mb-1">Index Path<InfoTip tip="Lokasi file indeks vektor RAG. Default data/cve_rag_index.pkl — ubah hanya jika paham." /></label>
            <input id="rag-index-path" v-model="config.rag.index_path" type="text" class="input-field font-mono" placeholder="data/cve_rag_index.pkl" />
          </div>
          <div>
            <label for="rag-top-k" class="text-xs text-txt-secondary block mb-1">Top K<InfoTip tip="Jumlah CVE paling relevan yang dilampirkan ke setiap temuan." /></label>
            <input id="rag-top-k" v-model.number="config.rag.top_k" type="number" min="1" class="input-field" />
          </div>
          <div>
            <label for="rag-min-score" class="text-xs text-txt-secondary block mb-1">Min Score<InfoTip tip="Skor relevansi minimum (0-1). CVE di bawah skor ini tidak dilampirkan." /></label>
            <input id="rag-min-score" v-model.number="config.rag.min_score" type="number" step="0.01" min="0" max="1" class="input-field" />
          </div>
        </div>
      </div>
      <div v-if="config.rate_limiting" class="glass p-4">
        <h3 class="font-bold mb-3">Rate Limiting<InfoTip tip="Batasi kecepatan request scanner agar tidak membebani target atau memicu mekanisme anti-abuse." /></h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.rate_limiting.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Rate Limiting<InfoTip tip="Aktifkan pembatasan kecepatan request." /></span>
        </label>
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label for="requests-per-second" class="text-xs text-txt-secondary block mb-1">Requests/sec<InfoTip tip="Jumlah maksimum request per detik." /></label>
            <input id="requests-per-second" v-model.number="config.rate_limiting.requests_per_second" type="number" min="1" class="input-field" />
          </div>
          <div>
            <label for="burst-size" class="text-xs text-txt-secondary block mb-1">Burst Size<InfoTip tip="Lonjakan request sesaat yang diizinkan sebelum kembali ke batas per detik." /></label>
            <input id="burst-size" v-model.number="config.rate_limiting.burst_size" type="number" min="1" class="input-field" />
          </div>
          <div>
            <label for="delay-on-error" class="text-xs text-txt-secondary block mb-1">Delay on Error (s)<InfoTip tip="Jeda tambahan (detik) setelah menerima error (mis. 429/503) sebelum melanjutkan." /></label>
            <input id="delay-on-error" v-model.number="config.rate_limiting.delay_on_error" type="number" min="0" class="input-field" />
          </div>
        </div>
      </div>
      <div v-if="config.logging" class="glass p-4">
        <h3 class="font-bold mb-3">Logging<InfoTip tip="Pengaturan pencatatan log scanner untuk audit dan pemecahan masalah." /></h3>
        <div class="grid grid-cols-3 gap-3 mb-3">
          <div>
            <label for="log-level" class="text-xs text-txt-secondary block mb-1">Level<InfoTip tip="Kedetailan log: DEBUG terbanyak, INFO normal, WARNING/ERROR/CRITICAL hanya masalah." /></label>
            <select id="log-level" v-model="config.logging.level" class="input-field">
              <option v-for="level in logLevels" :key="level" :value="level">{{ level }}</option>
            </select>
          </div>
          <div>
            <label for="log-file" class="text-xs text-txt-secondary block mb-1">Log File<InfoTip tip="Lokasi file log. Default logs/deep_eye.log." /></label>
            <input id="log-file" v-model="config.logging.log_file" type="text" class="input-field font-mono" placeholder="logs/deep_eye.log" />
          </div>
          <label class="flex items-center gap-2 cursor-pointer pb-2">
            <input v-model="config.logging.log_to_file" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
            <span class="text-sm">Log to File<InfoTip tip="Tulis log ke file. Jika mati, log hanya tampil di terminal/live view." /></span>
          </label>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="log-max-size" class="text-xs text-txt-secondary block mb-1">Max File Size (bytes)<InfoTip tip="Ukuran maksimum file log sebelum diputar (rotasi) ke file baru." /></label>
            <input id="log-max-size" v-model.number="config.logging.max_file_size" type="number" min="0" class="input-field" />
          </div>
          <div>
            <label for="log-backups" class="text-xs text-txt-secondary block mb-1">Backup Count<InfoTip tip="Jumlah file log lama yang disimpan saat rotasi." /></label>
            <input id="log-backups" v-model.number="config.logging.backup_count" type="number" min="0" class="input-field" />
          </div>
        </div>
      </div>
      <div v-if="config.database" class="glass p-4">
        <h3 class="font-bold mb-3">Database<InfoTip tip="Penyimpanan data scan dan temuan (SQLite). Perubahan jarang diperlukan." /></h3>
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label for="db-type" class="text-xs text-txt-secondary block mb-1">Type</label>
            <input id="db-type" :value="config.database.type" type="text" disabled class="input-field opacity-60" />
          </div>
          <div>
            <label for="db-path" class="text-xs text-txt-secondary block mb-1">Path<InfoTip tip="Lokasi file database SQLite. Default data/deep_eye.db — pindahkan hanya jika perlu." /></label>
            <input id="db-path" v-model="config.database.path" type="text" class="input-field font-mono" placeholder="data/deep_eye.db" />
          </div>
          <div>
            <label for="db-cleanup" class="text-xs text-txt-secondary block mb-1">Auto-Cleanup After (days)<InfoTip tip="Hapus otomatis data scan lebih lama dari jumlah hari ini. 0 = nonaktif." /></label>
            <input id="db-cleanup" v-model.number="config.database.auto_cleanup_days" type="number" min="0" class="input-field" />
          </div>
        </div>
      </div>
      <div v-if="config.login_replay" class="glass p-4">
        <h3 class="font-bold mb-3">Auth Macros &amp; Login Replay<InfoTip tip="Scan area yang butuh login: scanner menjalankan skrip login otomatis sehingga halaman setelah login ikut teruji." /></h3>
        <label class="flex items-center gap-2 cursor-pointer mb-3">
          <input v-model="config.login_replay.enabled" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Enable Login Replay<InfoTip tip="Aktifkan pemutaran ulang skenario login sebelum/di sela scan." /></span>
        </label>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="login-macro-path" class="text-xs text-txt-secondary block mb-1">Macro Path<InfoTip tip="File makro login (JSON) berisi langkah klik/isi form untuk masuk ke aplikasi." /></label>
            <input id="login-macro-path" v-model="config.login_replay.macro_path" type="text" class="input-field font-mono" placeholder="config/login_macro.json" />
          </div>
          <div>
            <label for="login-recheck-interval" class="text-xs text-txt-secondary block mb-1">Recheck Interval (s)<InfoTip tip="Selang waktu (detik) pengecekan sesi masih login. Jika kedaluwarsa, makro dijalankan lagi." /></label>
            <input id="login-recheck-interval" v-model.number="config.login_replay.recheck_interval_seconds" type="number" min="0" class="input-field" placeholder="600" />
          </div>
        </div>
        <label class="flex items-center gap-2 cursor-pointer mt-3">
          <input v-model="config.login_replay.abort_on_fail" type="checkbox" class="w-4 h-4 accent-[#00f0ff]" />
          <span class="text-sm">Abort Scan on Login Failure<InfoTip tip="Hentikan scan seluruhnya jika login gagal — mencegah scan tanpa akses yang sah." /></span>
        </label>
      </div>
      <div v-if="config.bug_bounty" class="glass p-4">
        <h3 class="font-bold mb-3">Bug Bounty<InfoTip tip="Format khusus untuk submit laporan ke platform bug bounty." /></h3>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="bounty-format" class="text-xs text-txt-secondary block mb-1">Format<InfoTip tip="Format laporan sesuai platform: HackerOne, Bugcrowd, atau generic." /></label>
            <select id="bounty-format" v-model="config.bug_bounty.format" class="input-field">
              <option value="hackerone">HackerOne</option>
              <option value="bugcrowd">Bugcrowd</option>
              <option value="generic">Generic</option>
            </select>
          </div>
          <div>
            <label for="bounty-output-directory" class="text-xs text-txt-secondary block mb-1">Output Directory<InfoTip tip="Folder tujuan penyimpanan laporan bug bounty. Default reports/bounty." /></label>
            <input id="bounty-output-directory" v-model="config.bug_bounty.output_directory" type="text" class="input-field font-mono" placeholder="reports/bounty" />
          </div>
        </div>
      </div>
    </div>

    <!-- Templates tab -->
    <SettingsTemplates v-if="activeTab === 'templates'" :config="config" />

    <!-- Maintenance tab -->
    <div v-if="activeTab === 'maintenance'" class="space-y-4">
      <div class="glass p-4 flex items-center justify-between">
        <div>
          <h3 class="font-bold">Update CVE Database<InfoTip tip="Unduh daftar kerentanan publik terbaru dari NVD (National Vulnerability Database). Jalankan berkala agar referensi CVE tetap baru. Proses berjalan di latar belakang." /></h3>
          <p class="text-xs text-txt-secondary mt-1">Fetch latest CVEs from NVD</p>
        </div>
        <button @click="updateCve" class="neon-btn text-sm">Run</button>
      </div>
      <div class="glass p-4 flex items-center justify-between">
        <div>
          <h3 class="font-bold">Build RAG Index<InfoTip tip="Bangun ulang indeks vektor RAG dari database CVE. Perlu dijalankan setelah Update CVE jika Auto-Rebuild mati. Proses berjalan di latar belakang." /></h3>
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
