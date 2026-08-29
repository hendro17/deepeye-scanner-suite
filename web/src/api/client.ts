const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

export type ScanRecord = Record<string, unknown> & { id: number; status: string };
export type HealthResponse = { status: string };
export type ConfigResponse = { config: Record<string, unknown>; masked: boolean };
export type ProviderStatus = Record<string, unknown> & { name: string };
export type TemplateInfo = Record<string, unknown> & { id?: string; name?: string; path: string };
export type ReportInfo = Record<string, unknown> & { filename: string; format: string; size: number };
export type CreateScanBody = Record<string, unknown> & { target_url: string };

export const api = {
  health: () => request<HealthResponse>("/health"),

  scans: {
    list: () => request<ScanRecord[]>("/scans"),
    get: (id: number) => request<ScanRecord>(`/scans/${id}`),
    create: (body: CreateScanBody) =>
      request<{ id: number; status: string }>("/scans", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    start: (id: number) =>
      request<Record<string, unknown>>(`/scans/${id}/start`, { method: "POST" }),
    stop: (id: number) =>
      request<Record<string, unknown>>(`/scans/${id}/stop`, { method: "POST" }),
    findings: (id: number) => request<{ vulnerabilities: Record<string, unknown>[]; total?: number }>(`/scans/${id}/findings`),
    compare: (scanIdA: number, scanIdB: number) =>
      request<Record<string, unknown>>("/scans/compare", {
        method: "POST",
        body: JSON.stringify({ scan_id_a: scanIdA, scan_id_b: scanIdB }),
      }),
    ingestOpenApi: (filename: string, content: string) =>
      request<{ targets: string[]; count: number }>("/scans/ingest-openapi", {
        method: "POST",
        body: JSON.stringify({ filename, content }),
      }),
    streamUrl: (id: number) => `${BASE}/scans/${id}/stream`,
  },

  config: {
    get: () => request<ConfigResponse>("/config"),
    update: (config: Record<string, unknown>) =>
      request<{ success: boolean }>("/config", {
        method: "PUT",
        body: JSON.stringify({ config }),
      }),
  },

  providers: {
    status: () => request<ProviderStatus[]>("/providers/status"),
    test: (name: string, body?: Record<string, unknown>) =>
      request<Record<string, unknown>>(`/providers/test/${name}`, {
        method: "POST",
        body: JSON.stringify(body ?? {}),
      }),
  },

  reports: {
    list: () => request<ReportInfo[]>("/reports"),
    downloadUrl: (filename: string) => `${BASE}/reports/${filename}`,
  },

  maintenance: {
    updateCve: () =>
      request<Record<string, unknown>>("/maintenance/update-cve", { method: "POST" }),
    buildRag: () =>
      request<Record<string, unknown>>("/maintenance/build-rag", { method: "POST" }),
  },

  templates: {
    list: () => request<TemplateInfo[]>("/templates"),
    get: (id: string) => request<{ content: string } & Record<string, unknown>>(`/templates/${id}`),
    create: (body: Record<string, unknown>) => request<Record<string, unknown>>("/templates", { method: "POST", body: JSON.stringify(body) }),
    update: (id: string, body: Record<string, unknown>) => request<Record<string, unknown>>(`/templates/${id}`, { method: "PUT", body: JSON.stringify(body) }),
    remove: (id: string) => fetch(`${BASE}/templates/${id}`, { method: "DELETE" }).then(async (r) => { if (!r.ok) throw new Error(`API ${r.status}: ${await r.text()}`); }),
    reload: () => request<Record<string, unknown>>("/templates/reload", { method: "POST" }),
  },
};
