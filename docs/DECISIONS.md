# DECISIONS.md

Owner decisions that resolve open questions in `docs/PRD.md`, `docs/DESIGN.md` and `docs/TECH_STACK.md`. The agent treats an **Accepted** decision as binding. Anything else is not binding: ask before relying on it.

Status values:
- `Accepted`: decided by the owner (or delegated to Claude by the owner, where marked).
- `Proposed`: recommended, waiting for the owner.
- `Needs input`: cannot be decided without the owner.
- `Blocked`: the agent must not build, enable or depend on anything this decision controls until it is `Accepted`.

Last updated: October 26, 2026.

## Open items for the owner (start here)

1. **D9 Live broker (Blocked, gate before Phase 2).** Take professional advice, then record the decision.
2. **D4 Forward-test numbers (Needs input).** Set them after the first backtest.
3. Read the `Proposed` items and mark each `Accepted` or edit it.
4. Check with your internet provider whether a static IP is available (matters only for an India-regulated broker API, see D9).

## Decisions from the owner's answers (October 26, 2026)

### D9. Live broker and jurisdiction
- **Owner's answer:** trading from India. Exness "most probably", and the app must let the broker be switched at any time.
- **Constraint found in research (see `docs/TECH_STACK.md` section 3; not legal advice):** Exness appears on the RBI Alert List of entities not authorised under FEMA to deal in forex or operate forex trading platforms. Press coverage says Indian residents cannot trade leveraged forex through offshore platforms. The regulated domestic route is NSE currency derivatives on INR pairs and exchange-traded gold products through an Indian broker's API, under SEBI's retail algo framework (algo ID tagging, static IP, broker-controlled API).
- **Decision:**
  - Phase 1 (backtest, paper trading, forward test) is broker-agnostic and does not depend on the live broker.
  - **No live broker adapter is built or enabled until this decision is `Accepted`.**
  - The instrument spec must support exchange-traded contracts: expiry and roll rule, exchange calendar and sessions, lot and tick size, margin model, settlement currency.
  - Phase 1 reference instrument: any instrument with usable historical data (for example XAUUSD or EURUSD history). Revisit once the live broker is chosen.
- **Owner must record when decided:** broker name, API or platform (for example MT5 or a domestic broker API), instruments, account currency, the legal basis the owner was advised on, and static IP availability.
- **Status:** Blocked (gate before Phase 2). Phase 1 broker-agnostic design: Accepted.

### D10. Account currency
- **Owner's answer:** USD or USDT.
- **Decision:** account currency is a per-account setting, default USD, and position sizing converts through the instrument's conversion path. How an account is funded (including USDT) is outside the platform and is part of the advice in D9.
- **Status:** Accepted

### D11. Where the engine runs
- **Owner's answer:** the owner's local Windows desktop or laptop.
- **Decision:** a local Windows PC for Phase 1 (paper trading and the forward test), set up as described in `docs/TECH_STACK.md` section 13 (no sleep, auto-start, backups, heartbeat monitor). A desktop is preferred over a laptop.
- **Proposed:** move to a Windows VPS before any live trading.
- **Status:** Accepted (local PC for Phase 1). Proposed (VPS before live).

### D12. AI provider
- **Owner's answer:** Google Gemini.
- **Decision:** the assistant uses Gemini through a provider-agnostic interface, in a separate low-privilege service. The model ID is a config setting, not hardcoded.
- **Proposed:** use a paid-tier API key, because Google's free tier may use content to improve its products. Re-check the current data terms before sending any trade data.
- **Status:** Accepted (provider). Proposed (paid tier).

### D13. Code review approach
- **Owner's answer:** the owner will rely on agents for code review.
- **Decision:** reviews are done by agents and CodeRabbit, backed by the mandatory automated tests in `docs/TECH_STACK.md` section 14.
- **Proposed:** the owner still approves a plain-language summary of any change that touches risk, execution, authentication, permissions or the live gate. An agent reviewing another agent's work is not an independent check.
- **Status:** Accepted (agent review). Proposed (human checkpoints).

### D14. Mobile platform
- **Owner's answer:** Android phone.
- **Decision:** Android first, built with React Native and Expo, installed directly as an APK on the owner's phone.
- **Status:** Accepted

### D15. Backtest history
- **Owner's answer:** 5 years.
- **Decision:** five years of bars with spread data. Source: the connected broker's history, plus a second source if it is short or has gaps. Each dataset records its source, and backtests warn if the data source differs from the live broker.
- **Status:** Accepted

### D16. Alert channels
- **Owner's answer:** yes to push notifications, Telegram and email.
- **Decision:** critical alerts go through at least two channels. An external heartbeat monitor alerts if the engine or the PC goes silent.
- **Status:** Accepted (channels). Proposed (external heartbeat monitor).

### D17. Technology stack
- **Owner's answer:** "the rest you can decide yourself".
- **Decision:** the choices in `docs/TECH_STACK.md` are adopted, including Python, FastAPI, SQLite, React with Tailwind, React Native with Expo, Apache ECharts, Lucide icons, Tailscale for remote access, and local Windows service setup. This also settles D7.
- **Status:** Accepted (delegated to Claude on October 26, 2026). The owner may revise any item after reading the document.

