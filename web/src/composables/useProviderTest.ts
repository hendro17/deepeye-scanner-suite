import { ref } from "vue";
import { api } from "../api/client";

type TestResult = { ok: boolean; message: string; ms: number };
type TestState = { running: boolean; result: TestResult | null };
export type ProviderConfig = Record<string, unknown> & { model?: string; api_key?: string; base_url?: string };

const keylessProviders = new Set(["ollama", "lmstudio"]);

function isKeyless(name: string): boolean {
  return keylessProviders.has(name);
}

function buildConfig(provider: ProviderConfig, name: string): Record<string, string> {
  const cfg: Record<string, string> = { model: String(provider.model ?? "") };
  if (!isKeyless(name)) cfg.api_key = String(provider.api_key ?? "");
  const baseUrl = provider.base_url;
  if (typeof baseUrl === "string") cfg.base_url = baseUrl;
  return cfg;
}

export function useProviderTest() {
  const providersTests = ref<Record<string, TestState>>({});
  try {
    localStorage.removeItem("deepeye:providers-connected");
  } catch {
    // ignore - storage unavailable
  }
  const connectedMap = ref<Record<string, { ok: boolean; at: string }>>({});

  function isConnected(name: string): boolean {
    return Boolean(connectedMap.value[name]?.ok);
  }

  function testStatus(name: string): TestState {
    return providersTests.value[name] ?? { running: false, result: null };
  }

  function markConnected(name: string): void {
    connectedMap.value = { ...connectedMap.value, [name]: { ok: true, at: new Date().toISOString() } };
  }

  async function testProvider(name: string, provider: ProviderConfig | undefined): Promise<void> {
    if (!provider || testStatus(name).running) return;
    providersTests.value = { ...providersTests.value, [name]: { running: true, result: null } };
    const payload = buildConfig(provider, name);
    try {
      const res = await api.providers.test(name, { config: payload });
      const ok = Boolean(res.success);
      if (ok) markConnected(name);
      providersTests.value[name] = {
        running: false,
        result: { ok, message: String(res.message ?? ""), ms: Number(res.latency_ms ?? 0) },
      };
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      providersTests.value[name] = { running: false, result: { ok: false, message, ms: 0 } };
    }
  }

  return { providersTests, connectedMap, isKeyless, isConnected, testStatus, testProvider };
}
