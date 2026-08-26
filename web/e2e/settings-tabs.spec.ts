import { test, expect } from "@playwright/test";
import { stubApi } from "./api-stubs";

// A complete config document so every tab's panel renders its controls.
const fullConfig = {
  ai_providers: {
    openai: { enabled: true, api_key: "", model: "gpt-4o-mini", base_url: "" },
  },
  scanner: {
    default_depth: 2,
    default_threads: 5,
    ai_provider: "openai",
    proxy: "",
    enable_recon: false,
    full_scan: false,
    quick_scan: false,
  },
  notifications: {
    enabled: true,
    notify_on_critical: true,
    email: {
      enabled: false,
      smtp_server: "smtp.corp.local",
      smtp_port: 587,
      username: "",
      password: "",
      from_address: "",
      to_addresses: ["sec@corp.local"],
    },
    slack: { enabled: false, webhook_url: "", channel: "", username: "", icon_emoji: "" },
    discord: { enabled: false, webhook_url: "", username: "", avatar_url: "" },
  },
  intercepting_proxy: {
    enabled: false,
    bind_host: "127.0.0.1",
    proxy_port: 8080,
    mitmweb_port: 8081,
    required: false,
  },
  proxy: { enabled: false, http: "", https: "" },
  tls_evasion: { enabled: false, impersonate: "chrome120" },
  compliance: { enabled: true, frameworks: ["pci_dss"] },
  advanced: {
    enable_javascript_rendering: false,
    screenshot_enabled: false,
    enable_browser_use_ai: false,
    browser_timeout: 30,
    browser_page_timeout: 30,
    browser_navigation_timeout: 30,
    ua_rotation: false,
    jitter_min: 0,
    jitter_max: 0,
    proxy_pool: [],
    exclude_extensions: [".jpg"],
    exclude_patterns: ["/logout"],
    max_response_size: 1048576,
  },
  ai_triage: { enabled: false, drop_false_positives: false, drop_threshold: 0.8, min_severity: "low" },
  rag: { enabled: false, auto_rebuild: false, index_path: "", top_k: 5, min_score: 0.1 },
  rate_limiting: { enabled: false, requests_per_second: 10, burst_size: 20, delay_on_error: 0 },
  logging: { level: "INFO", log_file: "", log_to_file: false, max_file_size: 10485760, backup_count: 5 },
  database: { type: "sqlite", path: "", auto_cleanup_days: 30 },
  login_replay: { enabled: false, macro_path: "", recheck_interval_seconds: 600, abort_on_fail: true },
  bug_bounty: { format: "generic", output_directory: "" },
};

test.describe("settings tabs", () => {
  test("clicking through every tab shows that tab's panel", async ({ page }) => {
    await stubApi(page, {
      "GET /api/config": { config: fullConfig, masked: false },
      "GET /api/providers/status": [],
      "GET /api/templates": [
        { name: "Nginx LFI", path: "templates/nginx_lfi.yaml", tags: ["lfi", "nginx"] },
      ],
    });

    await page.goto("/#/settings");
    await expect(page.getByRole("heading", { name: "Settings" })).toBeVisible();

    // [tab button label, marker text unique to that tab's panel]
    const tabs: Array<[string, string]> = [
      ["providers", "API Key"],
      ["scanner", "Default Depth"],
      ["notifications", "Enable Notifications"],
      ["proxy", "Intercepting Proxy"],
      ["compliance", "Compliance Mapping"],
      ["advanced", "Browser Automation"],
      ["templates", "Scan Templates"],
      ["maintenance", "Update CVE Database"],
    ];

    for (const [tab, marker] of tabs) {
      await page.getByRole("button", { name: tab, exact: true }).click();
      await expect(page.getByText(marker).first()).toBeVisible();
      // Panels are v-if mounted: the previous tab's content must be gone.
      if (tab !== "providers") {
        await expect(page.getByText("API Key")).toHaveCount(0);
      }
    }

    // Templates are lazy-loaded on first visit — assert the stubbed template arrived.
    await page.getByRole("button", { name: "templates", exact: true }).click();
    await expect(page.getByText("Nginx LFI")).toBeVisible();
    await expect(page.getByText("1 templates")).toBeVisible();

    // Compliance framework from the stubbed config is reflected in the checkbox list.
    await page.getByRole("button", { name: "compliance", exact: true }).click();
    await expect(page.getByText(/PCI-DSS/)).toBeVisible();
  });
});
