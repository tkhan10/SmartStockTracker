# Feature Specification: Notifications & Dashboard (Phase 2)

**Feature Branch**: `001-notifications-dashboard`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Phase 2 (1 week): Notifications system with Email alerts, and a Dashboard page. Build on top of the existing SmartStockTracker Phase 1 app (Streamlit, stock search, watchlist, stock detail pages, pluggable stock data providers via Finnhub/yfinance) without changing any existing Phase 1 functionality. Notifications & Email Alerts: users should be able to set up price alerts (e.g. price crosses above/below a threshold, or percent change threshold) on symbols in their watchlist, and receive an email notification when the condition is met. Needs a way to check prices periodically and trigger emails. Dashboard: a new page giving an at-a-glance overview of the user's watchlist - e.g. summary of gainers/losers, overall watchlist performance, recent alerts fired, and key stats - distinct from the existing per-stock Stock Detail page and the plain Watchlist list page."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a price alert on a watched stock (Priority: P1)

A user has one or more symbols in their watchlist. From the watchlist or stock detail page, they set up an alert for a symbol: "notify me when price goes above $X", "notify me when price goes below $X", or "notify me when it moves more than X% since last check". The user provides an email address to receive the notification.

**Why this priority**: This is the core value of Phase 2 — without the ability to create an alert, there is nothing to notify on and no dashboard content to show. It is the minimum viable slice.

**Independent Test**: Can be fully tested by adding a symbol to the watchlist, creating an alert with a threshold, and confirming the alert appears in a list of active alerts with the correct condition — delivers value (a saved, visible alert) even before any email has fired.

**Acceptance Scenarios**:

1. **Given** a symbol is in the watchlist, **When** the user creates a "price above $X" alert with a valid email, **Then** the alert is saved and listed as active for that symbol.
2. **Given** a symbol is in the watchlist, **When** the user creates a "price below $X" or "percent change" alert, **Then** the alert is saved with the correct condition type and threshold.
3. **Given** an invalid email address or a non-numeric/negative threshold, **When** the user submits the alert form, **Then** the system rejects it with a clear inline error and does not save it.
4. **Given** a symbol is removed from the watchlist, **When** the user views its alerts, **Then** the system clearly indicates the alert's symbol is no longer watched (see Edge Cases for handling).

---

### User Story 2 - Receive an email when an alert condition is met (Priority: P1)

Once an alert exists, the system periodically checks the latest price for that symbol. When the condition (threshold crossed, or percent-change threshold reached) is met, the system sends an email notification to the address configured on the alert and records that the alert fired.

**Why this priority**: This is the payoff of User Story 1 — an alert nobody is ever notified about delivers no real value. Together, Stories 1 and 2 form the smallest usable notifications feature.

**Independent Test**: Can be fully tested by creating an alert with a threshold that is already satisfied by the current price, running a price check, and confirming an email is sent and the alert is marked as fired — independently verifiable without the Dashboard existing yet.

**Acceptance Scenarios**:

1. **Given** an active "price above $X" alert where the latest price is above $X, **When** the periodic price check runs, **Then** exactly one email is sent to the alert's address and the alert is marked as fired (not re-sent on every subsequent check).
2. **Given** an active alert whose condition is not yet met, **When** the periodic price check runs, **Then** no email is sent and the alert remains active.
3. **Given** the stock data provider is temporarily unavailable during a check, **When** the periodic price check runs, **Then** the check fails gracefully for that symbol (logged/skipped) without crashing and is retried on the next cycle.
4. **Given** an alert has already fired, **When** the user wants to be notified again, **Then** they can re-arm (reactivate) the alert from the UI.

---

### User Story 3 - View portfolio-wide health on a Dashboard (Priority: P2)

The user opens a new "Dashboard" page and immediately sees an at-a-glance summary of their whole watchlist: which symbols are up or down today (gainers/losers), overall watchlist performance, key stats (e.g. number of symbols watched, average change), and a feed of recently fired alerts — without having to click into each stock individually.

