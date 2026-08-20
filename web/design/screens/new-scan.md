# Screen: New Scan Wizard

> Route: `/scan/new` | Data: `POST /api/scans` → `POST /api/scans/{id}/start` | Multi-step form

---

## Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│ TOPBAR: New Scan                                              [🔍] [⚙]   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ●─────●─────○─────○─────○                                               │
│  Target Checks Config Review Start                                       │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                                                                   │    │
│  │                    [STEP CONTENT]                                  │    │
│  │                                                                   │    │
│  │                                                                   │    │
│  │                                                                   │    │
│  │                                          [Back]  [Next →]        │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

Stepper at top. Step content in glass card below. Nav buttons bottom-right.

---

## Step 1: Target

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  TARGET CONFIGURATION                                             │
│                                                                   │
│  Target URL *                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ https://                                                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  Must start with http:// or https://                              │
│                                                                   │
│  Natural Language Scope                                           │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Only scan /api/* endpoints, skip /admin and /logout         │ │
│  │                                                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  Describe scan scope in plain English. Parsed by AI → scope rules.│
│                                                                   │
│  Authorization *                                                  │
│  ┌──┐ I have explicit authorization to scan this target.        │
│  │  │ Unauthorized scanning is illegal and against ToS.          │
│  └──┘                                                             │
│                                                                   │
│                                              [Back]  [Next →]    │
└──────────────────────────────────────────────────────────────────┘
```

### Fields

| Field | Type | Validation | Config Mapping |
|---|---|---|---|
| Target URL | text input | Required. Must match `^https?://` | `scanner.target_url` |
| Scope NL | textarea (2 rows) | Optional. Max 500 chars | `--scope-nl` CLI flag |
| Authorization | checkbox | Required (must check to proceed) | UI-only gate |

- Target URL: `font-mono` (URLs are code). Validation error below input: `Must start with http:// or https://` in danger color.
- Authorization checkbox: red border outline until checked. Helper text warns about legal implications.
- Next button disabled until target URL valid + authorization checked.

---

## Step 2: Vulnerability Checks

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  VULNERABILITY CHECKS                          [Select All] [Clear]│
│  34 of 71 selected                                               │
│                                                                   │
│  ┌─ Injection ──────────────────────┐ ┌─ SSRF & Path ────────────┐│
│  │ [●] SQL Injection               │ │ [●] SSRF                  ││
│  │ [●] XSS                          │ │ [●] SSRF Cloud            ││
│  │ [●] Stored XSS                  │ │ [●] Path Traversal       ││
│  │ [●] Command Injection            │ │ [●] LFI                   ││
│  │ [●] NoSQL Injection              │ │ [●] RFI                   ││
│  │ [●] LDAP Injection               │ │ [●] Open Redirect        ││
│  │ [●] XML Injection                │ │ [●] Open Redirect Deep   ││
│  │ [●] SSTI                         │ │                           ││
│  │ [●] SSTI Engines                 │ │                           ││
│  │ [●] CRLF Injection               │ │                           ││
│  │ [●] CRLF Header Inject Deep      │ │                           ││
│  │ [●] SSE Injection                │ │                           ││
│  └──────────────────────────────────┘ └───────────────────────────┘│
│                                                                   │
│  ┌─ Auth & Session ─────────────────┐ ┌─ Config & Exposure ──────┐│
│  │ [●] CSRF                         │ │ [●] Security Misconfig   ││
│  │ [●] Auth Bypass                   │ │ [●] Info Disclosure      ││
│  │ [●] Broken Auth                   │ │ [●] Sensitive Data Exp   ││
│  │ [●] JWT Vulnerabilities           │ │ [●] CORS Misconfig       ││
│  │ [●] JWT Deep                      │ │ [●] CORS/CSP             ││
│  │ [●] OAuth Testing                 │ │ [●] Cloud Misconfig      ││
│  │ [●] SAML Attacks                  │ │ [●] Email Injection      ││
│  └──────────────────────────────────┘ └───────────────────────────┘│
│  ... (more category groups)                                       │
│                                                                   │
│                                              [Back]  [Next →]    │
└──────────────────────────────────────────────────────────────────┘
```

### Check Categories (15 groups, 71 checks)

Grid: `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`, gap `12px`.

Each category is a sub-card:
- Glass background, `border-radius: 6px`, padding `12px`
- Header: category name (uppercase, `13px`, semibold, secondary) + count badge
- Toggles listed vertically inside, `8px` gap

**Toggle row:** toggle switch (40×22px) + label (`14px`, primary). Label uses `snake_case` display: `SQL Injection` (humanized from `sql_injection`).

| Category | Checks |
|---|---|
| **Injection** (12) | sql_injection, xss, stored_xss, command_injection, nosql_injection, ldap_injection, xml_injection, ssti, ssti_engines, crlf_injection, crlf_header_inject_deep, sse_injection |
| **SSRF & Path Traversal** (7) | ssrf, ssrf_cloud, path_traversal, lfi, rfi, open_redirect, open_redirect_deep |
| **Auth & Session** (7) | csrf, authentication_bypass, broken_authentication, jwt_vulnerabilities, jwt_deep, oauth_testing, saml_attacks |
| **Config & Exposure** (7) | security_misconfiguration, information_disclosure, sensitive_data_exposure, cors_misconfiguration, cors_csp, cloud_misconfig, email_injection |
| **XXE & Deserialization** (2) | xxe, insecure_deserialization |
| **HTTP Header Attacks** (5) | host_header_injection, host_header_deep, http_method_override, http_smuggling, h2_smuggle |
| **API & GraphQL** (5) | api_vulnerabilities, api_security, api_bola_deep, graphql_vulnerabilities, graphql_deep |
| **Business Logic** (3) | business_logic, race_condition, mass_assignment |
| **File & Webshell** (2) | file_upload, php_webshell |
| **WebSocket** (2) | websocket, websocket_deep |
| **Cache & Supply Chain** (3) | cache_poisoning, cache_deception, supply_chain_js |
| **Recon & Discovery** (4) | directory_bruteforce, port_scanner, subdomain_takeover, waf_fingerprint |
| **Mobile** (5) | frida_mobile, android_static, ios_plist, mobile_ssl_pinning, mobile_ai_chain |
| **Specialized** (3) | anomaly_detector, secret_scanning, log4shell |
| **Parameter Pollution** (1) | hpp_pollution |

### Controls

- **Select All**: toggles all 71 checks on
- **Clear**: toggles all off
- Selected count: live counter `34 of 71 selected` (accent-primary)
- Default state: all checks ON (matching `full_scan` behavior)
- Quick presets dropdown: "Quick Scan" (basic subset), "Full Scan" (all), "API Focus" (API/injection only), "Custom"

**Config mapping:** selected checks → `vulnerability_scanner.enabled_checks` array in POST body.

---

## Step 3: Configuration

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  SCAN CONFIGURATION                                                │
│                                                                   │
│  ┌─ Threads & Depth ────────────────────────────────────────────┐│
│  │                                                                ││
│  │  Threads                              5                       ││
│  │  ●════════════════●─────────────────────────                   ││
│  │  1                       25                        50          ││
│  │                                                                ││
│  │  Depth                                 2                       ││
│  │  ●══════●─────────────────────────                             ││
│  │  1              5               10                             ││
│  │                                                                ││
│  └────────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─ Scan Modes ──────────────────────────────────────────────────┐│
│  │  [○] Enable Reconnaissance (subdomain/DNS/WHOIS)              ││
│  │  [○] Quick Scan (basic tests only)                            ││
│  │  [●] Full Scan (all enabled checks)                           ││
│  │  [○] Passive Mode (no active payloads, read-only)            ││
│  └────────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─ Report Formats ──────────────────────────────────────────────┐│
│  │  [✓] HTML  [✓] JSON  [ ] PDF  [ ] SARIF  [ ] JUnit  [ ] CSV  [ ] XLSX ││
│  └────────────────────────────────────────────────────────────────┘│
│                                                                   │
│                                              [Back]  [Next →]    │
└──────────────────────────────────────────────────────────────────┘
```

### Fields

| Field | Type | Range/Values | Default | Config Mapping |
|---|---|---|---|---|
| Threads | slider | 1–50 | 5 | `scanner.default_threads` |
| Depth | slider | 1–10 | 2 | `scanner.default_depth` |
| Enable Recon | toggle | bool | false | `scanner.enable_recon` |
| Quick Scan | toggle (radio group with full) | bool | false | `scanner.quick_scan` |
| Full Scan | toggle (radio) | bool | true | `scanner.full_scan` |
| Passive Mode | toggle | bool | false | `passive_mode` |
| Report Formats | checkbox group | html, pdf, json, sarif, junit, csv, xlsx | [html, json] | `--formats` CLI flag |

- Threads/Depth: slider with neon thumb, value display right-aligned in `font-mono`
- Scan modes: radio group — mutually exclusive quick/full. Recon and passive are independent toggles.
- Report formats: checkbox chips. Each format has format badge color (see components.md §4).

---

## Step 4: Review

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  REVIEW & CONFIRM                                                │
│                                                                   │
│  Target:        https://example.com                              │
│  Scope:         Only scan /api/* endpoints                        │
│  Checks:        34 of 71 selected                                │
│  Threads:       5                                                 │
│  Depth:         2                                                 │
│  Modes:         Full Scan, Passive Mode                          │
│  Formats:       HTML, JSON                                        │
│  Authorization: ✓ Confirmed                                      │
│                                                                   │
│  ┌─ Estimated Impact ────────────────────────────────────────────┐│
│  │  ~50 URLs to crawl  •  ~8 min estimated  •  34 active checks  ││
│  └────────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ⚠ Ensure you have authorization. Unauthorized scanning           │
│    violates law and DeepEye ToS.                                   │
│                                                                   │
│                                    [Back]  [⚡ Start Scan]        │
└──────────────────────────────────────────────────────────────────┘
```

- Summary: read-only display of all selected options, `font-mono` for values
- Estimated impact: small glass sub-card with URL count estimate, time estimate, check count
- Warning banner: amber border, warning icon, `13px`
- Start button: primary, full-size, with lightning icon. Disabled if authorization not checked (re-validate).

---

## Step 5: Start (post-submit)

After `POST /api/scans` returns `{id, status}`:

1. Show success toast: "Scan created"
2. Immediately call `POST /api/scans/{id}/start`
3. On success: redirect to `/scan/:id/live` (ScanLive console)
4. On error: show error toast, stay on review step

---

## Data Flow

```
Step 1 → { target_url, scope_nl, authorized: true }
Step 2 → { checks: [enabled_checks] }
Step 3 → { threads, depth, modes, formats: [] }
Step 4 → review (no new data)
    ↓
POST /api/scans { target_url, scope_nl, checks, threads, depth, formats, extra_flags }
    → { id, status: "pending" }
POST /api/scans/{id}/start
    → { status: "running", pid }
    → redirect to /scan/{id}/live
```

### POST Body Shape

```json
{
  "target_url": "https://example.com",
  "scope_nl": "Only scan /api/* endpoints, skip /admin",
  "checks": ["sql_injection", "xss", "ssrf", "..."],
  "threads": 5,
  "depth": 2,
  "formats": ["html", "json"],
  "extra_flags": {
    "enable_recon": false,
    "quick_scan": false,
    "full_scan": true,
    "passive_mode": false
  }
}
```

---

## Validation Rules

| Field | Rule |
|---|---|
| Target URL | Required, must match `^https?://` |
| Scope NL | Max 500 chars |
| Authorization | Must be `true` to enable Start |
| Checks | At least 1 must be selected |
| Threads | Integer 1–50 |
| Depth | Integer 1–10 |
| Formats | At least 1 must be selected |

---

## Responsive

| Width | Layout |
|---|---|
| ≥1024px | Full wizard card, 2-column check grid |
| 768–1023px | Full card, 1-column checks |
| <768px | Full-width card, 1-column checks, stepper wraps |
