# DeepEye Scanner Suite — Component Specifications

> Every component defined with exact CSS values, dimensions, states, and variants.
> All tokens reference `tokens.css`. Developer can implement directly.

---

## 1. Buttons

### Variants

| Variant | Background | Text | Border | Usage |
|---|---|---|---|---|
| Primary | `var(--de-color-accent-primary)` | `var(--de-text-inverse)` | none | Main CTA, start scan, save |
| Secondary | `transparent` | `var(--de-color-accent-primary)` | `1px solid var(--de-border-strong)` | Secondary actions |
| Ghost | `transparent` | `var(--de-text-secondary)` | none | Tertiary, nav-adjacent |
| Danger | `var(--de-color-danger)` | `#fff` | none | Stop scan, delete |
| Success | `var(--de-color-accent-secondary)` | `var(--de-text-inverse)` | none | Confirm, test connection pass |

### Sizes

| Size | Height | Padding X | Font Size | Gap |
|---|---|---|---|---|
| Small | `28px` | `12px` | `13px` | `6px` |
| Medium | `36px` | `16px` | `14px` | `8px` |
| Large | `44px` | `24px` | `16px` | `10px` |

### CSS

```css
.de-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--de-btn-gap);
  height: var(--de-btn-height-md);     /* 36px */
  padding: 0 var(--de-btn-padding-x);  /* 0 16px */
  border: none;
  border-radius: var(--de-radius-sm);   /* 4px */
  font-family: var(--de-font-ui);
  font-size: var(--de-text-base);
  font-weight: var(--de-font-medium);
  letter-spacing: var(--de-tracking-wider);
  cursor: pointer;
  transition: all var(--de-transition-base);
  white-space: nowrap;
  user-select: none;
}

.de-btn--primary {
  background: var(--de-color-accent-primary);
  color: var(--de-text-inverse);
}
.de-btn--primary:hover {
  box-shadow: var(--de-glow-accent-strong);
  filter: brightness(1.1);
}

.de-btn--secondary {
  background: transparent;
  color: var(--de-color-accent-primary);
  border: 1px solid var(--de-border-strong);
}
.de-btn--secondary:hover {
  background: rgba(0, 240, 255, 0.08);
  border-color: var(--de-color-accent-primary);
}

.de-btn--ghost {
  background: transparent;
  color: var(--de-text-secondary);
}
.de-btn--ghost:hover {
  background: rgba(255, 255, 255, 0.04);
  color: var(--de-text-primary);
}

.de-btn--danger {
  background: var(--de-color-danger);
  color: #fff;
}
.de-btn--danger:hover {
  box-shadow: var(--de-glow-danger);
  filter: brightness(1.1);
}

.de-btn--success {
  background: var(--de-color-accent-secondary);
  color: var(--de-text-inverse);
}
.de-btn--success:hover {
  box-shadow: var(--de-glow-success);
  filter: brightness(1.1);
}

.de-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  filter: none;
  box-shadow: none;
}
```

### Icon Button (square)

```css
.de-icon-btn {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--de-radius-sm);
  background: transparent;
  color: var(--de-text-secondary);
  cursor: pointer;
  transition: all var(--de-transition-fast);
}
.de-icon-btn:hover {
  background: rgba(0, 240, 255, 0.08);
  color: var(--de-color-accent-primary);
}
```

---

## 2. Inputs

### Text Input

