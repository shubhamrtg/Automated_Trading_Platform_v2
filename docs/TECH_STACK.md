# Tech Stack Document: Automated Trading Platform

*Version 0.1 (Draft) · October 26, 2026 · Inputs: PRD v0.1, Design Document v0.1, and the owner's answers*

## 1. Purpose and Inputs

This document chooses the technologies for the platform described in the PRD and Design documents, and explains why. It is written so a coding agent can follow it.

**Owner inputs**

| Topic | Answer |
| --- | --- |
| Broker | Exness most likely, but the broker must be switchable at any time. Trading from India (see section 3, which affects this) |
| Account currency | USD or USDT |
| Where it runs | The owner's local Windows desktop or laptop |
| AI provider | Google Gemini |
| Code review | Mostly by agents; the owner will not review code line by line |
| Phone | Android |
| Backtest history | 5 years |
| Alerts | Telegram, push notifications, and email |
| Everything else | Decided in this document |

**Selection principles**

1. Boring, popular, strongly typed tools. Agents write and review the code, so favor ecosystems with strong static checking and heavy documentation.
2. Fewest moving parts. Everything runs on one Windows PC, so no Docker, Kubernetes, message brokers, or cloud databases in Phase 1.
3. Every external system (broker, data source, AI provider, alert channel) sits behind an interface and can be swapped.
4. Broker credentials never leave the engine's machine and are never visible to the AI service or any client.

## 2. Decisions at a Glance

| Area | Choice |
| --- | --- |
| Engine language | Python (latest version the MetaTrader5 package supports), managed with uv |
| Data and models | pandas, NumPy, Pydantic v2, Parquet files (pyarrow) |
| Database | SQLite in WAL mode via SQLAlchemy 2 and Alembic (Postgres possible later) |
| API gateway | FastAPI with Uvicorn, WebSocket for live updates, OpenAPI spec |
| Auth | Argon2 password, TOTP 2FA, short-lived JWT plus rotating refresh tokens, device registry, roles |
| Broker adapters | Interface with an MT5 adapter first; India-regulated broker adapter slot (section 3) |
| Web app | React + TypeScript + Vite, Tailwind CSS, Radix primitives, TanStack Query, Apache ECharts, Lucide icons |
| Desktop | Installable web app (PWA) |
| Mobile | React Native with Expo (Android first), shared TypeScript packages |
| AI | Google Gemini API (paid tier) through a provider-agnostic interface, in a separate service |
| Remote access | Tailscale between phone, laptop, and the home PC (no open router ports) |
| Alerts and monitoring | Telegram Bot API, Expo push, SMTP email, and an external heartbeat monitor |
| Quality | pytest, hypothesis, ruff, mypy, ESLint, tsc, Vitest, Playwright, axe, GitHub Actions, CodeRabbit |

## 3. Broker and Regulatory Constraint (read first)

This section is binding for the design. It is research, not legal advice.

**What was found**

- The Reserve Bank of India's Alert List (updated 19 November 2025) lists **Exness** (entry 6). The RBI says listed entities are neither authorised to deal in forex under FEMA nor to operate a forex electronic trading platform. Press coverage of the list says Indian residents cannot trade leveraged forex through offshore platforms, and that the RBI advises against sending money abroad for margin forex trading.
- Nothing found suggests that funding with USDT changes this position. Verify with a professional before relying on it.
- The regulated domestic route is different: NSE currency derivatives on INR pairs (for example USDINR, EURINR, GBPINR, JPYINR at Zerodha; cross-currency contracts such as EURUSD are not offered there) and exchange-traded gold products. Availability depends on the broker.
- Retail algorithmic trading in India is allowed through a broker's API under SEBI's framework, fully mandatory from 1 April 2026. Reported requirements include broker-controlled API access, unique algo ID tagging, static IP whitelisting, daily API session logout, and exchange registration above 10 orders per second. A bar-close strategy is far below that threshold. Some sources also say retail algos must be hosted on Indian servers. Confirm the exact current rules with the chosen broker.

**What this means for the build**

