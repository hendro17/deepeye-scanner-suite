# DeepEye Scanner Suite — Layout Specifications

> Grid system, spacing, responsive breakpoints, shell layout.

---

## 1. App Shell

```
┌──────────────────────────────────────────────────────────┐
│ SIDEBAR │                TOPBAR                            │
│ (260px) │  (56px height)                                   │
├─────────┼─────────────────────────────────────────────────┤
│         │                                                   │
│  Logo   │             MAIN CONTENT AREA                     │
│  ─────  │     (max-width: 1600px, centered)                 │
│  Nav    │                                                   │
│  items  │     ┌─────────┐ ┌─────────┐ ┌─────────┐         │
│         │     │  Card   │ │  Card   │ │  Card   │          │
│  ─────  │     └─────────┘ └─────────┘ └─────────┘          │
│  Status │     ┌──────────────────────────────┐              │
│         │     │       Full-width card         │              │
│         │     └──────────────────────────────┘              │
│  260px  │                                                   │
└─────────┴──────────────────────────────────────────────────┘
```

### Shell Dimensions

| Element | Token | Value |
|---|---|---|
| Sidebar width | `--de-sidebar-width` | `260px` |
| Sidebar collapsed | `--de-sidebar-collapsed` | `64px` |
| Topbar height | `--de-topbar-height` | `56px` |
| Content max-width | `--de-content-max-width` | `1600px` |

### CSS Grid

```css
.de-app-shell {
  display: grid;
  grid-template-columns: var(--de-sidebar-width) 1fr;
  grid-template-rows: var(--de-topbar-height) 1fr;
  grid-template-areas:
    "sidebar topbar"
    "sidebar main";
  height: 100vh;
  overflow: hidden;
}

.de-app-shell--collapsed {
  grid-template-columns: var(--de-sidebar-collapsed) 1fr;
}
```

---

## 2. Sidebar

```
┌────────────────────────┐
│  [logo] DeepEye        │  ← 56px height row, glass bg
│         Scanner Suite   │
├────────────────────────┤
│                        │
│  ▸ Dashboard           │  ← nav item, 40px height
│  ▸ New Scan            │
│  ▸ Scan Live           │
│  ▸ Findings            │
│  ▸ Reports             │
│  ▸ Settings            │
│                        │
├────────────────────────┤  ← flex: 1 (pushes status to bottom)
│  SYSTEM STATUS         │  ← section label
│  ● API: Online         │
│  ● Engine: Ready       │
│  CVE DB: 2024-08-20    │
│  RAG: Indexed          │
│                        │
│  [user@host]           │  ← bottom, 40px height
└────────────────────────┘
 260px width
```

- Background: `var(--de-bg-secondary)`
- Right border: `1px solid var(--de-border-separator)`
- Nav items: `padding: 0 16px`, `height: 40px`, icon (20px) + label gap `8px`
- Active nav item: left border `2px solid var(--de-color-accent-primary)`, text color primary, background `rgba(0, 240, 255, 0.05)`
- Hover: background `rgba(255, 255, 255, 0.03)`
- Collapsed: hide labels, show icon only, center icon

---

## 3. Topbar

```
┌──────────────────────────────────────────────────────────┐
│ [≡]  Page Title                          [🔍] [⚙] [👤]   │
└──────────────────────────────────────────────────────────┘
 56px height
```

- Background: `var(--de-glass-bg)` with `backdrop-filter: blur(12px)`
- Bottom border: `1px solid var(--de-border-separator)`
- Left: collapse toggle (hamburger) `32px × 32px` + page title
- Right: search input (`width: 240px`), settings icon, user avatar

---

## 4. Main Content Area

```css
.de-main-content {
  grid-area: main;
  overflow-y: auto;
  padding: var(--de-space-5); /* 24px */
}

.de-content-inner {
  max-width: var(--de-content-max-width); /* 1600px */
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--de-space-5); /* 24px between sections */
}
```

### Content Padding

