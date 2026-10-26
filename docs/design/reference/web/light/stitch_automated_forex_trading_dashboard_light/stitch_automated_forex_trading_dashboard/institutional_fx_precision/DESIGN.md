---
name: Institutional FX Precision
colors:
  surface: '#f9f9ff'
  surface-dim: '#d3daea'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f0f3ff'
  surface-container: '#e7eefe'
  surface-container-high: '#e2e8f8'
  surface-container-highest: '#dce2f3'
  on-surface: '#151c27'
  on-surface-variant: '#434655'
  inverse-surface: '#2a313d'
  inverse-on-surface: '#ebf1ff'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0053db'
  primary: '#004ac6'
  on-primary: '#ffffff'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#b4c5ff'
  secondary: '#006e2d'
  on-secondary: '#ffffff'
  secondary-container: '#7cf994'
  on-secondary-container: '#007230'
  tertiary: '#ae0010'
  on-tertiary: '#ffffff'
  tertiary-container: '#d52022'
  on-tertiary-container: '#ffecea'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#7ffc97'
  secondary-fixed-dim: '#62df7d'
  on-secondary-fixed: '#002109'
  on-secondary-fixed-variant: '#005320'
  tertiary-fixed: '#ffdad6'
  tertiary-fixed-dim: '#ffb4ab'
  on-tertiary-fixed: '#410002'
  on-tertiary-fixed-variant: '#93000b'
  background: '#f9f9ff'
  on-background: '#151c27'
  surface-variant: '#dce2f3'
typography:
  display:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0em
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.02em
  caption:
    fontFamily: Inter
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 12px
    letterSpacing: 0.03em
  data-lg:
    fontFamily: JetBrains Mono
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.02em
  data-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: -0.01em
  data-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '400'
    lineHeight: 14px
    letterSpacing: 0em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-dense: 0.5rem
  margin: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style

This design system targets tier-1 liquidity providers, institutional FX dealers, quantitative desks, and corporate treasuries executing high-notional transactions. The primary ethos is absolute regulatory clarity, zero latency perception, and uncompromising precision.

Drawing inspiration from Bloomberg terminal density refined through modern enterprise standards, the visual aesthetic is **Corporate / Modern** with high-density utilitarian polish. It discards decorative fluff in favor of structural grid balance, crisp border demarcations, and precise numeric legibility. The interface evokes trust, calm under volatile market conditions, and operational resilience.

## Colors

The palette is engineered specifically for low visual fatigue during extended multi-monitor trading sessions.

- **Canvas & Surfaces:**
  - Application Canvas: `#F7F8FA` provides an off-white, anti-glare foundation.
  - Surface Containers / Modules: `#FFFFFF` creates a clean, crisp focal plane for actionable components and data tables.
  - Panel Dividers & Borders: `#E5E7EB` delivers crisp 1px structural framing without high-contrast distraction.

- **Typography & Content:**
  - Primary Text: `#111827` (high contrast, WCAG AAA compliant for critical quotes).
  - Secondary / Metadata Text: `#6B7280` for labels, lot size units, timestamps, and order statuses.

- **Accents & Telemetry:**
  - Brand Blue (`#2563EB`): Primary callouts, active tabs, focused states, and execution CTAs.
  - Buy / Positive Yield (`#16A34A`): Long positions, profit indicators, and positive spread deltas.
  - Sell / Negative Yield (`#DC2626`): Short positions, drawdown, stop-loss triggers, and negative tick deltas.
  - Unchanged / Flat (`#6B7280`): Stale prices and neutral balances.

## Typography

The typographic hierarchy implements a dual-font structure:

- **Inter** governs all UI copy, modal headers, navigation, form labels, and status annotations. Tabular figures (`tnum`) should be enabled across all Inter styles by default.
- **JetBrains Mono** is reserved exclusively for numerical financial figures: bid/ask quotes, pips, order book depth levels, filled quantities, notionals, PnL tickers, and millisecond execution timestamps. This guarantees fixed-width vertical alignment across dynamic market ladders.

### Micro-Typographic Rules
- For currency pair quotes, format base pips in `data-md` or `data-lg`, with large visual emphasis on the dealing pip numbers (e.g., standard pip display where the 3rd and 4th decimals are enlarged).
- Use strictly uppercase styling for ISO currency codes (e.g., `EUR/USD`, `USD/JPY`) paired with `label-sm`.

## Layout & Spacing

The layout is anchored on an institutional 8px base grid, scalable into a dense 4px sub-grid for high-frequency trading modules (DOM ladders, blotters, and order books).