```css
.de-input {
  width: 100%;
  height: var(--de-input-height);    /* 36px */
  padding: var(--de-input-padding-y) var(--de-input-padding-x);
  background: var(--de-bg-tertiary);
  border: 1px solid var(--de-border-default);
  border-radius: var(--de-radius-sm);
  color: var(--de-text-primary);
  font-family: var(--de-font-ui);
  font-size: var(--de-text-base);
  transition: all var(--de-transition-base);
  box-shadow: var(--de-glow-inset);
}

.de-input::placeholder {
  color: var(--de-text-tertiary);
}

.de-input:focus {
  outline: none;
  border-color: var(--de-color-accent-primary);
  box-shadow: var(--de-focus-ring);
}

.de-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### Password Input (masked API keys)

- Same as text input but `type="password"` with a toggle-visibility icon button inside (right-aligned).
- Masked value pattern: `sk-••••••••1234` (keep last 4 chars).
- Font: `var(--de-font-mono)` — API keys are code, not prose.

### Textarea

```css
.de-textarea {
  min-height: 100px;
  padding: var(--de-space-2) var(--de-space-3);
  /* same styling as .de-input */
  resize: vertical;
  line-height: var(--de-leading-normal);
}
```

### Select / Dropdown

```css
.de-select {
  /* same as .de-input */
  appearance: none;
  background-image: url('data:image/svg+xml;utf8,<svg ...chevron-down...');
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
  cursor: pointer;
}
```

Dropdown panel (opens below):
- Background: `var(--de-bg-elevated)`
- Border: `var(--de-glass-border)`
- Border radius: `var(--de-radius-md)`
- Box shadow: `var(--de-shadow-lg)`
- Each item: `height: 36px`, `padding: 0 12px`, hover `rgba(0, 240, 255, 0.06)`
- Selected item: text `var(--de-color-accent-primary)`, left border `2px solid`

### Input Group (with label)

```
┌─────────────────────────────────┐
│ Label                           │  ← 13px, medium, secondary
│ ┌─────────────────────────────┐ │
│ │ [value              ] [icon] │ │  ← 36px height
│ └─────────────────────────────┘ │
│ Helper text                     │  ← 11px, tertiary
└─────────────────────────────────┘
```

- Label gap: `4px` above input
- Helper/error gap: `4px` below input
- Error text color: `var(--de-color-danger)`, `11px`

---

## 3. Cards

### Glass Card (base — see layouts.md for full CSS)

```
┌────────────────────────────────────────┐
│ CARD TITLE                    [action] │
├────────────────────────────────────────┤
│                                         │
│  content                                 │
│                                         │
└────────────────────────────────────────┘
  background: rgba(18, 24, 38, 0.70)
  backdrop-filter: blur(12px)
  border: 1px solid rgba(0, 240, 255, 0.10)
  border-radius: 8px
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.40)
  padding: 16px
```

### Stat Card

```
┌────────────────────────┐
│ TOTAL SCANS           │  ← card title style (uppercase, secondary)
│                        │
│  147                   │  ← stat number (24px, bold, primary)
│  ▲ 12% this week       │  ← caption (11px, secondary or accent-secondary)
│                        │
└────────────────────────┘
```

- Min-height: `120px`
- Padding: `16px`
- Internal gap: `8px`
- Number: `--de-text-2xl` (24px), `--de-font-bold`
- Trend indicator: icon (12px) + text, gap `4px`

### Interactive Card (clickable)

- Adds `cursor: pointer`
- Hover: border `--de-glass-border-hover`, shadow `--de-glass-shadow-lg`
- Active: `transform: scale(0.99)`

---

## 4. Badges

### Severity Badge

| Severity | Text Color | Background | Border |
|---|---|---|---|
| Critical | `#ff3366` | `rgba(255, 51, 102, 0.12)` | `rgba(255, 51, 102, 0.35)` |
| High | `#ff6644` | `rgba(255, 102, 68, 0.12)` | `rgba(255, 102, 68, 0.35)` |
| Medium | `#ffaa00` | `rgba(255, 170, 0, 0.12)` | `rgba(255, 170, 0, 0.35)` |
| Low | `#4a9eff` | `rgba(74, 158, 255, 0.12)` | `rgba(74, 158, 255, 0.35)` |
| Info | `#6b7d99` | `rgba(107, 125, 153, 0.12)` | `rgba(107, 125, 153, 0.35)` |

```css
.de-badge {
  display: inline-flex;
  align-items: center;
  height: var(--de-badge-height);    /* 20px */
  padding: 0 var(--de-badge-padding-x); /* 0 8px */
  border-radius: var(--de-radius-sm);
  font-family: var(--de-font-ui);
  font-size: var(--de-text-xs);       /* 11px */
  font-weight: var(--de-font-semibold);
  text-transform: uppercase;
  letter-spacing: var(--de-tracking-wide);
  border: 1px solid;
  line-height: 1;
}

.de-badge--critical {
  color: var(--de-severity-critical);
  background: rgba(255, 51, 102, 0.12);
  border-color: rgba(255, 51, 102, 0.35);
}
/* ...same pattern for high, medium, low, info */
```

### Status Badge

