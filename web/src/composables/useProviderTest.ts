import { ref } from "vue";
import { api } from "../api/client";

type TestResult = { ok: boolean; message: string; ms: number };
type TestState = { running: boolean; result: TestResult | null };

const CONNECTED_STORE_KEY = "deepeye:providers-connected";
const keylessProviders = new Set(["ollama", "lmstudio"]);

function loadConnectedStore(): Record<string, { ok: boolean; at: string }> {
  try {
    return JSON.parse(localStorage.getItem(CONNECTED_STORE_KEY) ?? "{}");
  } catch {
    return {};
  }
}

function persistConnectedStore(map: Record<string, { ok: boolean; at: string }>): void {
  try {
    localStorage.setItem(CONNECTED_STORE_KEY, JSON.stringify(map));
  } catch {
    /* best effort */
  }
}

function buildConfig(provider: Record<string, unknown>, name: string): Record<string, string> {
  const cfg: Record<string, string> = { model: String((provider.model as string) ?? "") };
  if (!isKeyless(name)) cfg.api_key = String((provider.api_key as string) ?? "");
  const baseUrl = provider.base_url;
  if (typeof baseUrl === "string") cfg.base_url = baseUrl;
  return cfg;
}

function isKeyless(name: string): boolean {
  return keylessProviders.has(name);
}

export function useProviderTest() {
  const providersTests = ref<Record<string, TestState>>({});
  const connectedMap = ref<Record<string, { ok: boolean; at: string }>>(loadConnectedStore());

  function isConnected(name: string): boolean {
    return Boolean(connectedMap.value[name]?.ok);
  }

  function testStatus(name: string): TestState {
    return providersTests.value[name] ?? { running: false, result: null };
  }

  function markConnected(name: string): void {
    connectedMap.value = { ...connectedMap.value, [name]: { ok: true, at: new Date().toISOString() } };
    persistConnectedStore(connectedMap.value);
  }

  async function testProvider(name: string, provider: Record<string, unknown> | undefined): Promise<void> {
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
