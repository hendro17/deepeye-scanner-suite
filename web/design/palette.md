# DeepEye Scanner Suite — Color Palette

> Dark futuristic / SOC (Security Operations Center) theme.
> All hex values are final production tokens. Match `tokens.css` exactly.

---

## Primary Palette

| Token | Hex | Usage |
|---|---|---|
| `--de-bg-primary` | `#0a0e1a` | App canvas — deepest layer behind everything |
| `--de-bg-secondary` | `#121826` | Sidebars, panels, cards (solid base) |
| `--de-bg-tertiary` | `#1a2133` | Nested cards, input fields, table rows |
| `--de-bg-elevated` | `#1e2640` | Modals, dropdown menus, popovers, tooltips |

### Background Visual

```
#0a0e1a  ████████████████████  deepest — app canvas
#121826  ████████████████████  panels / sidebars
#1a2133  ████████████████████  nested cards / inputs
#1e2640  ████████████████████  modals / dropdowns
```

Layering rule: each level up gets lighter by ~6–8 luminance units. Visual depth = lighter + more glass blur.

---

## Accent Colors (Neon)

| Token | Hex | Usage |
|---|---|---|
| `--de-color-accent-primary` | `#00f0ff` | Primary actions, active nav, links, focus rings, chart primary series |
| `--de-color-accent-secondary` | `#00ff88` | Success states, active toggles, online status, chart success series |

### Neon Swatches

```
#00f0ff  ████████████████████  cyan — primary brand accent
#00ff88  ████████████████████  green — success / secondary
```

These two neons define the **DeepEye identity**. Cyan leads; green accents.

---

## Semantic Colors

| Token | Hex | Usage |
|---|---|---|
| `--de-color-warning` | `#ffaa00` | Warnings, medium-severity badges, caution banners |
| `--de-color-danger` | `#ff3366` | Errors, critical-severity, destructive buttons, danger focus ring |
| `--de-color-info` | `#4a9eff` | Info banners, low-severity badges, informational tooltips |
| `--de-color-success` | `#00ff88` | Alias of accent-secondary; success toasts, confirmed states |

### Semantic Swatches

```
#ffaa00  ████████████████████  amber — warning / medium
#ff3366  ████████████████████  red — danger / critical
#4a9eff  ████████████████████  blue — info / low
#00ff88  ████████████████████  green — success (same as accent-secondary)
```

---

## Severity Scale (Finding Badges)

Distinct from semantic colors — used specifically for vulnerability severity badges and chart series.

| Severity | Token | Hex | Background (badge) | Text | Border |
|---|---|---|---|---|---|
| Critical | `--de-severity-critical` | `#ff3366` | `rgba(255, 51, 102, 0.12)` | `#ff3366` | `rgba(255, 51, 102, 0.35)` |
| High | `--de-severity-high` | `#ff6644` | `rgba(255, 102, 68, 0.12)` | `#ff6644` | `rgba(255, 102, 68, 0.35)` |
| Medium | `--de-severity-medium` | `#ffaa00` | `rgba(255, 170, 0, 0.12)` | `#ffaa00` | `rgba(255, 170, 0, 0.35)` |
| Low | `--de-severity-low` | `#4a9eff` | `rgba(74, 158, 255, 0.12)` | `#4a9eff` | `rgba(74, 158, 255, 0.35)` |
| Info | `--de-severity-info` | `#6b7d99` | `rgba(107, 125, 153, 0.12)` | `#6b7d99` | `rgba(107, 125, 153, 0.35)` |

### Severity Swatches

```
#ff3366  ████████████████████  CRITICAL
#ff6644  ████████████████████  HIGH
#ffaa00  ████████████████████  MEDIUM
#4a9eff  ████████████████████  LOW
#6b7d99  ████████████████████  INFO
```

**Severity → ApexCharts series color order:**
```js
['#ff3366', '#ff6644', '#ffaa00', '#4a9eff', '#6b7d99']
// critical → high → medium → low → info
```

---

## Text Colors

| Token | Hex | Usage |
|---|---|---|
| `--de-text-primary` | `#e0e6ed` | Headings, body text, default content |
| `--de-text-secondary` | `#8b95a7` | Labels, captions, table headers, meta info |
| `--de-text-tertiary` | `#5a6577` | Placeholders, disabled text, empty states |
| `--de-text-inverse` | `#0a0e1a` | Text placed on neon-accent backgrounds (e.g., primary button text) |
| `--de-text-link` | `#00f0ff` | Hyperlinks, inline links |