| Status | Color | Icon |
|---|---|---|
| Online / Ready | `var(--de-color-accent-secondary)` | filled dot |
| Running / Active | `var(--de-color-accent-primary)` | pulsing dot |
| Offline / Error | `var(--de-color-danger)` | hollow dot |
| Pending | `var(--de-text-tertiary)` | hollow dot |
| Configured | `var(--de-color-accent-secondary)` | checkmark |
| Missing key | `var(--de-color-warning)` | warning |
| Reachable | `var(--de-color-accent-secondary)` | filled dot |
| Unreachable | `var(--de-color-danger)` | hollow dot |

```css
.de-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  /* same base as .de-badge but no uppercase, lowercase ok */
  font-size: var(--de-text-xs);
  color: var(--de-text-secondary);
}

.de-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.de-status-dot--running {
  background: var(--de-color-accent-primary);
  animation: de-pulse 1.5s ease-in-out infinite;
}

@keyframes de-pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--de-color-accent-primary); }
  50% { opacity: 0.4; box-shadow: 0 0 4px var(--de-color-accent-primary); }
}
```

### Format Badge (report formats)

| Format | Color | Label |
|---|---|---|
| HTML | `var(--de-color-info)` | `HTML` |
| PDF | `var(--de-color-danger)` | `PDF` |
| JSON | `var(--de-color-accent-secondary)` | `JSON` |
| SARIF | `var(--de-color-accent-primary)` | `SARIF` |
| JUnit | `var(--de-color-warning)` | `JUNIT` |
| CSV | `var(--de-text-secondary)` | `CSV` |
| XLSX | `var(--de-severity-high)` | `XLSX` |

Uses `.de-badge` base with format-specific colors.

---

## 5. Terminal Console

```
┌──────────────────────────────────────────────────────────┐
│ [●] deep_eye.py — Scan #42          [Stop] [Clear] [⤢] │  ← header, 40px
├──────────────────────────────────────────────────────────┤
│ 10:00:01 [INFO] Starting scan on http://example.com     │
│ 10:00:02 [INFO] Crawling URLs...                         │
│ 10:00:05 [WARN] SSL certificate not valid for subdomain   │
│ 10:00:08 [INFO] Testing SQL injection on /login          │
│ 10:00:12 [CRITICAL] SQL injection found in /login         │
│ 10:00:13 [INFO] Testing XSS on /search                   │
│ 10:00:15 [SUCCESS] Scan complete. 3 vulnerabilities.     │
│ ▌                                                         │  ← auto-scroll cursor
└──────────────────────────────────────────────────────────┘
  font-family: JetBrains Mono, 13px, line-height 1.6
```

### Log Line Format

```
{timestamp} [{LEVEL}] {message}
```

- Timestamp: `var(--de-text-tertiary)` (`#5a6577`)
- `[INFO]`: `var(--de-color-accent-primary)` (cyan)
- `[WARN]`: `var(--de-color-warning)` (amber)
- `[ERROR]`: `var(--de-color-danger)` (red)
- `[CRITICAL]`: `var(--de-color-danger)` (red) + `font-weight: 700`
- `[DEBUG]`: `var(--de-severity-info)` (muted blue-gray)
- `[SUCCESS]`: `var(--de-color-accent-secondary)` (green)
- Message: `var(--de-terminal-text)` (`#c8d4e0`)

```css
.de-terminal-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--de-terminal-padding);
  font-family: var(--de-font-mono);
  font-size: var(--de-terminal-font-size);
  line-height: var(--de-terminal-line-height);
  background: var(--de-terminal-bg);
}

.de-log-line {
  white-space: pre-wrap;
  word-break: break-all;
}

.de-log-timestamp { color: var(--de-text-tertiary); }
.de-log-info      { color: var(--de-color-accent-primary); }
.de-log-warn      { color: var(--de-color-warning); }
.de-log-error     { color: var(--de-color-danger); }
.de-log-critical  { color: var(--de-color-danger); font-weight: 700; }
.de-log-debug     { color: var(--de-severity-info); }
.de-log-success   { color: var(--de-color-accent-secondary); }
.de-log-msg       { color: var(--de-terminal-text); }
```

### Terminal Header

```css
.de-terminal-header {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--de-space-3);
  border-bottom: 1px solid var(--de-border-default);
  background: rgba(0, 240, 255, 0.03);
}
```

- Left: status dot (pulsing if running) + process name + scan ID
- Right: Stop button (danger, small), Clear (ghost icon button), Fullscreen toggle

### Auto-Scroll

- New lines appended to bottom.
- `scrollTop = scrollHeight` after each append (unless user has scrolled up — detect via `scrollHeight - scrollTop - clientHeight < 50`).
- Max 10,000 lines — trim oldest when exceeded.

