# DeepEye Scanner Suite — Project Plan

> **Goal**: Web GUI wrapper over [deep-eye](https://github.com/zakirkun/deep-eye) vulnerability scanner. Deployable, futuristic UI, all CLI features exposed via phased delivery.

---

## 1. Stack Decision

| Layer | Technology | Verified Reason |
|---|---|---|
| Engine | `deep-eye` v1.4.0 as **git submodule** at `scanner/deep-eye/` (unmodified) | Upstream sync via `git submodule update --remote`; no fork maintenance |
| Backend | **FastAPI** (Python, same runtime as deep-eye) | Direct subprocess to `deep_eye.py`; no language-bridge indirection |
| Frontend | **Vue 3 + Vite + Tailwind CSS + Pinia** | User preference; pnpm 11.5.2 verified locally |
| Charts | **ApexCharts** via `@apexcharts` MCP subagent | Severity distribution, scan trends, history |
| Design | **Open Design MCP** via `@open-design` subagent | Futuristic dark theme mockups + design system |
| Package mgr | **pnpm** (11.5.2 installed locally) | User specified `pnpm run dev` |
| Local dev | `pnpm dev` (Vite proxy → FastAPI :8000) + `uv run uvicorn` | No Docker needed for local development |
| Deploy | `docker-compose.yml` (compose up on server) | User confirmed |
| Local test target | **OWASP Juice Shop via `npx juice-shop`** | No Docker needed; runs on Node 22 |
| Python | uv venv, 3.12 fallback if 3.14 has C-ext wheel issues | `uv python install 3.12` available |
| Config secrets | EnvSitter for `.env` management | API keys never sent to browser |

### Why FastAPI + Vue (not Laravel)

deep-eye is Python. Laravel (PHP) cannot import the engine — requires subprocess + output parsing (fragile, hard to maintain). FastAPI runs in the same Python runtime, shares venv, launches deep_eye.py directly. Vue satisfies the frontend preference. Single runtime = easiest integration + easiest to maintain.

---

## 2. Custom OpenAI-Compatible Provider (Verified)

**Source verified**: `ai_providers/openai_provider.py` line:
```python
self.base_url = (self.config.get("base_url") or "").strip() or None
# ...
if self.base_url:
    kwargs["base_url"] = self.base_url
self.client = OpenAI(**kwargs)
```

The `openai` provider reads `base_url` from config and passes it to the OpenAI SDK client constructor. This means **any OpenAI-compatible API** (Azure, local LLM, third-party proxy) can be configured natively.

### Settings UI form fields for providers:
- **Provider selector** (dropdown): OpenAI, Claude, Grok, Gemini, Ollama, OpenRouter, Groq, Mistral, LiteLLM, LM Studio, OrcaRouter, Requesty, **+ Custom**
- **Standard providers**: api_key + model (base_url pre-filled from config defaults)
- **Custom mode**: base_url + api_key + model name → written to `ai_providers.openai.{base_url, api_key, model}` in `config/config.yaml`
- API keys stored **server-side only** (`.env` via EnvSitter); UI shows `sk-••••` masked status

---

## 3. Repo Structure

```
DeepEye-scanner-suite/
├── scanner/
│   └── deep-eye/              # git submodule (upstream, read-only)
│       ├── deep_eye.py          # CLI entrypoint
│       ├── config/
│       │   └── config.example.yaml
│       ├── core/
│       ├── ai_providers/
│       ├── modules/
│       ├── utils/
│       ├── templates/
│       ├── scripts/
│       └── requirements.txt
├── api/                        # FastAPI bridge
│   ├── main.py
│   ├── routers/
│   │   ├── scans.py            # CRUD + SSE stream + start/stop
│   │   ├── config.py            # read/write config.yaml
│   │   ├── reports.py            # serve report files
│   │   └── providers.py          # status + test API keys
│   ├── services/
│   │   ├── engine_runner.py     # subprocess + stdout parse + ANSI strip
│   │   ├── config_service.py    # yaml read/write, key masking
│   │   └── report_store.py      # parse findings JSON → SQLite
│   └── database.py              # SQLite stdlib (jobs table)
├── web/                        # Vue 3 SPA
│   ├── src/
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── NewScan.vue
│   │   │   ├── ScanLive.vue      # terminal-style console
│   │   │   ├── Findings.vue
│   │   │   ├── Reports.vue
│   │   │   └── Settings.vue
│   │   ├── components/
│   │   ├── stores/               # Pinia
│   │   ├── api/                 # API client
│   │   └── design/              # Open Design MCP output
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml           # deploy target
├── scripts/
│   └── dev.sh                   # one cmd: venv + api + web
├── plans/
│   ├── PLAN.md                  # this file
│   └── SPEC.md                  # technical specification
└── README.md
```

---

## 4. API Surface

```
POST   /api/scans                     # body: {target_url, scope_nl?, checks[], threads, depth, formats[]}
GET    /api/scans                      # list all scans
GET    /api/scans/{id}                 # detail + findings summary
POST   /api/scans/{id}/start            # launch deep_eye.py subprocess
POST   /api/scans/{id}/stop             # kill subprocess
GET    /api/scans/{id}/stream           # SSE: stdout lines (ANSI stripped)
GET    /api/scans/{id}/findings         # parsed vulnerabilities from report JSON
GET    /api/reports?scan_id={id}        # list report artifacts for scan
GET    /api/reports/{filename}          # download report file
GET    /api/config                       # read config.yaml (api_key values masked)
PUT    /api/config                       # write config.yaml
GET    /api/providers/status             # which providers enabled + reachable
POST   /api/providers/test/{name}        # quick API key validation call
POST   /api/maintenance/update-cve        # trigger scripts/update_cve_database.py
POST   /api/maintenance/build-rag         # trigger scripts/build_cve_rag_index.py
```

### Job store schema (SQLite, stdlib)

```sql
CREATE TABLE jobs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    target      TEXT NOT NULL,
    args_json   TEXT NOT NULL,        -- full CLI arg dict
    status      TEXT NOT NULL,        -- pending|running|completed|failed|stopped
    pid         INTEGER,
    report_path TEXT,
    started_at  TEXT,
    ended_at    TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
```

---

## 5. Data Flow

```
Vue SPA ⇄ FastAPI ⇄ subprocess `python deep_eye.py -u URL -c config.yaml` (cwd: scanner/deep-eye)
├─ SSE stream: live stdout → strip ANSI → emit to browser EventSource
├─ config/config.yaml: written by Settings UI (API keys server-side only)
└─ reports/: artifacts (HTML/PDF/JSON/SARIF/JUnit/CSV/XLSX) served + findings JSON indexed to SQLite
```

---

## 6. Execution Phases

### Phase 0 — Foundation & Python Verification

**Tasks:**
1. `git init` in `DeepEye-scanner-suite/`
2. `git submodule add https://github.com/zakirkun/deep-eye scanner/deep-eye`
3. `uv venv` → `uv pip install -r scanner/deep-eye/requirements.txt` (try Python 3.14 first; fallback `uv python install 3.12`)
4. `cp scanner/deep-eye/config/config.example.yaml scanner/deep-eye/config/config.yaml`
5. Verify: `cd scanner/deep-eye && python deep_eye.py --help` runs clean

**Acceptance criteria:**
- `deep_eye.py --help` outputs without error
- venv created and requirements installed
- config.yaml copied from example

---

### Phase 1 — FastAPI Bridge

**Tasks:**
1. Scaffold FastAPI app (`api/main.py`) + uvicorn runner
2. `engine_runner.py`: `subprocess.Popen(["python", "deep_eye.py", ...args], cwd=scanner/deep-eye)`, capture stdout line-by-line, strip ANSI via `re.sub(r'\x1b\[[0-9;]*m', '', line)`, emit to async queue
3. SSE endpoint `/api/scans/{id}/stream` via `StreamingResponse` (no extra dep — `sse-starlette` optional)
4. SQLite job store via `sqlite3` stdlib
5. `config_service.py`: read/write `config.yaml` via `pyyaml` (already a deep-eye dep), mask `api_key` values on GET
6. Serve `reports/` as static files via `StaticFiles`
7. `report_store.py`: parse report JSON → extract `vulnerabilities` list → index in SQLite

**Acceptance criteria:**
- `curl POST /api/scans` creates job
- `curl POST /api/scans/{id}/start` launches subprocess
- `curl GET /api/scans/{id}/stream` receives SSE log lines
- `curl POST /api/scans/{id}/stop` kills process
- Report file downloadable via `/api/reports/{filename}`

---

### Phase 2 — UI via Open Design MCP

**Tasks:**
1. Call `@open-design` subagent for:
   - Design system spec: dark futuristic theme (navy/black background, neon cyan/green accents, glassmorphism cards, monospace terminal font)
   - Mockups for each screen: Dashboard, New Scan Wizard, Live Scan Console, Findings Table, Report Viewer, Settings
2. Implement Vue 3 views per design output
3. ApexCharts dashboard:
   - Severity distribution (donut: critical/high/medium/low/info)
   - Scan history timeline (bar chart)
   - URLs crawled per scan
4. Terminal console component: `<pre>` + auto-scroll for SSE log stream
5. Settings page: provider form with Custom OpenAI-compatible (base_url + api_key + model)

**Screens:**
| Screen | Purpose |
|---|---|
| Dashboard | Overview: total scans, findings by severity (ApexCharts), recent scans list |
| New Scan | Wizard: target URL, scope-nl, enabled checks (60+ toggles), threads/depth, formats, authorization checkbox |
| ScanLive | Real-time terminal console (SSE), progress, stop button |
| Findings | Table: severity filter, type filter, search; expandable rows for evidence/remediation |
| Reports | List artifacts per scan, download buttons (html/pdf/json/sarif/junit/csv/xlsx) |
| Settings | AI provider config (incl. Custom), scanner settings, notifications, proxy, compliance |

**Acceptance criteria:**
- Full flow works in browser: input target → start scan → live log → findings appear → download report → configure provider keys
- Design matches Open Design MCP output
- Responsive layout

---

### Phase 3 — CLI Parity (All Features, Phased)

Expose every deep-eye CLI feature through the UI:

| Feature Group | UI Surface |
|---|---|
| Diff & retest | "Compare Scans" page: select two scans → diff view (html/json/csv) |
| Format selector | Report download dropdown: html, pdf, json, sarif, junit, csv, xlsx |
| Notifications | Settings: email (from/to), Slack (webhook+channel), Discord (webhook) |
| Auth macros | Settings: login macro upload/config, multi-role session store |
| Proxy toggle | Settings: mitmproxy/mitmweb toggle, proxy URL |
| CVE DB maintenance | Settings: "Update CVE DB" + "Build RAG Index" buttons → trigger scripts |
| Subdomain/recon toggles | New Scan wizard: enable_recon, full_scan, quick_scan, scan_subdomains |
| OpenAPI ingest | New Scan: upload OpenAPI spec → seed crawl targets |
| Scope-nl | New Scan: natural language scope input field |
| Compliance toggle | Settings: enable, select frameworks (PCI-DSS, SOC2, ISO 27001) |
| Templates browser | Settings: list YAML templates, tag filters |
| Login replay | Settings: macro_path, abort_on_fail, recheck_interval |
| Secrets scanner | New Scan: toggle, pattern selection |
| Rate limiting | Settings: requests_per_second, burst_size, delay_on_error |
| TLS evasion | Settings: impersonate (chrome120 etc.) |
| Advanced rendering | Settings: enable_javascript_rendering, screenshot, browser_use_ai |
| AI triage | Settings: enable, drop_false_positives, drop_threshold, min_severity |
| Bug bounty | Settings: format (hackerone/bugcrowd/generic), output_directory |

**Acceptance criteria:**
- Every config.yaml section has corresponding UI
- Every CLI flag has corresponding UI control
- Scan wizard can reproduce any CLI invocation

---

### Phase 4 — Deploy Hardening

**Tasks:**
1. `docker-compose.yml`:
   - `api` service: Python + uvicorn, mounts scanner/ + reports/ + data/
   - `web` service: Vue built static files served by nginx (or built into api)
   - Optional `chromium` service for Playwright (lazy start)
   - Volume mounts: `scanner/deep-eye/data/`, `scanner/deep-eye/reports/`, `scanner/deep-eye/logs/`
2. Auth: token-based (local-first), configurable via `.env`
3. HTTPS: Caddy or Traefik reverse proxy notes in README
4. Data persistence: named volumes for SQLite + reports + auth sessions
5. Health check endpoint: `GET /api/health`

**Acceptance criteria:**
- `docker compose up` → full app accessible at `localhost`
- Reports and data persist across container restarts
- Auth token required for API access

---

## 7. Local Dev Workflow (No Docker)

```bash
# Terminal 1: test target (no Docker needed)
npx juice-shop   # → localhost:3000

# Terminal 2: backend
cd api && uv run uvicorn main:app --reload --port 8000

# Terminal 3: frontend
cd web && pnpm install && pnpm dev   # Vite proxy → localhost:8000
```

Or single command:
```bash
./scripts/dev.sh   # starts all three
```

---

## 8. Risk Mitigations

| Risk | Mitigation |
|---|---|
| Python 3.14 C-ext wheel missing (numpy, pandas, scikit-learn) | `uv python install 3.12` fallback; test in Phase 0 |
| CLI stdout has ANSI/rich colors | `re.sub(r'\x1b\[[0-9;]*m', '', line)` in engine_runner |
| Scan killed mid-run (process orphaned) | Track PID in SQLite; `POST /stop` sends SIGTERM then SIGKILL |
| API key leak | Keys server-side `.env` only (EnvSitter); UI shows `sk-••••` masked; config GET masks values |
| Playwright heavy in deploy | Separate optional service in docker-compose; lazy chromium download |
| Legal liability | Authorization checkbox + disclaimer banner in New Scan wizard |
| Upstream deep-eye breaking changes | Submodule pinned to commit; update deliberately with tests |
| Long-running scan blocks event loop | Subprocess in thread pool; SSE uses async generator |

---

## 9. Testing Strategy

| Level | Tool | Target |
|---|---|---|
| Engine smoke | manual | `deep_eye.py --help` + scan against `npx juice-shop` |
| API | pytest + httpx | All endpoints; mock subprocess for unit, real juice-shop for integration |
| Frontend | Vitest (light) | API client, stores, key components |
| E2E | manual | Full browser flow: scan → log → findings → report |

---

## 10. Open Design MCP Usage Plan

1. **Design system**: dark futuristic theme spec — color palette (navy `#0a0e1a`, neon cyan `#00f0ff`, neon green `#00ff88`, warning amber `#ffaa00`, danger red `#ff3366`), typography (Inter for UI, JetBrains Mono for terminal), glassmorphism card spec, spacing scale
2. **Mockups per screen**: Dashboard, New Scan Wizard, ScanLive Console, Findings Table, Reports, Settings (provider form)
3. **Component library**: buttons, inputs, cards, badges (severity), terminal component, chart containers
4. **Export**: design tokens as CSS variables → `web/src/assets/design-tokens.css`; mockup images → `web/design/`

---

## 11. Milestone Summary

| Phase | Deliverable | Exit Criteria |
|---|---|---|
| 0 | Repo + submodule + venv + CLI verified | `--help` runs clean |
| 1 | FastAPI bridge + SSE + config + reports | curl full scan lifecycle works |
| 2 | Vue UI with all core screens | Browser end-to-end flow works |
| 3 | All CLI features exposed in UI | Every config section has UI |
| 4 | Docker deploy + auth + persistence | `docker compose up` serves app |

---

## 12. Constraints & Rules

- **Zero assumption**: every technical claim verified from source or environment
- **deep-eye unmodified**: submodule, never edit upstream files
- **API keys never reach browser**: server-side `.env` only
- **English UI** (user decision)
- **All features, phased delivery** (user decision)
- **pnpm** as package manager (user decision)
- **docker-compose** for deployment (user decision)
- **No new dependencies** unless stdlib or already-installed package solves it
- **Shortest diff wins**: minimum code that works