### Contrast Ratios (on `#0a0e1a`)

| Token | Hex | Ratio vs `#0a0e1a` | WCAG AA (4.5:1) |
|---|---|---|---|
| `--de-text-primary` | `#e0e6ed` | 14.8:1 | ✅ Pass |
| `--de-text-secondary` | `#8b95a7` | 6.2:1 | ✅ Pass |
| `--de-text-tertiary` | `#5a6577` | 3.1:1 | ❌ Large text / icons only |
| `--de-color-accent-primary` | `#00f0ff` | 11.9:1 | ✅ Pass |
| `--de-color-accent-secondary` | `#00ff88` | 13.1:1 | ✅ Pass |

---

## Border Colors

| Token | Value | Usage |
|---|---|---|
| `--de-border-subtle` | `rgba(0, 240, 255, 0.08)` | Card inner dividers, subtle separations |
| `--de-border-default` | `rgba(0, 240, 255, 0.12)` | Default card borders, input borders |
| `--de-border-strong` | `rgba(0, 240, 255, 0.25)` | Hover/focus borders, active card borders |
| `--de-border-separator` | `rgba(255, 255, 255, 0.06)` | Table row separators, list dividers |

All borders use cyan-tinted RGBA so glass cards blend with the neon identity. White-rgba for neutral separators.

---

## Glassmorphism Recipe

```css
background:     rgba(18, 24, 38, 0.70);
backdrop-filter: blur(12px);
border:         1px solid rgba(0, 240, 255, 0.10);
box-shadow:     0 4px 24px rgba(0, 0, 0, 0.40);
border-radius:  8px;
```

| Property | Token | Value |
|---|---|---|
| Background | `--de-glass-bg` | `rgba(18, 24, 38, 0.70)` |
| Background (hover) | `--de-glass-bg-hover` | `rgba(26, 33, 51, 0.80)` |
| Blur | `--de-glass-blur` | `12px` |
| Blur (heavy) | `--de-glass-blur-heavy` | `20px` |
| Border | `--de-glass-border` | `1px solid rgba(0, 240, 255, 0.10)` |
| Border (hover) | `--de-glass-border-hover` | `1px solid rgba(0, 240, 255, 0.25)` |
| Shadow | `--de-glass-shadow` | `0 4px 24px rgba(0, 0, 0, 0.40)` |
| Shadow (large) | `--de-glass-shadow-lg` | `0 8px 48px rgba(0, 0, 0, 0.55)` |

---

## Neon Glow Effects

Used on hover, active, and critical-state elements.

| Token | Value | Apply To |
|---|---|---|
| `--de-glow-accent` | `0 0 12px rgba(0, 240, 255, 0.40)` | Primary button hover, active nav item |
| `--de-glow-accent-strong` | `0 0 20px rgba(0, 240, 255, 0.60), 0 0 4px rgba(0, 240, 255, 0.80)` | Critical CTAs, scanning-in-progress indicator |
| `--de-glow-success` | `0 0 12px rgba(0, 255, 136, 0.40)` | Success badges, confirmed connections |
| `--de-glow-danger` | `0 0 12px rgba(255, 51, 102, 0.45)` | Critical severity badge, stop button |
| `--de-glow-warning` | `0 0 12px rgba(255, 170, 0, 0.40)` | Warning banner, medium severity |
| `--de-glow-inset` | `inset 0 0 8px rgba(0, 240, 255, 0.06)` | Input fields (subtle inner glow) |

---

## Terminal Console Colors

For the live scan console log output. Color-coded by log level.

| Log Level | Color | Hex |
|---|---|---|
| `INFO` | cyan | `#00f0ff` |
| `WARN` | amber | `#ffaa00` |
| `ERROR` | red | `#ff3366` |
| `CRITICAL` | danger red (bold) | `#ff3366` |
| `DEBUG` | muted blue-gray | `#6b7d99` |
| `SUCCESS` | neon green | `#00ff88` |
| Timestamp | secondary | `#5a6577` |
| Default text | light gray | `#c8d4e0` |

---

## Don't

- Don't introduce new hex values not in this palette.
- Don't use `--de-text-tertiary` for body text (fails WCAG AA on small text).
- Don't apply neon glows to static elements — reserve for interactive/critical states.
- Don't mix severity colors with semantic colors in the same context (e.g., don't use `--de-color-danger` for a "high" finding — use `--de-severity-high`).