## Design decisions (from DESIGN.md section 14)

### D1. Product name
- **Decision:** keep a neutral working name in one config constant (`APP_NAME = "Automated Trading Platform"`). Do not use "AuraFX" or the version history from the Stitch brief anywhere in code, UI or docs.
- **Status:** Accepted

### D2. Strategy activation behavior
- **Proposed:** in Phase 1, activation is **blocked until the profile is flat** (no open position, no pending order). The button is disabled with a tooltip. No queued or scheduled swaps. Activating resets the combination to Draft and restarts the forward-test clock.
- **Why:** matches PRD FR-PRO-4, needs no extra engine state machine, and a scheduled "swap when flat" can be added later.
- **Status:** Proposed

### D3. Hardware key for live mode
- **Proposed:** not needed in Phase 1 (live is disabled). For Phase 2, require desktop or CLI re-authentication plus 2FA. A hardware key is an optional later upgrade.
- **Status:** Proposed

### D4. Forward-test criteria
- **Proposed:** criteria are set per profile before the test starts and locked once it starts. The numbers in the Stitch designs (40 trades, 5% drawdown, 1.40 profit factor, 15% deviation, 0.15 pip slippage) are **not** adopted. In particular, 40 trades in 30 days is unrealistic for an H1 crossover strategy, which may produce only a handful of trades a month.
- **Starting points for the owner to adjust before the first test:**
  - Duration: 30 calendar days.
  - Minimum trades: about half the trade count the backtest implies for 30 days, with a floor of 10.
  - Maximum drawdown: relative to the backtest (for example no worse than 1.5 times the backtest maximum drawdown).
  - Minimum profit factor: a fixed floor set by the owner (for example 1.2) and not far below the backtest value.
  - Maximum deviation from backtest: a tolerance band set by the owner.
  - Maximum slippage: relative to the slippage assumed in the backtest (for example 2 times), measured in account currency or instrument points. Do not use "pips" as a universal unit.
- **Status:** Needs input (owner sets the numbers; these are suggestions, not financial advice)

### D5. Stop controls
- **Proposed:** a global Kill switch in the top bar, plus per-profile Pause. Pause stops new entries and does not close open positions, and the UI says so. A per-profile "close and halt" is a later addition.
- **Status:** Proposed

### D6. Mobile scope (Phase 1)
- **Proposed:** Home, Positions and trade detail, Profiles (pause/resume only), Kill switch, Alerts, AI chat, activation approval, sign-in and devices. Everything else is read-only or desktop-only. No strategy editing, no risk-limit editing, no live-mode enablement on mobile.
- **Status:** Proposed

### D7. Icon set and chart library
- **Decision:** Lucide icons, Apache ECharts, and self-hosted Inter and JetBrains Mono fonts, all bundled locally with no CDN assets (see D17 and `docs/TECH_STACK.md` section 10).
- **Status:** Accepted (delegated to Claude)

### D8. Roles and permissions
- **Proposed:**

| Capability | Viewer | Operator | Admin |
|---|---|---|---|
| View P&L, positions, reports, journal | Yes | Yes | Yes |
| Run backtests, create draft strategies, add journal notes | No | Yes | Yes |
| Pause or resume a profile, use the Kill switch | No | Yes | Yes |
| Activate a strategy version | No | No | Yes |
| Edit risk limits and settings, manage devices | No | No | Yes |
| Enable live mode | Separate privilege: desktop or CLI with re-authentication, never mobile | | |
| Withdraw funds | Not possible for any role or code path | | |

- The AI service uses its own AI role (read data, request backtests, create drafts, append AI-tagged journal notes) and never receives engine control permissions.
- **Status:** Accepted

## PRD open questions (PRD section 14)

| # | Question | Answer | Status |
|---|---|---|---|
| 1 | Broker, account currency, jurisdiction | India. Exness stated as likely but switchable. USD or USDT. See D9 and D10. | Blocked for live trading. Accepted for the broker-agnostic Phase 1 |
| 2 | Concurrent profiles in Phase 1 | Data model supports many. The first forward test runs **one** profile so results are attributable. Others can exist as Draft or Backtested. | Proposed |
| 3 | Server location | Local Windows PC for Phase 1 (D11). Windows VPS before live. | Accepted (local PC). Proposed (VPS) |
| 4 | Other users | Owner only in Phase 1. Roles exist in the data model. | Proposed |
| 5 | Secondary alert channel | Telegram, push and email (D16). | Accepted |
| 6 | Forward-test thresholds | See D4. | Needs input |
| 7 | AI provider | Google Gemini (D12). | Accepted |
| 8 | Native desktop app | No. An installable web app (PWA) first. | Accepted (delegated to Claude) |

## How to use this file

1. Read each `Proposed` item and change it if you disagree.
2. Change `Proposed` to `Accepted` on the ones you agree with.
3. Fill in the `Needs input` and `Blocked` rows when you are ready (D4 numbers, D9 live broker).
4. Add a new decision here whenever the agent asks a question and you answer it, so the answer is not lost.

## Change log

- 2026-10-26: Added owner answers (D9 to D17), settled D7, and updated the PRD question table. D9 added as a gate before Phase 2.
- 2026-10-19: Initial version with proposed answers (D1 to D8).
