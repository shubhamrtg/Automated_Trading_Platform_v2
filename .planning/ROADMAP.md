# Project Roadmap: Automated Trading Platform (Phase 1)

**Structure:** 12 Milestones (from PRD Section 12).  
**Execution Order:** Engine Phases (1 to 7) come strictly before API (8), Web Client (9), AI Service (10), Forward Testing (11), and Gated Live Stub (12).  
**Quality Rule:** Tests come first. Mandatory tests from TECH_STACK Section 14 are created in the phase where their subject is built and stay green continuously.

---

## Phase Overview

| Phase | Milestone Name | Focus | Key Deliverable | Mandatory Test Added |
|---|---|---|---|---|
| **Phase 1** | Foundations | Repo, config, models, DB, audit log | Core interfaces, SQLite WAL, audit trigger | Role-permission schema validation |
| **Phase 2** | Data Layer & Instrument Specs | Specs, historical data, conversion | Parquet loader, currency path, validator | Second instrument zero engine changes |
| **Phase 3** | Strategy Plugins & Reference Strategy | Determinism, versioning, indicators | `ema_atr_trend_v1`, parameter schemas | Lookahead test & Second strategy test |
| **Phase 4** | Risk Manager & Kill Switch | Sizing, hard limits, halts, filters | Layered risk engine, KillSwitch controller | Kill-switch flat confirmation test |
| **Phase 5** | Backtester with Realistic Costs | Simulation, costs, ECharts reports | Bar-by-bar engine, spread/swap/slippage | End-to-end backtest reproducibility |
| **Phase 6** | Walk-Forward & Sensitivity Analysis | Overfitting prevention, worker | Job runner, sensitivity surfaces | Out-of-sample split isolation |
| **Phase 7** | MT5 Paper Adapter & Reconciliation | Broker adapter, state sync, retry | MT5 adapter, MockMt5, reconciler | Simulated failures test |
| **Phase 8** | API Gateway & Authentication | Fast API, 2FA, JWT, roles, IPC | Auth gateway, engine IPC, WebSocket hub | Role-permission enforcement test |
| **Phase 9** | Web Client & Notifications | React UI, ECharts, multi-channel alerts | 11 web screens, PWA, Telegram bot | Banned UI phrases test |
| **Phase 10** | AI Service | Research, backtest runner, drafts | Gemini client, sandbox tools, diff engine | AI execution isolation test |
| **Phase 11** | Forward-Test Tooling | 30-day paper test against locked criteria | Evaluation report, clock reset manager | Parameter change clock reset test |
| **Phase 12** | Gated Live Stub & Documentation | Safety gate, go-live checklist | Gated live stub, runbook, checklist | Unconditional live refusal test |

---

## Phase Details

### Phase 1: Foundations
- **Goal:** Initialize project structure, configuration management, domain models, logging, base interfaces, database migrations, and the tamper-resistant append-only audit log.
- **PRD Requirements Covered:** `FR-INS-5`, `FR-SEC-1`, `FR-SEC-3`, `FR-SEC-4`, `FR-EXE-4`.
- **Deliverables:**
  - Python workspace configuration (`pyproject.toml`, `uv.lock`, strict `ruff`, strict `mypy`).
  - Core interfaces (`engine/core/`): `Strategy`, `DataFeed`, `ExecutionBroker`, `RiskManager`, `InstrumentSpec`.
  - Pydantic v2 configuration system (`engine/core/config.py`) loading `.env` (demo credentials only) with strict UTC timestamp utilities.
  - SQLite database in WAL mode via SQLAlchemy 2 and Alembic migrations.
  - SQLite append-only triggers (`BEFORE UPDATE` and `BEFORE DELETE` raising `ABORT` on audit and journal tables).
  - Append-only audit logger (`engine/storage/audit.py`) recording signals, decisions, orders, fills, commands, and AI interactions.
  - Structured logging subsystem with `structlog`.
- **Tests That Must Pass:**
  - Configuration loading and UTC validation tests.
  - SQLite database trigger tests (confirm `UPDATE` and `DELETE` on audit table raise exceptions).
  - Secret scanning test (confirm `.env` demo secrets are never logged or exported).
