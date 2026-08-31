<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useScansStore } from "../stores/scans";
import { CHECK_CATEGORIES, ALL_CHECKS, checkLabel, presetChecks, type PresetId } from "../constants/checks";
import { SECRET_PATTERNS, ALL_SECRET_PATTERNS } from "../constants/secrets";
import { CATEGORY_TIPS } from "../constants/scanTips";
import {
  ALL_REPORT_FORMATS,
  AUTH_MODE,
  PRESET_IDS,
  PRESET_LIST,
  LOGIN_FIELD_DEFAULTS,
  PLACEHOLDERS,
  ERR_PREFIX,
  ERR_SPEC_PREFIX,
  SEPARATORS,
  SCOPE_PREFIX,
  scanRoute,
} from "../constants/scanLabels";
import { api } from "../api/client";
import InfoTip from "../components/InfoTip.vue";

const router = useRouter();
const store = useScansStore();

const targetUrl = ref("");
const scopeNl = ref("");
const threads = ref(5);
const depth = ref(2);
const formats = ref<string[]>([ALL_REPORT_FORMATS[0]]);
const authorized = ref(false);
const submitting = ref(false);

const secretsEnabled = ref(false);
const selectedPatterns = ref<string[]>([...ALL_SECRET_PATTERNS]);

// --- Auth for maximal scan behind login ---
const authMode = ref<(typeof AUTH_MODE)[keyof typeof AUTH_MODE]>(AUTH_MODE.NONE);
const authHeadersRaw = ref("");
const authCookiesRaw = ref("");
const loginUrl = ref("");
const loginUsername = ref("");
const loginPassword = ref("");
const loginUField = ref(LOGIN_FIELD_DEFAULTS.USERNAME);
const loginPField = ref(LOGIN_FIELD_DEFAULTS.PASSWORD);

function _tryParseJsonHeaders(raw: string): Record<string, string> | null {
  try {
    const j = JSON.parse(raw);
    if (!j || typeof j !== "object") return null;
    const out: Record<string, string> = {};
    for (const [k, v] of Object.entries(j)) out[k] = String(v);
    return out;
  } catch {
    return null;
  }
}

function _parseHeaderLines(trimmed: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const line of trimmed.split(SEPARATORS.NEWLINE)) {
    const l = line.trim();
    if (!l) continue;
    let sep = l.indexOf(SEPARATORS.COLON);
    if (sep === -1) sep = l.indexOf(SEPARATORS.EQUALS);
    if (sep === -1) continue;
    const k = l.slice(0, sep).trim();
    const v = l.slice(sep + 1).trim();
    if (k) out[k] = v;
  }
  return out;
}

function parseHeadersCookies(raw: string): Record<string, string> {
  const trimmed = raw.trim();
  if (!trimmed) return {};
  const parsed = _tryParseJsonHeaders(trimmed);
  if (parsed) return parsed;
  return _parseHeaderLines(trimmed);
}

function togglePattern({ id }: { id: string }) {
  const idx = selectedPatterns.value.indexOf(id);
  if (idx >= 0) selectedPatterns.value.splice(idx, 1);
  else selectedPatterns.value.push(id);
}

const crawlTargets = ref<string[]>([]);
const ingesting = ref(false);

function getErrorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

async function onSpecFile(e: Event) {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = "";
  if (!file) return;
  ingesting.value = true;
  try {
    const res = await api.scans.ingestOpenApi(file.name, await file.text());
    crawlTargets.value = res.targets;
  } catch (err: unknown) {
    alert(ERR_SPEC_PREFIX + getErrorMessage(err));
  } finally {
    ingesting.value = false;
  }
}

function applyTarget({ t }: { t: string }) {
  targetUrl.value = t;
}

function applyAllToScope() {
  if (!crawlTargets.value.length) return;
  if (!targetUrl.value) targetUrl.value = crawlTargets.value[0];
  scopeNl.value = SCOPE_PREFIX + crawlTargets.value.join(SEPARATORS.SPACE);
}

function toggleFormat({ fmt }: { fmt: string }) {
  const idx = formats.value.indexOf(fmt);
  if (idx >= 0) formats.value.splice(idx, 1);
  else formats.value.push(fmt);
}

const selectedChecks = ref<string[]>([...ALL_CHECKS]);

function isCheckSelected({ id }: { id: string }) {
  return selectedChecks.value.includes(id);
}

function toggleCheck({ id }: { id: string }) {
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
  if (preset === PRESET_IDS.CUSTOM) return;
  selectedChecks.value = presetChecks(preset);
}

function categorySelectedCount({ checks }: { checks: string[] }) {
  return checks.filter((c) => selectedChecks.value.includes(c)).length;
}

