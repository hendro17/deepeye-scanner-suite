# Screen: Dashboard

> Route: `/` | Data: `GET /api/scans` | Primary view — SOC overview

---

## Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│ TOPBAR: Dashboard                                            [🔍] [⚙]   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                    │
│  │ TOTAL    │ │ CRITICAL │ │ ACTIVE   │ │ URLS     │                    │
│  │ SCANS    │ │ FINDINGS │ │ SCANS    │ │ CRAWLED  │                    │
│  │  147     │ │   23     │ │    2     │ │  4,892   │                    │
│  │ ▲12% wk  │ │ ▲5 today │ │ running  │ │ all-time │                    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘                    │
│                                                                          │
│  ┌──────────────────────────┐ ┌──────────────────────────┐             │
│  │ SEVERITY DISTRIBUTION    │ │ SCAN HISTORY (7 days)    │             │
│  │                          │ │                           │             │
│  │     [donut chart]        │ │  [bar chart]              │             │
│  │     Critical 8           │ │   ██  ██  ██  ██  ██  ██  │             │
│  │     High 15              │ │   ██  ██  ██  ██  ██  ██  │             │
│  │     Medium 31           │ │   ██  ██  ██  ██  ██  ██  │             │
│  │     Low 22              │ │   M   T   W   T   F   S   S│             │
│  │     Info 5              │ │                           │             │
│  │     Total: 81           │ │                           │             │
│  └──────────────────────────┘ └──────────────────────────┘             │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │ RECENT SCANS                              [View All →]   │           │
│  ├──────────┬──────────┬────────┬──────────┬──────────────┤           │
│  │ TARGET   │ STATUS   │ SEV    │ DURATION │ CREATED        │           │
│  ├──────────┼──────────┼────────┼──────────┼──────────────┤           │
│  │ http://..│ ●Running │ 3C 2H  │ 4m 12s   │ 2 min ago     │           │
│  │ http://..│ ✓Done     │ 1C 0H  │ 8m 45s   │ 1 hr ago      │           │
│  │ http://..│ ✓Done     │ 0C 5M  │ 12m 03s  │ 3 hr ago      │           │
│  │ http://..│ ✕Failed   │ —      │ 2m 30s   │ 5 hr ago      │           │
│  │ http://..│ ⊘Stopped  │ 2C 1H  │ 6m 18s   │ 1 day ago     │           │
│  └──────────┴──────────┴────────┴──────────┴──────────────┘           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Component Composition

### 1. Stat Cards Row

- Layout: `grid-template-columns: repeat(4, 1fr)`, gap `16px`
- Responsive: 2 columns at `<1280px`, 1 column at `<640px`

| Card | Label | Number Source | Trend | Color |
|---|---|---|---|---|
| Total Scans | `TOTAL SCANS` | `scans.length` | % change vs last week | accent-secondary (up) / danger (down) |
| Critical Findings | `CRITICAL FINDINGS` | sum of `severity_counts.critical` across all scans | count today | danger |
| Active Scans | `ACTIVE SCANS` | `scans.filter(s => s.status === 'running').length` | status text | accent-primary |
| URLs Crawled | `URLS CRAWLED` | sum of all `urls_crawled` | all-time label | info |

Each card: glass card, `120px` min-height, stat number `24px` bold, label uppercase `13px` secondary, trend `11px`.

**Click behavior:** cards are interactive — clicking "Critical Findings" navigates to Findings filtered by severity=critical. Clicking "Active Scans" navigates to ScanLive of the most recent running scan.

### 2. Severity Distribution Donut

- Layout: `grid-template-columns: 8fr 4fr` (left: donut, right: bar chart), gap `16px`
- At `<1024px`: stack vertically (1 column)
- Container: glass card, `min-height: 280px`, padding `16px`

Chart: ApexCharts donut. See `components.md` §6 for full config.

**Data mapping:**
```js
// Aggregate severity counts across ALL scans
const allFindings = scans.flatMap(s => s.severity_counts);
const counts = {
  critical: sum(allFindings.map(f => f.critical)),
  high:     sum(allFindings.map(f => f.high)),
  medium:   sum(allFindings.map(f => f.medium)),
  low:      sum(allFindings.map(f => f.low)),
  info:     sum(allFindings.map(f => f.info)),
};
series: [counts.critical, counts.high, counts.medium, counts.low, counts.info]
```

Center label: total findings count + "FINDINGS" label.

### 3. Scan History Bar Chart

- Container: glass card, same row as donut
- Chart: ApexCharts bar chart (vertical bars)
- X-axis: last 7 days (Mon–Sun)
- Y-axis: vulnerability count per day
- Color: single series `#00f0ff` (neon cyan)
- Bar radius: `4px`, column width `60%`

**Data mapping:**
```js
// Group scans by created_at date, sum vulnerabilities per day
const dailyCounts = groupByDate(scans, 'created_at').map(day => day.totalVulns);
categories: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
```

### 4. Recent Scans Table

- Layout: full-width glass card
- Table columns:

| Column | Width | Content | Sortable |
|---|---|---|---|
| Target | `flex: 2` | URL, truncated with ellipsis, `font-mono` for URL | Yes |
| Status | `100px` | status badge (Running/Done/Failed/Stopped) | Yes |
| Severity | `120px` | mini badges: `3C 2H 4M 1L` (compact severity counts) | Yes |
| Duration | `100px` | `4m 12s` format, `font-mono` | No |
| Created | `120px` | relative time (`2 min ago`), tooltip with full timestamp | Yes |

- Rows: clickable → navigate to `/scan/:id/findings`
- Max 10 rows shown; "View All →" link navigates to full scan list
- Severity mini badges: tiny inline badges (Critical=red, High=orange, etc.) showing count per severity, format: `3C 2H 4M 1L 0I`

### 5. Empty State

When no scans exist:
- Centered icon (clipboard / radar), title "No scans yet", description "Start your first scan to see results here.", CTA button "New Scan" → `/scan/new`

---

## Data Flow

```
GET /api/scans → [{ id, target, status, created_at, severity_counts }]
                       ↓
              Pinia store: scans[]
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   StatCards      Charts         RecentTable
```

- Pinia store fetches on mount (`onMounted`)
- Loading state: skeleton placeholders (glass card with animated pulse `rgba(0,240,255,0.04)`)
- Error state: toast error + retry button
- Auto-refresh: poll `GET /api/scans` every `30s` if any scan is `running` (stop polling when none running)

---

## Responsive Behavior

| Width | Layout |
|---|---|
| ≥1280px | 4 stat cards in row, donut + bar side by side, full table |
| 1024–1279px | 4 stat cards, donut + bar side by side, table scrolls |
| 768–1023px | 2×2 stat cards, charts stacked, table scrolls |
| <768px | 1 stat card per row, charts stacked, table scrolls horizontally |