---

## 6. Charts (ApexCharts)

### Donut Chart — Severity Distribution

```js
const severityDonut = {
  series: [/* counts: critical, high, medium, low, info */],
  options: {
    chart: {
      type: 'donut',
      background: 'transparent',
      foreColor: '#8b95a7',
    },
    labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
    colors: ['#ff3366', '#ff6644', '#ffaa00', '#4a9eff', '#6b7d99'],
    stroke: { width: 0 },
    legend: {
      position: 'right',
      fontSize: '13px',
      labels: { colors: '#8b95a7' },
      markers: { width: 8, height: 8, radius: 4 },
    },
    dataLabels: { enabled: false },
    plotOptions: {
      pie: {
        donut: {
          size: '72%',
          labels: {
            show: true,
            name: { color: '#8b95a7', fontSize: '13px' },
            value: { color: '#e0e6ed', fontSize: '24px', fontWeight: 700 },
            total: {
              show: true,
              label: 'Findings',
              color: '#8b95a7',
              fontSize: '11px',
            }
          }
        }
      }
    },
    tooltip: {
      theme: 'dark',
      style: { background: 'rgba(18, 24, 38, 0.95)' },
    }
  }
}
```

### Bar Chart — Scan History

```js
const scanHistoryBar = {
  series: [{ name: 'Vulnerabilities', data: [/* counts per day */] }],
  options: {
    chart: {
      type: 'bar',
      background: 'transparent',
      foreColor: '#8b95a7',
      toolbar: { show: false },
    },
    colors: ['#00f0ff'],
    plotOptions: {
      bar: {
        borderRadius: 4,
        columnWidth: '60%',
      }
    },
    grid: {
      borderColor: 'rgba(255, 255, 255, 0.05)',
      strokeDashArray: 0,
    },
    xaxis: {
      categories: [/* date labels */],
      labels: { style: { colors: '#8b95a7' } },
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: { labels: { style: { colors: '#8b95a7' } } },
    tooltip: { theme: 'dark' },
  }
}
```

### Chart Container

```css
.de-chart-container {
  background: var(--de-glass-bg);
  backdrop-filter: blur(var(--de-glass-blur));
  border: var(--de-glass-border);
  border-radius: var(--de-radius-lg);
  padding: var(--de-space-4);
  min-height: 280px;
}
```

ApexCharts global defaults set via `apex.global` or `ApexCharts` config injection — `fontFamily: 'Inter'`, `foreColor: '#8b95a7'`.

---

## 7. Tables

```css
.de-table-wrapper {
  overflow-x: auto;
  border-radius: var(--de-radius-lg);
  border: var(--de-glass-border);
  background: var(--de-glass-bg);
  backdrop-filter: blur(var(--de-glass-blur));
}

.de-table { width: 100%; border-collapse: collapse; }

.de-table th {
  text-align: left;
  padding: var(--de-space-2) var(--de-space-3);
  font-size: var(--de-text-xs);
  font-weight: var(--de-font-semibold);
  text-transform: uppercase;
  letter-spacing: var(--de-tracking-wide);
  color: var(--de-text-secondary);
  background: rgba(0, 240, 255, 0.03);
  border-bottom: 1px solid var(--de-border-default);
  white-space: nowrap;
}

.de-table td {
  padding: var(--de-space-2) var(--de-space-3);
  font-size: var(--de-text-base);
  color: var(--de-text-primary);
  border-bottom: 1px solid var(--de-border-separator);
}

.de-table tbody tr { transition: background var(--de-transition-fast); }
.de-table tbody tr:hover { background: rgba(0, 240, 255, 0.02); }
```

### Sortable Header

- Clickable `th`: `cursor: pointer`
- Active sort: text color `--de-color-accent-primary`, sort arrow icon (8px)
- Inactive sort: hover shows faint arrow

### Expandable Row

```
| sev badge | type | url | param | [v] |
└── expanded detail panel ──────────┘
```

- Chevron icon (16px) in last column, rotates 90° when expanded
- Expanded row: `background: var(--de-bg-tertiary)`, full-width detail panel below
- Detail panel padding: `16px`, internal gap: `12px`

### Filterable Table (toolbar above)

```
┌──────────────────────────────────────────────────────────┐
│ [🔍 Search...]  [Severity ▾] [Type ▾] [FP only ☐]  [Export] │
└──────────────────────────────────────────────────────────┘
```

