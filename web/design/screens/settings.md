# Screen: Settings

> Route: `/settings` | Data: `GET/PUT /api/config`, `GET /api/providers/status`, `POST /api/providers/test/{name}` | Full config surface

---

## Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│ TOPBAR: Settings                                                [⚙]     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [AI Providers] [Scanner] [Notifications] [Proxy] [Compliance] [Advanced] │
│  ───────────────────────────────────────────────────────────              │
│                                                                          │
│  ┌─ Tab Content ─────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │                     [active tab panel]                            │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

Tab navigation at top. Content area below. Tab order: AI Providers → Scanner → Notifications → Proxy → Compliance → Advanced → Maintenance.

---

## Tab 1: AI Providers

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  AI PROVIDER CONFIGURATION                                               │
│                                                                          │
│  ┌─ Provider Status Grid ──────────────────────────────────────────────┐│
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                ││
│  │ │ OpenAI   │ │ Claude   │ │ Grok     │ │ Gemini   │                ││
│  │ │ ● Reach  │ │ ✓ Config │ │ ✗ No key │ │ ✗ No key │                ││
│  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘                ││
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                ││
│  │ │ Ollama   │ │ OpenRtr  │ │ Groq     │ │ Mistral  │                ││
│  │ │ ○ Unreach│ │ ✓ Config │ │ ✗ No key │ │ ✗ No key │                ││
│  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘                ││
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                ││
│  │ │ LiteLLM  │ │ LM Studio│ │ OrcaRtr  │ │ Requesty │                ││
│  │ │ ✗ No key │ │ ○ Unreach│ │ ✗ No key │ │ ✗ No key │                ││
│  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘                ││
│  │ ┌──────────┐                                                          ││
│  │ │ + Custom │                                                          ││
│  │ └──────────┘                                                          ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ Provider Configuration ────────────────────────────────────────────┐│
│  │                                                                       ││
│  │  Provider *                                                            ││
│  │  ┌──────────────────────────────────────────────────────────────┐    ││
│  │  │ OpenAI                                              [▾]      │    ││
│  │  └──────────────────────────────────────────────────────────────┘    ││
│  │                                                                       ││
│  │  ┌──────────────────────────┐  ┌──────────────────────────────┐   ││
│  │  │ API Key                   │  │ Model                         │   ││
│  │  │ ┌──────────────────────┐ │  │ ┌──────────────────────────┐ │   ││
│  │  │ │ sk-•••••••••1234  [👁]│ │  │ │ gpt-4o                    │ │   ││
│  │  │ └──────────────────────┘ │  │ └──────────────────────────┘ │   ││
│  │  └──────────────────────────┘  └──────────────────────────────┘   ││
│  │                                                                       ││
│  │  ┌─ Custom only ──────────────────────────────────────────────────┐  ││
│  │  │ Base URL                                                        │  ││
│  │  │ ┌──────────────────────────────────────────────────────────┐  │  ││
│  │  │ │ https://your-api.com/v1                                    │  │  ││
│  │  │ └──────────────────────────────────────────────────────────┘  │  ││
│  │  └────────────────────────────────────────────────────────────────┘  ││
│  │                                                                       ││
│  │  Temperature              0.7                                         ││
│  │  ●═════════════●══════════════                                         ││
│  │  0.0          0.5          1.0          1.5          2.0             ││
│  │                                                                       ││
│  │  Max Tokens                Timeout (s)                                 ││
│  │  ┌──────────┐              ┌──────────┐                               ││
│  │  │ 2000     │              │ 60       │                               ││
│  │  └──────────┘              └──────────┘                               ││
│  │                                                                       ││
│  │  [Test Connection]                              [Save Provider]     ││
│  └───────────────────────────────────────────────────────────────────────┘│
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Provider Status Grid

- Layout: `grid-template-columns: repeat(auto-fill, minmax(140px, 1fr))`, gap `12px`
- Each card: glass sub-card, `padding: 12px`, `min-height: 80px`, centered content
- Provider name: `14px`, semibold, primary
- Status badge below: status-dot + text (`11px`)

| Status | Dot | Text Color | Meaning |
|---|---|---|---|
| Reachable | filled green, pulsing | accent-secondary | Configured + API responded |
| Configured | checkmark | accent-secondary | API key set, not tested |
| Missing key | warning | warning | No API key configured |
| Unreachable | hollow red | danger | Test failed / connection error |
| Disabled | hollow gray | tertiary | `enabled: false` in config |

Click a card to select it → loads into Provider Configuration form below.

