---
name: Institutional Forex Engine
colors:
  surface: '#0a141e'
  surface-dim: '#0a141e'
  surface-bright: '#303a45'
  surface-container-lowest: '#050f18'
  surface-container-low: '#121d26'
  surface-container: '#16212a'
  surface-container-high: '#212b35'
  surface-container-highest: '#2c3640'
  on-surface: '#d9e3f1'
  on-surface-variant: '#c2c6d6'
  inverse-surface: '#d9e3f1'
  inverse-on-surface: '#27313c'
  outline: '#8c909f'
  outline-variant: '#424754'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e6a'
  primary-container: '#4d8eff'
  on-primary-container: '#00285d'
  inverse-primary: '#005ac2'
  secondary: '#c1c7d3'
  on-secondary: '#2b313a'
  secondary-container: '#434954'
  on-secondary-container: '#b3b8c5'
  tertiary: '#ffb786'
  on-tertiary: '#502400'
  tertiary-container: '#df7412'
  on-tertiary-container: '#461f00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#dde2f0'
  secondary-fixed-dim: '#c1c7d3'
  on-secondary-fixed: '#161c25'
  on-secondary-fixed-variant: '#414751'
  tertiary-fixed: '#ffdcc6'
  tertiary-fixed-dim: '#ffb786'
  on-tertiary-fixed: '#311400'
  on-tertiary-fixed-variant: '#723600'
  background: '#0a141e'
  on-background: '#d9e3f1'
  surface-variant: '#2c3640'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  tabular-lg:
    fontFamily: JetBrains Mono
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  tabular-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  tabular-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-compact: 0.5rem
  margin: 1.5rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system delivers a calm, high-precision visual environment engineered for automated foreign exchange trading. The aesthetic rejects speculative hype and visual clutter in favor of institutional-grade operational clarity, emotional composure, and quantitative rigor. Designed for professional traders and systematic capital allocators, the interface prioritizes immediate legibility, rapid risk assessment, and frictionless telemetry over decorative trends.

The visual style merges utilitarian minimalism with systematic enterprise precision. A foundational dark mode anchors high-density data visualizations, execution blotters, and real-time streaming rates against deep, non-reflective surfaces. Visual hierarchy is established via strict tonal relationships, disciplined optical margins, and structured tabular typography rather than aggressive depth or gratuitous animations.

## Colors

The palette is engineered around visual stability and unambiguous semantic signals. The primary dark environment is anchored by `#0B0F14` at the base canvas, stepping up to `#121821` for elevated surfaces and analytical cards, bounded by structural `#1F2933` borders. Text hierarchy maintains crisp legibility through primary `#E5E7EB` and secondary `#9CA3AF`.

Actionable elements and focal metrics utilize institutional blue (`#3B82F6` dark, `#2563EB` light). 

Financial telemetry follows strict performance and accessibility rules:
- **Profit / In-the-Money**: `#22C55E` in dark mode (`#16A34A` in light mode). Must always be paired with explicit visual indicators (`+` prefix and `▲` directional glyph).
- **Loss / At-Risk**: `#EF4444` in dark mode (`#DC2626` in light mode). Must always be paired with explicit visual indicators (`-` prefix and `▼` directional glyph).
- **Neutral / Par**: `#6B7280` across both modes, used for flat executions, break-even fills, and zero-delta states.

Light mode shifts the canvas to `#F7F8FA`, cards to `#FFFFFF`, and structural boundaries to `#E5E7EB`, ensuring full visual parity across environmental shifts without degrading data scan rates.

## Typography

Typography enforces a strict division between interface orientation and quantitative assessment.

`Inter` governs all standard user interface layers, administrative headers, notifications, and navigation labels. Its neutral geometry prevents visual fatigue during prolonged algorithmic monitoring sessions. Structural tracking is tightened slightly on display layers to maintain density and expanded on upper-case micro-labels for rapid legibility.

All pricing arrays, exchange rates, order book depths, lot volumes, and execution timestamps mandate `JetBrains Mono` with tabular lining figures enabled (`tnum`). This prevents visual shifting during live web-socket price updates, ensuring absolute column alignment across streaming execution feeds and depth charts.

## Layout & Spacing

The layout is structured around an uncompromising 8px baseline grid with an internal 4px half-step for dense financial components. 