function detectPreset(): PresetId {
  const current = [...selectedChecks.value].sort();
  for (const p of PRESET_LIST as unknown as PresetId[]) {
    if (JSON.stringify(current) === JSON.stringify([...presetChecks(p)].sort())) return p;
  }
  return PRESET_IDS.CUSTOM as PresetId;
}

const activePreset = computed(detectPreset);
const selectedCount = computed(() => selectedChecks.value.length);
const totalCount = ALL_CHECKS.length;

const canSubmit = computed(
  () => Boolean(targetUrl.value) && authorized.value && selectedCount.value > 0 && !submitting.value,
);

function _buildBaseBody(): Record<string, unknown> {
  return {
    target_url: targetUrl.value,
    scope_nl: scopeNl.value || undefined,
    checks: selectedChecks.value,
    threads: threads.value,
    depth: depth.value,
    formats: formats.value,
    secrets_enabled: secretsEnabled.value,
    secret_patterns: secretsEnabled.value ? selectedPatterns.value : undefined,
    auth_mode: authMode.value,
  };
}

function _applyCookieHeaders(body: Record<string, unknown>): void {
  const h = parseHeadersCookies(authHeadersRaw.value);
  const c = parseHeadersCookies(authCookiesRaw.value);
  if (Object.keys(h).length) body.auth_headers = h;
  if (Object.keys(c).length) body.auth_cookies = c;
}

function _applyFormLogin(body: Record<string, unknown>): void {
  body.login_url = loginUrl.value || targetUrl.value;
  body.login_username = loginUsername.value;
  body.login_password = loginPassword.value;
  body.login_username_field = loginUField.value || LOGIN_FIELD_DEFAULTS.USERNAME;
  body.login_password_field = loginPField.value || LOGIN_FIELD_DEFAULTS.PASSWORD;
}

function _applyAuthToBody(body: Record<string, unknown>, mode: string): void {
  if (mode === AUTH_MODE.COOKIE_HEADERS) _applyCookieHeaders(body);
  else if (mode === AUTH_MODE.FORM_LOGIN) _applyFormLogin(body);
}