1. The broker is a plug-in. Phase 1 (backtest, paper trading, and forward test) must not depend on which broker is used for live trading.
2. **No live adapter is built or enabled until the owner records a live-broker decision in DECISIONS.md.** This is a gate before Phase 2.
3. The instrument spec must support exchange-traded contracts, not only spot forex. Add: contract expiry and roll rule, exchange calendar and trading sessions, lot size and tick size, margin model, settlement currency (INR). Account currency becomes a per-account setting (USD, INR, others).
4. A home internet connection usually has a dynamic IP. An India-regulated API would need a static IP (a paid ISP option), so confirm this before choosing that route.
5. The reference scenario (EMA + ATR trend) stays valid. The instrument it is demonstrated on may change from XAUUSD to a domestically available instrument. Backtests can use any historical data without a broker.
6. Ask a qualified Indian lawyer or chartered accountant before any real funds are used, including whether using a demo account with a broker on the Alert List is acceptable.

## 4. Architecture on One PC

```
Phone (Expo app) --Tailscale--+
Laptop browser / PWA --Tailscale--+--> API Gateway (FastAPI, auth, roles, audit)
                                         |            |             |
                                         v            v             v
                                  Engine control   Backtest     AI Service
                                  (127.0.0.1 only) worker       (Gemini)
                                         |
                              Engine (asyncio) --> Broker adapter --> MT5 terminal (Windows)
                                         |
                              SQLite (WAL) + Parquet history + logs
```

**Processes**

| Process | Owns | Notes |
| --- | --- | --- |
| Engine | Strategy loop, risk manager, execution, reconciliation, kill switch | The only process that sees broker credentials. Runs with zero clients connected |
| Engine control API | Commands: pause, resume, kill, activate | A small FastAPI app bound to 127.0.0.1 only, shared-secret header; only the gateway calls it |
| API gateway | Auth, roles, REST and WebSocket for all clients, audit log writes | The only thing reachable over Tailscale |
| Backtest worker | Runs backtests and walk-forward jobs from a job table | Reads historical files only; no broker access |
| AI service | Chat, analysis, draft strategy authoring, journal comments | Talks only to the gateway using an AI-role token (section 9) |
| MT5 terminal | Broker connection for the MT5 adapter | A desktop app; must run in a logged-in user session |

**Isolation on a single machine**

- Run the AI service under a separate low-privilege Windows user that cannot read the engine's files or the Windows Credential Manager entries holding broker credentials.
- The gateway enforces roles. The AI role can read data, request backtests, create draft strategies, and append journal comments. It has no route to the engine control API and no pause, resume, kill, or activation permission.
- The engine control API listens on localhost and requires a secret the AI service never receives.

## 5. Backend and Engine

| Concern | Choice | Why |
| --- | --- | --- |
| Language | Python, pinned to the newest version the official MetaTrader5 package supports (verify when installing) | The MT5 package is Python; the same language for engine, backtester, and API |
| Packaging | uv with a lockfile | Fast, reproducible installs |
| Data | pandas and NumPy | Standard for bars and indicators |
| Indicators | Implemented in the codebase (EMA, ATR, etc.) and tested against reference values | Few indicators needed; avoids a heavy dependency and keeps results deterministic |
| Models and config | Pydantic v2 | Validates strategy specs, instrument specs, profiles, and API payloads |
| Strategy specs | YAML parsed and validated against a schema; Python class plugins through the registry | Matches the PRD plugin model |
| Event loop | asyncio in the engine | No Celery or Redis; one process with scheduled tasks is enough |
| Backtest simulator | Custom event-driven code using the same strategy and risk classes as paper and live | Required by the PRD; existing libraries are not used because they would split the code paths |
| Database | SQLite (WAL) via SQLAlchemy 2 and Alembic migrations | Zero administration; Postgres can replace it later without changing models |
| Audit log | Append-only table with database triggers that block UPDATE and DELETE | Makes the audit trail tamper-resistant |
| Historical data | Parquet files, one per instrument and timeframe, with a validation step | Fast and compact for 5 years of bars |
| Logging | structlog, JSON, rotating files | Searchable, and easy for the AI analyst to read through the API |
| Secrets | Windows Credential Manager via the keyring library; .env only for non-secret config and demo values in development | Avoids a plain-text password file on a shared PC |

## 6. Broker and Data Abstraction

Interfaces (all in the engine package, none importing a vendor SDK):

- `MarketDataFeed`: historical bars, live bars, quotes with bid/ask spread.
- `ExecutionBroker`: place, modify, cancel, close, query orders and positions, account info.
- `InstrumentSpecProvider`: loads the instrument spec from the broker or from config.