**+ Custom** card: dashed border, accent-primary text, `font-mono`. Clicking creates a custom provider config (writes to `ai_providers.openai` with custom `base_url`).

### Provider Configuration Form

| Field | Type | Validation | Config Mapping |
|---|---|---|---|
| Provider | dropdown | Required | `scanner.ai_provider` |
| API Key | password input + toggle | Optional (Ollama/LM Studio use base_url only) | `ai_providers.{name}.api_key` → `.env` (server-side) |
| Model | text input | Required | `ai_providers.{name}.model` |
| Base URL | text input | Only visible in Custom mode | `ai_providers.{name}.base_url` |
| Temperature | slider 0.0–2.0 | Step 0.1 | `ai_providers.{name}.temperature` |
| Max Tokens | number input | 1–8192 | `ai_providers.{name}.max_tokens` |
| Timeout | number input | 1–300 (seconds) | `ai_providers.{name}.timeout` |

- API Key: `font-mono`, masked as `sk-••••••••1234` (last 4 visible), eye icon toggles reveal
- Base URL: only shown when provider = "Custom". Placeholder: `https://your-api.com/v1`
- Temperature: slider, value shown right in `font-mono`
- Test Connection: ghost/secondary button, sends `POST /api/providers/test/{name}`. Shows spinner during test. Result: success toast + status badge update, or error toast with message.
- Save: primary button, sends `PUT /api/config` with updated provider section. Success toast: "Provider saved".

### Provider List (13 total)

OpenAI, Claude, Grok, Gemini, Ollama, OpenRouter, Groq, Mistral, LiteLLM, LM Studio, OrcaRouter, Requesty, + Custom.

- Ollama & LM Studio: no API key field (use `base_url` only, defaults `http://localhost:11434` / `http://127.0.0.1:1234`)
- LiteLLM: no api_key/base_url in config (uses LiteLLM proxy defaults)
- Custom: writes to `ai_providers.openai` with `base_url` override (OpenAI-compatible)

---

## Tab 2: Scanner

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  SCANNER SETTINGS                                                        │
│                                                                          │
│  ┌─ Crawling ────────────────────────────────────────────────────────┐  │
│  │  Default Threads         5        Default Depth         2          │  │
│  │  Max URLs           1000         Scan URL Timeout     60s          │  │
│  │  User Agent     [Deep-Eye/1.0...]                                    │  │
│  │  [●] Follow Redirects   [●] Verify SSL   Max Retries: 3           │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ Scan Modes ──────────────────────────────────────────────────────┐  │
│  │  [○] Enable Recon    [○] Quick Scan    [●] Full Scan             │  │
│  │  [○] Passive Mode (read-only, no active payloads)                 │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ Custom Headers & Cookies ────────────────────────────────────────┐  │
│  │  Headers: [key: value] [key: value] [+ Add]                       │  │
│  │  Cookies: [name: value] [+ Add]                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ Payload Generation ──────────────────────────────────────────────┐  │
│  │  [●] Use AI for payload generation                                 │  │
│  │  [○] Context-aware payloads                                      │  │
│  │  [●] CVE database integration                                    │  │
│  │  [○] Custom wordlists                                            │  │
│  │  [○] Payload obfuscation (WAF bypass)                           │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ Testing Depth ────────────────────────────────────────────────────┐  │
│  │  [○] Thorough mode                                                │  │
│  │  Time-based detection delay: 5s                                    │  │
│  │  Blind injection attempts: 3                                       │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│                                                       [Save Scanner]   │
└──────────────────────────────────────────────────────────────────────────┘
```

### Fields

| Field | Type | Config Mapping |
|---|---|---|
| Default Threads | number (1–50) | `scanner.default_threads` |
| Default Depth | number (1–10) | `scanner.default_depth` |
| Max URLs | number | `scanner.max_urls` |
| Scan URL Timeout | number (seconds) | `scanner.scan_url_timeout` |
| User Agent | text input | `scanner.user_agent` |
| Follow Redirects | toggle | `scanner.follow_redirects` |
| Verify SSL | toggle | `scanner.verify_ssl` |
| Max Retries | number | `scanner.max_retries` |
| Enable Recon | toggle | `scanner.enable_recon` |
| Quick Scan | toggle (radio) | `scanner.quick_scan` |
| Full Scan | toggle (radio) | `scanner.full_scan` |
| Passive Mode | toggle | `passive_mode` |
| Custom Headers | key-value editor | `scanner.custom_headers` |
| Cookies | key-value editor | `scanner.cookies` |
| Use AI payloads | toggle | `payload_generation.use_ai` |
| Context-aware | toggle | `payload_generation.context_aware` |
| CVE database | toggle | `payload_generation.cve_database` |
| Custom wordlists | toggle | `payload_generation.custom_wordlists` |
| Obfuscation | toggle | `payload_generation.use_payload_obfuscation` |
| Thorough mode | toggle | `vulnerability_scanner.testing.thorough_mode` |
| Time-based delay | number | `vulnerability_scanner.testing.time_based_detection_delay` |
| Blind injection attempts | number | `vulnerability_scanner.testing.blind_injection_attempts` |

Key-value editor: list of input pairs + remove button + add button. `font-mono` for values.

---

## Tab 3: Notifications

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  NOTIFICATION SETTINGS                                                  │
│                                                                          │
│  [●] Enable notifications                                              │
│  [●] Notify on critical findings                                        │
│                                                                          │
│  ┌─ Email ──────────────────────────────────────────────────────────────┐│
│  │  [○] Enable email notifications                                    ││
│  │  SMTP Server     [smtp.gmail.com]    Port    [587]                 ││
│  │  Username        [your@email.com]                                  ││
│  │  Password        [••••••••]                                        ││
│  │  From Address    [deep-eye@company.com]                           ││
│  │  To Addresses    [security@company.com] [+ Add]                    ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ Slack ─────────────────────────────────────────────────────────────┐│
│  │  [○] Enable Slack notifications                                    ││
│  │  Webhook URL    [https://hooks.slack.com/...]                     ││
│  │  Channel        [#security-alerts]                                   ││
│  │  Bot Name       [Deep Eye Scanner]                                 ││
│  │  Icon           [:shield:]                                           ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ Discord ───────────────────────────────────────────────────────────┐│
│  │  [○] Enable Discord notifications                                   ││
│  │  Webhook URL    [https://discord.com/api/webhooks/...]            ││
│  │  Bot Name       [Deep Eye Scanner]                                 ││
│  │  Avatar URL     [https://...]                                      ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│                                                   [Save Notifications]│
└──────────────────────────────────────────────────────────────────────────┘
```