async function submit() {
  submitting.value = true;
  try {
    const body = _buildBaseBody();
    _applyAuthToBody(body, authMode.value);
    const res = await store.createScan(body as unknown as { target_url: string });
    await store.startScan(res.id);
    router.push(scanRoute(res.id));
  } catch (err: unknown) {
    alert(ERR_PREFIX + getErrorMessage(err));
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
        <label for="target-url" class="text-sm font-medium block mb-2">Target URL<InfoTip tip="Alamat lengkap halaman web yang akan diuji keamanan. Wajib diawali http:// atau https://. Contoh: https://contoh.com" /></label>
        <input id="target-url" v-model="targetUrl" type="text" :placeholder="PLACEHOLDERS.TARGET"
               class="input-field font-mono" />
      </div>

      <!-- Scope NL -->
      <div class="glass p-5">
        <label for="scope-nl" class="text-sm font-medium block mb-2">Natural Language Scope <span class="text-txt-tertiary">(optional)</span><InfoTip tip="Kalimat bebas dalam bahasa sehari-hari untuk membatasi fokus scan. Contoh: 'fokus ke halaman login dan API'. Kosongkan jika ingin scope penuh." /></label>
        <input id="scope-nl" v-model="scopeNl" type="text" :placeholder="PLACEHOLDERS.SCOPE"
               class="input-field" />
      </div>

      <!-- OpenAPI Import -->
      <div class="glass p-5">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-1">
          <div>
            <label for="openapi-file" class="text-sm font-medium block cursor-pointer">Import OpenAPI Specification<InfoTip tip="Unggah file spesifikasi OpenAPI/Swagger (.json atau .yaml). Setiap endpoint di dalamnya akan menjadi daftar target crawl. Tombol 'Use' memilih satu target, 'Apply all to target & scope' memakai semuanya sekaligus." /></label>
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
              <button type="button" @click="applyTarget({ t })"
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
            <p class="text-xs font-semibold uppercase tracking-wider text-txt-secondary">Vulnerability Checks<InfoTip tip="Daftar pengujian celah keamanan yang akan dijalankan. Semakin banyak dipilih, semakin lama scan. Gunakan preset (dropdown) untuk memilih cepat, atau atur manual per kategori." /></p>
            <p class="text-xs mt-1"><span class="text-neon-cyan font-medium">{{ selectedCount }}</span> of {{ totalCount }} selected</p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <select :value="activePreset" @change="applyPreset(($event.target as HTMLSelectElement).value as PresetId)"
                    aria-label="Check presets"
                    class="bg-transparent border border-[rgba(0,240,255,0.12)] hover:border-[rgba(0,240,255,0.25)] rounded px-2 py-1.5 text-xs font-medium text-txt-secondary transition-all">
              <option :value="PRESET_IDS.QUICK">Quick Scan</option>
              <option :value="PRESET_IDS.FULL">Full Scan</option>
              <option :value="PRESET_IDS.API_FOCUS">API Focus</option>
              <option :value="PRESET_IDS.CUSTOM" disabled>Custom</option>
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
                {{ categorySelectedCount({ checks: category.checks }) }}/{{ category.checks.length }}
              </span>
            </div>
            <ul class="space-y-2">
              <li v-for="checkId in category.checks" :key="checkId">
                <div class="flex items-center gap-2.5 cursor-pointer select-none" @click="toggleCheck({ id: checkId })">
                  <button type="button" role="switch" :aria-checked="isCheckSelected({ id: checkId })"
                          @click.stop="toggleCheck({ id: checkId })"
                          class="relative shrink-0 w-10 h-[22px] rounded-full transition-colors duration-150 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neon-cyan"
                          :class="isCheckSelected({ id: checkId }) ? 'bg-[rgba(0,240,255,0.35)]' : 'bg-[rgba(255,255,255,0.08)]'">
                    <span aria-hidden="true"
                          class="absolute top-[2px] left-[2px] w-[18px] h-[18px] rounded-full transition-transform duration-150"
                          :class="isCheckSelected({ id: checkId }) ? 'translate-x-[18px] bg-neon-cyan' : 'translate-x-0 bg-txt-tertiary'"></span>
                  </button>
                  <span class="text-sm" :class="isCheckSelected({ id: checkId }) ? 'text-txt-primary' : 'text-txt-secondary'">{{ checkLabel(checkId) }}<InfoTip :tip="CATEGORY_TIPS[category.id]" /></span>
                </div>
              </li>
            </ul>
          </fieldset>
        </div>
      </div>

      <!-- Sliders -->
      <div class="grid grid-cols-2 gap-4">
        <div class="glass p-5">
          <label for="scan-threads" class="text-sm font-medium block mb-2">Threads: <span class="text-neon-cyan">{{ threads }}</span><InfoTip tip="Jumlah permintaan paralel ke target. Semakin tinggi semakin cepat, tapi membebani server target dan berisiko kena blokir/rate limit. Rekomendasi: 5." /></label>
          <input id="scan-threads" v-model.number="threads" type="range" min="1" max="50" class="w-full" />
        </div>
        <div class="glass p-5">
          <label for="scan-depth" class="text-sm font-medium block mb-2">Depth: <span class="text-neon-cyan">{{ depth }}</span><InfoTip tip="Kedalaman penjelajahan halaman dari halaman awal. 1 = halaman pertama saja; semakin besar, semakin banyak halaman yang dikunjungi (lebih lama)." /></label>
          <input id="scan-depth" v-model.number="depth" type="range" min="1" max="10" class="w-full" />
        </div>
      </div>

      <!-- Formats -->
      <div class="glass p-5">
        <p class="text-sm font-medium block mb-3">Report Formats<InfoTip tip="Format file laporan hasil scan — bebas pilih lebih dari satu. HTML untuk dibaca di browser, PDF untuk dokumen formal, JSON/SARIF untuk tools lain, JUnit untuk CI/CD, CSV/XLSX untuk spreadsheet." /></p>
        <div class="flex flex-wrap gap-2">
          <button v-for="fmt in ALL_REPORT_FORMATS" :key="fmt"
                  @click="toggleFormat({ fmt })"
                  :class="['px-3 py-1.5 rounded text-xs font-medium border transition-all',
                    formats.includes(fmt)
                      ? 'bg-[rgba(0,240,255,0.15)] text-neon-cyan border-[rgba(0,240,255,0.4)]'
                      : 'text-txt-secondary border-[rgba(0,240,255,0.12)] hover:border-[rgba(0,240,255,0.25)]']">
            {{ fmt }}
          </button>
        </div>
      </div>

      <!-- Secrets Scanner -->
      <div class="glass p-5">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p class="text-sm font-medium">Secrets Scanner<InfoTip tip="Mendeteksi kredensial bocor (API key, token, secret) di halaman dan file yang ditemukan. Setelah aktif, pilih pola credential yang ingin dicari." /></p>
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
          <button v-for="p in SECRET_PATTERNS" :key="p.id" type="button" @click="togglePattern({ id: p.id })"
                  :class="['px-3 py-1.5 rounded text-xs font-medium border transition-all',
                    selectedPatterns.includes(p.id)
                      ? 'bg-[rgba(0,240,255,0.15)] text-neon-cyan border-[rgba(0,240,255,0.4)]'
                      : 'text-txt-secondary border-[rgba(0,240,255,0.12)] hover:border-[rgba(0,240,255,0.25)]']">
            {{ p.label }}
          </button>
        </div>
      </div>

      <!-- Authentication (maximal scan behind login) -->
      <div class="glass p-5">
        <p class="text-sm font-medium block mb-3">Authentication <span class="text-txt-tertiary">(optional - untuk scan maksimal di balik login)</span><InfoTip tip="Pilih mode auth agar crawler bisa masuk ke halaman terproteksi. None = publik saja. Cookie/Headers = paste session/token dari DevTools. Form Login = scanner login otomatis pakai username/password dan handle CSRF." /></p>
        <div class="flex flex-wrap gap-2 mb-4">
          <button type="button" @click="authMode = AUTH_MODE.NONE"
                  :class="['px-3 py-1.5 rounded text-xs font-medium border transition-all',
                    authMode === AUTH_MODE.NONE ? 'bg-[rgba(0,240,255,0.15)] text-neon-cyan border-[rgba(0,240,255,0.4)]' : 'text-txt-secondary border-[rgba(0,240,255,0.12)]']">None (publik)</button>
          <button type="button" @click="authMode = AUTH_MODE.COOKIE_HEADERS"
                  :class="['px-3 py-1.5 rounded text-xs font-medium border transition-all',
                    authMode === AUTH_MODE.COOKIE_HEADERS ? 'bg-[rgba(0,240,255,0.15)] text-neon-cyan border-[rgba(0,240,255,0.4)]' : 'text-txt-secondary border-[rgba(0,240,255,0.12)]']">Cookie / Headers</button>
          <button type="button" @click="authMode = AUTH_MODE.FORM_LOGIN"
                  :class="['px-3 py-1.5 rounded text-xs font-medium border transition-all',
                    authMode === AUTH_MODE.FORM_LOGIN ? 'bg-[rgba(0,240,255,0.15)] text-neon-cyan border-[rgba(0,240,255,0.4)]' : 'text-txt-secondary border-[rgba(0,240,255,0.12)]']">Form Login</button>
        </div>

        <div v-if="authMode === AUTH_MODE.COOKIE_HEADERS" class="space-y-3">
          <div>
            <label for="auth-headers" class="text-xs font-medium block mb-1">Custom Headers <span class="text-txt-tertiary">(JSON atau per baris "Key: Value")</span></label>
            <textarea id="auth-headers" v-model="authHeadersRaw" rows="3" :placeholder="PLACEHOLDERS.AUTH_HEADERS"
                      class="input-field font-mono text-xs"></textarea>
          </div>
          <div>
            <label for="auth-cookies" class="text-xs font-medium block mb-1">Cookies <span class="text-txt-tertiary">(JSON atau per baris "key=value" / "key: value")</span></label>
            <textarea id="auth-cookies" v-model="authCookiesRaw" rows="3" :placeholder="PLACEHOLDERS.AUTH_COOKIES"
                      class="input-field font-mono text-xs"></textarea>
          </div>
          <p class="text-[11px] text-txt-tertiary">Copy dari DevTools → Application → Cookies / Network → Request Headers. Dikirim di setiap request crawl & scan.</p>
        </div>

        <div v-if="authMode === AUTH_MODE.FORM_LOGIN" class="space-y-3">
          <div>
            <label for="login-url" class="text-xs font-medium block mb-1">Login URL</label>
            <input id="login-url" v-model="loginUrl" type="text" :placeholder="targetUrl || PLACEHOLDERS.TARGET_LOGIN" class="input-field font-mono text-xs" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label for="login-username" class="text-xs font-medium block mb-1">Username / Email</label>
              <input id="login-username" v-model="loginUsername" type="text" :placeholder="PLACEHOLDERS.USERNAME" class="input-field text-xs" />
            </div>
            <div>
              <label for="login-password" class="text-xs font-medium block mb-1">Password</label>
              <input id="login-password" v-model="loginPassword" type="password" :placeholder="PLACEHOLDERS.PASSWORD" class="input-field text-xs" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label for="login-u-field" class="text-xs font-medium block mb-1">Username field name</label>
              <input id="login-u-field" v-model="loginUField" type="text" :placeholder="PLACEHOLDERS.USERNAME_FIELD" class="input-field font-mono text-xs" />
            </div>
            <div>
              <label for="login-p-field" class="text-xs font-medium block mb-1">Password field name</label>
              <input id="login-p-field" v-model="loginPField" type="text" :placeholder="PLACEHOLDERS.PASSWORD_FIELD" class="input-field font-mono text-xs" />
            </div>
          </div>
          <p class="text-[11px] text-txt-tertiary">Scanner akan GET login page → extract CSRF (csrf_token/_token/authenticity_token) → POST credentials → crawl sebagai user login. Cek field name via Inspect → &lt;input name="..."&gt; di form login.</p>
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