Adapters:

| Adapter | Purpose | Phase |
| --- | --- | --- |
| ParquetFeed + BacktestBroker | Backtesting with modeled spread, commission, slippage, swap | 1 |
| Mt5Adapter | Live quotes and orders for any MT5 broker (demo in Phase 1). Symbol mapping lives in config (for example a suffix such as XAUUSDm on some account types) | 1 |
| MockMt5 | Lets all non-MT5 code and CI run on any machine without a terminal | 1 |
| IndiaBrokerAdapter | Domestic broker API (for example Zerodha Kite Connect, Dhan, Upstox, Angel One), added only after the live-broker decision | 2, if chosen |

Notes:

- MT5 is not a FIX API. Any text that says FIX in the designs is wrong for this stack.
- Switching brokers means writing one adapter and one instrument-spec mapping, with zero changes to the engine, strategies, or risk manager.
- A simulated paper broker (fills computed internally against live quotes) is available as a fallback for brokers that have no demo environment.

## 7. Historical Data (5 Years)

- Primary: export from the connected MT5 broker (rates and spreads), stored as Parquet.
- If the broker's history is shorter than 5 years or has gaps, add a second source such as Dukascopy's free historical exports. Record the source in each dataset's metadata.
- Backtests report the data source, and warn when the backtest data and the live broker differ.
- A validation step checks gaps, duplicates, bad ticks, timezone offsets, and missing spread data before any dataset is accepted.
- For an Indian domestic broker, historical data from its API may be limited or paid. Plan for a separate data source.

## 8. API, Auth, and Security

| Concern | Choice |
| --- | --- |
| Framework | FastAPI, with Pydantic models producing the OpenAPI spec |
| Realtime | WebSocket stream of engine events (positions, P&L, status, alerts) |
| Client types | Generated TypeScript client from the OpenAPI spec, shared by web and mobile |
| Passwords | Argon2 (argon2-cffi) |
| 2FA | TOTP (pyotp); hardware keys deferred to Phase 2 |
| Tokens | Short-lived JWT access tokens, rotating refresh tokens stored hashed, per-device registration and revocation |
| Roles | Viewer, Operator, Admin, plus an AI role and a Live-enable privilege that is never available from mobile (see DECISIONS.md D8) |
| Idempotency | Every command carries an idempotency key; the gateway and engine reject duplicates |
| Remote access | Tailscale on the PC, laptop, and phone. No router port forwarding, no public URL |
| Transport | HTTPS inside the Tailscale network |
| Local security | Full-disk encryption (BitLocker) on the PC, and a locked screen when idle |
| Audit | Every command and configuration change is written to the append-only audit table with user, device, and time |

## 9. AI Service (Gemini)

- **SDK and interface:** Google's official Gemini SDK for Python, wrapped in a provider-agnostic `LLMClient` interface so the provider can change.
- **Model choice:** the model ID is an environment setting, not hardcoded, because model names change quickly. Start with a Flash-class model for chat and analysis, and use a Pro-class model only for strategy authoring if needed. Pin an explicit model ID rather than a moving alias for reproducible behavior.
- **Paid tier required.** Google states that content on the free tier may be used to improve its products and that the paid tier does not use it for that purpose. Use a paid-tier API key, and re-check the current data terms before sending trade data.
- **Data minimization:** send only the aggregates and records a question needs; never send credentials, tokens, or account numbers.
- **Tools given to the model (function calling):** read P&L and trades, read reports, request a backtest, create a draft strategy version, append a journal comment (AI-tagged). Nothing else.
- **Never given:** broker access, engine control, pause, resume, kill switch, activation, risk-limit edits, live enablement.
- **Guardrails in code:** a tool allowlist, an AI-role token with those permissions only, rate limits, logging of every prompt, tool call, and result to the audit log, and untrusted text (news, web pages) never treated as commands.
- **Curve-fitting control:** draft changes proposed from recent losses must come with an out-of-sample backtest before they can be reviewed.
- **Run without it:** the engine and clients work normally with the AI service stopped.
- **No framework needed:** direct SDK calls. LangChain-style agent frameworks add complexity with no benefit here.

## 10. Web and Desktop App