- **Mandatory Test Created:**
  - **Role-permission schema validation test** (verifies database constraints for Viewer, Operator, Admin, AI; verifies no withdrawal permission exists).
- **Acceptance Criteria (PRD §11):**
  - Database initializes in WAL mode with passing migrations.
  - Append-only audit triggers reject any mutation or deletion.
  - Core interfaces are cleanly defined without external broker imports.
- **Dependencies on DECISIONS.md:**
  - D1 (`Accepted`: `APP_NAME = "Automated Trading Platform"`).
  - D8 (`Accepted`: Roles `Viewer`, `Operator`, `Admin`, `AI`).
  - D10 (`Accepted`: Account currency default `USD`).
  - D11 (`Accepted`: Local Windows PC setup).

---

### Phase 2: Data Layer and Instrument Specs
- **Goal:** Build the data ingestion, validation, caching, and storage pipeline for historical and live market data, along with flexible instrument specifications supporting spot forex and exchange-traded contracts.
- **PRD Requirements Covered:** `FR-INS-1`, `FR-INS-2`, `FR-INS-3`, `FR-INS-4`, `FR-DAT-1`, `FR-DAT-2`, `FR-DAT-3`.
- **Deliverables:**
  - Instrument specification parser and models (`engine/data/instrument.py`) with support for contract size, pip/tick size, lot constraints, sessions, commission, swap, exchange calendar, expiry, roll rules, and margin models.
  - Symbol mapping and conversion path resolver (`engine/data/conversion.py`).
  - Historical data loader & Parquet storage (`engine/data/historical.py`) using pyarrow and pandas.
  - Data hygiene and validation module (`engine/data/validator.py`).
- **Tests That Must Pass:**
  - Data validation tests (detect gaps, duplicate timestamps, bad ticks, missing spreads).
  - Timezone conversion tests (broker server-time offset normalized to UTC).
  - Cross-pair currency conversion path tests (e.g. resolving pip value for EURGBP in USD account).
- **Mandatory Test Created:**
  - **Second instrument with zero engine changes test** (instantiate spec for XAUUSD and a secondary instrument like EURUSD or USDJPY with zero engine code changes).
- **Acceptance Criteria (PRD §11):**
  - Instrument specs load without hardcoded assumptions in engine code.
  - Cross-pair conversion correctly calculates tick values in USD.
  - 5-year historical Parquet datasets pass gap and timezone validation.
- **Dependencies on DECISIONS.md:**
  - D9 (`Accepted` for Phase 1 broker-agnostic instrument specs supporting exchange-traded contracts; `Blocked` for live broker).
  - D15 (`Accepted`: 5 years of historical bar and spread data).

---

### Phase 3: Strategy Plugins and Reference Strategy
- **Goal:** Implement the deterministic, lookahead-free strategy plugin architecture, registry, schema validation, technical indicators (EMA, ATR), and the bundled reference strategy (`ema_atr_trend_v1`).
- **PRD Requirements Covered:** `FR-STR-1`, `FR-STR-2`, `FR-STR-3`, `FR-STR-4`, `FR-STR-5`, `FR-STR-6`, `FR-PRO-1`, `FR-PRO-2`, `FR-PRO-3`, `FR-PRO-4`.
- **Deliverables:**
  - Strategy base class and registry (`engine/strategies/base.py`, `registry.py`).
  - Technical indicator library (`engine/strategies/indicators.py`): EMA, ATR calculated on bar series without lookahead.
  - Reference strategy implementation (`engine/strategies/builtin/ema_atr_trend_v1.py`): EMA 20/50 crossover, EMA 200 trend filter, ATR stop-loss and take-profit.
  - Parameter hashing and immutability validator (`engine/strategies/versioning.py`).
  - Profile state manager (`engine/core/profile.py`) enforcing flat-only activation.
- **Tests That Must Pass:**
  - Determinism test (multiple runs on identical bar data yield identical signals).
  - Parameter schema validation tests (reject out-of-range bounds or invalid types).
  - Reference strategy indicator verification against standard benchmark formulas.
- **Mandatory Tests Created:**
  - **Lookahead test** (verify output at bar N is strictly unchanged when future bars N+1...M are altered or truncated).
  - **Second strategy with zero engine changes test** (register a secondary breakout strategy alongside `ema_atr_trend_v1` with zero engine changes).
