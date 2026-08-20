# Screen: Live Scan Console

> Route: `/scan/:id/live` | Data: `GET /api/scans/{id}/stream` (SSE) | Real-time terminal output

---

## Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│ TOPBAR: Scan #42 — example.com                                 [🔍] [⚙]  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─ Progress Bar ─────────────────────────────────────────────────────┐ │
│  │  Scanning... ████████████░░░░░░░░░░░░░░  45%    [Stop Scan]       │ │
│  │  URLs crawled: 23   •   Current: http://example.com/admin           │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─ Terminal ──────────────────────────────────────────────────────────┐ │
│  │ [●] deep_eye.py — Scan #42          [Clear] [⤢ Fullscreen]        │ │
│  ├────────────────────────────────────────────────────────────────────┤ │
│  │ 10:00:01 [INFO] Starting scan on https://example.com              │ │
│  │ 10:00:02 [INFO] Loading config from config/config.yaml             │ │
│  │ 10:00:02 [INFO] AI provider: openai (gpt-4o)                       │ │
│  │ 10:00:03 [INFO] Crawling phase started (depth=2, threads=5)       │ │
│  │ 10:00:05 [INFO] Found URL: https://example.com/login              │ │
│  │ 10:00:05 [INFO] Found URL: https://example.com/api/users          │ │
│  │ 10:00:06 [WARN] SSL certificate not valid for sub.example.com     │ │
│  │ 10:00:08 [INFO] Testing: sql_injection on /login                  │ │
│  │ 10:00:10 [SUCCESS] sql_injection passed — no vulnerability        │ │
│  │ 10:00:12 [CRITICAL] SQL injection found in /login (parameter: user)│ │
│  │ 10:00:13 [INFO] Testing: xss on /search                           │ │
│  │ 10:00:15 [SUCCESS] xss passed — no vulnerability                  │ │
│  │ 10:00:18 [INFO] Testing: ssrf on /api/fetch                       │ │
│  │ 10:00:20 [ERROR] Connection timeout on /api/fetch                 │ │
│  │ 10:00:22 [INFO] Scan phase complete. Generating report...         │ │
│  │ ▌                                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

Terminal fills remaining vertical space. `flex: 1`.

---

## Component Composition

### 1. Progress Bar Section

- Glass card, `padding: 16px`
- Top row: status label left, percentage + Stop button right
- Progress bar: full width, `6px` height, neon cyan fill
- Sub-row: URLs crawled counter, current URL being scanned

```
┌──────────────────────────────────────────────────────────────────────┐
│  ● Scanning...     ████████████░░░░░░░░░░  45%     [Stop Scan]    │
│  URLs crawled: 23   •   Current: http://example.com/admin           │
└──────────────────────────────────────────────────────────────────────┘
```

| Element | Style |
|---|---|
| Status label | `13px` medium, accent-primary + pulsing dot (if running) |
| Percentage | `16px` bold, `font-mono`, accent-primary |
| Stop button | danger variant, small, with stop icon |
| Progress bar | `6px`, track `--de-bg-tertiary`, fill accent-primary + glow |
| URLs counter | `13px`, secondary, `font-mono` for number |
| Current URL | `13px`, secondary, `font-mono`, truncated with ellipsis |

**Stop behavior:** `POST /api/scans/{id}/stop` → close EventSource → show "Scan stopped" status → terminal shows final line `[STOPPED] Scan terminated by user`.

### 2. Terminal Console

Full component spec in `components.md` §5. Key behaviors:

#### SSE Connection

```js
const eventSource = new EventSource(`/api/scans/${scanId}/stream`);

eventSource.addEventListener('log', (e) => {
  const { line, timestamp } = JSON.parse(e.data);
  appendLogLine(line, timestamp);
});

eventSource.addEventListener('progress', (e) => {
  const { urls_crawled, current_url } = JSON.parse(e.data);
  updateProgress(urls_crawled, current_url);
});

eventSource.addEventListener('done', (e) => {
  const { exit_code, report_path } = JSON.parse(e.data);
  handleScanComplete(exit_code, report_path);
  eventSource.close();
});

eventSource.addEventListener('error', (e) => {
  const { message, exit_code } = JSON.parse(e.data);
  appendLogLine(`[ERROR] ${message}`);
  eventSource.close();
});
```

#### Log Line Rendering

```js
function appendLogLine(line, timestamp) {
  // Parse: [LEVEL] message
  const match = line.match(/\[(INFO|WARN|ERROR|CRITICAL|DEBUG|SUCCESS)\]/);
  const level = match ? match[1] : 'INFO';
  const message = match ? line.replace(match[0], '').trim() : line;
  
  const html = `
    <span class="de-log-timestamp">${formatTime(timestamp)}</span>
    <span class="de-log-${level.toLowerCase()}">[${level}]</span>
    <span class="de-log-msg">${escapeHtml(message)}</span>
  `;
  
  terminalBody.insertAdjacentHTML('beforeend', `<div class="de-log-line">${html}</div>`);
  
  // Auto-scroll if near bottom
  if (isNearBottom()) terminalBody.scrollTop = terminalBody.scrollHeight;
  
  // Trim oldest lines
  trimLines(10000);
}
```

#### ANSI Stripping

Backend strips ANSI via `re.sub(r'\x1b\[[0-9;]*m', '', line)`. Frontend also escapes HTML (`& < > " '`) to prevent injection from log content.

#### Auto-Scroll Logic

```js
function isNearBottom() {
  return terminalBody.scrollHeight - terminalBody.scrollTop - terminalBody.clientHeight < 50;
}
```

If user scrolls up (not near bottom), auto-scroll pauses. A "↓ Jump to latest" button appears at bottom-right when paused. Clicking it scrolls to bottom and resumes auto-scroll.

### 3. Terminal Header

```
[●] deep_eye.py — Scan #42          [Clear] [⤢]
```

- Status dot: pulsing accent-primary when running, accent-secondary when done, danger when failed/stopped
- Process label: `font-mono`, `13px`, secondary
- Clear: ghost icon button — clears terminal body (confirmation not needed, logs still on server)
- Fullscreen: ghost icon button — toggles terminal to `position: fixed; inset: 0; z-index: var(--de-z-overlay)`

---

## Scan Completion States

| Exit Code | Status | Terminal Final Line | Action |
|---|---|---|---|
| 0 | Done | `[SUCCESS] Scan complete. N vulnerabilities found.` | Show "View Findings" button → `/scan/:id/findings` |
| 0 | Done | `[SUCCESS] Scan complete. No vulnerabilities found.` | Show "View Reports" button → `/scan/:id/reports` |
| ≠0 | Failed | `[ERROR] Scan failed with exit code N.` | Show error toast + retry button |
| -15 | Stopped | `[STOPPED] Scan terminated by user.` | Show "stopped" status badge |

On completion:
- Progress bar reaches 100% (green fill)
- Status dot stops pulsing
- Stop button replaced by "View Findings" + "View Reports" buttons
- EventSource closed

---

## Data Flow

```
GET /api/scans/{id} → { id, target, status, pid, started_at }
          ↓
EventSource(/api/scans/{id}/stream)
    ├── event:log      → appendLogLine()
    ├── event:progress → updateProgressBar()
    ├── event:done     → handleComplete()
    └── event:error     → handleError()
          ↓
POST /api/scans/{id}/stop (user action)
    → event:error { message: "Process killed", exit_code: -15 }
```

---

## Responsive

| Width | Layout |
|---|---|
| ≥768px | Progress bar above terminal, terminal fills height |
| <768px | Progress bar collapses to single row, terminal min-height `300px` |