| Concern | Choice | Why |
| --- | --- | --- |
| Framework | React with TypeScript (strict) and Vite | Single-page app against a separate API; no server rendering needed |
| Styling | Tailwind CSS with CSS-variable tokens for dark and light | The Stitch exports are Tailwind-based; tokens come from the Design document |
| Accessible primitives | Radix UI (tooltip, dialog, tabs, accordion, switch) | Keyboard and screen-reader behavior built in; matches the tooltip spec |
| Server state | TanStack Query, with the WebSocket feeding its cache | Less custom state code |
| Routing | React Router | Standard |
| Forms | React Hook Form with Zod | Validates strategy parameters in the browser against the same ranges as the schema |
| Charts | Apache ECharts | One library covers area, drawdown, heatmap, and comparison overlays with theming |
| Icons and fonts | Lucide icons; Inter and JetBrains Mono self-hosted through Fontsource | Replaces the CDN assets in the exports |
| Theme toggle | Tailwind dark class on the root, saved in local storage, defaulting to the OS setting, applied before first paint | Meets the no-flash requirement |
| Desktop | PWA through vite-plugin-pwa | Installable; a native wrapper is not needed |
| Tests | Vitest and React Testing Library, Playwright end to end, axe for accessibility | Agent-friendly automated checks |

## 11. Mobile App (Android)

| Concern | Choice |
| --- | --- |
| Framework | React Native with Expo, TypeScript strict, Expo Router |
| Styling | NativeWind so the same Tailwind tokens apply |
| Shared code | A pnpm workspace with packages for the generated API client, design tokens, and formatting (P&L signs, arrows, currency) |
| Auth storage | expo-secure-store; biometric unlock through expo-local-authentication |
| Push | Expo push notifications (Firebase Cloud Messaging on Android) |
| Install | A debug or release APK built with EAS Build or locally, installed directly on the owner's phone; a store account is not needed for personal use |
| Rules | No broker credentials on the phone; no live enablement; no offline queue for trade-affecting commands; stale-data banner when disconnected |

Mobile screens follow the Design document once the mobile designs are exported.

## 12. Notifications and Monitoring

