# DECISIONS.md

Owner decisions that resolve open questions in `docs/PRD.md` and `docs/DESIGN.md`. The agent treats an **Accepted** decision as binding. Anything marked **Proposed** or **Needs input** is not binding: ask before relying on it.

Status values: `Accepted`, `Proposed` (recommended, waiting for the owner), `Needs input` (cannot be decided without the owner).

## Design decisions (from DESIGN.md section 14)

### D1. Product name
- **Proposed:** keep a neutral working name in one config constant (`APP_NAME`). Do not use "AuraFX" or the version history from the Stitch brief anywhere in code, UI or docs.
- **Status:** Proposed

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
- **Proposed:** decide in `docs/TECH_STACK.md`. The exports use Material Symbols and CDN fonts; the build must bundle all icons, fonts and images locally.
- **Status:** Proposed

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

- **Status:** Proposed

## PRD open questions (PRD section 14)

| # | Question | Proposed answer | Status |
|---|---|---|---|
| 1 | Broker, account currency, jurisdiction | Cannot be proposed. Blocks `TECH_STACK.md`. | Needs input |
| 2 | Concurrent profiles in Phase 1 | Data model supports many. The first forward test runs **one** profile so results are attributable. Others can exist as Draft or Backtested. | Proposed |
| 3 | Server location | A Windows VPS (required by the MT5 Python package), placed near the broker's server. Provider is the owner's choice. | Needs input |
| 4 | Other users | Owner only in Phase 1. Roles exist in the data model. | Proposed |
| 5 | Secondary alert channel | Telegram, with email as backup. | Proposed |
| 6 | Forward-test thresholds | See D4. | Needs input |
| 7 | AI provider | Use a provider-agnostic interface. Choose a provider whose terms allow no training on your data and clear retention limits, and send only the data a task needs. | Needs input |
| 8 | Native desktop app | No. An installable web app first. | Proposed |

## How to use this file

1. Read each Proposed item and change it if you disagree.
2. Change `Proposed` to `Accepted` on the ones you agree with.
3. Fill in the `Needs input` rows (D4 numbers, broker, server, AI provider).
4. Add a new decision here whenever the agent asks a question and you answer it, so the answer is not lost.