### Fields

| Field | Config Mapping |
|---|---|
| Enable notifications | `notifications.enabled` |
| Notify on critical | `notifications.notify_on_critical` |
| Email enable | `notifications.email.enabled` |
| SMTP server/port | `notifications.email.smtp_server` / `smtp_port` |
| Email username/password | `notifications.email.username` / `password` → `.env` |
| From address | `notifications.email.from_address` |
| To addresses | `notifications.email.to_addresses` (list) |
| Slack enable | `notifications.slack.enabled` |
| Slack webhook | `notifications.slack.webhook_url` → `.env` |
| Slack channel | `notifications.slack.channel` |
| Slack username | `notifications.slack.username` |
| Slack emoji | `notifications.slack.icon_emoji` |
| Discord enable | `notifications.discord.enabled` |
| Discord webhook | `notifications.discord.webhook_url` → `.env` |
| Discord username | `notifications.discord.username` |
| Discord avatar | `notifications.discord.avatar_url` |

Passwords and webhook URLs are masked / stored server-side in `.env`. UI shows masked values.

---

## Tab 4: Proxy

```
┌──────────────────────────────────────────────────────────────────────────┐
│  PROXY SETTINGS                                                         │
│                                                                          │
│  [○] Enable intercepting proxy (mitmweb)                              │
│                                                                          │
│  ┌─ Proxy Configuration ──────────────────────────────────────────────┐│
│  │  Bind Host     [127.0.0.1]                                          ││
│  │  Proxy Port    [8080]        Web UI Port    [8081]                ││
│  │  Required      [○] Abort scan if mitmweb missing                  ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ Scanner Proxy ────────────────────────────────────────────────────┐│
│  │  [○] Enable HTTP proxy                                              ││
│  │  HTTP Proxy    [http://127.0.0.1:8080]                             ││
│  │  HTTPS Proxy   [http://127.0.0.1:8080]                             ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ TLS Evasion ──────────────────────────────────────────────────────┐│
│  │  [○] Enable TLS fingerprint evasion (curl_cffi)                   ││
│  │  Impersonate   [chrome120 ▾]                                       ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│                                                       [Save Proxy]     │
└──────────────────────────────────────────────────────────────────────────┘
```

### Fields