| Breakpoint | Padding | Gutter |
|---|---|---|
| Mobile (<640px) | 16px | 16px |
| Tablet (640–1023px) | 24px | 24px |
| Desktop (1024–1599px) | 24px | 24px |
| Wide (≥1600px) | 32px | 32px |

---

## 5. Grid System

### 12-Column Grid

```css
.de-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--de-space-4); /* 16px between columns */
}
```

### Common Column Spans

| Layout | Columns | Gap | Use Case |
|---|---|---|---|
| 3-up cards | `repeat(3, 1fr)` | 16px | Dashboard stat cards |
| 2-up + 1-up | `8fr 4fr` | 16px | Chart + side panel |
| 1-up full | `1fr` | — | Tables, terminal |
| 2-up | `1fr 1fr` | 16px | Settings sections |
| 4-up | `repeat(4, 1fr)` | 16px | Provider status cards |

### Responsive Grid Behavior

```css
.de-grid--cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--de-space-4);
}

@media (max-width: 1280px) { .de-grid--cards { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px)  { .de-grid--cards { grid-template-columns: 1fr; } }
```

---

## 6. Card Layout

### Glass Card Container

```css
.de-card {
  background: var(--de-glass-bg);
  backdrop-filter: blur(var(--de-glass-blur));
  -webkit-backdrop-filter: blur(var(--de-glass-blur));
  border: var(--de-glass-border);
  border-radius: var(--de-radius-lg); /* 8px */
  box-shadow: var(--de-glass-shadow);
  padding: var(--de-space-4); /* 16px */
  display: flex;
  flex-direction: column;
  gap: var(--de-space-3); /* 12px internal */
  transition: border var(--de-transition-base), box-shadow var(--de-transition-base);
}

.de-card--hoverable:hover {
  border: var(--de-glass-border-hover);
  box-shadow: var(--de-glass-shadow-lg);
}
```

### Card Header Pattern

```
┌────────────────────────────────────────┐
│ CARD TITLE                    [action] │  ← header row
├────────────────────────────────────────┤
│                                         │
│  content                                 │
│                                         │
└────────────────────────────────────────┘
```

- Header: `display: flex`, `justify-content: space-between`, `align-items: center`
- Title: card title typography (uppercase, secondary color, `13px`)
- Action: icon button or small button, right-aligned

---

## 7. Spacing Scale

| Token | Value | Usage |
|---|---|---|
| `--de-space-0` | `0` | Reset |
| `--de-space-1` | `4px` | Icon-text gap, badge padding, tight gaps |
| `--de-space-2` | `8px` | Component-internal gaps, input padding-y |
| `--de-space-3` | `12px` | Card internal gap, badge-to-text, checkbox gap |
| `--de-space-4` | `16px` | Card padding, grid gap, section-internal |
| `--de-space-5` | `24px` | Content padding, section gap, card-to-card |
| `--de-space-6` | `32px` | Page section gap, sidebar section gap |
| `--de-space-7` | `48px` | Large page section separation |
| `--de-space-8` | `64px` | Reserved for hero/onboarding spacing |

### Spacing Rules

- **Always use tokens** — no magic numbers.
- Between elements within a card: `--de-space-2` or `--de-space-3`.
- Between cards in a grid: `--de-space-4`.
- Between page sections: `--de-space-5` or `--de-space-6`.
- Form field vertical gap: `--de-space-3` (12px).

---

## 8. Responsive Breakpoints

| Name | Min Width | Tailwind Equiv | Behavior |
|---|---|---|---|
| `xs` | 0px | — | Mobile, single column, sidebar hidden |
| `sm` | 640px | `sm:` | Small tablet, 2-column grids |
| `md` | 768px | `md:` | Tablet, sidebar visible (collapsed) |
| `lg` | 1024px | `lg:` | Desktop, sidebar expanded, 3-col grids |
| `xl` | 1280px | `xl:` | Large desktop, 4-col grids |
| `2xl` | 1536px | `2xl:` | Wide, max content width enforced |

### Sidebar Behavior