- Toolbar: `height: 48px`, glass card background, `padding: 0 12px`
- Search input: `width: 240px`, expandable on focus
- Filter dropdowns: `width: auto`, `min-width: 120px`

---

## 8. Modals

```css
.de-modal-backdrop {
  position: fixed;
  inset: 0;
  background: var(--de-bg-scrim);
  backdrop-filter: blur(4px);
  z-index: var(--de-z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
}

.de-modal {
  background: var(--de-bg-elevated);
  border: var(--de-glass-border);
  border-radius: var(--de-radius-xl);  /* 12px */
  box-shadow: var(--de-glass-shadow-lg);
  width: 100%;
  max-width: 560px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  animation: de-modal-enter 200ms ease-out;
}

@keyframes de-modal-enter {
  from { opacity: 0; transform: translateY(8px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
```

### Modal Structure

```
┌────────────────────────────────────────┐
│ Modal Title                    [×]      │  ← header, 48px
├────────────────────────────────────────┤
│                                         │
│  content                                 │  ← scrollable body
│                                         │
├────────────────────────────────────────┤
│              [Cancel]  [Confirm]         │  ← footer, 56px
└────────────────────────────────────────┘
```

- Header: `padding: 0 16px`, border-bottom, title left, close button right
- Body: `padding: 16px`, `overflow-y: auto`, `flex: 1`
- Footer: `padding: 0 16px`, border-top, buttons right-aligned, gap `8px`

---

## 9. Sliders

```css
.de-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  background: var(--de-bg-tertiary);
  border-radius: var(--de-radius-full);
  outline: none;
  cursor: pointer;
}

.de-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: var(--de-color-accent-primary);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: var(--de-glow-accent);
  transition: transform var(--de-transition-fast);
}

.de-slider::-webkit-slider-thumb:hover { transform: scale(1.2); }

.de-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: var(--de-color-accent-primary);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: var(--de-glow-accent);
}
```

### Slider with Label

```
Threads                              5
●──────────────●═══════════════
1                        25          50
```

- Label row: label left, value right (`--de-font-mono`, accent-primary)
- Track: `4px` height, filled portion uses `accent-primary`
- Thumb: `16px` circle, neon cyan, glow on hover
- Min/max labels: `--de-text-xs`, `--de-text-tertiary`

---

## 10. Toggles (Switches)

```css
.de-toggle {
  position: relative;
  width: var(--de-toggle-width);    /* 40px */
  height: var(--de-toggle-height);  /* 22px */
  background: var(--de-bg-tertiary);
  border-radius: var(--de-radius-full);
  cursor: pointer;
  transition: background var(--de-transition-base);
  border: 1px solid var(--de-border-default);
}

.de-toggle--on {
  background: rgba(0, 255, 136, 0.15);
  border-color: rgba(0, 255, 136, 0.35);
  box-shadow: var(--de-glow-success);
}

.de-toggle-knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: var(--de-toggle-knob);  /* 16px */
  height: var(--de-toggle-knob);
  background: var(--de-text-secondary);
  border-radius: 50%;
  transition: all var(--de-transition-base);
}

.de-toggle--on .de-toggle-knob {
  transform: translateX(18px);
  background: var(--de-color-accent-secondary);
}
```

### Toggle Row (check list pattern)

```
[●──] SQL Injection        [○──] XSS
```

- Toggle: `40px × 22px`
- Label: `--de-text-base`, `--de-text-primary`
- Gap between toggle and label: `8px`
- Row gap in check lists: `8px`

---

## 11. Progress Bar

```css
.de-progress {
  width: 100%;
  height: 6px;
  background: var(--de-bg-tertiary);
  border-radius: var(--de-radius-full);
  overflow: hidden;
}

.de-progress-bar {
  height: 100%;
  background: var(--de-color-accent-primary);
  border-radius: var(--de-radius-full);
  box-shadow: var(--de-glow-accent);
  transition: width var(--de-transition-slow);
}
```

### Scan Progress

```
┌──────────────────────────────────────────────────────────┐
│ Scanning... ████████████░░░░░░░░░░░░░░  45%   [Stop]      │
│ URLs crawled: 23 / ~50                                    │
└──────────────────────────────────────────────────────────┘
```

- Progress bar: full width, `6px` height
- Percentage: `--de-font-mono`, `--de-color-accent-primary`
- Sub-label: `--de-text-sm`, `--de-text-secondary`

