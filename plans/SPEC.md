# DeepEye Scanner Suite — Technical Specification

> **Purpose**: Inline spec to prevent scope creep. Every feature, endpoint, config field, and UI screen is defined here. If it's not in this spec, it doesn't get built.

---

## 1. Engine Interface (deep-eye CLI)

### 1.1 CLI Command

```bash
python deep_eye.py \
  -u <target_url> \
  -c <config_path> \
  [--formats html,pdf,json,sarif,junit,csv,xlsx] \
  [--scope-nl "<natural language scope>"] \
  [--diff <baseline.json> <current.json>] \
  [--diff-output <path>] \
  [--diff-format html|json|csv] \
  [--retest-new <baseline.json>] \
  [--setup] \
  [--setup-force] \
  [--no-banner] \
  [--version] \
  [-v]
```

### 1.2 Config Validation Rules (from source)

| Field | Constraint | Source |
|---|---|---|
| `target_url` | must start with `http://` or `https://` | `validate_config()` |
| `scanner.default_depth` | 1–10 | `validate_config()` |
| `scanner.default_threads` | 1–50 | `validate_config()` |
| `reporting.output_directory` | default `reports/`, relative to cwd | `ReportGenerator` |
| `reporting.output_filename` | empty string = auto timestamped | `ReportGenerator` |
| `reporting.default_format` | `html` | config.example.yaml |
| Config file missing | triggers interactive onboard wizard | `main()` |

### 1.3 Finding Data Shape

```python
{
    "type": str,              # e.g. "sql_injection", "xss", "ssrf"
    "severity": str,          # "critical" | "high" | "medium" | "low" | "info"
    "url": str,
    "parameter": str | None,
    "payload": str | None,
    "evidence": str,
    "remediation": str,
    "fingerprint": str | None,
    "cve_references": list | None,
    "ai_evidence_summary": str | None,
    "false_positive": bool | None,
}
```

### 1.4 Scan Result Shape

```python
results = {
    "vulnerabilities": [Finding, ...],
    "urls_crawled": int,
    "duration": str,
    # severity counts in summary panel
}
```

### 1.5 Report Output

- Directory: `reporting.output_directory` (default `reports/`)
- Path relative to **cwd** when `deep_eye.py` is executed
- Formats: `html`, `pdf`, `json`, `sarif`, `junit`, `csv`, `xlsx`
- Format resolution: CLI `--formats` > config `reporting.formats` > `reporting.default_format`

---

## 2. Config Schema (config.yaml)

Full schema from `config.example.yaml`. Every field below must have a UI surface in Phase 3.

### 2.1 AI Providers

```yaml
ai_providers:
  openai:
    enabled: bool
    api_key: str          # server-side only, masked in UI
    model: str            # default: gpt-4o
    base_url: str | null  # optional; OpenAI-compatible custom endpoint
    temperature: float     # default 0.7
    max_tokens: int        # default 2000
    timeout: float         # default 60
  claude:
    enabled: bool
    api_key: str
    model: str
    temperature: float
    max_tokens: int
    timeout: float
  # ... same shape for: grok, gemini, groq, mistral, openrouter, orcarouter, litellm, lmstudio
  ollama:
    enabled: bool
    base_url: str         # default http://localhost:11434
    model: str
    temperature: float
    max_tokens: int
    timeout: float
```

**Custom OpenAI-compatible provider**: use `ai_providers.openai` with custom `base_url` + `api_key` + `model`. Verified in `openai_provider.py`:
```python
self.base_url = (self.config.get("base_url") or "").strip() or None
if self.base_url:
    kwargs["base_url"] = self.base_url
self.client = OpenAI(**kwargs)
```

### 2.2 Scanner

```yaml
scanner:
  default_depth: int        # 1-10, default 2
  default_threads: int      # 1-50, default 5
  ai_provider: str           # which provider to use
  enable_recon: bool
  full_scan: bool
  quick_scan: bool
  proxy: str | null
  custom_headers: dict
  cookies: dict
```