| Field | Config Mapping |
|---|---|
| Intercepting proxy enable | `intercepting_proxy.enabled` |
| Bind host | `intercepting_proxy.bind_host` |
| Proxy port | `intercepting_proxy.proxy_port` |
| Web UI port | `intercepting_proxy.mitmweb_port` |
| Required | `intercepting_proxy.required` |
| HTTP proxy enable | `proxy.enabled` |
| HTTP proxy URL | `proxy.http` / `scanner.proxy` |
| HTTPS proxy URL | `proxy.https` |
| TLS evasion | `tls_evasion.enabled` |
| Impersonate | `tls_evasion.impersonate` (dropdown: chrome120, firefox120, safari17, etc.) |

---

## Tab 5: Compliance

```
┌──────────────────────────────────────────────────────────────────────────┐
│  COMPLIANCE FRAMEWORKS                                                  │
│                                                                          │
│  [●] Enable compliance mapping                                         │
│                                                                          │
│  ┌─ Frameworks ───────────────────────────────────────────────────────┐│
│  │  [●] PCI-DSS (Payment Card Industry Data Security Standard)        ││
│  │  [●] SOC 2 (Service Organization Control 2)                       ││
│  │  [○] ISO 27001 (Information Security Management)                 ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│                                                       [Save Compliance]│
└──────────────────────────────────────────────────────────────────────────┘
```

| Field | Config Mapping |
|---|---|
| Enable compliance | `compliance.enabled` |
| PCI-DSS | `compliance.frameworks` (toggle in/out of array) |
| SOC 2 | `compliance.frameworks` |
| ISO 27001 | `compliance.frameworks` |

---

