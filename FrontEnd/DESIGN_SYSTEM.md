# Smart Strap — Design System Guide
### *"Earthy Pulse" — Warm, Organic, Approachable Medical UI*

> **Purpose**: This document defines the visual language, component patterns, and implementation rules for the Smart Strap web application. All future features and agent-built additions MUST follow this guide to maintain visual consistency.

---

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [Color System](#2-color-system)
3. [Typography](#3-typography)
4. [Icon System](#4-icon-system)
5. [Spacing & Layout](#5-spacing--layout)
6. [Component Library](#6-component-library)
7. [Animation Catalog](#7-animation-catalog)
8. [Chart Styling](#8-chart-styling)
9. [Toast Notifications](#9-toast-notifications)
10. [Do's and Don'ts](#10-dos-and-donts)

---

## 1. Design Philosophy

The Smart Strap UI is **warm, organic, and approachable** — designed to reduce the clinical intimidation typical of medical interfaces. Users are combat veterans with blast-induced hearing loss; the experience should feel **supportive and personal**, not sterile.

### Core Principles

| Principle | Description |
|-----------|-------------|
| **Warm surfaces** | Sand/parchment backgrounds instead of cold whites or blacks. Cards feel like paper, not metal. |
| **Teal life** | Deep teal (`#0d8a96`) is the primary accent — it's calming, clinical-appropriate, and carries trust. |
| **Personal voice** | Use "Hi, Yossi" not "Patient Dashboard". Use "your" not "the patient's" in patient views. |
| **Purposeful motion** | Animations are subtle and meaningful (pulse = haptic, slide-up = new content). No gratuitous effects. |
| **Data mono** | Numeric values (frequencies, percentages, scores) use the `Spline Sans Mono` typeface to visually separate data from prose. |

---

## 2. Color System

### CSS Variables

All colors are defined as CSS custom properties in `:root`. **Always use the variable, never hardcode hex values.**

#### Surfaces

| Variable | Hex | Usage |
|----------|-----|-------|
| `--bg-base` | `#ece3d6` | Page background |
| `--bg-card` | `#fffdf9` | Card surfaces |
| `--bg-card-hover` | `#f4efe7` | Hover states, segmented control backgrounds |
| `--bg-input` | `#faf7f1` | Input field backgrounds |

#### Text

| Variable | Hex | Usage |
|----------|-----|-------|
| `--text-primary` | `#25302f` | Headings, body text |
| `--text-secondary` | `#6f6a60` | Captions, labels, descriptions |
| `--text-muted` | `#a99f8e` | Chart labels, fine print, hints |

#### Primary — Deep Teal

| Variable | Hex | Usage |
|----------|-----|-------|
| `--primary-teal` | `#0d8a96` | Buttons, links, active states, primary accents |
| `--primary-teal-hover` | `#0a6b75` | Hover state for primary |
| `--primary-teal-light` | `rgba(13,138,150,0.12)` | Badge backgrounds, icon box tints |
| `--primary-teal-glow` | `rgba(13,138,150,0.15)` | Focus ring glow |

#### Semantic Colors

| Variable | Hex | Meaning |
|----------|-----|---------|
| `--accent-green` | `#2f8f6b` | Success, positive trends, good relief |
| `--accent-green-bg` | `#e7f4ed` | Green background tint |
| `--accent-amber` | `#c8861f` | Warning, needs attention |
| `--accent-amber-bg` | `#fcf2dd` | Amber background tint |
| `--accent-red` | `#c4503e` | Danger, low scores |

#### Borders

| Variable | Hex | Usage |
|----------|-----|-------|
| `--border-color` | `#e7ded2` | Card borders, table borders |
| `--border-color-light` | `#f1ebe1` | Inner dividers, config item separators |

### Color Pairing Rules

- **Text on `--bg-card`**: Use `--text-primary` for headings, `--text-secondary` for descriptions.
- **Text on teal/dark backgrounds** (login, game panel): Use `#fff` for headings, `rgba(255,255,255,0.78)` for body.
- **Data values**: Always `--primary-teal` in `--font-mono`.
- **Danger scores** (e.g. 3/10): Use `--accent-red` with `font-weight: 700`.
- **Success scores** (e.g. 9/10): Use `--accent-green` with `font-weight: 700`.

---

## 3. Typography

### Font Families

```css
--font-sans: 'Inter', sans-serif;     /* All UI text */
--font-mono: 'Spline Sans Mono', monospace;  /* Data values only */
```

### When to Use Each

| Font | Usage |
|------|-------|
| **Inter** | All headings, body text, labels, buttons, descriptions |
| **Spline Sans Mono** | Frequencies (e.g. "4000 Hz"), percentages ("94%"), scores ("8 / 10"), IDs ("#001"), countdown values |

### Type Scale

| Element | Font Spec | Example |
|---------|-----------|---------|
| Page heading | `600 28px Inter` | "Clinical Dashboard" |
| Section heading | `600 26px Inter` | "My Profile" |
| Card heading | `600 16–18px Inter` | "Your hearing" |
| Body text | `400 14–15px Inter` | Card descriptions |
| Label | `500 13px Inter` | Form labels |
| Badge text | `600 11–12px Inter` | Role badge |
| Muted hint | `400 11–12px Inter` | "Administrator access is managed separately." |
| Data value | `600 15px Spline Sans Mono` | "4000 Hz" |
| KPI value | `700 28–30px Inter` | "85%" |

### Google Fonts Import

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Spline+Sans+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

---

## 4. Icon System

### Font: Material Symbols Outlined

```html
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap" rel="stylesheet">
```

### Usage

```html
<span class="ms">icon_name</span>
```

The `.ms` class is defined in the CSS:
```css
.ms {
    font-family: 'Material Symbols Outlined';
    font-weight: normal;
    font-style: normal;
    line-height: 1;
    white-space: nowrap;
    -webkit-font-feature-settings: 'liga';
    -webkit-font-smoothing: antialiased;
}
```

### Icon Size Convention

| Context | Size | Example |
|---------|------|---------|
| Navigation brand | `24px` | `graphic_eq` |
| Card icon box | `28px` | `monitor_heart` |
| Button inline icon | `17–18px` | `arrow_forward`, `logout` |
| Alert/Toast icon | `18–22px` | `warning`, `check_circle` |

### Icon Semantic Mapping

| Icon Name | Meaning |
|-----------|---------|
| `graphic_eq` | Smart Strap brand / Normal mode |
| `monitor_heart` | Medical profile / audiogram |
| `vibration` | Device / Discreet mode |
| `rate_review` | Feedback |
| `insights` | Progress & statistics |
| `person` | Patient role |
| `stethoscope` | Clinician role |
| `warning` | Alert / attention needed |
| `check_circle` | Success / confirmed |
| `lock_clock` | Feedback locked / countdown |
| `arrow_back` | Navigation back |
| `arrow_forward` | Proceed / enter |
| `logout` | Log out |
| `play_arrow` / `stop` | Game controls |

### Rules

- ❌ **NEVER use emoji** (`🩺 🎮 📝 📊 🔒 ⚠️ ▶ ⏹`) as icons
- ✅ **ALWAYS use Material Symbols Outlined** with the `.ms` class
- ❌ **NEVER use filled/rounded variants** — only Outlined

---

## 5. Spacing & Layout

### Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | `7px` | Label margins, tight gaps |
| `sm` | `10–12px` | Input margins, inner gaps |
| `md` | `16–18px` | Card heading margins, grid gaps |
| `lg` | `22–24px` | Section spacing, card padding |
| `xl` | `30–32px` | Dashboard wrap padding, major sections |

### Content Width

```css
--content-max: 1080px;
```

All dashboard content should be wrapped in:
```html
<div class="dashboard-wrap">
    <!-- Content here -->
</div>
```

### Grid Patterns

```css
/* Two-column layout (most common) */
.grid-2col { grid-template-columns: 1fr 1fr; gap: 18px; }

/* Three-column KPI row */
.grid-3col { grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
```

Both collapse to single-column on screens ≤ 768px.

### Border Radius Scale

| Variable | Value | Usage |
|----------|-------|-------|
| `--radius` | `12px` | Buttons, inputs |
| `--radius-lg` | `20px` | Cards, game panel |
| `--radius-pill` | `20px` | Badges, pills |
| `--radius-icon` | `15px` | Icon boxes |

---

## 6. Component Library

### Cards

```html
<div class="card">
    <h3>Card Title</h3>
    <p>Card description text.</p>
</div>
```

Clickable variant:
```html
<div class="card clickable-card" onclick="...">
    <div class="card-icon-box teal"><span class="ms">icon_name</span></div>
    <h3 style="margin-top:16px;">Title</h3>
    <p style="margin-top:7px;">Description.</p>
</div>
```

Icon box tint classes: `.teal`, `.amber`, `.green`

### Buttons

```html
<!-- Primary (teal fill) -->
<button class="btn-primary">Save configuration</button>

<!-- Outline (border only) -->
<button class="btn-outline">Cancel</button>

<!-- Back navigation -->
<button class="btn-back" onclick="app.showView('view-patient')">
    <span class="ms">arrow_back</span>Back to dashboard
</button>

<!-- View button (table row) -->
<button class="btn-view" onclick="...">View</button>
```

### Inputs

```html
<div class="form-group">
    <label>Notch centre frequency (Hz)</label>
    <input type="number" value="4000">
</div>
```

All inputs use `--bg-input` background, `--border-color` border, `11px` radius.

### Segmented Control

```html
<div class="segmented-control">
    <button class="segment active" data-mode="normal">Normal</button>
    <button class="segment" data-mode="discreet">Discreet</button>
    <button class="segment" data-mode="training">Training</button>
</div>
```

### Status Badge

```html
<div class="status-badge">
    <span class="status-dot"></span>
    Strap connected · AA:BB:CC:01
</div>
```

### KPI Card

```html
<div class="kpi-card">
    <div class="kpi-label">Patient compliance</div>
    <div class="kpi-value large green">85%</div>
</div>
```

Value color classes: `.green`, `.teal`, `.dark`

### Alert Banner

```html
<div class="alert-banner amber">
    <span class="ms">warning</span>
    <span class="alert-text"><b>Needs attention</b> — description text.</span>
</div>
```

### Info Callout

```html
<div class="info-callout">
    Explanatory text with a teal-tinted background.
</div>
```

---

## 7. Animation Catalog

### `pulse-ring` — Concentric Pulse

```css
@keyframes pulse-ring {
    0%   { transform: scale(0.7); opacity: 0; }
    30%  { opacity: 0.5; }
    100% { transform: scale(1.25); opacity: 0; }
}
```

**Where**: Login hero (infinite, 2.6s), training game haptic event (infinite, 1s).
**What it communicates**: Haptic sensation, alive/active system.

### `slide-up-fade` — View Entrance

```css
@keyframes slide-up-fade {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
```

**Where**: Every `.view` when it becomes `.active`.
**What it communicates**: New content arriving, spatial awareness.

### Card Hover

Applied via `.clickable-card:hover`:
```css
transform: translateY(-4px);
border-color: var(--primary-teal);
box-shadow: var(--shadow-card-hover);
```

**What it communicates**: Interactivity, inviting the click.

### Button Hover

Applied via `.btn-primary:hover`:
```css
transform: translateY(-1px);
```

Subtle, not distracting. Button presses use `:active { transform: translateY(0); }`.

### Rules for New Animations

1. **Duration**: Keep between 0.15s (micro-feedback) and 0.35s (view transitions). Max 2.6s for ambient loops.
2. **Easing**: Use `ease` or `ease-out`. Never `linear` for UI elements.
3. **Purpose**: Every animation must answer "what does this tell the user?" If you can't answer, don't animate.
4. **Performance**: Only animate `transform` and `opacity`. Never animate `width`, `height`, or `top/left`.

---

## 8. Chart Styling

We use **Chart.js** for all data-driven charts. Charts render real data from the database, so inline SVGs are NOT appropriate for data visualization.

### Warm Palette Configuration

```javascript
const chartColors = {
    teal:          '#0d8a96',       // Primary data lines
    green:         '#2f8f6b',       // Positive trends
    red:           '#c4503e',       // Danger/highlight points
    textMuted:     '#a99f8e',       // Axis labels
    textSecondary: '#6f6a60',       // Legend text
    grid:          '#e7ded2',       // Major grid lines
    gridLight:     '#f1ebe1',       // Minor grid lines
    cardBg:        '#fffdf9'        // Background (inherited from card)
};
```

### Shared Defaults

```javascript
Chart.defaults.color = '#a99f8e';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.plugins.legend.labels.usePointStyle = true;
```

### Standard Chart Options

```javascript
scales: {
    y: {
        grid: { color: '#f1ebe1' },
        ticks: { color: '#a99f8e' }
    },
    x: {
        grid: { color: '#f1ebe1' },   // or display: false for bar charts
        ticks: { color: '#a99f8e' }
    }
},
plugins: {
    legend: { labels: { color: '#6f6a60' } }
}
```

### Key Data Point Highlighting

For audiogram charts, highlight the 4kHz notch point with red:
```javascript
pointBackgroundColor: (ctx) => ctx.dataIndex === 5 ? '#c4503e' : '#0d8a96',
pointRadius: (ctx) => ctx.dataIndex === 5 ? 7 : 5
```

### Bar Chart Graduated Opacity

For training accuracy bars, use increasing opacity to show progression:
```javascript
backgroundColor: [
    'rgba(13, 138, 150, 0.55)',
    'rgba(13, 138, 150, 0.7)',
    'rgba(13, 138, 150, 0.85)',
    'rgba(13, 138, 150, 1)'
]
```

---

## 9. Toast Notifications

### Usage (JavaScript)

```javascript
showToast('Message text');                    // Success (default)
showToast('Something went wrong', 'error');   // Error
```

### Styling

- **Success**: Sage-green gradient (`#1a5c42 → #2f8f6b`) with `check_circle` icon
- **Error**: Terracotta gradient (`#6b2e24 → #c4503e`) with `error` icon
- **Duration**: 3.5 seconds
- **Position**: Bottom-right corner
- **Animation**: Slide up + fade in

### Adding New Toast Types

To add a new type (e.g. `info`):
1. Add a `.toast.toast-info` class in `styles.css`
2. Use the teal gradient: `linear-gradient(135deg, #0a4a53, #0d8a96)`
3. Use `info` Material Symbol icon

---

## 10. Do's and Don'ts

### ✅ DO

- Use CSS variables for all colors — `var(--primary-teal)`, not `#0d8a96`
- Use the `.card` class for all content containers
- Use `.ms` class for all icons
- Use `Spline Sans Mono` for all numeric/data values
- Wrap dashboard content in `.dashboard-wrap`
- Include `.btn-back` navigation on all sub-views
- Use `slide-up-fade` animation on all views
- Keep card padding at `24px`
- Use `grid-2col` or `grid-3col` for layouts
- Test responsive behavior at 768px breakpoint

### ❌ DON'T

- Use emoji as icons (🩺 📊 🔒 etc.)
- Use dark-mode colors or `rgba(255,255,255,0.1)` borders on content views
- Use `backdrop-filter: blur()` on content cards (only for login auth card)
- Use `glass-card` class (deprecated — use `.card` instead)
- Hardcode colors outside of `:root` variables
- Create animations > 0.35s for UI transitions
- Use Chart.js default blue/orange colors
- Use `<table>` elements — use CSS grid patterns instead (`.patient-table-header` + `.patient-table-row`)
- Add an Admin tab to the main login screen (admin access is separate)

---

## File Structure Reference

```
FrontEnd/
├── index.html           ← Main SPA (all views)
├── DESIGN_SYSTEM.md     ← This file
├── css/
│   └── styles.css       ← All styles (design tokens + components)
└── js/
    ├── api.js           ← Mock API (backend simulation)
    └── app.js           ← Application logic, routing, charts, game
```

---

*Last updated: June 2026 · Design: "Earthy Pulse" v1.0*