### 2.3 Vulnerability Scanner

```yaml
vulnerability_scanner:
  enabled_checks:            # 60+ entries
    - sql_injection
    - xss
    - ssrf
    - jwt_deep
    - idor
    - graphql_deep
    - cors_csp
    - # ... (full list in config.example.yaml)
```

### 2.4 Payload Generation

```yaml
vulnerability_scanner:
  payload_generation:
    use_ai: bool
    context_aware: bool
    cve_database: bool
    custom_wordlists: bool
    use_payload_obfuscation: bool   # enable obfuscation for WAF bypass
```

### 2.4b Payload Obfuscation

```yaml
payload_obfuscation:
  enabled: bool
  techniques:
    - base64_encoding
    - url_encoding
    - unicode_encoding
    - hex_encoding
    - case_manipulation
    - comment_insertion
    - concatenation
    - null_byte_injection
    - double_encoding
    - character_substitution
  waf_bypass_mode: bool
```

### 2.5 Modules

```yaml
api_security: bool
business_logic: bool
authentication: bool
file_upload: bool
collaboration:
  data: bool
  sessions: bool
reconnaissance:
  enabled_modules: list
```

### 2.6 Reporting

```yaml
reporting:
  enabled: bool
  output_directory: str      # default "reports"
  output_filename: str       # "" = auto timestamped
  default_format: str        # "html"
  formats: list              # []
  dedupe: bool
```

### 2.7 Compliance

```yaml
compliance:
  enabled: bool
  frameworks:
    - pci_dss
    - soc2
    - iso_27001
```

### 2.8 RAG

```yaml
rag:
  enabled: bool
  index_path: str            # data/cve_rag_index.pkl
  auto_rebuild: bool
  top_k: int
  min_score: float
```

### 2.9 AI Triage

```yaml
ai_triage:
  enabled: bool
  drop_false_positives: bool
  drop_threshold: float      # 0.8
  min_severity: str          # "high"
```

### 2.10 Bug Bounty

```yaml
bug_bounty:
  format: str                 # hackerone | bugcrowd | generic
  output_directory: str       # reports/bounty
```

### 2.11 Captcha

```yaml
captcha:
  vendors:
    - recaptcha
    - hcaptcha
    - turnstile
    - generic
```

### 2.12 Login Replay

```yaml
login_replay:
  macro_path: str            # config/login_macro.json
  abort_on_fail: bool
  recheck_interval_seconds: int
```

### 2.13 Templates

```yaml
templates:
  template_directories:
    - templates
  tag_filters: list
```

### 2.14 TLS Evasion

```yaml
tls_evasion:
  impersonate: str           # e.g. "chrome120"
```

### 2.15 Logging

```yaml
logging:
  level: str                 # INFO
  log_file: str              # logs/deep_eye.log
```

### 2.16 Database

```yaml
database:
  enabled: bool
  type: str               # "sqlite"
  path: str               # data/deep_eye.db
  auto_cleanup_days: int   # 30
```

### 2.17 Rate Limiting

```yaml
rate_limiting:
  requests_per_second: int  # 10
  burst_size: int            # 20
  delay_on_error: int
```

### 2.18 Advanced

```yaml
advanced:
  enable_javascript_rendering: bool
  screenshot_enabled: bool
  enable_browser_use_ai: bool    # default false
  browser_timeout: int          # 120
  browser_page_timeout: int     # 10
  browser_navigation_timeout: int  # 10
```

### 2.19 Scope

```yaml
scope:
  excluded_paths:
    - /logout
    - /admin
  allowed_ports:
    - 80
    - 443
    - 8080
    - 8443
```

### 2.20 OAST

```yaml
oast:
  host: str                    # 0.0.0.0
  port: int                    # 9999
```

### 2.21 Passive Mode

```yaml
passive_mode: bool
```

### 2.22 Experimental

