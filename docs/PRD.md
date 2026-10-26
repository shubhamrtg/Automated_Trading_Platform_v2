PRD: Automated Trading Platform
Version 0.1 (Draft) · October 13, 2026 · Status: for review
1. Overview
A strategy-agnostic, instrument-agnostic platform that automates forex trading. The user defines or imports a trading strategy, backtests it on historical data, runs it on a demo account with live market data, forward-tests it for about a month, and only then trades it with real money. Once a strategy is active, the platform places trades purely according to that strategy's rules, with no manual order entry and no AI in the trading path.
The first reference setup is an EMA + ATR trend strategy on XAUUSD (gold) through MetaTrader 5. This is only an example: the strategy, the currency pair, and the timeframe are configuration and can be changed at any time the strategy is not trading.
The platform is used from web, desktop, and mobile. An AI assistant helps with research, strategy authoring, trade analysis, and journaling, but it is isolated from live trading by design.
2. Problem and Vision
Problem. Manual trading is time-consuming and inconsistent. Ad-hoc scripts are hard to test properly, easy to deploy untested, and hard to monitor remotely.
Vision. One trustworthy system where what is tested is exactly what is deployed, switching strategy or pair is a configuration change, safety is enforced by architecture rather than by good intentions, and the owner can monitor and control everything from a phone.
3. Goals and Non-Goals
Goals
• G1. Run the same strategy code in backtest, paper, and live modes; only the data source and execution layer differ.
• G2. Make strategy, instrument, and timeframe interchangeable with no engine changes.
• G3. Enforce a promotion pipeline so nothing reaches live trading without passing its own backtest and forward test.
• G4. Protect capital with mandatory, code-enforced risk limits and a reliable kill switch.
• G5. Provide web, desktop, and mobile clients for monitoring and controlled operation.
• G6. Provide an AI assistant for research and authoring that has no path into live trading.
• G7. Keep a complete, tamper-resistant audit trail of every signal, decision, order, fill, command, and AI interaction.
Non-Goals (for now)
• AI or LLM making buy/sell decisions, or any AI call inside the trading path.
• High-frequency or latency-sensitive trading.
• Asset classes beyond forex and spot metals (CFDs, crypto, equities are future work).
• Multi-tenant or public SaaS usage; copy-trading; social features.
• Managing other people's money, or providing financial advice.
• Running the trading engine on a phone or in a browser.
4. Users and Roles
Primary user: the owner, an individual trader running the system for their own account. Roles are defined now so multi-user support is possible later.
Role
Can do
Viewer
Read-only: P&L, positions, reports, journal
Operator
Viewer + pause/resume profiles, trigger kill switch
Admin
Operator + activate strategy versions, edit risk limits and settings, manage devices
Enabling live mode is a separate privilege available only on desktop/CLI with re-authentication. It is never available from mobile.
5. Key Concepts
• Strategy: a plugin with metadata, a parameter schema, indicator and warm-up requirements, and a deterministic on_bar(context) -> signals function. It never imports broker or execution code. Strategies may be declarative (YAML rules) or code.
• Strategy version: an immutable snapshot of a strategy and its parameters, identified by version and config hash.
• Instrument spec: all instrument facts as data: broker symbol mapping, contract size, tick size and value, pip size, lot min/max/step, quote currency, sessions, commission, swap, and the currency-conversion path.
• Profile: a binding of strategy version + instrument + timeframe + parameters + risk profile + mode.
• Mode: backtest, paper, or live.
• Promotion state: per combination of strategy version + instrument + timeframe + parameters: draft ? backtested ? paper ? forward-tested ? live-eligible.
• Journal: per-day and per-trade notes written by the user or the AI, stored separately from trade records.
6. Phases
Phase
Scope
Phase 1
Platform core, strategy and instrument plugins, backtesting, paper trading on a demo account, one-month forward test, web + mobile monitoring, AI research assistant. Live adapter exists but is disabled.
Phase 2
Live trading with small capital after the promotion pipeline is satisfied; gradual scale-up; live-vs-paper slippage comparison.
Phase 3
Additional brokers, multiple concurrent profiles, portfolio-level analytics, optional ML-based strategy plugins (versioned and tested like any other strategy).
7. Functional Requirements
7.1 Strategy management
• FR-STR-1 Import or define strategies through a versioned registry; each version is immutable.
• FR-STR-2 Validate parameters against the strategy's schema (types, ranges, defaults) before any run.
• FR-STR-3 Record the strategy version and config hash on every backtest, paper, and live run.
• FR-STR-4 Strategies must be deterministic: identical inputs always produce identical signals.
• FR-STR-5 Provide a bundled reference strategy (ema_atr_trend_v1) used as the integration-test fixture.
• FR-STR-6 Strategies receive only completed bars; a strategy's output at bar N must not change if future bars are altered (lookahead guard, verified by test).
7.2 Instrument management
• FR-INS-1 Instruments are defined by an instrument spec loaded from the broker at startup and cached, with a manual override option.
• FR-INS-2 No engine, strategy, or risk code may hardcode instrument assumptions (no fixed contract size, pip size, or symbol name).
• FR-INS-3 Map canonical symbols to broker symbols (for example XAUUSD vs GOLD vs EURUSD.m) in configuration.
• FR-INS-4 Support cross pairs by resolving the conversion path needed to express pip value and P&L in account currency.
• FR-INS-5 All timestamps stored in UTC; broker server-time offsets handled explicitly and tested.
7.3 Profiles
• FR-PRO-1 A profile binds strategy version, instrument, timeframe, parameters, risk profile, and mode.
• FR-PRO-2 Support multiple profiles (at least in the data model from Phase 1); each profile tags its orders with a unique ID so positions can be attributed during reconciliation.
• FR-PRO-3 Switching strategy, pair, timeframe, or any parameter creates a new combination with its own promotion state.
• FR-PRO-4 A profile cannot be changed in place while it has an open position or pending order; changes are drafted, validated, and activated only when the profile is flat.
7.4 Market data
• FR-DAT-1 Load historical data from broker exports and CSV/Parquet, and live data from the broker feed.
• FR-DAT-2 Validate data: gaps, duplicates, bad ticks, timezone consistency, and spread availability.
• FR-DAT-3 Backtest data should match the broker that will be traded, or the mismatch must be reported.
7.5 Backtesting
• FR-BT-1 Event-driven, bar-by-bar simulation using the same strategy and risk code as paper and live.
• FR-BT-2 Signals computed on bar close and filled at the next bar's open (or next tick in paper/live).
• FR-BT-3 Realistic costs: variable bid/ask spread, commission, slippage model, swap/overnight fees, and weekend gaps.
• FR-BT-4 Metrics: total return, CAGR, max drawdown and duration, Sharpe, Sortino, profit factor, win rate, average R, expectancy, trade count, exposure, monthly returns.
• FR-BT-5 In-sample vs out-of-sample reporting, rolling walk-forward, and a parameter-sensitivity check.
• FR-BT-6 Reports (HTML/Markdown or in-app) with equity curve, drawdown chart, trade list, and a warning when trade count is too low to be statistically meaningful.
• FR-BT-7 Backtests can be launched from any client and run as background jobs in an isolated worker.
7.6 Paper trading
• FR-PAP-1 Run profiles on a broker demo account using live market data, with the identical engine loop used in backtest.
• FR-PAP-2 Log expected (theoretical) fill vs actual fill for every trade to measure slippage.
• FR-PAP-3 Handle market closed, weekends, missing symbols, disconnects, and rejected orders without crashing.
7.7 Forward testing
• FR-FWD-1 A forward test runs for approximately one month on paper trading.
• FR-FWD-2 Pass/fail criteria are defined per profile in a config file before the test starts and are locked once it begins (examples: minimum trade count, maximum drawdown, minimum profit factor, maximum deviation from backtest, maximum slippage).
• FR-FWD-3 An evaluation report compares paper results with the backtest over the same period and states pass or fail against the locked criteria.
• FR-FWD-4 Changing the strategy mid-test resets the forward-test clock.
7.8 Live trading (gated)
• FR-LIVE-1 Live mode requires an explicit config setting plus a deliberate confirmation, and is disabled in Phase 1.
• FR-LIVE-2 Live mode refuses any combination whose promotion state is not live-eligible.
• FR-LIVE-3 Live trading starts with a small fraction of intended capital, with a documented go-live checklist and scale-up plan.
• FR-LIVE-4 Enabling live mode is impossible from the mobile client and requires re-authentication on desktop or CLI.
7.9 Risk management
• FR-RSK-1 Every order passes through the risk manager, which approves, resizes, or blocks it, and logs the reason.
• FR-RSK-2 Position size is computed from stop distance, account equity, risk-per-trade, and the instrument spec (default risk 0.5% of equity, configurable).
• FR-RSK-3 Limits: max daily loss (halts trading for the day), max drawdown (halts until manually reset), max open positions, max lot size, max spread, max slippage tolerance.
• FR-RSK-4 Layered risk: account-level limits, per-profile limits, and portfolio-level exposure checks (for example net USD exposure across pairs).
• FR-RSK-5 Pluggable filters configured per instrument and profile: spread, trading session, news blackout (event-to-currency mapping), Friday/weekend cutoff.
• FR-RSK-6 Hard limits live in code and configuration, never in prompts, and cannot be overridden by the AI.
7.10 Execution and reconciliation
• FR-EXE-1 Execution is behind a broker interface with backtest simulator, paper, and live implementations; MT5 is the first adapter.
• FR-EXE-2 Continuously reconcile internal state against the broker so actual positions and orders are always known.
• FR-EXE-3 Reconnect and retry with backoff, heartbeat monitoring, and safe handling of partial fills, requotes, and rejections.
• FR-EXE-4 The engine must run correctly with zero clients connected and with the AI service switched off.
7.11 Kill switch and halts
• FR-KIL-1 A kill switch cancels pending orders, flattens positions, and halts the engine.
• FR-KIL-2 Triggerable from CLI, file/flag, and one tap in every client; it works independently of the AI service.
• FR-KIL-3 Automatic halts (daily loss, drawdown, repeated errors, stale data, broker disconnect beyond a threshold) are logged and alerted.
7.12 AI assistant
The AI is a research and authoring layer with no path into live trading.
Allowed:
• Show P&L and performance (read-only, from the database).
• Run backtests in a sandbox on historical data, for any strategy, pair, or timeframe.
• Analyze trades: why taken, why lost, filter behavior, fills vs backtest.
• Add journal comments (append-only, labeled AI-authored, stored separately from trade records).
• Create or modify strategies as new draft versions.
Forbidden:
• Placing, modifying, cancelling, or closing orders; pausing, resuming, or stopping profiles; touching the kill switch.
• Changing risk limits, mode, credentials, or any running strategy version.
• Holding broker credentials or having any network route to the execution layer.
Requirements:
• FR-AI-1 The AI service runs as a separate process with its own permissions and read-only database access to trading data.
• FR-AI-2 Strategy changes by the AI produce a draft version with a diff; activation is a deterministic engine operation triggered by a human, and only when the profile is flat.
• FR-AI-3 Every AI prompt, interpretation, diff, approval, and resulting version is audit-logged.
• FR-AI-4 Untrusted text (news, web content) is never treated as commands.
• FR-AI-5 The AI warns when a requested change looks like curve-fitting to recent results and requires out-of-sample testing before a parameter change is accepted.
• FR-AI-6 Limits on how often a strategy can be activated, to discourage reactive tweaking.
7.13 Clients: web, desktop, mobile
• FR-CLI-1 All clients use the same authenticated API; none connects to the broker or engine directly.
• FR-CLI-2 Mobile is monitor-and-light-control: live P&L, positions, equity curve, risk status, recent signals, alerts, pause/resume, kill switch, AI chat, and approval of draft activations with biometric confirmation.
• FR-CLI-3 Web and desktop provide the full workstation: strategy authoring and diff review, large backtest reports, parameter-sensitivity views, journal, and settings.
• FR-CLI-4 Desktop may be delivered as an installable web app first, with a native wrapper later if needed.
• FR-CLI-5 No offline queueing of trade-affecting commands; clients show a stale-data banner when disconnected and disable those actions.
• FR-CLI-6 Commands are idempotent and server-authoritative, so retries and double taps are safe.
7.14 Notifications
• FR-NOT-1 Push alerts for fills, stop-outs, risk halts, kill-switch events, disconnects, rejected orders, and unexpected positions, plus a daily summary.
• FR-NOT-2 Critical alerts also go through a secondary channel (for example Telegram or email).
• FR-NOT-3 A dead-man check alerts the owner if the engine heartbeat stops.
7.15 Journal and reporting
• FR-JRN-1 Daily and per-trade journal entries by the user and the AI, always attributed.
• FR-JRN-2 Trade journal stores signal, risk decision, order, fill, expected vs actual fill, and strategy version.
• FR-JRN-3 Daily and weekly performance summaries available in-app.
7.16 Security and audit
• FR-SEC-1 Broker credentials exist only on the server in a secrets manager or environment variables, with trade-only permissions, and never on any client device.
• FR-SEC-2 Authentication with 2FA, short-lived tokens with refresh rotation, device registration and revocation, and biometric unlock on mobile.
• FR-SEC-3 The engine is never exposed to the internet; only the API gateway is, and the engine accepts commands only from it.
• FR-SEC-4 Append-only audit log of signals, risk decisions, orders, fills, commands (user, device, time), configuration changes, and AI interactions.
• FR-SEC-5 Step-up confirmation for consequential actions such as strategy activation.
8. Promotion Pipeline
Each combination of strategy version + instrument + timeframe + parameters moves through these states:
State
Entry requirement
Draft
Created (by the user or the AI).
Backtested
Backtest completed with valid data and reported costs, including out-of-sample results.
Paper
Running on a demo account.
Forward-tested
Forward test finished and passed its locked criteria.
Live-eligible
Forward-tested, with a human sign-off.
Any change to the combination resets its state to Draft. Live mode refuses anything that is not live-eligible.
9. Reference Scenario (First Acceptance Case)
The first end-to-end scenario is ema_atr_trend_v1 on XAUUSD, H1 (M15 supported), through MT5:
• Long when EMA(20) crosses above EMA(50) and close is above EMA(200); short is the mirror.
• Stop loss 2.0 x ATR(14); take profit 3.0 x ATR (or a 2.5 x ATR trailing stop as an alternative mode).
• Exit on stop, target, or opposite crossover; one position at a time; no pyramiding.
• Optional filters: session window, max spread, news blackout, Friday cutoff.
• All parameters live in the strategy file, none hardcoded.
This strategy exists to prove the platform works. It is not expected to be the final edge.
10. Non-Functional Requirements
• Reliability: engine recovers from disconnects and restarts without losing track of positions; stale or missing data blocks new trades.
• Reproducibility: a backtest with the same data, version, and config produces identical results.
• Performance: signal-to-order latency is not critical (bar-close strategies), but must stay well within the bar interval; backtests on years of M15 data complete in a reasonable time as background jobs.
• Observability: structured logs, health and heartbeat endpoints, and clear error states in every client.
• Portability: non-MT5 code develops and tests on any OS using a mock feed; MT5-specific code is isolated in the adapter (the MT5 Python package is Windows-only).
• Maintainability: typed code, automated tests, linting, and documented extension guides.
• Security: as in section 7.16; failures default to safe states (halt rather than guess).
11. Success Metrics and Acceptance Criteria
Platform acceptance (Phase 1):
• The reference strategy backtests end to end with deterministic, reproducible results.
• A second strategy and a second pair (for example EURUSD or USDJPY) are added with zero engine changes. If this requires engine changes, the abstraction has leaked.
• The lookahead test passes; risk-limit, kill-switch, timezone, and position-sizing tests pass.
• Simulated failures (disconnect, rejected order, partial fill, stale data) are handled without incorrect positions.
• A full month of paper trading completes with continuous reconciliation and a forward-test evaluation report.
• Web and mobile clients show live state and can pause, resume, and trigger the kill switch.
• Shutting down the AI service and all clients does not affect trading.
• No code path exists from the AI service to the execution layer.
Trading success is intentionally not a Phase 1 metric. The forward test checks that the system behaves correctly and matches its backtest, not that it is profitable.
12. Milestones
1. Foundations: repo, config system, models, logging, interfaces, audit log.
2. Data layer, instrument specs, and indicators.
3. Strategy plugin system, registry, versioning, and the reference strategy.
4. Risk manager, filters, and kill switch.
5. Backtest simulator with realistic costs, metrics, and reports.
6. Walk-forward, out-of-sample testing, and sensitivity analysis.
7. MT5 paper adapter, reconciliation, and reconnect handling.
8. API gateway, authentication, roles, and event streaming.
9. Web client, then mobile client, plus notifications.
10. AI service: read-only analysis, backtest runner, draft strategy authoring, journaling.
11. Forward-test evaluation tooling; the one-month forward test.
12. Gated live adapter, go-live checklist, and documentation.
13. Risks and Assumptions
Risk
Mitigation
Backtest results overstate live performance (costs, overfitting, lookahead)
Realistic cost models, out-of-sample and walk-forward testing, lookahead test, sensitivity analysis
Demo fills are better than live fills
Compare paper and live slippage; start live with small capital
One month yields few trades
Treat forward test as a bug and execution check, not proof of profitability
News events cause gaps and slippage in gold and FX
News blackout, max-spread filter, conservative stop sizing
Mobile or API compromise
2FA, device registration, roles, no broker credentials on clients, live mode not enableable from mobile
AI misreads a request or is manipulated
AI has no execution path; drafts only; human activation when flat; audit log
Overfitting from frequent strategy edits
Activation cooldowns, out-of-sample requirement, promotion reset on any change
MT5 dependencies (Windows-only, terminal must stay running)
Isolated adapter, mock feed for development, Windows VPS with monitoring
Regulatory limits on leveraged FX/CFD trading and automated trading
Verify rules and broker regulation for the owner's jurisdiction before going live
Assumptions: the owner trades their own account; an always-on Windows server or VPS is available; the chosen broker offers an MT5 demo and live account with the desired instruments; the owner sets forward-test criteria before the test begins.
14. Open Questions
1. Which broker and account currency will be used, and in which jurisdiction (affects compliance and available instruments)?
2. How many profiles should run concurrently in Phase 1: one, or a few?
3. Where should the server run (VPS provider and region)?
4. Who besides the owner, if anyone, needs access in the near term?
5. Which secondary alert channel is preferred: Telegram, email, or SMS?
6. What are the owner's forward-test pass/fail thresholds for the reference strategy?
7. Which AI model or provider is acceptable for the assistant (cost, privacy of trade data)?
8. Is a native desktop app needed, or is an installable web app sufficient?
15. Out of Scope Here
Visual design and user flows (covered in the Design document, to follow), architecture and technology choices (covered in the Tech Stack document), and trading strategy research beyond the reference strategy.
This document is a product requirements specification, not financial advice. Trading leveraged instruments carries a risk of loss, and backtested or paper results do not guarantee live results.