| Width | Sidebar State |
|---|---|
| < 768px | Hidden — toggle via topbar hamburger, slides over as drawer |
| 768–1023px | Collapsed (64px, icon-only) |
| ≥ 1024px | Expanded (260px, full labels) |

---

## 9. Table Layout

```css
.de-table-wrapper {
  overflow-x: auto;
  border-radius: var(--de-radius-lg);
}

.de-table {
  width: 100%;
  border-collapse: collapse;
}

.de-table th {
  text-align: left;
  padding: var(--de-space-2) var(--de-space-3);
  background: rgba(0, 240, 255, 0.03);
  border-bottom: 1px solid var(--de-border-default);
  /* label typography */
}

.de-table td {
  padding: var(--de-space-2) var(--de-space-3);
  border-bottom: 1px solid var(--de-border-separator);
}

.de-table tr:hover td {
  background: rgba(0, 240, 255, 0.02);
}
```

### Row Heights

| Row Type | Height | Padding |
|---|---|---|
| Compact | `36px` | `8px 12px` |
| Default | `44px` | `12px 16px` |
| Expanded detail | `auto` | `16px` |

---

## 10. Terminal Layout

```css
.de-terminal {
  height: 100%;
  min-height: 400px;
  background: var(--de-terminal-bg);
  border: var(--de-glass-border);
  border-radius: var(--de-radius-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.de-terminal-header {
  height: 40px;
  border-bottom: 1px solid var(--de-border-default);
  padding: 0 var(--de-space-3);
}

.de-terminal-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--de-terminal-padding);
  font-family: var(--de-font-mono);
  font-size: var(--de-terminal-font-size);
  line-height: var(--de-terminal-line-height);
}
```

Terminal fills available vertical space. `flex: 1` in the main content area. Header bar (40px) is fixed; body scrolls.

---

## 11. Modal Layout

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
  padding: var(--de-space-5);
}

.de-modal {
  background: var(--de-bg-elevated);
  border: var(--de-glass-border);
  border-radius: var(--de-radius-xl);
  box-shadow: var(--de-glass-shadow-lg);
  width: 100%;
  max-width: 560px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}
```

### Modal Sizes

| Size | Max Width | Usage |
|---|---|---|
| Small | 400px | Confirm dialogs, quick actions |
| Medium | 560px | Default, forms, settings sub-panels |
| Large | 800px | Complex forms, multi-step wizards |
| XLarge | 1100px | Evidence detail, report preview |

---

## 12. Form Layout

```css
.de-form {
  display: flex;
  flex-direction: column;
  gap: var(--de-space-3); /* 12px between fields */
}

.de-form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--de-space-4);
}
```

| Pattern | Gap | Layout |
|---|---|---|
| Field stack | 12px vertical | Single column |
| Two-up fields | 16px horizontal | `grid-template-columns: 1fr 1fr` |
| Label + input | 4px vertical | Label above input |
| Checkbox group | 12px vertical | Stack with 8px horizontal label gap |

Label: `--de-text-sm`, `--de-font-medium`, `--de-text-secondary`. Input: `--de-text-base`, height `36px`.

---

## 13. Scrollbar Styling

```css
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 240, 255, 0.15);
  border-radius: var(--de-radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 240, 255, 0.30);
}

/* Terminal scrollbar — slightly more visible */
.de-terminal-body::-webkit-scrollbar-thumb {
  background: rgba(0, 240, 255, 0.20);
}
```

---

## 14. Z-Index Layering

| Layer | Token | Value | Elements |
|---|---|---|---|
| Base | `--de-z-base` | 0 | Cards, tables, content |
| Dropdown | `--de-z-dropdown` | 100 | Select menus, dropdown panels |
| Sticky | `--de-z-sticky` | 200 | Sticky table headers, sticky toolbars |
| Overlay | `--de-z-overlay` | 300 | Slide-over panels, drawers |
| Modal | `--de-z-modal` | 1000 | Modal dialogs |
| Toast | `--de-z-toast` | 2000 | Toast notifications |
| Tooltip | `--de-z-tooltip` | 3000 | Hover tooltips (highest) |