- **Acceptance Criteria (PRD §11):**
  - The lookahead test passes.
  - The reference strategy produces deterministic signals on completed bars.
  - A second strategy registers and runs with zero engine modifications.
- **Dependencies on DECISIONS.md:**
  - D1 (`Accepted`: `APP_NAME`).
  - D2 (`Accepted`: Strategy activation blocked until profile is flat).

---

### Phase 4: Risk Manager and Kill Switch
- **Goal:** Build the layered risk management engine, pluggable trade filters (spread, session, blackout, weekend cutoff), dynamic position sizing engine, and global/profile kill switch and halt mechanics.
- **PRD Requirements Covered:** `FR-RSK-1`, `FR-RSK-2`, `FR-RSK-3`, `FR-RSK-4`, `FR-RSK-5`, `FR-RSK-6`, `FR-KIL-1`, `FR-KIL-2`, `FR-KIL-3`.
- **Deliverables:**
  - RiskManager core (`engine/risk/manager.py`).
  - Position sizing engine (`engine/risk/sizing.py`) computing volume from stop distance, equity, and risk-per-trade (default 0.5%).
  - Pluggable filters (`engine/risk/filters/`): `spread_filter.py`, `session_filter.py`, `news_blackout.py`, `weekend_cutoff.py`.
  - KillSwitch controller (`engine/risk/kill_switch.py`) with persistent halt state.
- **Tests That Must Pass:**
  - Hypothesis property tests for position sizing (sizing never exceeds configured risk % across arbitrary equity and stop distances).
  - Risk limit violation tests (daily loss halt, max drawdown halt, max spread block).
  - Pluggable filter unit tests (session hours, Friday close, news blackout window).
- **Mandatory Test Created:**
  - **Kill-switch test** (pending orders cancelled, open positions closed, engine halted; verify broker connection stays open until flat is confirmed, never disconnecting early).
- **Acceptance Criteria (PRD §11):**
  - Kill-switch test passes.
  - Risk limits and sizing tests pass with Hypothesis.
  - Zero orders bypass the RiskManager under any execution branch.
- **Dependencies on DECISIONS.md:**
  - D5 (`Proposed`: global Kill Switch in top bar + per-profile Pause stopping new entries without closing open positions).

---

### Phase 5: Backtester with Realistic Costs and Reports
- **Goal:** Implement the event-driven, bar-by-bar backtest simulator utilizing identical strategy and risk code, modeling realistic spreads, commissions, slippage, and overnight swaps, with institutional metrics and reporting.
- **PRD Requirements Covered:** `FR-BT-1`, `FR-BT-2`, `FR-BT-3`, `FR-BT-4`, `FR-BT-6`.
- **Deliverables:**
  - Backtest execution simulator (`engine/backtest/engine.py`).
  - Realistic cost models (`engine/backtest/costs.py`): variable spreads, slippage models, commission, overnight swaps.
  - Performance analytics engine (`engine/backtest/metrics.py`): CAGR, max drawdown & duration, Sharpe, Sortino, profit factor, win rate, expectancy.
  - Report generator (`engine/backtest/report.py`): structured JSON data for ECharts and HTML summaries.
- **Tests That Must Pass:**
  - Backtest reproducibility test (identical config and data yields bit-for-bit identical trade results).
  - Cost model accuracy tests (verify proper deduction of spreads, commissions, swaps, and slippage).
  - Bar close/open fill timing test (verify signal on bar N close fills at bar N+1 open).
- **Mandatory Test Created:**
  - **End-to-end reference strategy backtest test** (reproducible backtest of `ema_atr_trend_v1` on XAUUSD/EURUSD).
- **Acceptance Criteria (PRD §11):**
  - The reference strategy backtests end to end with deterministic, reproducible results.
  - Backtest metrics match manual calculation fixtures.
- **Dependencies on DECISIONS.md:**
  - D15 (`Accepted`: 5-year history).

---

