// Shared API stubbing for E2E specs.
//
// Every spec installs a single catch-all route matching every "/api" request,
// so the suite runs with NO backend. Register this BEFORE interacting with
// the page. Handlers are keyed by "METHOD /api/path" (pathname only, query
// ignored).
import type { Page, Route } from "@playwright/test";

export type StubHandler =
  | unknown /* JSON payload to fulfill with */
  | ((route: Route) => Promise<void> | void);

export type StubMap = Record<string, StubHandler>;

export async function fulfillJson(route: Route, payload: unknown, status = 200): Promise<void> {
  await route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(payload),
  });
}

export async function stubApi(page: Page, stubs: StubMap = {}): Promise<void> {
  // Anchor on the pathname prefix. A naive "**/api/**" glob also matches app
  // modules that merely live under an "api" directory (e.g. Vite serving
  // /src/api/client.ts), which would poison module loading with JSON.
  await page.route(
    (url) => url.pathname === "/api" || url.pathname.startsWith("/api/"),
    async (route) => {
      const req = route.request();
      const pathname = new URL(req.url()).pathname;
      const key = `${req.method()} ${pathname}`;

      const handler = stubs[key];
      if (handler !== undefined) {
        if (typeof handler === "function") {
          await (handler as (r: Route) => Promise<void> | void)(route);
          return;
        }
        await fulfillJson(route, handler);
        return;
      }

      // Fallback: answer anything unmapped (incl. the SSE /stream endpoint)
      // with an empty JSON document so the SPA never hits the real backend.
      await fulfillJson(route, null);
    }
  );
}
