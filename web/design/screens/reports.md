# Screen: Report Viewer

> Route: `/scan/:id/reports` | Data: `GET /api/reports?scan_id={id}` | List + download + preview

---

## Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│ TOPBAR: Reports — Scan #42                                      [⚙]     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─ Report Artifacts ────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  ┌──────────────────────────────────────────────────────────────┐│  │
│  │  │ [HTML]  scan_20260820_100000.html        248 KB   [Download]  ││  │
│  │  │                              2026-08-20 10:00:00  [Preview →] ││  │
│  │  ├──────────────────────────────────────────────────────────────┤│  │
│  │  │ [JSON]  scan_20260820_100000.json         12 KB   [Download]  ││  │
│  │  │                              2026-08-20 10:00:00               ││  │
│  │  ├──────────────────────────────────────────────────────────────┤│  │
│  │  │ [SARIF] scan_20260820_100000.sarif        18 KB   [Download]  ││  │
│  │  │                              2026-08-20 10:00:00               ││  │
│  │  ├──────────────────────────────────────────────────────────────┤│  │
│  │  │ [JUNIT] scan_20260820_100000.junit.xml      8 KB   [Download]  ││  │
│  │  │                              2026-08-20 10:00:00               ││  │
│  │  ├──────────────────────────────────────────────────────────────┤│  │
│  │  │ [CSV]   scan_20260820_100000.csv          4 KB   [Download]   ││  │
│  │  │                              2026-08-20 10:00:00               ││  │
│  │  └──────────────────────────────────────────────────────────────┘│  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ HTML Preview ───────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  [iframe: sandboxed HTML report preview]                          │  │
│  │                                                                    │  │
│  │  ┌────────────────────────────────────────────────────────────┐   │  │
│  │  │ # Deep Eye Security Report                                  │   │  │
│  │  │                                                              │   │  │
│  │  │ ## Executive Summary                                         │   │  │
│  │  │ Target: https://example.com                                 │   │  │
│  │  │ Scan Date: 2026-08-20                                        │   │  │
│  │  │                                                              │   │  │
│  │  │ ## Vulnerability Summary                                     │   │  │
│  │  │ Critical: 3  High: 5  Medium: 12  Low: 8  Info: 2          │   │  │
│  │  │                                                              │   │  │
│  │  │ ## Findings                                                  │   │  │
│  │  │ ...                                                          │   │  │
│  │  └────────────────────────────────────────────────────────────┘   │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Component Composition

### 1. Report Artifacts List

Glass card container. Inside: stacked list of report files.

Each report row:

```
[FORMAT]  filename                    size    [Download]
                    date timestamp    [Preview →]
```

| Element | Style | Notes |
|---|---|---|
| Format badge | format badge (see components.md §4) | Left-aligned, `min-width: 56px` |
| Filename | `font-mono`, `14px`, primary | Full filename, truncates with tooltip if long |
| File size | `font-mono`, `13px`, secondary | e.g., `248 KB` |
| Timestamp | `13px`, tertiary | `2026-08-20 10:00:00` |
| Download button | secondary, small | icon (download) + text, `GET /api/reports/{filename}` |
| Preview button | ghost, small | icon (eye) + text, only for HTML format |

Row layout: `grid-template-columns: 64px 1fr auto auto`, `gap: 12px`, `align-items: center`, `padding: 12px 16px`, `border-bottom: 1px solid var(--de-border-separator)`.

Hover: `background: rgba(0, 240, 255, 0.02)`.

### Format Badge Colors

| Format | Badge Color | Visible? |
|---|---|---|
| HTML | `var(--de-color-info)` (blue) | Preview available |
| PDF | `var(--de-color-danger)` (red) | Download only |
| JSON | `var(--de-color-accent-secondary)` (green) | Download only |
| SARIF | `var(--de-color-accent-primary)` (cyan) | Download only |
| JUnit | `var(--de-color-warning)` (amber) | Download only |
| CSV | `var(--de-text-secondary)` (gray) | Download only |
| XLSX | `var(--de-severity-high)` (orange) | Download only |

Only HTML has inline preview. PDF preview could be a future enhancement (not in scope per SPEC.md).

### 2. Download Behavior

```js
async function downloadReport(filename) {
  const response = await fetch(`/api/reports/${filename}`);
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
```

- Download button: triggers file download via blob
- Success toast: `Downloaded {filename}`
- Error toast: `Failed to download report`

### 3. HTML Preview Panel

Below the artifacts list. Only shows if HTML report exists.

- Glass card, `min-height: 400px`
- Iframe: `width: 100%`, `height: 600px` (or `flex: 1`), `sandbox` attribute (no scripts, allow same-origin for styling)
- Source: `/api/reports/{html_filename}` loaded directly in iframe `src`
- Fallback: if HTML not available, hide panel entirely

```html
<iframe
  src="/api/reports/scan_20260820_100000.html"
  sandbox="allow-same-origin"
  class="de-report-preview"
></iframe>
```

```css
.de-report-preview {
  width: 100%;
  height: 600px;
  border: var(--de-glass-border);
  border-radius: var(--de-radius-lg);
  background: #fff; /* reports are light-themed internally */
}
```

The HTML report from deep-eye uses its own internal styling (`severity_colors` from config). The iframe isolates it from the dark theme.

### 4. Preview Controls

Small toolbar above iframe:
- Filename label
- "Open in new tab" button (ghost, small) — opens `/api/reports/{filename}` in new browser tab
- "Download" button (secondary, small)

---

## Data Flow

```
GET /api/scans/{id} → { report_path }
          ↓
GET /api/reports?scan_id={id} → [{ filename, format, size, created_at }]
          ↓
    ┌──────────────┐          ┌───────────────┐
    │ ArtifactList │          │ HTML Preview  │
    │   (rows)     │          │   (iframe)    │
    └──────────────┘          └───────────────┘
          ↓                         ↓
    GET /api/reports/{filename}  (download or iframe src)
```

---

## Empty State

When no reports exist (scan not yet complete):
- Icon: file/document, `48px`
- Title: "No reports available yet"
- Description: "Reports are generated when the scan completes. Check back shortly."
- If scan is running: "View Live Console →" link to `/scan/:id/live`
- If scan hasn't started: "Start Scan" button to `/scan/new`

---

## Loading State

- Skeleton list rows: 3 placeholder rows with pulsing animation
- Preview panel: skeleton with pulsing background

---

## Responsive

| Width | Behavior |
|---|---|
| ≥1024px | Artifacts list + preview side by side (`grid: 1fr 1fr`), or stacked |
| 768–1023px | Stacked: artifacts list full-width, preview below |
| <768px | Stacked, filename truncates earlier, preview hidden (download only) |