### Phase 6: Walk-Forward, Out-of-Sample, and Sensitivity Analysis
- **Goal:** Build the optimization and robustness testing suite: rolling walk-forward analysis, in-sample vs out-of-sample partitioning, parameter sensitivity grids, and isolated background worker execution.
- **PRD Requirements Covered:** `FR-BT-5`, `FR-BT-7`.
- **Deliverables:**
  - Walk-forward engine (`engine/backtest/walk_forward.py`).
  - Parameter sensitivity grid analyzer (`engine/backtest/sensitivity.py`).
  - Background worker process (`engine/backtest/worker.py`) running tasks from SQLite job table.
- **Tests That Must Pass:**
  - Train/test data split isolation test (strictly zero data leakage between in-sample and out-of-sample windows).
  - Background worker concurrency, timeout, and cancellation tests.
  - Sensitivity surface generation test.
- **Acceptance Criteria (PRD §11):**
  - Walk-forward metrics detect parameter degradation out-of-sample.
  - Backtest jobs execute in worker without blocking engine operation.
- **Dependencies on DECISIONS.md:**
  - D11 (`Accepted`: local PC execution).

---

### Phase 7: MT5 Paper Adapter, Reconciliation, and Reconnect
- **Goal:** Build the MetaTrader 5 execution adapter for paper trading on a demo account, continuous broker position reconciliation, automated reconnect with exponential backoff, and order failure handlers.
- **PRD Requirements Covered:** `FR-EXE-1`, `FR-EXE-2`, `FR-EXE-3`, `FR-PAP-1`, `FR-PAP-2`, `FR-PAP-3`.
- **Deliverables:**
  - MT5 execution adapter (`engine/adapters/mt5/adapter.py`) using MetaTrader5 package.
  - Mock MT5 adapter (`engine/adapters/mt5/mock.py`) for deterministic automated testing on Linux/Windows CI without terminal.
  - Continuous reconciliation engine (`engine/execution/reconciliation.py`).
  - Connection monitor and reconnect state machine (`engine/execution/connection.py`).
- **Tests That Must Pass:**
  - Reconciliation mismatch test (detects and resolves untracked or orphaned broker positions).
  - Reconnect with backoff test (simulates connection drops and automatic recovery).
  - Theoretical expected fill vs actual fill slippage logging test.
- **Mandatory Test Created:**
  - **Simulated failures test** (broker disconnect, rejected order, requote, partial fill, stale data feed; verify engine halts or recovers safely without phantom positions).
- **Acceptance Criteria (PRD §11):**
  - MockMt5 unit and integration tests run in CI without MT5 terminal.
  - Continuous reconciliation flags discrepancies within one tick cycle.
  - Simulated failures test passes.
- **Dependencies on DECISIONS.md:**
  - D9 (`Accepted` for Phase 1 demo/paper trading; `Blocked` for live broker).
  - D11 (`Accepted`: Windows PC running MT5 terminal in user session).

---

### Phase 8: API Gateway, Authentication, and Event Streaming
- **Goal:** Build the secure FastAPI gateway providing token authentication (Argon2, TOTP 2FA, JWT with rotation), role-based access control, WebSocket live streaming, and internal engine control IPC.
- **PRD Requirements Covered:** `FR-CLI-1`, `FR-CLI-6`, `FR-SEC-2`, `FR-SEC-5`, `D8-AUTH`.
- **Deliverables:**
  - FastAPI application (`gateway/app.py`).
  - Auth module (`gateway/auth/`): Argon2 password hashing, TOTP 2FA, JWT token service with rotating refresh tokens, device registry.
  - Role-based authorization middleware (`gateway/middleware/roles.py`).
  - Internal IPC client (`gateway/ipc/engine_client.py`) connecting to Engine Control API (127.0.0.1 with shared secret).
  - WebSocket hub (`gateway/websocket/hub.py`) for streaming live ticks, order updates, and risk events.
- **Tests That Must Pass:**
  - 2FA verification and JWT rotation tests.
  - Engine control isolation test (verify engine control API unconditionally rejects requests lacking local shared secret).
  - Idempotency test (duplicate client commands execute only once).
- **Mandatory Test Created:**
  - **Role-permission enforcement test** (Viewer cannot pause/kill; Operator cannot activate strategy or edit risk limits; Admin can edit risk limits; zero roles can withdraw funds; AI role cannot reach engine control).
- **Acceptance Criteria (PRD §11):**
  - Role-permission test passes across all endpoints.
  - Engine control API is unreachable without the local secret.