**Why this priority**: Valuable and clearly requested, but it is a read-only aggregation view that depends on data (watchlist prices, fired alerts) that already exists once Stories 1-2 (or even just Phase 1's watchlist) are in place. The app is still useful without it.

**Independent Test**: Can be fully tested by populating the watchlist with a few symbols and confirming the Dashboard page renders a gainers/losers breakdown and summary stats that match what the existing Watchlist page shows for the same symbols — independently verifiable by comparing the two pages' numbers.

**Acceptance Scenarios**:

1. **Given** the watchlist has multiple symbols with mixed price movement, **When** the user opens the Dashboard, **Then** they see the symbols grouped or ranked into gainers and losers with their current change.
2. **Given** one or more alerts have fired recently, **When** the user opens the Dashboard, **Then** they see a "recent alerts" section listing what fired and when.
3. **Given** the watchlist is empty, **When** the user opens the Dashboard, **Then** the page shows a friendly empty state instead of an error.
4. **Given** the stock data provider fails for one symbol, **When** the user opens the Dashboard, **Then** the rest of the dashboard still renders using the symbols that succeeded, with the failing symbol clearly marked as unavailable.

---

### Edge Cases

- What happens when a user creates a duplicate alert (same symbol, same condition, same threshold)? System should prevent exact duplicates or clearly show both without confusion.
- What happens when a watched symbol backing an active alert is removed from the watchlist? The alert is not silently orphaned — it is either automatically deactivated or clearly flagged as referring to an unwatched symbol.
- How does the system handle an alert threshold that can never realistically be met (e.g., a percent-change threshold of 0%)? Basic input validation (e.g., threshold must be > 0) prevents the most obvious cases.
- What happens if email sending fails (bad credentials, provider outage)? The failure is logged and the alert remains active/unfired so it can be retried on the next check, rather than being silently marked as fired.
- What happens when two alerts on the same symbol fire in the same check cycle? Each alert is evaluated and notified independently.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to create a price alert on any symbol currently in their watchlist, specifying a condition type (price above threshold, price below threshold, or percent-change threshold) and a notification email address.
- **FR-002**: System MUST validate alert input (numeric positive threshold, well-formed email) before saving and show inline errors otherwise.
- **FR-003**: Users MUST be able to view a list of their alerts, showing symbol, condition, threshold, destination email, and status (active / fired / inactive).
- **FR-004**: Users MUST be able to deactivate (disable) an alert and re-arm (reactivate) a previously fired alert.
- **FR-005**: Users MUST be able to delete an alert.
- **FR-006**: System MUST periodically evaluate all active alerts against the latest available price for their symbol using the app's existing stock data provider.
- **FR-007**: System MUST send an email notification to the alert's configured address when its condition is met, and MUST mark the alert as "fired" so the same condition does not re-notify repeatedly.
- **FR-008**: System MUST record a history of fired alerts (symbol, condition, threshold, price at trigger, timestamp) for display on the Dashboard.
- **FR-009**: System MUST continue to function (fail gracefully, without crashing the app) if the email provider or the stock data provider is unavailable during a check cycle.
- **FR-010**: System MUST provide a new Dashboard page presenting: a gainers/losers breakdown of the current watchlist, summary stats (e.g. total symbols watched, average/aggregate change), and a recent-alerts feed.
- **FR-011**: The Dashboard MUST handle an empty watchlist and partial data-provider failures without erroring the whole page.
- **FR-012**: Phase 2 MUST NOT alter the existing behavior of the Search, Watchlist, or Stock Detail pages, or the existing provider-selection mechanism; it only adds new pages/capabilities alongside them.
- **FR-013**: System MUST evaluate alerts and send emails on a recurring schedule triggered by a scheduled script (e.g. cron / CI schedule / task scheduler) that runs independently of whether a user has the Streamlit app open in a browser, so that alerts fire even when no one is actively viewing the app.
- **FR-014**: System MUST send alert emails via a configurable SMTP account (host, port, username, password/app-password, from-address supplied through the existing environment-variable/`st.secrets` configuration pattern used for `FINNHUB_API_KEY`), so no new third-party email service account is required to get started.

### Key Entities

- **Alert**: A user-defined rule tied to one watchlist symbol — condition type (above / below / percent-change), threshold value, destination email, current status (active, fired, inactive), created timestamp, and last-fired timestamp (if any).
- **Alert Event**: A record of a specific time an alert's condition was met and a notification was attempted — references the alert, the symbol, the triggering price, the timestamp, and whether the email send succeeded.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can go from "symbol in watchlist" to "alert created and visible in their alert list" in under 1 minute.
- **SC-002**: When an alert's condition is genuinely met, the corresponding email notification arrives within one scheduled check cycle (see Assumptions for the default cycle length), with no duplicate emails for the same fire event.
- **SC-003**: Opening the Dashboard with an existing watchlist shows a complete gainers/losers and summary view within the same load-time expectations as the existing Watchlist page (i.e., no perceptibly slower experience).
- **SC-004**: Existing Phase 1 flows (search, add/remove from watchlist, view stock detail, switch provider) continue to work exactly as before, with zero regressions, after Phase 2 ships.
- **SC-005**: 100% of alert-check cycles that encounter a provider or email-send failure are logged and do not crash the running app or corrupt alert state.

## Assumptions

- The app remains single-user (matching Phase 1, which has no login/accounts): all alerts belong to one shared watchlist/alert list, each alert simply carries its own destination email address rather than being scoped to a user account.
- The scheduled price-check cycle runs by default every 15 minutes; this is configurable but not exposed as an end-user setting in Phase 1 of this feature.
- "Recent alerts" on the Dashboard shows, by default, alert events from the last 7 days.
- Percent-change alerts are evaluated against the same reference point already used by the stock data providers for "change"/"percent change" (i.e., previous close), not a rolling custom window.
- An alert that has fired must be manually re-armed by the user rather than automatically resetting itself, to avoid duplicate-email spam on a stock that hovers around a threshold.
