# DeepEye Scanner Suite — Typography Reference

> Inter for UI. JetBrains Mono for terminal/console. No other typefaces.

---

## Font Families

| Token | Stack | Usage |
|---|---|---|
| `--de-font-ui` | `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` | All UI text: headings, body, labels, buttons, inputs, tables, badges |
| `--de-font-mono` | `'JetBrains Mono', 'Fira Code', 'SF Mono', Menlo, Consolas, monospace` | Terminal console, code blocks, evidence snippets, CLI args, file paths, CVE IDs |

### Self-Hosting

Both fonts loaded as variable `.woff2` via `@font-face` in `tokens.css`. Serve from `/fonts/`:

```
web/public/fonts/Inter.woff2          # variable weight 100–900
web/public/fonts/JetBrainsMono.woff2  # variable weight 100–800
```

`font-display: swap` — text renders system font first, swaps when ready.

**Fallback chain:** Inter → system sans → Roboto → Segoe UI. JetBrains Mono → SF Mono → Menlo → Consolas.

---

## Type Scale

8-step modular scale. Base = `14px` (0.875rem).

| Token | rem | px | Usage |
|---|---|---|---|
| `--de-text-xs` | `0.6875rem` | 11px | Badge text, table cell meta, timestamps, micro-labels |
| `--de-text-sm` | `0.8125rem` | 13px | Terminal font size, secondary labels, small captions |
| `--de-text-base` | `0.875rem` | 14px | **Base body text**, table cells, input text, button text |
| `--de-text-md` | `1rem` | 16px | Card titles, section headings, modal body |
| `--de-text-lg` | `1.125rem` | 18px | Page section headers |
| `--de-text-xl` | `1.25rem` | 20px | Page titles |
| `--de-text-2xl` | `1.5rem` | 24px | Dashboard stat numbers, hero numbers |
| `--de-text-3xl` | `1.875rem` | 30px | Large display numbers |
| `--de-text-4xl` | `2.25rem` | 36px | Reserved — splash/onboarding hero |

---

## Font Weights

| Token | Weight | Usage |
|---|---|---|
| `--de-font-regular` | 400 | Body text, paragraphs, descriptions |
| `--de-font-medium` | 500 | Labels, buttons, table headers, nav items |
| `--de-font-semibold` | 600 | Card titles, section headings, stat labels |
| `--de-font-bold` | 700 | Page titles, critical numbers, `[CRITICAL]` log level |

---

## Line Heights

| Token | Value | Usage |
|---|---|---|
| `--de-leading-tight` | `1.25` | Headings, stat numbers, single-line elements |
| `--de-leading-normal` | `1.5` | Body text, table cells, form labels |
| `--de-leading-relaxed` | `1.75` | Descriptions, evidence text, remediation guides |

Terminal console: **1.6** line-height (hardcoded, not tokenized — terminal-specific).

---

## Letter Spacing

| Token | Value | Usage |
|---|---|---|
| `--de-tracking-tight` | `-0.01em` | Large headings (2xl+), stat numbers |
| `--de-tracking-normal` | `0` | Body text, descriptions |
| `--de-tracking-wide` | `0.025em` | Labels, small headings |
| `--de-tracking-wider` | `0.05em` | Button text, nav items |
| `--de-tracking-widest` | `0.1em` | Uppercase labels (status, section headers) — always paired with `text-transform: uppercase` |

---

## Type Specimens

### Page Title
```css
font-family: var(--de-font-ui);
font-size: var(--de-text-xl);        /* 20px */
font-weight: var(--de-font-bold);     /* 700 */
line-height: var(--de-leading-tight); /* 1.25 */
letter-spacing: var(--de-tracking-wide); /* 0.025em */
color: var(--de-text-primary);
```

### Section Header
```css
font-family: var(--de-font-ui);
font-size: var(--de-text-md);         /* 16px */
font-weight: var(--de-font-semibold); /* 600 */
line-height: var(--de-leading-tight);  /* 1.25 */
color: var(--de-text-primary);
```

### Card Title
```css
font-family: var(--de-font-ui);
font-size: var(--de-text-sm);          /* 13px */
font-weight: var(--de-font-semibold);  /* 600 */
text-transform: uppercase;
letter-spacing: var(--de-tracking-widest); /* 0.1em */
color: var(--de-text-secondary);
```

### Stat Number
```css
font-family: var(--de-font-ui);
font-size: var(--de-text-2xl);        /* 24px */
font-weight: var(--de-font-bold);      /* 700 */
line-height: var(--de-leading-tight);   /* 1.25 */
letter-spacing: var(--de-tracking-tight); /* -0.01em */
```

### Body Text
```css
font-family: var(--de-font-ui);
font-size: var(--de-text-base);         /* 14px */
font-weight: var(--de-font-regular);    /* 400 */
line-height: var(--de-leading-normal); /* 1.5 */
color: var(--de-text-primary);
```

### Label
```css
font-family: var(--de-font-ui);
font-size: var(--de-text-sm);           /* 13px */
font-weight: var(--de-font-medium);     /* 500 */
color: var(--de-text-secondary);
```

### Button Text
```css
font-family: var(--de-font-ui);
font-size: var(--de-text-base);          /* 14px */
font-weight: var(--de-font-medium);       /* 500 */
letter-spacing: var(--de-tracking-wider); /* 0.05em */
```

### Badge Text
```css
font-family: var(--de-font-ui);
font-size: var(--de-text-xs);            /* 11px */
font-weight: var(--de-font-semibold);    /* 600 */
text-transform: uppercase;
letter-spacing: var(--de-tracking-wide); /* 0.025em */
```

### Terminal / Code
```css
font-family: var(--de-font-mono);
font-size: var(--de-text-sm);            /* 13px */
font-weight: var(--de-font-regular);     /* 400 */
line-height: 1.6;
```

### Evidence Snippet
```css
font-family: var(--de-font-mono);
font-size: var(--de-text-xs);            /* 11px */
font-weight: var(--de-font-regular);     /* 400 */
line-height: var(--de-leading-normal);   /* 1.5 */
color: var(--de-text-secondary);
background: var(--de-bg-primary);
padding: var(--de-space-2) var(--de-space-3);
border-radius: var(--de-radius-sm);
```

---

## Inter Usage Rules

- Use for **everything except** terminal output, code blocks, and monospace data.
- Tabular figures: add `font-feature-settings: 'tnum'` to stat numbers and table numeric columns for stable alignment.
- Avoid `font-weight: 300` or below — too thin on dark backgrounds.

## JetBrains Mono Usage Rules

- Terminal console, log lines, code snippets, file paths, CVE IDs, CLI arguments.
- Never use for headings or body paragraphs.
- In terminal console: `font-size: 13px` (not rem) for consistent rendering.

---

## Accessibility

- Minimum body text: `--de-text-base` (14px). Never go below `--de-text-sm` (13px) for interactive text.
- `--de-text-xs` (11px) is for badges and meta only — always uppercase + semibold for legibility.
- Color contrast: see `palette.md` contrast table. Body text on `#0a0e1a` must be `--de-text-primary` or `--de-text-secondary`.