- **Dependencies on DECISIONS.md:**
  - D8 (`Accepted`: Roles and permissions).
  - D17 (`Accepted`: FastAPI, SQLite, Tailscale).

---

### Phase 9: Web Client and Notifications
- **Goal:** Build the React + Vite + Tailwind desktop/web workstation (and installable PWA) following semantic design tokens, integrating Apache ECharts, Lucide icons, multi-channel alerts (Telegram, push, email), and a placeholder structure for mobile.
- **PRD Requirements Covered:** `FR-CLI-3`, `FR-CLI-4`, `FR-CLI-5`, `FR-NOT-1`, `FR-NOT-2`, `FR-NOT-3`, `FR-JRN-1`, `FR-JRN-2`, `FR-JRN-3`, `DSG-12`.
- **Deliverables:**
  - Frontend app (`web/`): React, TypeScript, Vite, Tailwind CSS, Radix UI, TanStack Query, Apache ECharts, Lucide icons.
  - Self-hosted Inter & JetBrains Mono font bundles (strictly zero CDN dependencies).
  - WebSocket client with auto-reconnect and stale-data banner.
  - 11 web screens per `docs/DESIGN.md`: Dashboard, Profiles, Profile Detail, Strategies, Backtests, Forward Tests, Trades & Journal, AI Assistant, Risk & Settings, Help, Welcome Wizard.
  - Notification service (`gateway/notifications/`): Telegram bot adapter, SMTP emailer, push notification dispatcher.
  - External heartbeat monitor script (`scripts/heartbeat.py` to Healthchecks.io).
  - Mobile placeholder package (`mobile/` folder with shared TypeScript types; mobile screens deferred until designs exist).
- **Binding DESIGN.md §12 Corrections in Acceptance Criteria:**
  - Top-bar title dynamically follows current route (no persistent 'Dashboard' title).
  - Forward test duration displayed as 30 days (FR-FWD-1).
  - No fixed rules shown as platform law (editable defaults only, locked after test start).
  - **No assurance claims:** remove 'Zero-Risk Protocol', '100% Risk-Free Simulation', 'Zero financial risk', '100% Guarded', '<18ms' guarantees, 'Institutional grade' claims.
  - **FAQ accurate:** funds remain with broker; platform never holds custody or withdrawal rights.
  - **Sample data labeled:** mock/sample data visibly labeled as sample.
  - **No AI projections:** remove projected returns/win rates; AI suggestions show backtest evidence and require out-of-sample testing.
  - **No withdrawal references:** all withdrawal UI removed.
  - **Kill switch wording accurate:** cancels orders, closes positions, halts engine; maintains connection until flat.
  - **Strategy activation button is accent blue** (never green). Blocked when profile is not flat.
  - **No Buy/Sell quick-trade buttons:** BUY/SELL appear only as trade direction badges.
  - **Profit green with + and ▲, loss red with - and ▼, zero neutral gray.** Never color alone.
  - **All assets bundled locally:** no external CDN dependencies.
- **Mandatory Test Created:**
  - **Banned UI phrases test** (static scan of all web source code for prohibited marketing claims: "zero-risk", "100% safe", "guaranteed", "custody", "withdrawal", "institutional execution desk").
- **Acceptance Criteria (PRD §11):**
  - Web client displays live engine state, connects via WebSocket, and triggers pause/kill switch.
  - Banned UI phrases test passes.
  - All section 12 design corrections verified.
- **Dependencies on DECISIONS.md:**
  - D1 (`Accepted`: `APP_NAME`).
  - D5 (`Proposed`: Stop controls).
  - D6 (`Proposed`: Mobile scope).
  - D7 & D17 (`Accepted`: Lucide icons, Apache ECharts, bundled fonts).
  - D14 (`Accepted`: Android phone via Expo; deferred until designs exist).
  - D16 (`Accepted`: Telegram, push, email channels).

---