---

## 12. Toasts

```css
.de-toast-container {
  position: fixed;
  top: var(--de-space-4);
  right: var(--de-space-4);
  z-index: var(--de-z-toast);
  display: flex;
  flex-direction: column;
  gap: var(--de-space-2);
}

.de-toast {
  display: flex;
  align-items: center;
  gap: var(--de-space-2);
  padding: var(--de-space-2) var(--de-space-3);
  background: var(--de-bg-elevated);
  border: var(--de-glass-border);
  border-radius: var(--de-radius-md);
  box-shadow: var(--de-shadow-lg);
  font-size: var(--de-text-sm);
  max-width: 380px;
  animation: de-toast-enter 300ms ease-out;
}
```

| Type | Border Color | Icon |
|---|---|---|
| Success | `rgba(0, 255, 136, 0.35)` | check-circle |
| Error | `rgba(255, 51, 102, 0.35)` | alert-circle |
| Warning | `rgba(255, 170, 0, 0.35)` | alert-triangle |
| Info | `rgba(74, 158, 255, 0.35)` | info |

Auto-dismiss after 4s (success/info), 6s (warning), persist (error).

---

## 13. Empty States

```
┌──────────────────────────────────────┐
│                                       │
│           [icon 48px]                 │
│                                       │
│        No scans yet                   │  ← 16px, semibold, primary
│  Start your first scan to see         │  ← 14px, regular, secondary
│  results here.                         │
│                                       │
│         [New Scan]                    │  ← primary button
│                                       │
└──────────────────────────────────────┘
```

- Centered content, `padding: 48px`
- Icon: `48px`, color `--de-text-tertiary`
- Title: `--de-text-md`, `--de-font-semibold`
- Description: `--de-text-base`, `--de-text-secondary`
- CTA: primary or secondary button

---

## 14. Tabs

```css
.de-tabs {
  display: flex;
  gap: var(--de-space-1);
  border-bottom: 1px solid var(--de-border-separator);
}

.de-tab {
  padding: var(--de-space-2) var(--de-space-3);
  font-size: var(--de-text-sm);
  font-weight: var(--de-font-medium);
  color: var(--de-text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all var(--de-transition-fast);
}

.de-tab:hover { color: var(--de-text-primary); }

.de-tab--active {
  color: var(--de-color-accent-primary);
  border-bottom-color: var(--de-color-accent-primary);
}
```

---

## 15. Stepper (Wizard)

```
  ●─────●─────○─────○─────○
 Target  Checks  Config  Review  Start
```

```css
.de-stepper {
  display: flex;
  align-items: center;
  gap: var(--de-space-1);
}

.de-step {
  display: flex;
  align-items: center;
  gap: var(--de-space-2);
  font-size: var(--de-text-sm);
  color: var(--de-text-tertiary);
}

.de-step--active { color: var(--de-color-accent-primary); }
.de-step--done   { color: var(--de-color-accent-secondary); }

.de-step-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid currentColor;
  font-size: var(--de-text-xs);
  font-weight: var(--de-font-semibold);
}

.de-step--done .de-step-circle {
  background: var(--de-color-accent-secondary);
  border-color: var(--de-color-accent-secondary);
  color: var(--de-text-inverse);
}

.de-step-line {
  flex: 1;
  height: 2px;
  background: var(--de-border-default);
  margin: 0 var(--de-space-1);
}

.de-step--done + .de-step-line { background: var(--de-color-accent-secondary); }
```

---

## 16. Tooltip

```css
.de-tooltip {
  position: absolute;
  padding: var(--de-space-1) var(--de-space-2);
  background: var(--de-bg-elevated);
  border: var(--de-glass-border);
  border-radius: var(--de-radius-sm);
  font-size: var(--de-text-xs);
  color: var(--de-text-secondary);
  white-space: nowrap;
  z-index: var(--de-z-tooltip);
  box-shadow: var(--de-shadow-md);
  pointer-events: none;
}
```

Delay: `500ms` hover. Max width: `240px`. Wrap to 2 lines if needed.

---

## 17. Divider

```css
.de-divider {
  height: 1px;
  background: var(--de-border-separator);
  margin: var(--de-space-3) 0;
}

.de-divider--with-label {
  display: flex;
  align-items: center;
  gap: var(--de-space-2);
  height: auto;
  background: transparent;
}

.de-divider--with-label::before,
.de-divider--with-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--de-border-separator);
}
```