| Need | Choice |
| --- | --- |
| Push | Expo push to the Android app |
| Telegram | Telegram Bot API through plain HTTPS calls (httpx) |
| Email | SMTP (smtplib) |
| Engine-down detection | An external heartbeat monitor (for example Healthchecks.io's free plan). The engine pings it every minute; if the pings stop, the service emails and messages the owner. This catches a powered-off or frozen PC, which the engine cannot report on itself |
| Critical alerts | Sent through at least two channels (push plus Telegram) |
| Health | Health and heartbeat endpoints on the gateway; engine status pill in every client |

## 13. Running on the Local PC

| Concern | Approach |
| --- | --- |
| Always on | Disable sleep and hibernate; set Windows Update active hours; use a UPS if power cuts are common; wired Ethernet is preferred |
| Starting up | The MT5 terminal is a desktop app, so use an auto-logon user and Task Scheduler tasks at logon to start MT5, then the engine, gateway, worker, and AI service (the AI service under its own user). Restart on failure |
| Reboots and restarts | On start, the engine reconciles with the broker before taking any new trade |
| Security trade-off | Auto-logon is convenient but weakens physical security, so use BitLocker and keep the PC in a safe place |
| Sleeping laptop | A laptop is a weaker host than a desktop. If it must be used, plug it in, set the lid action to do nothing, and treat it as a paper-phase host only |
| Backups | Daily copy of the SQLite database, strategy files, and config to a second drive or cloud storage you control, with no credentials included |
| Move to a VPS | Plan to move to a Windows VPS before live trading. A home PC has outages and a dynamic IP |

## 14. Quality, Testing, and Review (Agent-Reliant)

Because review is delegated to agents, automated checks have to be strict and independent of the agent that wrote the code.

**Python:** pytest, hypothesis (property tests for position sizing, risk limits, and the lookahead guard), ruff, mypy in strict mode for the engine, risk, and execution packages, and a coverage floor on risk and execution code.

**Frontend:** ESLint, tsc in strict mode, Vitest, Playwright, and axe accessibility checks in both themes.

**Mandatory tests that must always stay green:**

- lookahead test (output at bar N unchanged when future bars change)
- role-permission tests (no role can change risk limits unless Admin; no code path can withdraw funds; the AI role cannot reach engine control)
- kill-switch test (orders cancelled and positions closed before any disconnect)
- simulated failures (disconnect, rejection, partial fill, stale data)
- a banned-phrases test on UI text (guarantees, safety, regulation, custody claims)
- adding a second strategy and a second instrument with zero engine changes

**Pipeline:** GitHub Actions on Windows and Linux (with MockMt5), pre-commit hooks including secret scanning (gitleaks), CodeRabbit on every pull request, branch protection on main, and lockfiles (uv, pnpm). Avoid dependency releases less than about two weeks old.

**Human checkpoints, even though review is delegated:** read the plain-language summary of any change that touches risk, execution, authentication, permissions, or the live gate, and approve those yourself. An agent reviewing another agent's work is not an independent check on its own.

## 15. Repository Layout

```
trading-platform/
  AGENTS.md  TASKS.md  .gitignore  .env.example
  docs/            PRD.md  DESIGN.md  TECH_STACK.md  DECISIONS.md  design/reference/
  engine/          core, strategies, risk, execution, data, backtest, storage
  engine/adapters/ mt5, backtest, (india, later)
  gateway/         FastAPI app, auth, roles, websocket
  ai_service/      Gemini client, tools, guardrails
  web/             React app
  mobile/          Expo app
  packages/        api-client, tokens, formatting
  scripts/         data export, service setup
  tests/
```

## 16. Mapping to PRD Milestones

| PRD milestone | Main stack pieces |
| --- | --- |
| 1. Foundations | uv, Pydantic, SQLAlchemy and Alembic, structlog, audit triggers, interfaces |
| 2. Data layer and instruments | pandas, Parquet, validation, instrument spec (with expiry, sessions, and currency fields) |
| 3. Strategy plugins | YAML schema, registry, EMA and ATR indicators |
| 4. Risk and kill switch | Risk manager, filters, kill switch, hypothesis tests |
| 5. Backtester | Event-driven simulator, cost models, reports, ECharts data |
| 6. Walk-forward and sensitivity | Worker process and job table |
| 7. MT5 paper adapter | MetaTrader5 package, reconciliation, reconnect, MockMt5 |
| 8. API and auth | FastAPI, Argon2, TOTP, JWT, roles, WebSocket, OpenAPI |
| 9. Web, then mobile, plus alerts | React and Vite, Tailwind tokens, Expo, Telegram, push, email |
| 10. AI service | Gemini SDK, tool allowlist, AI role |
| 11. Forward test | Local PC operations, heartbeat monitor, evaluation script |
| 12. Live gate | Only after the live-broker decision; a broker adapter and compliance check |

## 17. Alternatives Considered

| Rejected for now | Reason |
| --- | --- |
| Next.js | A separate API already exists; server rendering adds complexity |
| Celery, Redis, RabbitMQ | One PC; asyncio and a job table are enough |
| PostgreSQL | SQLite handles one owner; migration path kept open |
| Docker or Kubernetes | MT5 needs a Windows desktop session |
| Flutter | Would not share TypeScript code with the web app |
| backtrader, vectorbt, NautilusTrader | The PRD requires identical code in backtest, paper, and live |
| LangChain or agent frameworks | Direct SDK calls with a tool allowlist are simpler and easier to audit |
| Public cloud hosting of the engine | Broker credentials would leave the owner's machine; revisit with a VPS in Phase 2 |

## 18. Risks and Open Items

| Item | Detail | Owner action |
| --- | --- | --- |
| Live-broker legality and choice | See section 3 | Decide and record in DECISIONS.md before Phase 2; seek professional advice |
| Static IP | Needed for an India-regulated API | Ask the ISP |
| Home PC reliability | Outages, updates, sleep | Follow section 13; move to a VPS before live |
| MT5 package support | Windows only; Python version limits | Verify during setup |
| Gemini data terms and model names | Change over time | Use the paid tier; re-check terms; keep the model ID in config |
| Accounts to create | GitHub, Telegram bot, Google Cloud billing for Gemini, Tailscale, Healthchecks.io, an MT5 demo from a broker you are comfortable with | Create when each milestone needs it |
| Agent-only review | No human code review | Keep the mandatory tests and human checkpoints in section 14 |

*This document is a technical specification, not legal or financial advice.*
