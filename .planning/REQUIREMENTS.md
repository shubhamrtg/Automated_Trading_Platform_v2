# Requirements: Automated Trading Platform (Phase 1)

## v1 Requirements (Phase 1 Scope)

### Core Engine & Architecture
- [ ] **FR-INS-5**: All timestamps stored and processed in UTC; broker server-time offsets explicitly handled and tested.
- [ ] **FR-SEC-1**: Broker credentials exist only on server in secrets manager/env vars with trade-only permissions; never exposed to clients or AI.
- [ ] **FR-SEC-3**: Trading engine never exposed to public internet; communicates only with local API gateway via localhost.
- [ ] **FR-SEC-4**: Append-only, tamper-resistant audit log for signals, risk decisions, orders, fills, commands, config changes, and AI interactions.
- [ ] **FR-EXE-4**: Trading engine runs correctly with zero clients connected and AI service switched off.

### Instrument & Market Data Layer
- [ ] **FR-INS-1**: Instruments defined by specs loaded from broker/config and cached, with manual override support.
- [ ] **FR-INS-2**: Zero hardcoded instrument facts (contract size, pip/tick size, symbol names) in engine or strategy code.
- [ ] **FR-INS-3**: Canonical symbol mapping to broker-specific symbols (e.g. XAUUSD vs GOLD vs EURUSD.m).
- [ ] **FR-INS-4**: Cross-pair currency conversion path resolution for pip values and P&L in account currency (default USD).
- [ ] **FR-DAT-1**: Historical data ingestion from CSV/Parquet and live feed streaming.
- [ ] **FR-DAT-2**: Comprehensive data validation: gap detection, duplicates, bad ticks, timezone verification, spread availability.
- [ ] **FR-DAT-3**: Historical backtest data matched to broker feed; discrepancies reported.

### Strategy Plugins & Execution
- [ ] **FR-STR-1**: Versioned, immutable strategy registry.
- [ ] **FR-STR-2**: Strict schema validation for strategy parameters (types, bounds, defaults) prior to execution.
- [ ] **FR-STR-3**: Version ID and parameter config hash recorded on every backtest, paper, and forward-test run.
- [ ] **FR-STR-4**: Deterministic strategies: identical completed bar inputs always produce identical signals.
- [ ] **FR-STR-5**: Bundled reference strategy (`ema_atr_trend_v1`) serving as the primary integration fixture.
- [ ] **FR-STR-6**: Completed bars only (lookahead guard); bar N output cannot be altered by future bars N+1...M.
- [ ] **FR-PRO-1**: Profile abstraction binding strategy version, instrument, timeframe, parameters, risk profile, and mode.
- [ ] **FR-PRO-2**: Multi-profile data model tagging all orders with unique profile ID for reconciliation.
- [ ] **FR-PRO-3**: Modifying strategy version, instrument, timeframe, or parameter creates a new combination and resets promotion state.
- [ ] **FR-PRO-4**: Strategy activation blocked unless profile is completely flat (no open positions, no pending orders).

### Risk Management & Halts
- [ ] **FR-RSK-1**: Every order passes through RiskManager; approves, resizes, or blocks with logged reason.
- [ ] **FR-RSK-2**: Dynamic position sizing computed from stop distance, account equity, risk-per-trade (default 0.5%), and instrument spec.
- [ ] **FR-RSK-3**: Hard risk limits: max daily loss (halts for day), max drawdown (halts until reset), max open positions, max lot size, max spread, slippage tolerance.
- [ ] **FR-RSK-4**: Layered risk controls: account-level, per-profile, and portfolio-level net exposure limits.
- [ ] **FR-RSK-5**: Pluggable filters: spread filter, session window, news blackout, Friday/weekend cutoff.
- [ ] **FR-RSK-6**: Hard limits reside strictly in code and config, never in prompts; cannot be overridden by AI.
- [ ] **FR-KIL-1**: Global kill switch cancels pending orders, closes positions, and halts engine while keeping broker connection open until flat is confirmed.
- [ ] **FR-KIL-2**: Kill switch triggerable via CLI, local flag file, and one tap in web UI; operates independently of AI.
- [ ] **FR-KIL-3**: Automatic halts for loss limits, drawdowns, stale data, and disconnects are logged and alerted.

