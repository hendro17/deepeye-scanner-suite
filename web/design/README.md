# DeepEye Scanner Suite — Design System

> Dark futuristic / SOC (Security Operations Center) theme for the AI-driven vulnerability scanner web GUI.

---

## Quick Start

1. Import tokens: `@import 'design/tokens.css';` in your main CSS entry.
2. Load fonts: Inter (variable) + JetBrains Mono (variable) from `/fonts/`.
3. Reference all colors, spacing, radii via `var(--de-*)` tokens — never hardcode hex.
4. Implement components per `components.md` specs.
5. Build screens per `screens/*.md` layouts.

---

## Files

| File | Contents |
|---|---|
| `tokens.css` | All CSS custom properties (colors, spacing, typography, shadows, z-index, transitions) |
| `palette.md` | Color palette reference with hex values, contrast ratios, usage rules |
| `typography.md` | Type scale, font specs, line heights, letter spacing, specimens |
| `components.md` | Component specs: buttons, inputs, cards, badges, terminal, charts, tables, modals, sliders, toggles, toasts, stepper |
| `layouts.md` | Grid system, app shell, sidebar, topbar, spacing, responsive breakpoints |
| `screens/dashboard.md` | Dashboard mockup: stat cards, severity donut, scan history bar, recent scans table |
| `screens/new-scan.md` | New Scan Wizard: 5-step form (target → checks → config → review → start) |
| `screens/scan-live.md` | Live Scan Console: SSE terminal, progress bar, stop control |
| `screens/findings.md` | Findings Table: filterable, sortable, expandable detail rows |
| `screens/reports.md` | Report Viewer: artifact list, download, HTML preview |
| `screens/settings.md` | Settings: AI providers, scanner, notifications, proxy, compliance, advanced, maintenance |

---

## Design Tokens Summary

| Category | Key Tokens |
|---|---|
| Backgrounds | `--de-bg-primary` `#0a0e1a`, `--de-bg-secondary` `#121826`, `--de-bg-tertiary` `#1a2133`, `--de-bg-elevated` `#1e2640` |
| Accents | `--de-color-accent-primary` `#00f0ff` (cyan), `--de-color-accent-secondary` `#00ff88` (green) |
| Semantic | `--de-color-warning` `#ffaa00`, `--de-color-danger` `#ff3366`, `--de-color-info` `#4a9eff` |
| Severity | critical `#ff3366`, high `#ff6644`, medium `#ffaa00`, low `#4a9eff`, info `#6b7d99` |
| Text | primary `#e0e6ed`, secondary `#8b95a7`, tertiary `#5a6577` |
| Fonts | UI: Inter, Terminal: JetBrains Mono |
| Spacing | `4px 8px 12px 16px 24px 32px 48px 64px` |
| Radius | sm `4px`, md `6px`, lg `8px`, xl `12px` |
| Glass | `rgba(18,24,38,0.70)` + `blur(12px)` + cyan border `rgba(0,240,255,0.10)` |

---

## Component Count

| Component | Spec Location |
|---|---|
| Buttons (5 variants, 3 sizes) | `components.md` §1 |
| Inputs (text, password, textarea, select) | `components.md` §2 |
| Cards (glass, stat, interactive) | `components.md` §3 |
| Badges (severity, status, format) | `components.md` §4 |
| Terminal Console | `components.md` §5 |
| Charts (donut, bar — ApexCharts) | `components.md` §6 |
| Tables (sortable, expandable, filterable) | `components.md` §7 |
| Modals (4 sizes) | `components.md` §8 |
| Sliders | `components.md` §9 |
| Toggles | `components.md` §10 |
| Progress Bars | `components.md` §11 |
| Toasts | `components.md` §12 |
| Empty States | `components.md` §13 |
| Tabs | `components.md` §14 |
| Stepper | `components.md` §15 |
| Tooltip | `components.md` §16 |
| Divider | `components.md` §17 |

---

## Screen Count

| Screen | Route | Spec |
|---|---|---|
| Dashboard | `/` | `screens/dashboard.md` |
| New Scan Wizard | `/scan/new` | `screens/new-scan.md` |
| Live Scan Console | `/scan/:id/live` | `screens/scan-live.md` |
| Findings Table | `/scan/:id/findings` | `screens/findings.md` |
| Report Viewer | `/scan/:id/reports` | `screens/reports.md` |
| Settings | `/settings` | `screens/settings.md` |

---

## Implementation Notes

- **Vue 3 + Vite + Tailwind CSS + Pinia** (per PLAN.md stack decision)
- Tailwind config: extend theme with `--de-*` tokens via `theme.extend.colors` etc.
- ApexCharts: import `vue3-apexcharts`, set global defaults (`fontFamily: 'Inter'`, `foreColor: '#8b95a7'`)
- Glassmorphism: requires `backdrop-filter` support (all modern browsers; `-webkit-` prefix for Safari)
- Fonts: self-host variable woff2 files in `web/public/fonts/`
- API keys: never sent to browser. Backend masks via `sk-••••` pattern. Config GET returns masked values only.
