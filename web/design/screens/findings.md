# Screen: Findings Table

> Route: `/scan/:id/findings` | Data: `GET /api/scans/{id}/findings` | Filterable, sortable, expandable

---

## Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│ TOPBAR: Findings — Scan #42                                      [⚙]     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─ Summary Bar ────────────────────────────────────────────────────────┐│
│  │ [CRITICAL: 3] [HIGH: 5] [MEDIUM: 12] [LOW: 8] [INFO: 2]   Total: 30  ││
│  │ URLs crawled: 50   •   Duration: 8m 45s   •   [View Reports →]      ││
│  └──────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ Filter Toolbar ─────────────────────────────────────────────────────┐│
│  │ [🔍 Search findings...]  [Severity ▾] [Type ▾] [FP only ☐]  [Export] ││
│  └──────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─ Findings Table ────────────────────────────────────────────────────┐│
│  │ SEV    TYPE            URL                  PARAMETER    [v]         ││
│  ├──────────────────────────────────────────────────────────────────────┤│
│  │ ●CRIT  sql_injection   /login               user         [v]        ││
│  │  └─ expanded detail ───────────────────────────────────────────────┘ ││
│  │ ●HIGH  xss              /search              q            [v]         ││
│  │ ●HIGH  ssrf             /api/fetch           url          [v]         ││
│  │ ●MED   csrf             /change-password     —            [v]         ││
│  │ ●MED   open_redirect    /redirect            next         [v]         ││
│  │ ●LOW   info_disclosure  /.git/config         —            [v]         ││
│  │ ●INFO  cors_misconfig   /api/*               —            [v]         ││
│  └──────────────────────────────────────────────────────────────────────┘│
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Component Composition

### 1. Summary Bar

Glass card, `padding: 12px 16px`, single row.

```
[●CRIT: 3] [●HIGH: 5] [●MED: 12] [●LOW: 8] [●INFO: 2]    Total: 30
URLs crawled: 50  •  Duration: 8m 45s  •  [View Reports →]
```

- Severity mini-badges: clickable filters. Clicking `CRIT: 3` sets severity filter to `critical`.
- Each badge: severity-colored dot + count, `font-mono` for count
- Active filter badge: highlighted border (`border-strong`)
- Total: `14px` semibold, primary
- Meta: `13px` secondary, `font-mono` for values
- "View Reports" link: accent-primary, navigates to `/scan/:id/reports`

**Data:** `severity_counts` from `GET /api/scans/{id}/findings` response.

### 2. Filter Toolbar

Glass card, `height: 48px`, `padding: 0 12px`.

| Element | Width | Type |
|---|---|---|
| Search | `240px` (expands on focus to `320px`) | text input, searches type/url/parameter |
| Severity | `auto` (min 120px) | dropdown: All, Critical, High, Medium, Low, Info |
| Type | `auto` (min 140px) | dropdown: All + all unique finding types |
| FP Only | `auto` | checkbox: show false positives only |
| Export | `auto` | dropdown: CSV, JSON, SARIF |

- Search: `font-mono`, placeholder `Search findings...`
- Dropdowns: use `.de-select` styling, glass dropdown panel
- Export: triggers `GET /api/reports/{filename}` or client-side export from current filtered data

### 3. Findings Table

Full table spec in `components.md` §7. Columns:

| Column | Width | Content | Sortable |
|---|---|---|---|
| Severity | `80px` | severity badge (CRIT/HIGH/MED/LOW/INFO) | Yes |
| Type | `160px` | finding type in `font-mono` (e.g., `sql_injection`) | Yes |
| URL | `flex: 2` | URL path, `font-mono`, truncated | Yes |
| Parameter | `120px` | parameter name or `—`, `font-mono` | No |
| Expand | `40px` | chevron icon, rotates 90° when expanded | No |

Row height: `44px` (default). Expanded row: detail panel below, `background: var(--de-bg-tertiary)`.

### 4. Expanded Detail Panel

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ●CRIT  sql_injection   /login               user         [∧]            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  EVIDENCE                                                                │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │ HTTP Request:                                                    │    │
│  │ POST /login HTTP/1.1                                             │    │
│  │ user=admin' OR '1'='1'--&pass=test                              │    │
│  │                                                                  │    │
│  │ Response: 200 OK (auth bypassed)                                │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌──────────────────────────┐  ┌──────────────────────────────────┐   │
│  │ REMEDIATION               │  │ AI EVIDENCE SUMMARY              │   │
│  │ Use parameterized         │  │ The AI analyzed this finding     │   │
│  │ queries / prepared        │  │ and confirms high likelihood of   │   │
│  │ statements. Never          │  │ SQL injection. The payload       │   │
│  │ concatenate user input     │  │ bypassed authentication via      │   │
│  │ into SQL. Use ORM or        │  │ boolean-based injection.         │   │
│  │ parameterized queries.     │  │ Confidence: 94%                 │   │
│  └──────────────────────────┘  └──────────────────────────────────┘   │
│                                                                          │
│  CVE REFERENCES                                              [FP Toggle] │
│  [CVE-2021-44228] [CVE-2019-11043]                                      │
│                                                                          │
│  Fingerprint: a1b2c3d4...                                                │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

Expanded panel layout: `padding: 16px`, internal sections with `12px` gap.

#### Evidence Section

- Label: `EVIDENCE` (card title style — uppercase, secondary, `13px`)
- Content: `font-mono`, `11px`, `--de-text-secondary`, in code block
- Code block: `background: var(--de-bg-primary)`, `padding: 12px`, `border-radius: 4px`, `border: 1px solid var(--de-border-subtle)`
- Pre-wrapped, `white-space: pre-wrap`, `word-break: break-all`

#### Remediation Section

- Half-width column (`grid: 1fr 1fr` if AI summary exists, full-width otherwise)
- Label: `REMEDIATION`
- Content: `14px` regular, `--de-text-primary`, `line-height: 1.5`

#### AI Evidence Summary Section

- Half-width column (side by side with remediation)
- Label: `AI EVIDENCE SUMMARY`
- Content: `14px` regular, `--de-text-secondary`
- If `ai_evidence_summary` is null: show "AI summary not available" in tertiary text
- Confidence badge if present: badge style, accent-secondary

#### CVE References

- Label: `CVE REFERENCES`
- CVE IDs as clickable chips: `font-mono`, `11px`, info-blue border, link to NVD
- Each chip: `CVE-XXXX-XXXXX`, `padding: 2px 8px`, `border-radius: 4px`, hover = info border strong
- If `cve_references` is null/empty: "No CVE references" in tertiary

#### Fingerprint

- Label: `FINGERPRINT`
- Value: `font-mono`, `11px`, `--de-text-tertiary`, truncated with tooltip showing full hash
- If null: hidden

#### False Positive Toggle

- Right-aligned in CVE references row
- Toggle + label: `Mark as False Positive`
- When `true`: toggle on (accent-secondary), row gets strikethrough + opacity `0.5`, severity badge gets `FP` suffix
- Updates `finding.false_positive` — `PUT` to API or local state if no endpoint

---

## Data Shape (Finding)

```typescript
interface Finding {
  type: string;              // "sql_injection"
  severity: string;          // "critical" | "high" | "medium" | "low" | "info"
  url: string;
  parameter: string | null;
  payload: string | null;
  evidence: string;
  remediation: string;
  fingerprint: string | null;
  cve_references: string[] | null;
  ai_evidence_summary: string | null;
  false_positive: boolean | null;
}
```

From `GET /api/scans/{id}/findings`:
```json
{
  "vulnerabilities": [Finding, ...],
  "urls_crawled": 50,
  "duration": "8m 45s"
}
```

---

## Filtering & Sorting

### Client-Side Filters

```js
const filtered = findings
  .filter(f => !searchQuery || 
    f.type.includes(searchQuery) || 
    f.url.includes(searchQuery) || 
    (f.parameter?.includes(searchQuery)))
  .filter(f => severityFilter === 'all' || f.severity === severityFilter)
  .filter(f => typeFilter === 'all' || f.type === typeFilter)
  .filter(f => !fpOnly || f.false_positive === true);
```

### Sorting

- Severity: custom order `critical > high > medium > low > info`
- Type: alphabetical
- URL: alphabetical
- Sort direction toggles on column header click (asc → desc → none)

### Row Expansion

- Only one row expanded at a time (accordion behavior). Clicking another collapses the previous.
- Expanded state preserved across filter changes if row still visible.

---

## Empty States

| Condition | Message |
|---|---|
| No findings | "No vulnerabilities found. This scan came back clean." + success icon |
| No findings match filters | "No findings match your filters." + "Clear Filters" button |
| Scan still running | "Scan in progress. Findings will appear when the scan completes." + "View Live Console →" link |

---

## Responsive

| Width | Behavior |
|---|---|
| ≥1024px | Full table, all columns visible |
| 768–1023px | Hide Parameter column, keep Severity/Type/URL/Expand |
| <768px | Card list — each finding as a card with severity badge + type + URL, tap to expand |