### Phase 10: AI Service (Research, Backtests, Draft Strategies, Journaling)
- **Goal:** Build the isolated AI service powered by Google Gemini (paid tier) with read-only database access, draft-only strategy authoring, trade analysis, backtest triggering, and attributed journaling.
- **PRD Requirements Covered:** `FR-AI-1`, `FR-AI-2`, `FR-AI-3`, `FR-AI-4`, `FR-AI-5`, `FR-AI-6`.
- **Deliverables:**
  - AI service process (`ai_service/app.py`).
  - Gemini SDK client with provider-agnostic interface (`ai_service/provider/gemini.py`).
  - Tool allowlist (`ai_service/tools/`): read trading data, request backtest, draft strategy, write journal note.
  - Strict input sanitization and prompt injection guardrails.
  - Diff generator for strategy authoring.
- **Tests That Must Pass:**
  - Process isolation test (AI service has zero access to broker credentials and cannot reach Engine Control API).
  - Draft-only enforcement test (verify AI cannot activate, pause, resume, or place orders).
  - Attribution test (verify all notes authored by AI are tagged 'AI').
- **Acceptance Criteria (PRD §11):**
  - Shutting down the AI service and all clients has zero effect on the trading engine loop.
  - Zero code paths exist from the AI service to the execution layer.
- **Dependencies on DECISIONS.md:**
  - D12 (`Accepted`: Google Gemini provider; `Proposed`: paid tier).

---

### Phase 11: Forward-Test Tooling and 30-Day Forward Test
- **Goal:** Build the forward-test lifecycle manager, evaluation report generator, and operational monitoring tooling to conduct the 30-day paper test on an MT5 demo account.
- **PRD Requirements Covered:** `FR-FWD-1`, `FR-FWD-2`, `FR-FWD-3`, `FR-FWD-4`.
- **Deliverables:**
  - Forward-test controller (`engine/forward_test/manager.py`).
  - Criteria locking and validation engine (`engine/forward_test/criteria.py`).
  - Comparison evaluation report generator (`engine/forward_test/evaluation.py`).
  - Automated daily summary and heartbeat health check scripts.
- **Tests That Must Pass:**
  - Parameter change clock reset test (verify altering any parameter resets forward-test days to 0 and state to Draft).
  - Evaluation report calculation test against locked criteria.
- **Acceptance Criteria (PRD §11):**
  - Forward-test tooling tracks continuous paper trading and produces comparison reports against backtest.
  - Forward test checks execution validity and slippage without claiming profit guarantees.
- **Dependencies on DECISIONS.md:**
  - D4 (`Needs input`: forward-test threshold numbers; suggested defaults: 30 days, floor 10 trades, DD <= 1.5x backtest, PF >= 1.2).
  - D9 (`Accepted` for Phase 1 broker-agnostic paper testing).

---

### Phase 12: Gated Live Stub, Go-Live Checklist, and Documentation
- **Goal:** Implement the locked, gated live-adapter stub (with hard runtime blocks preventing execution), document the complete go-live checklist, and provide architectural and operational documentation. Live mode remains completely disabled.
- **PRD Requirements Covered:** `FR-LIVE-1`, `FR-LIVE-2`, `FR-LIVE-3`, `FR-LIVE-4`.
- **Deliverables:**
  - Gated live execution adapter stub (`engine/adapters/live_stub.py`) with hard runtime exception (`RuntimeError("Live trading is disabled in Phase 1")`).
  - Promotion pipeline validator (`engine/core/promotion.py`) verifying `Live-eligible` status before any live initialization.
  - Go-live checklist (`docs/GO_LIVE_CHECKLIST.md`) documenting broker selection, legal review (RBI/SEBI compliance per D9), static IP, capital scaling.
  - Complete operational runbook (`docs/RUNBOOK.md`).
- **Tests That Must Pass:**
  - Live gate refusal test (verify engine unconditionally refuses to initialize in live mode).
  - Non-eligible promotion rejection test (verify non-live-eligible strategies are rejected).
  - Mobile live enablement block test (verify API rejects live toggle requests originating from mobile tokens).
- **Acceptance Criteria (PRD §11):**
  - Live mode stays 100% disabled; no enabled live path or real-money broker adapter exists.
  - The live gate raises a hard failure if invoked.
- **Dependencies on DECISIONS.md:**
  - D3 (`Proposed`: desktop/CLI re-authentication + 2FA for live mode; no hardware key in Phase 1).
  - D9 (`Blocked`: live broker and legal jurisdiction decision must be accepted before Phase 2 live adapter can be built).
