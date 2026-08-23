const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  scans: {
    list: () => request<any[]>("/scans"),
    get: (id: number) => request<any>(`/scans/${id}`),
    create: (body: any) =>
      request<{ id: number; status: string }>("/scans", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    start: (id: number) =>
      request<any>(`/scans/${id}/start`, { method: "POST" }),
    stop: (id: number) =>
      request<any>(`/scans/${id}/stop`, { method: "POST" }),
    findings: (id: number) => request<any>(`/scans/${id}/findings`),
    streamUrl: (id: number) => `${BASE}/scans/${id}/stream`,
  },

  config: {
    get: () => request<{ config: any; masked: boolean }>("/config"),
    update: (config: any) =>
      request<{ success: boolean }>("/config", {
        method: "PUT",
        body: JSON.stringify({ config }),
      }),
  },

  providers: {
    status: () => request<any[]>("/providers/status"),
    test: (name: string) =>
      request<any>(`/providers/test/${name}`, { method: "POST" }),
  },

  reports: {
    list: () => request<any[]>("/reports"),
    downloadUrl: (filename: string) => `${BASE}/reports/${filename}`,
  },

  maintenance: {
    updateCve: () =>
      request<any>("/maintenance/update-cve", { method: "POST" }),
    buildRag: () =>
      request<any>("/maintenance/build-rag", { method: "POST" }),
  },
};