```yaml
experimental:
  enable_subdomain_scanning: bool
  aggressive_subdomain_enum: bool
  max_subdomains_to_scan: int   # 50
  enable_cve_matching: bool
  cve_database_path: str        # data/cve_intelligence.db
  auto_update_cve_db: bool
  cve_lookback_days: int        # 365
  cve_live_lookup: bool         # false; public NVD + GitHub live lookup
  nvd_api_key: str              # optional, higher rate limit
  github_token: str             # optional, for POC search
```

### 2.23 Notifications

```yaml
notifications:
  email:
    from_address: str
    to_addresses: list
  slack:
    webhook_url: str
    channel: str
  discord:
    webhook_url: str
```

### 2.24 Secrets Scanner

```yaml
secrets_scanner:
  enabled: bool
  scan_response_body: bool
  scan_response_headers: bool
  scan_javascript_files: bool
  check_git_exposure: bool
  enable_entropy_detection: bool   # detect high-entropy strings
  min_entropy: float               # 4.5 (0-8, higher = more random)
  min_length: int                  # 20
  enabled_patterns:                # specific pattern names (see config.example.yaml for full list)
    - aws_access_key
    - aws_secret_key
    - gcp_api_key
    - azure_storage_key
    - github_token
    - gitlab_token
    - slack_token
    - stripe_api_key
    - twilio_api_key
    - # ... (30+ patterns in config.example.yaml)
  severity_mapping: dict           # per-pattern severity override + default
  whitelist:
    emails: list
    domains: list
```

---

## 3. API Specification

### 3.1 Endpoints

| Method | Path | Body | Response | Notes |
|---|---|---|---|---|
| POST | `/api/scans` | `{target_url, scope_nl?, checks[], threads, depth, formats[], extra_flags?}` | `{id, status}` | Creates job record |
| GET | `/api/scans` | — | `[{id, target, status, created_at, severity_counts}]` | List all |
| GET | `/api/scans/{id}` | — | `{id, target, args, status, pid, report_path, started_at, ended_at, findings_summary}` | Detail |
| POST | `/api/scans/{id}/start` | — | `{status: "running", pid}` | Launches subprocess |
| POST | `/api/scans/{id}/stop` | — | `{status: "stopped"}` | SIGTERM → SIGKILL |
| GET | `/api/scans/{id}/stream` | — | SSE stream | `text/event-stream`; each event: `{type: "log"|"done"|"error", data: str}` |
| GET | `/api/scans/{id}/findings` | — | `{vulnerabilities: [Finding], urls_crawled, duration}` | Parsed from report JSON |
| GET | `/api/reports?scan_id={id}` | — | `[{filename, format, size, created_at}]` | List artifacts |
| GET | `/api/reports/{filename}` | — | file blob | Download |
| GET | `/api/config` | — | `{config_yaml, masked: true}` | api_key values replaced with `sk-••••` |
| PUT | `/api/config` | `{config_yaml}` | `{success: true}` | Write full config.yaml |
| GET | `/api/providers/status` | — | `[{name, enabled, configured, reachable}]` | Per provider |
| POST | `/api/providers/test/{name}` | — | `{success: bool, error?}` | **Phase 2 stub** — config-only check (api_key present = configured) |
| POST | `/api/maintenance/update-cve` | — | `{status, pid}` | Async trigger |
| POST | `/api/maintenance/build-rag` | — | `{status, pid}` | Async trigger |
| GET | `/api/health` | — | `{status: "ok"}` | Health check |

### 3.2 SSE Event Format

```
event: log
data: {"line": "[INFO] Starting scan...", "timestamp": "2026-08-20T10:00:00Z"}

event: done
data: {"exit_code": 0, "report_path": "reports/scan_20260820_100000.html"}

event: error
data: {"message": "Process killed", "exit_code": -15}
```