## Tab 6: Advanced

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ADVANCED SETTINGS                                                      │
│                                                                          │
│  ┌─ Browser Automation ────────────────────────────────────────────────┐│
│  │  [○] Enable JavaScript rendering (Playwright)                     ││
│  │  [○] Screenshot capture (base64)                                  ││
│  │  [○] Browser Use AI (experimental, requires OpenAI)              ││
│  │  Browser Timeout:     [120]s                                       ││
│  │  Page Timeout:        [10]s                                        ││
│  │  Navigation Timeout:  [10]s                                        ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ Stealth & Anti-Detection ─────────────────────────────────────────┐│
│  │  [○] User-Agent rotation                                          ││
│  │  Jitter min: [0.0]s    Jitter max: [0.0]s                         ││
│  │  Proxy Pool: [+] [http://proxy1:8080] [x]                        ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ URL Filtering ────────────────────────────────────────────────────┐│
│  │  Exclude Extensions: [.jpg] [.png] [.css] [.js] [+]              ││
│  │  Exclude Patterns: [+] [pattern] [x]                               ││
│  │  Max Response Size: [5242880] bytes (5MB)                        ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ AI Triage & FP Reduction ─────────────────────────────────────────┐│
│  │  [○] Enable AI auto-triage                                        ││
│  │  [○] Drop false positives (confidence ≥ threshold)               ││
│  │  Drop Threshold: [0.8]                                              ││
│  │  Min Severity: [high ▾]                                            ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ RAG (CVE Retrieval-Augmented Generation) ───────────────────────┐│
│  │  [○] Enable RAG                                                    ││
│  │  Index Path:    [data/cve_rag_index.pkl]                         ││
│  │  [○] Auto-rebuild index when CVE DB updates                      ││
│  │  Top K:         [5]        Min Score: [0.15]                    ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ Rate Limiting ────────────────────────────────────────────────────┐│
│  │  [●] Enable rate limiting                                          ││
│  │  Requests/sec: [10]   Burst: [20]   Delay on error: [2]s         ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ Logging ──────────────────────────────────────────────────────────┐│
│  │  Level: [INFO ▾]   [●] Log to file                                 ││
│  │  Log file: [logs/deep_eye.log]   Max size: [10]MB   Backups: [5]  ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ Database ─────────────────────────────────────────────────────────┐│
│  │  Type: SQLite    Path: [data/deep_eye.db]                         ││
│  │  Auto-cleanup after: [30] days                                    ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│                                                       [Save Advanced]   │
└──────────────────────────────────────────────────────────────────────────┘
```

### Fields

| Field | Config Mapping |
|---|---|
| JS rendering | `advanced.enable_javascript_rendering` |
| Screenshots | `advanced.screenshot_enabled` |
| Browser Use AI | `advanced.enable_browser_use_ai` |
| Browser timeout | `advanced.browser_timeout` |
| Page timeout | `advanced.browser_page_timeout` |
| Nav timeout | `advanced.browser_navigation_timeout` |
| UA rotation | `advanced.ua_rotation` |
| Jitter min/max | `advanced.jitter_min` / `jitter_max` |
| Proxy pool | `advanced.proxy_pool` (list editor) |
| Exclude extensions | `advanced.exclude_extensions` (tag editor) |
| Exclude patterns | `advanced.exclude_patterns` (list editor) |
| Max response size | `advanced.max_response_size` |
| AI triage enable | `ai_triage.enabled` |
| Drop FPs | `ai_triage.drop_false_positives` |
| Drop threshold | `ai_triage.drop_threshold` |
| Min severity | `ai_triage.min_severity` (dropdown: high, medium, low, critical) |
| RAG enable | `rag.enabled` |
| Index path | `rag.index_path` |
| Auto-rebuild | `rag.auto_rebuild` |
| Top K | `rag.top_k` |
| Min score | `rag.min_score` |
| Rate limiting enable | `rate_limiting.enabled` |
| Requests/sec | `rate_limiting.requests_per_second` |
| Burst size | `rate_limiting.burst_size` |
| Delay on error | `rate_limiting.delay_on_error` |
| Log level | `logging.level` (dropdown: DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| Log to file | `logging.log_to_file` |
| Log file | `logging.log_file` |
| Max file size | `logging.max_file_size` |
| Backup count | `logging.backup_count` |
| DB path | `database.path` |
| Auto-cleanup | `database.auto_cleanup_days` |

### Additional Sub-sections (collapsible)

- **Secrets Scanner**: `secrets_scanner.enabled`, pattern selection, entropy settings
- **Bug Bounty**: `bug_bounty.enabled`, format, min severity, output directory
- **CAPTCHA**: `captcha.enabled`, vendor selection
- **Login Replay**: `login_replay.enabled`, macro path, abort on fail, recheck interval
- **Templates**: `templates.enabled`, directories, tag filters
- **Challenge Solver**: `challenge_solver.enabled`, vendors, timeout
- **Experimental**: subdomain scanning, CVE matching, live lookup, mobile settings

Each sub-section is a collapsible glass card (accordion). Label in header, chevron to expand/collapse.

---

## Tab 7: Maintenance

```
┌──────────────────────────────────────────────────────────────────────────┐
│  MAINTENANCE & SYSTEM                                                    │
│                                                                          │
│  ┌─ CVE Database ──────────────────────────────────────────────────────┐│
│  │  Status: Last updated 2026-08-15    Entries: 241,847               ││
│  │  Path: data/cve_intelligence.db                                    ││
│  │  [Update CVE Database]    [Build RAG Index]                       ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ System Info ───────────────────────────────────────────────────────┐│
│  │  Engine: deep-eye v1.4.0 Hanzou                                   ││
│  │  API: FastAPI :8000                                               ││
│  │  Python: 3.12.x                                                    ││
│  │  SQLite: data/deep_eye.db (12.4 MB)                              ││
│  │  [GET /api/health]                                                 ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

| Button | Action | API |
|---|---|---|
| Update CVE Database | Runs `scripts/update_cve_database.py` async | `POST /api/maintenance/update-cve` |
| Build RAG Index | Runs `scripts/build_cve_rag_index.py` async | `POST /api/maintenance/build-rag` |

Both are async — return `{status, pid}`. Show progress in toast or inline status. Running state: button disabled + spinner + "Running..." text. Completion: success toast.

---

## Data Flow

```
GET /api/config → { config_yaml (masked) }
          ↓
   Populate all tabs from config
          ↓
User edits → PUT /api/config { config_yaml }
          ↓
   Success toast: "Settings saved"

GET /api/providers/status → [{ name, enabled, configured, reachable }]
          ↓
   Provider status grid

POST /api/providers/test/{name} → { success: bool, error? }
          ↓
   Update provider status badge
```

### Config Masking

- API keys: `sk-••••••••1234` (last 4 chars visible)
- Passwords (email SMTP, Slack webhooks): fully masked `••••••••`
- On `PUT /api/config`: if value is still masked (`sk-••••...`), backend preserves existing value. Only updates if value changed from masked state.

---

## Save Behavior

- Each tab has its own Save button (bottom-right of tab content)
- Save sends `PUT /api/config` with the full config object (merged with existing)
- Loading state: button shows spinner, disabled
- Success: toast "Settings saved", button returns to normal
- Error: toast "Failed to save: {error}", button returns to normal
- Unsaved changes warning: if user switches tabs with unsaved changes, show confirm dialog "You have unsaved changes. Discard?"

---

## Responsive

| Width | Behavior |
|---|---|
| ≥1024px | Tabs horizontal, 2-column form layouts |
| 768–1023px | Tabs horizontal, 1-column forms |
| <768px | Tabs become scrollable horizontal, forms stack |
