<script setup lang="ts">
import { ref, onMounted } from "vue";
import { api } from "../api/client";
import InfoTip from "../components/InfoTip.vue";

type TemplateMeta = Record<string, unknown> & { id?: string; name?: string; path: string; severity?: string; tags?: string[]; http_count?: number; enabled?: boolean };

const props = withDefaults(defineProps<{ config?: Record<string, unknown> }>(), { config: undefined });

const templates = ref<TemplateMeta[]>([]);
const templatesLoaded = ref(false);
const tplEditingId = ref<string | null>(null);
const tplEditorContent = ref("");
const tplUploadContent = ref("");
const tplError = ref("");
const tplBusy = ref("");

function getErrorMessage(err: unknown, fallback: string): string {
  if (err instanceof Error && err.message) return err.message;
  return fallback;
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
async function reloadTemplates() {
  tplBusy.value = "reload";
  tplError.value = "";
  try {
    await api.templates.reload();
    await loadTemplates();
  } catch (err: unknown) {
    tplError.value = getErrorMessage(err, "reload failed");
  } finally {
    tplBusy.value = "";
  }
}
async function openTplEdit(tpl: TemplateMeta) {
  tplError.value = "";
  try {
    const data = await api.templates.get(tpl.id ?? tpl.name ?? "");
    tplEditingId.value = tpl.id ?? tpl.name ?? null;
    tplEditorContent.value = String(data.content ?? "");
  } catch (err: unknown) {
    tplError.value = getErrorMessage(err, "load failed");
  }
}
async function saveTplEdit() {
  if (!tplEditingId.value) return;
  tplBusy.value = "save";
  tplError.value = "";
  try {
    await api.templates.update(tplEditingId.value, { content: tplEditorContent.value });
    tplEditingId.value = null;
    tplEditorContent.value = "";
    await loadTemplates();
  } catch (err: unknown) {
    tplError.value = getErrorMessage(err, "save failed");
  } finally {
    tplBusy.value = "";
  }
}
async function duplicateTpl(tpl: TemplateMeta) {
  const tplId = tpl.id ?? tpl.name ?? "";
  tplBusy.value = `dup-${tplId}`;
  tplError.value = "";
  try {
    const data = await api.templates.get(tplId);
    let content = String(data.content);
    const newId = `${tplId}-copy-${Date.now().toString(36)}`;
    content = content.replace(/^id:\s*\S+/m, `id: ${newId}`);
    if (!/^id:/m.test(content)) content = `id: ${newId}\n` + content;
    await api.templates.create({ content });
    await loadTemplates();
  } catch (err: unknown) {
    tplError.value = getErrorMessage(err, "duplicate failed");
  } finally {
    tplBusy.value = "";
  }
}
async function deleteTpl(tpl: TemplateMeta) {
  const tplId = tpl.id ?? tpl.name ?? "";
  if (!confirm(`Delete template '${tplId}'?`)) return;
  tplBusy.value = `del-${tplId}`;
  tplError.value = "";
  try {
    await api.templates.remove(tplId);
    await loadTemplates();
  } catch (err: unknown) {
    tplError.value = getErrorMessage(err, "delete failed");
    try {
      const r = await fetch(`/api/templates/${tplId}`, { method: "DELETE" });
      if (!r.ok) tplError.value = await r.text();
    } catch {
      // ignore secondary fetch failure
    }
  } finally {
    tplBusy.value = "";
  }
}
async function uploadTpl() {
  tplError.value = "";
  if (!tplUploadContent.value.trim()) { tplError.value = "YAML content required"; return; }
  tplBusy.value = "upload";
  try {
    await api.templates.create({ content: tplUploadContent.value });
    tplUploadContent.value = "";
    await loadTemplates();
  } catch (err: unknown) {
    tplError.value = getErrorMessage(err, "upload failed");
  } finally {
    tplBusy.value = "";
  }
}
function downloadTpl(tpl: TemplateMeta) {
  const tplId = tpl.id ?? tpl.name ?? "";
  api.templates.get(tplId).then((data) => {
    const blob = new Blob([String(data.content)], { type: "text/yaml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `${tplId}.yaml`; a.click();
    URL.revokeObjectURL(url);
  }).catch((err: unknown) => { tplError.value = getErrorMessage(err, "download failed"); });
}

onMounted(loadTemplates);
</script>

<template>
  <div class="space-y-4">
    <div class="glass p-4 flex items-center justify-between">
      <div>
        <h3 class="font-bold">Scan Templates<InfoTip tip="Template deteksi YAML bawaan mesin scan — aturan siap pakai untuk menemukan pola kerentanan tertentu. Custom hanya di templates/custom/." /></h3>
        <p class="text-xs text-txt-secondary mt-1">YAML detection templates — shipped read-only, custom in templates/custom/</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="sev-badge sev-info">{{ templates.length }} templates</span>
        <button @click="reloadTemplates" :disabled="tplBusy==='reload'" class="neon-btn text-xs">{{ tplBusy==='reload' ? 'Reloading…' : 'Reload' }}</button>
      </div>
    </div>

    <div v-if="props.config" class="glass p-4 space-y-3">
      <h4 class="font-bold text-sm">Template Config</h4>
      <label class="flex items-center gap-2 text-sm">
        <input type="checkbox" :checked="!!(props.config.templates as Record<string, unknown>)?.enabled" @change="props.config!.templates = { ...((props.config!.templates as Record<string, unknown>)||{}), enabled: ($event.target as HTMLInputElement).checked }" />
        Enabled — jalankan templates saat scan
      </label>
      <div>
        <label for="template-directories" class="text-xs text-txt-secondary block mb-1">Template directories (comma-separated)</label>
        <input id="template-directories" :value="((props.config.templates as Record<string, unknown>)?.template_directories as string[]||[]).join(', ')" @input="props.config!.templates = { ...((props.config!.templates as Record<string, unknown>)||{}), template_directories: ($event.target as HTMLInputElement).value.split(',').map(s=>s.trim()).filter(Boolean) }" type="text" class="input-field font-mono text-sm" placeholder="templates" />
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label for="tag-filters" class="text-xs text-txt-secondary block mb-1">Tag filters (comma-separated, empty=all)</label>
          <input id="tag-filters" :value="((props.config.templates as Record<string, unknown>)?.tag_filters as string[]||[]).join(', ')" @input="props.config!.templates = { ...((props.config!.templates as Record<string, unknown>)||{}), tag_filters: ($event.target as HTMLInputElement).value.split(',').map(s=>s.trim()).filter(Boolean) }" type="text" class="input-field font-mono text-sm" placeholder="exposure, misconfig" />
        </div>
        <div>
          <label for="severity-filter" class="text-xs text-txt-secondary block mb-1">Severity filter (comma-separated)</label>
          <input id="severity-filter" :value="((props.config.templates as Record<string, unknown>)?.severity_filter as string[]||[]).join(', ')" @input="props.config!.templates = { ...((props.config!.templates as Record<string, unknown>)||{}), severity_filter: ($event.target as HTMLInputElement).value.split(',').map(s=>s.trim()).filter(Boolean) }" type="text" class="input-field font-mono text-sm" placeholder="high, critical" />
        </div>
      </div>
      <p class="text-xs text-txt-tertiary">Save via bottom Save Config. GET /api/templates reflects enabled via filters.</p>
    </div>

    <div class="glass p-4 space-y-2">
      <h4 class="font-bold text-sm">Upload YAML Template</h4>
      <p class="text-xs text-txt-secondary">Paste valid YAML (must have id, info.name, info.severity, http). Akan disimpan ke templates/custom/</p>
      <label for="tpl-upload-content" class="sr-only">YAML Template Content</label>
      <textarea id="tpl-upload-content" v-model="tplUploadContent" rows="6" class="input-field font-mono text-xs w-full" placeholder="id: my-custom-check&#10;info:&#10;  name: My Check&#10;  severity: medium&#10;  tags: [custom]&#10;http:&#10;  - method: GET&#10;    path: /&#10;    matchers:&#10;      - type: word&#10;        words: [admin]"></textarea>
      <div class="flex items-center gap-2">
        <button @click="uploadTpl" :disabled="tplBusy==='upload'" class="neon-btn text-xs">{{ tplBusy==='upload' ? 'Uploading…' : 'Upload' }}</button>
        <span v-if="tplError" class="text-sev-critical text-xs break-all">{{ tplError }}</span>
      </div>
    </div>

    <div v-for="tpl in templates" :key="tpl.path" class="glass p-4">
      <div class="flex items-start justify-between gap-4">
        <div class="min-w-0">
          <h4 class="font-bold truncate flex items-center gap-2">{{ tpl.id || tpl.name }} <span :class="['sev-badge', tpl.severity==='critical' ? 'sev-critical' : tpl.severity==='high' ? 'sev-high' : tpl.severity==='medium' ? 'sev-medium' : 'sev-info']">{{ tpl.severity || 'n/a' }}</span> <span v-if="String(tpl.path).includes('custom/')" class="sev-badge sev-info">custom</span><span v-else class="sev-badge" style="background:rgba(255,255,255,0.08)">shipped</span></h4>
          <p class="text-xs text-txt-tertiary font-mono mt-0.5 break-all">{{ tpl.path }} · http: {{ tpl.http_count ?? 0 }} · {{ tpl.enabled ? 'enabled' : 'disabled' }}</p>
        </div>
        <div class="flex gap-1 flex-wrap justify-end shrink-0">
          <span v-for="tag in (tpl.tags ?? [])" :key="String(tag)" class="sev-badge sev-info">{{ tag }}</span>
          <span v-if="!tpl.tags || !tpl.tags.length" class="sev-badge sev-info">untagged</span>
        </div>
      </div>
      <div class="flex flex-wrap gap-2 mt-3">
        <button @click="openTplEdit(tpl)" class="neon-btn text-xs">Edit</button>
        <button @click="duplicateTpl(tpl)" :disabled="tplBusy===`dup-${tpl.id ?? tpl.name}`" class="neon-btn text-xs">Duplicate</button>
        <button @click="downloadTpl(tpl)" class="neon-btn text-xs">Download</button>
        <button @click="deleteTpl(tpl)" :disabled="tplBusy===`del-${tpl.id ?? tpl.name}`" class="neon-btn text-xs border-red-500/30">Delete</button>
      </div>
      <div v-if="tplEditingId===(tpl.id||tpl.name)" class="mt-3 space-y-2">
        <label for="tpl-editor-content" class="sr-only">Edit Template YAML</label>
        <textarea id="tpl-editor-content" v-model="tplEditorContent" rows="12" class="input-field font-mono text-xs w-full"></textarea>
        <div class="flex gap-2">
          <button @click="saveTplEdit" :disabled="tplBusy==='save'" class="neon-btn text-xs">{{ tplBusy==='save' ? 'Saving…' : 'Save' }}</button>
          <button @click="tplEditingId=null" class="neon-btn text-xs">Cancel</button>
        </div>
      </div>
    </div>
    <div v-if="tplError" class="glass p-3 text-sev-critical text-xs break-all">{{ tplError }}</div>
    <div v-if="templatesLoaded && !templates.length" class="glass p-6 text-center text-txt-secondary text-sm">
      No templates found
    </div>
  </div>
</template>