### Backtesting & Robustness
- [ ] **FR-BT-1**: Event-driven, bar-by-bar simulator running identical strategy and risk code as paper/live.
- [ ] **FR-BT-2**: Signal on bar close; fill at next bar's open.
- [ ] **FR-BT-3**: Realistic cost modeling: variable spreads, commissions, slippage models, overnight swaps, weekend gaps.
- [ ] **FR-BT-4**: Institutional performance metrics: CAGR, max drawdown & duration, Sharpe, Sortino, profit factor, win rate, expectancy.
- [ ] **FR-BT-5**: In-sample vs out-of-sample partitioning, rolling walk-forward analysis, parameter sensitivity grids.
- [ ] **FR-BT-6**: Comprehensive backtest reports (ECharts JSON & HTML) with equity curves, drawdowns, trade lists, sample size warnings.
- [ ] **FR-BT-7**: Client-launched backtests run as background worker jobs via SQLite job table.

### Broker Paper Adapter & Execution
- [ ] **FR-EXE-1**: Execution decoupled behind broker interface; MT5 demo adapter with MockMt5 test harness.
- [ ] **FR-EXE-2**: Continuous automated reconciliation of internal state against broker positions and orders.
- [ ] **FR-EXE-3**: Reconnect loop with exponential backoff; resilient handling of partial fills, requotes, and rejections.
- [ ] **FR-PAP-1**: Profiles execute on MT5 demo account with live market data using identical engine loop.
- [ ] **FR-PAP-2**: Theoretical expected fill vs actual fill logged on every trade to quantify execution slippage.
- [ ] **FR-PAP-3**: Graceful handling of market closure, weekend holds, and network dropouts without state corruption.

### API Gateway & Authentication
- [ ] **FR-CLI-1**: Unified authenticated API gateway for all clients; no client connects to broker or engine directly.
- [ ] **FR-CLI-6**: Idempotent, server-authoritative command processing.
- [ ] **FR-SEC-2**: Secure authentication: Argon2 password hashing, TOTP 2FA, rotating JWT refresh tokens, device registry.
- [ ] **FR-SEC-5**: Step-up confirmation for consequential actions (e.g. strategy activation, risk setting updates).
- [ ] **D8-AUTH**: Role-based access control enforcing Viewer, Operator, Admin, and low-privilege AI role permissions. No withdrawal route for any role.

### Web Workstation & Notifications
- [ ] **FR-CLI-3**: Desktop web workstation implementing 11 screens per `docs/DESIGN.md`: Dashboard, Profiles, Profile Detail, Strategies, Backtests, Forward Tests, Trades & Journal, AI Assistant, Risk & Settings, Help, Welcome Wizard.
- [ ] **FR-CLI-4**: Installable Progressive Web App (PWA).
- [ ] **FR-CLI-5**: No offline queueing; stale-data banner displayed when connection to gateway is lost.
- [ ] **FR-NOT-1**: Push alerts for fills, stop-outs, risk halts, kill switch events, disconnects, daily summaries.
- [ ] **FR-NOT-2**: Secondary critical alert channels: Telegram bot and SMTP email.
- [ ] **FR-NOT-3**: Dead-man check sending heartbeat telemetry to external monitor (Healthchecks.io).
- [ ] **FR-JRN-1**: Append-only user and AI journal notes, visibly attributed.
- [ ] **FR-JRN-2**: Structured trade journal capturing signal, risk decision, order, expected vs actual fill, strategy version.
- [ ] **FR-JRN-3**: In-app daily and weekly performance rollups.
- [ ] **DSG-12**: Full adherence to binding DESIGN.md Section 12 corrections (no assurance claims, no Buy/Sell quick buttons, profit green / loss red semantics, local asset bundling).