> **Note**: No `progress` event — deep-eye engine uses Rich console live display (in-place progress bars/spinners), not discrete stdout events. Parsing progress would require modifying the engine (out of scope §8). `done` event includes `report_path` (engine runner finds the new report file).

### 3.3 Engine Runner Specification

```
engine_runner.py:
  - build_cmd(job_args) → list[str]  # ["python", "deep_eye.py", "-u", url, "-c", config_path, ...]
  - Popen(cmd, cwd="scanner/deep-eye", stdout=PIPE, stderr=STDOUT, text=True, bufsize=1)
  - for line in process.stdout:
      clean = re.sub(r'\x1b\[[0-9;]*m', '', line.rstrip())  # strip ANSI
      yield (clean, datetime.utcnow().isoformat())
  - process.wait() → exit_code
  - on stop: process.send_signal(SIGTERM); timeout 5s; if still alive: SIGKILL
  - parse report JSON (if exists) → findings list → update SQLite
```

### 3.4 Config Service Specification

```
config_service.py:
  - read_config(path) → dict           # pyyaml safe_load
  - write_config(path, data: dict)      # pyyaml safe_dump, preserve comments via ruamel.yaml if needed
  - mask_config(data: dict) → dict     # replace api_key values with "sk-••••" (keep last 4 chars)
  - update_provider(name, fields)       # update single provider section
  - get_provider_status(name) → dict   # enabled? configured? reachable?
```

---

## 4. Frontend Specification

### 4.1 Design System (Open Design MCP)

| Token | Value |
|---|---|
| Background primary | `#0a0e1a` (deep navy/black) |
| Background secondary | `#121826` (panel) |
| Accent primary | `#00f0ff` (neon cyan) |
| Accent secondary | `#00ff88` (neon green) |
| Warning | `#ffaa00` (amber) |
| Danger | `#ff3366` (red) |
| Info | `#4a9eff` (blue) |
| Text primary | `#e0e6ed` |
| Text secondary | `#8b95a7` |
| Font UI | Inter |
| Font terminal | JetBrains Mono |
| Card style | glassmorphism: `backdrop-filter: blur(12px)`, `background: rgba(18, 24, 38, 0.7)`, `border: 1px solid rgba(0, 240, 255, 0.1)` |
| Border radius | `8px` (cards), `4px` (inputs) |
| Spacing scale | `4px | 8px | 12px | 16px | 24px | 32px | 48px` |

### 4.2 Views

| View | Route | Components | Data Source |
|---|---|---|---|
| Dashboard | `/` | SeverityDonut (ApexCharts), ScanHistoryBar, RecentScansList, StatCards | `GET /api/scans` |
| NewScan | `/scan/new` | TargetInput, ScopeNLInput, ChecksToggles (60+), ThreadsDepthSliders, FormatSelector, AuthorizationCheckbox, StartButton | `POST /api/scans` → `POST /api/scans/{id}/start` |
| ScanLive | `/scan/:id/live` | TerminalConsole (`<pre>` + auto-scroll), StopButton | `GET /api/scans/{id}/stream` (SSE) |
| Findings | `/scan/:id/findings` | FindingsTable, SeverityFilter, TypeFilter, SearchBar, FindingDetail (expandable) | `GET /api/scans/{id}/findings` |
| Reports | `/scan/:id/reports` | ReportList, DownloadButtons, FormatBadges | `GET /api/reports?scan_id=` |
| Settings | `/settings` | ProviderForms (incl. Custom), ScannerSettings, NotificationSettings, ProxyToggle, ComplianceToggle, AdvancedToggle, MaintenanceButtons | `GET/PUT /api/config`, `GET /api/providers/status` |

### 4.3 Terminal Console Component

```
<ScanLiveConsole>
  - <pre> element with overflow-y: auto
  - EventSource('/api/scans/{id}/stream')
  - onmessage: append line, auto-scroll to bottom
  - max lines: 10000 (trim oldest)
  - monospace font, color-coded by log level:
    [INFO] → cyan, [WARN] → amber, [ERROR] → red, [CRITICAL] → danger red bold
  - Stop button: POST /api/scans/{id}/stop, close EventSource
```