### Viewport Strategy
- **Desktop (>= 1440px):** 24-column fluid CSS grid layout or multi-window tile manager. Gutters default to `gutter-dense` (8px) within functional trading suites to maximize vertical viewport utilization. Outer margins are fixed at `16px`.
- **Laptop / Compact Workstation (1024px - 1439px):** 12-column responsive layout. Modules auto-collapse into segmented panels or tabbed card arrays.
- **Mobile / Tablet Execution Oversight (< 1024px):** Single-column stack with persistent bottom-pinned execution bar and floating order book summary.

Padding within components should remain compact (`space-xs` and `space-sm`) to support dense data presentation without overlapping boundaries.

## Elevation & Depth

To maximize cognitive speed and reduce rendering overhead, this design system avoids heavy blurred drop shadows and multi-tiered ambient glows. Depth is defined through **low-contrast outlines** and subtle surface separation.

- **Level 0 (Canvas):** `#F7F8FA`
- **Level 1 (Card & Module Shells):** `#FFFFFF` bounded by a 1px solid border of `#E5E7EB`. No shadow.
- **Level 2 (Popovers, Select Menus, Dropdown Ladders):** `#FFFFFF` bounded by `#E5E7EB` with a crisp micro-shadow: `0 4px 12px -2px rgba(17, 24, 39, 0.08)`.
- **Level 3 (Modal Confirmation Windows, Liquidity Routing Overlays):** `#FFFFFF` enclosed in `#D1D5DB` with an ambient containment shadow: `0 12px 28px -4px rgba(17, 24, 39, 0.12)`.

## Shapes

The design system standardizes on crisp geometric containers. The base roundedness token of `2` provides:
- Core UI elements (inputs, select fields, buttons, badges): `0.5rem` (8px).
- Structural containers & analytical cards: `0.75rem` (12px) border radius to establish clearly defined module regions.
- Micro badges, status pills, and directional tags: `0.25rem` (4px).

Pill shapes are strictly restricted to state pills (e.g., "LIVE", "CONNECTED", "REJECTED"). Precision analytical tools maintain structured, non-distracting rounded corners.

## Components

### Buttons & Trading Triggers
- **Primary / Dealing CTAs:** Flat fill `#2563EB` with `#FFFFFF` label, height 36px (or 44px for one-click trading execution tiles). Hover: `#1D4ED8`. Active: `#1E40AF`.
- **Buy / Bid Button:** `#16A34A` background, white bold numeric typography, incorporating an upward indicator `▲`.
- **Sell / Ask Button:** `#DC2626` background, white bold numeric typography, incorporating a downward indicator `▼`.
- **Secondary / Utility Actions:** White surface with 1px `#E5E7EB` border, `#111827` text. Hover: `#F9FAFB` with border `#D1D5DB`.

### Input Fields & Order Entry Steppers
- Height: 32px (compact data entry) or 36px (standard forms).
- Background: `#FFFFFF`, border: 1px solid `#E5E7EB`, text: `#111827` (`Inter` for asset search, `JetBrains Mono` for quantity/limit prices).
- Focus state: 1px solid `#2563EB` with an external 2px ring at 20% opacity (`#2563EB33`).
- Incremental quick-steppers (`+100k`, `+1M`, `Max`) styled as secondary compact tags within input borders.

### Data Blotters & Order Books
- Headers: `11px` uppercase `Inter`, `#6B7280`, 28px row height, border-bottom 1px solid `#E5E7EB`.
- Data Rows: Alternating hover state with `#F9FAFB`. PnL columns rendered with `JetBrains Mono` featuring explicit `+` and `▲` in `#16A34A` for gains, or `-` and `▼` in `#DC2626` for losses.
- Depth Visualizer: Subtle horizontal bar fill with `#16A34A15` for bid depth and `#DC262615` for ask depth.

### Cards & Module Containers
- Solid `#FFFFFF` background with 12px corner radius and a 1px `#E5E7EB` perimeter border.
- Card Header: 36px height containing title in `headline-sm`, trailing tools (minimize, pop-out, configure), and a 1px border-bottom divider separating the card body.

### Status Badges & Chips
- PnL / Directional Badges: Tinted backgrounds with high-contrast text (`#16A34A1A` fill with `#16A34A` text; `#DC26261A` fill with `#DC2626` text).
- Engine Health: Small 6px solid dot with `#16A34A` (Fix Engine Active) or `#6B7280` (Idle/Standby).