### AI Research & Authoring Service
- [ ] **FR-AI-1**: AI service isolated in separate process with own AI-role token and read-only DB access; zero broker credentials or execution routes.
- [ ] **FR-AI-2**: Strategy changes produce draft version with diff; activation strictly human-initiated when profile is flat.
- [ ] **FR-AI-3**: Tamper-resistant audit log of every AI prompt, interpretation, diff, approval, and resulting version.
- [ ] **FR-AI-4**: Strict prompt sanitization; external/untrusted content never treated as commands.
- [ ] **FR-AI-5**: Curve-fitting heuristics warning against overfitting; mandates out-of-sample backtest before accepting changes.
- [ ] **FR-AI-6**: Activation cooldown frequency limits to prevent reactive tweaking.

### Forward-Test Tooling
- [ ] **FR-FWD-1**: 30-day paper forward test on MT5 demo account.
- [ ] **FR-FWD-2**: Pre-test locked pass/fail criteria per profile (trade count, max DD, min profit factor, slippage band).
- [ ] **FR-FWD-3**: Evaluation report comparing live paper performance against backtest baseline.
- [ ] **FR-FWD-4**: Any strategy or parameter modification resets forward-test clock to 0 and state to Draft.

### Gated Live Stub (Safety Boundary)
- [ ] **FR-LIVE-1**: Live trading disabled; explicit configuration and confirmation required.
- [ ] **FR-LIVE-2**: Engine unconditionally refuses combinations not in Live-eligible promotion state.
- [ ] **FR-LIVE-3**: Documented go-live checklist, compliance runbook, and scaling plan.
- [ ] **FR-LIVE-4**: Live enablement blocked on mobile; desktop/CLI re-authentication required.

---

## Traceability to Roadmap Phases

| Phase | Milestone Name | Covered Requirement IDs |
|---|---|---|
| Phase 1 | Foundations | FR-INS-5, FR-SEC-1, FR-SEC-3, FR-SEC-4, FR-EXE-4 |
| Phase 2 | Data Layer & Instrument Specs | FR-INS-1, FR-INS-2, FR-INS-3, FR-INS-4, FR-DAT-1, FR-DAT-2, FR-DAT-3 |
| Phase 3 | Strategy Plugins & Reference Strategy | FR-STR-1, FR-STR-2, FR-STR-3, FR-STR-4, FR-STR-5, FR-STR-6, FR-PRO-1, FR-PRO-2, FR-PRO-3, FR-PRO-4 |
| Phase 4 | Risk Manager & Kill Switch | FR-RSK-1, FR-RSK-2, FR-RSK-3, FR-RSK-4, FR-RSK-5, FR-RSK-6, FR-KIL-1, FR-KIL-2, FR-KIL-3 |
| Phase 5 | Backtester with Realistic Costs | FR-BT-1, FR-BT-2, FR-BT-3, FR-BT-4, FR-BT-6 |
| Phase 6 | Walk-Forward & Sensitivity Analysis | FR-BT-5, FR-BT-7 |
| Phase 7 | MT5 Paper Adapter & Reconciliation | FR-EXE-1, FR-EXE-2, FR-EXE-3, FR-PAP-1, FR-PAP-2, FR-PAP-3 |
| Phase 8 | API Gateway & Authentication | FR-CLI-1, FR-CLI-6, FR-SEC-2, FR-SEC-5, D8-AUTH |
| Phase 9 | Web Client & Notifications | FR-CLI-3, FR-CLI-4, FR-CLI-5, FR-NOT-1, FR-NOT-2, FR-NOT-3, FR-JRN-1, FR-JRN-2, FR-JRN-3, DSG-12 |
| Phase 10 | AI Service | FR-AI-1, FR-AI-2, FR-AI-3, FR-AI-4, FR-AI-5, FR-AI-6 |
| Phase 11 | Forward-Test Tooling | FR-FWD-1, FR-FWD-2, FR-FWD-3, FR-FWD-4 |
| Phase 12 | Gated Live Stub & Documentation | FR-LIVE-1, FR-LIVE-2, FR-LIVE-3, FR-LIVE-4 |
