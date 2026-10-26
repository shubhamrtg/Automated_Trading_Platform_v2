# Automated Trading Platform (Phase 1)

## What This Is
A strategy-agnostic, instrument-agnostic automated forex and CFD trading platform built for individual use. One engine runs identical deterministic strategy code across backtest, paper trading, and live execution; only the data source and execution layer change.

Phase 1 delivers the core trading engine, historical backtesting, paper trading on an MT5 demo account, a 30-day forward test, an API gateway, a web workstation client, and an isolated AI research assistant. Live trading is strictly disabled.

## Core Value
**What is tested is exactly what is deployed.** Safety and risk limits are enforced by code and architecture rather than discipline or prompts. A single configuration change switches strategy, instrument, or timeframe with zero engine modifications.

## Scope (Phase 1)

### In Scope
- **Core Engine & Architecture:** Event-driven bar-close execution, completed bars only (no lookahead), strict UTC timestamps.
- **Data & Instrument Abstraction:** Instrument specifications for spot forex and exchange-traded contracts (contract size, pip/tick values, sessions, exchange calendar, roll rules). 5 years of historical bar and spread data.
- **Strategy Plugin System:** Versioned, immutable strategies with schema validation. Reference strategy `ema_atr_trend_v1` on XAUUSD/EURUSD.
- **Layered Risk Management & Kill Switch:** Position sizing by risk %, daily loss halts, drawdown halts, pluggable filters (spread, session, news blackout, weekend cutoff). Global and per-profile kill switch.
- **Backtesting & Robustness:** Bar-by-bar simulator with realistic spread, slippage, commission, and swap costs. Walk-forward analysis and parameter sensitivity surfaces.
- **Paper Trading (MT5 Demo):** Broker execution adapter for MetaTrader 5 demo accounts with continuous state reconciliation and reconnect handling.
- **API Gateway & Security:** FastAPI gateway, Argon2 + TOTP 2FA, JWT with rotation, role-based access control (Viewer, Operator, Admin, AI), WebSocket event streaming.
- **Web Client & Alerts:** React + Vite + Tailwind desktop/web workstation and PWA. Local font and icon assets (no CDN). Multi-channel alerts (Telegram, push, email) and dead-man heartbeat monitor.
- **Isolated AI Assistant:** Separate low-privilege service using Google Gemini (paid tier) with read-only DB access, draft-only strategy authoring, trade analysis, and attributed journaling. No broker credentials or route to execution.
- **Forward-Test Tooling:** 30-day paper forward test against locked criteria with backtest-vs-paper evaluation reports.
- **Gated Live Stub:** Unconditionally disabled live adapter stub and complete go-live checklist.

### Out of Scope (Phase 1)
- Live trading execution or real-money broker adapters (DECISIONS D9 is Blocked; gate before Phase 2).
- Manual order entry or discretionary buy/sell buttons.
- LLM inside the execution or signal-generation path.
- High-frequency or sub-second latency trading.
- Multi-tenant SaaS, copy-trading, or social features.
- Dedicated mobile app implementation (mobile is a placeholder phase until UI designs are provided).

## Key Decisions

| Decision | Summary | Status |
|---|---|---|
| D1 Product Name | `APP_NAME = "Automated Trading Platform"`. No "AuraFX". | Accepted |
| D2 Activation | Activation blocked until profile is flat. Resets promotion state and forward-test clock. | Accepted |
| D3 Live Re-auth | Re-authentication + 2FA on desktop/CLI required for live mode (Phase 2). | Proposed |
| D4 Forward Test Criteria | Set and locked per profile before start. Stitch thresholds rejected. Suggested baseline: 30 days, min 10 trades, DD <= 1.5x backtest, PF >= 1.2. | Needs input |
| D5 Stop Controls | Global Kill Switch in top bar + per-profile Pause (stops entries, keeps open positions). | Proposed |
| D6 Mobile Scope | Read-only monitoring, pause/resume, kill switch, biometric activation. | Proposed |
| D7 Icons & Charts | Lucide icons, Apache ECharts, self-hosted Inter & JetBrains Mono fonts. | Accepted |
| D8 Roles & Auth | Viewer, Operator, Admin, and isolated low-privilege AI role. No withdrawal capability. | Accepted |
| D9 Live Broker & Jurisdiction | Exness on RBI Alert List. Phase 1 broker-agnostic with MT5 demo; live adapter blocked until legal route chosen. | Blocked (Live) / Accepted (Phase 1) |
| D10 Account Currency | Per-account setting, default USD, conversion path in instrument spec. | Accepted |
| D11 Engine Host | Local Windows PC for Phase 1. Windows VPS before live. | Accepted (Local PC) |
| D12 AI Provider | Google Gemini API via provider-agnostic interface, paid tier. | Accepted (Provider) / Proposed (Paid tier) |
| D13 Code Review | Agent review + CodeRabbit + mandatory automated tests + human sign-off on risk/execution. | Accepted |
| D14 Mobile Platform | React Native with Expo (Android first). Implementation deferred until designs exist. | Accepted |
| D15 Backtest History | 5 years of historical bars with spread data. | Accepted |
| D16 Alert Channels | Telegram bot, push notifications, SMTP email, external heartbeat monitor. | Accepted (Channels) |
| D17 Tech Stack | Python, uv, FastAPI, SQLite WAL, React, Tailwind, ECharts, Lucide, Tailscale. | Accepted |

## Evolution
This document evolves at milestone boundaries. Changes to safety, risk, or execution require explicit owner sign-off.

---
*Last updated: October 26, 2026 after project initialization*