### 4.4 Settings Provider Form

```
<ProviderSettings>
  - Provider selector (dropdown): OpenAI, Claude, Grok, ..., + Custom
  - Standard fields: api_key (password input, masked), model (text)
  - Custom mode adds: base_url (text input, placeholder "https://your-api.com/v1")
  - "Save" → PUT /api/config with updated provider section
  - Status badge: ✓ Configured / ✗ Missing key
```

> **Phase 2 (descoped)**: temperature slider, max_tokens, timeout fields, "Test Connection" button, ● Reachable / ○ Unreachable badges. Current UI uses minimal form (api_key + model + base_url + enabled).

---

## 5. SQLite Schema

```sql
CREATE TABLE IF NOT EXISTS jobs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    target      TEXT NOT NULL,
    args_json   TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending',
    pid         INTEGER,
    report_path TEXT,
    started_at  TEXT,
    ended_at    TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS findings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id      INTEGER NOT NULL,
    type        TEXT,
    severity    TEXT,
    url         TEXT,
    parameter   TEXT,
    payload     TEXT,
    evidence    TEXT,
    remediation TEXT,
    fingerprint TEXT,
    cve_refs    TEXT,          -- JSON array stringified
    ai_summary  TEXT,
    false_positive INTEGER,   -- 0/1
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE INDEX IF NOT EXISTS idx_findings_job ON findings(job_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
```

---

## 6. Docker Compose Spec

> **Phase 2 (descoped)** — Docker deployment deferred. Use `scripts/dev.sh` for local development.

```yaml
# docker-compose.yml (structure, not final)
services:
  api:
    build: ./api
    ports: ["8000:8000"]
    volumes:
      - ./scanner:/app/scanner       # deep-eye submodule + data + reports
      - api-data:/app/data
    env_file: .env

  web:
    build: ./web
    ports: ["80:80"]
    depends_on: [api]

  chromium:              # optional, for Playwright
    image: browserless/chrome
    profiles: ["browser"]
    ports: ["3000:3000"]

volumes:
  api-data:
```

---

## 7. Dev Script Spec

```bash
#!/bin/bash
# scripts/dev.sh
# Starts: FastAPI backend + Vue frontend
# juice-shop is OPTIONAL — run 'npx juice-shop' in a separate terminal if needed

# 1. Backend
.venv/bin/python -m uvicorn api.main:app --reload --port 8000 &

# 2. Frontend
cd web && pnpm install && pnpm dev

# Trap cleanup
trap 'kill $(jobs -p)' EXIT
```

---

## 8. Scope Boundaries

### IN SCOPE
- Web UI wrapping deep-eye CLI
- FastAPI bridge with SSE streaming
- Vue 3 SPA with all screens
- Docker compose deployment
- Open Design MCP for UI mockups
- ApexCharts for dashboard
- Custom OpenAI-compatible provider support

### OUT OF SCOPE
- Modifying deep-eye source code (submodule stays unmodified)
- Writing new vulnerability checks (use deep-eye's existing 60+)
- Building a custom auth system (token-based, local-first, no OAuth)
- Mobile app (web only)
- Real-time collaboration / multi-user (single-user)
- Custom report formats (use deep-eye's 7 formats)
- Replacing deep-eye's AI providers (wrap, don't replace)
- Building a new scanning engine (wrap, don't rebuild)

### DELIBERATE SIMPLIFICATIONS
- SQLite stdlib (no SQLAlchemy ORM) — 2 tables, simple CRUD
- SSE via StreamingResponse (no WebSocket, no sse-starlette dep)
- Terminal console via `<pre>` (no xterm.js — 10000 line cap sufficient)
- No Vue router history mode (hash mode OK for SPA in Docker)
- No i18n (English only per user decision)