Workspace views utilize a 12-column adaptive grid capable of transitioning between analytical dashboards and modular multi-monitor execution docks. 
- Desktop screens (1280px and above) implement a standard `1.5rem` canvas margin with flexible `1rem` column gutters, allowing simultaneous rendering of charting surfaces, live depth ladders, and position logs.
- High-density telemetry sections (such as order blotters or currency quote matrices) compress to `gutter-compact` (`0.5rem`) to eliminate dead space.
- Tablet viewports (768px to 1279px) reflow into an 8-column layout with fixed side navigation folding into an icon rail.
- Mobile viewports (below 768px) transition to a 4-column flow with a strict `1rem` canvas margin, stacking execution controls into persistent anchored bottom sheets.

## Elevation & Depth

Visual depth is communicated primarily through flat tonal stacking and low-contrast borders rather than diffuse drop shadows. This prevents optical noise from distorting complex data visualizations and chart overlays.

1. **Base Layer (Level 0)**: The primary application background (`#0B0F14`) hosts global navigation, status bars, and canvas boundaries.
2. **Surface Layer (Level 1)**: Trading panels, chart containers, and card modules utilize `#121821` with a continuous 1px solid border (`#1F2933`). No drop shadow is applied at this level.
3. **Interactive & Flyout Layer (Level 2)**: Dropdown menus, tooltips, and modal confirmations remain on `#121821` but introduce a sharp, low-spread ambient occlusion shadow (`0 4px 20px -2px rgba(0, 0, 0, 0.65)`) with an accented upper border highlight (`rgba(255, 255, 255, 0.05)`) to cleanly separate floating actions from streaming background cards.

## Shapes

The design system maintains geometric precision with controlled corner radii to balance modern software tactility with tabular data density. 

Structural containers, primary analytical cards, and viewport modules employ an exact 12px radius (`rounded-xl` within this base scale). Smaller interactive nodes—such as form controls, status pills, and contextual buttons—use an 8px base radius (`rounded-md`). Small internal data tags and micro-indicators resolve at 4px (`rounded-sm`), preventing overlapping curves in high-density data tables.

## Components

### Buttons
- **Primary Action (Execute / Deploy)**: Solid `#3B82F6` fill with `#FFFFFF` text. 8px border radius, 36px standard height (`space-md` horizontal padding). Hover transitions to `#2563EB` with a crisp 150ms ease. Focus states leverage a 2px outer ring offset by 2px `#0B0F14`.
- **Secondary / Utility**: Transparent background with a 1px `#1F2933` border and `#E5E7EB` text. Active states trigger `#121821` background fill.
- **Directional Quick-Trade**: Dedicated Buy (`#22C55E` border/tint) and Sell (`#EF4444` border/tint) split buttons featuring uppercase micro-labels and embedded tabular quote pricing.

### Cards & Panels
- Constructed using `#121821` background, 12px border radius, and a 1px structural outline of `#1F2933`. 
- Header bars within cards are strictly 44px tall, demarcated by a 1px bottom border, housing clear Inter Semibold title groupings and trailing tabular control toggles.

### Status Chips & Badges
- Compact 20px height with 4px border radius.
- **Profit / Positive Delta**: 10% opacity `#22C55E` background, `#22C55E` text, formatted strictly as `+0.42% ▲` using `JetBrains Mono`.
- **Loss / Drawdown**: 10% opacity `#EF4444` background, `#EF4444` text, formatted strictly as `-1.18% ▼` using `JetBrains Mono`.
- **Bot State / Neutral**: 10% opacity `#6B7280` background with `#9CA3AF` text and a 6px static status dot indicating socket connectivity.

### Input Fields & Controls
- 36px height with 8px border radius, `#0B0F14` interior background, and `#1F2933` border. Text renders in `#E5E7EB` with `#6B7280` placeholder values. 
- Active focus state shifts the border to `#3B82F6` with zero glow. Financial numeric fields are fixed to `JetBrains Mono` and include pinned trailing currency units (e.g., `USD`, `EUR`).

### Execution Blotters & Data Tables
- Row height fixed at 36px for dense scans. Border-bottom is 1px `#1F2933`.
- Hovering over an order row triggers an instantaneous `#182230` background highlight across the full row. Numeric telemetry columns right-align without exception.