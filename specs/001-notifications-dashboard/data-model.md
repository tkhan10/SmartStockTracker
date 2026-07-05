# Phase 1 Design: Data Model

Two new SQLite tables, added additively to `storage/db.py`'s existing `SCHEMA`
alongside the untouched `watchlist` table.

## Alert

Represents a user-defined rule tied to one watchlist symbol.

| Field | Type | Notes |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | |
| `symbol` | TEXT NOT NULL | Uppercased ticker; not a strict FK to `watchlist.symbol` so an alert can still be shown/flagged after its symbol is removed from the watchlist (see Edge Cases in spec.md) |
| `condition_type` | TEXT NOT NULL | One of `above`, `below`, `pct_change` |
| `threshold` | REAL NOT NULL | Must be > 0 at creation time (validated in `alert_service`, not the DB) |
| `email` | TEXT NOT NULL | Destination address for this alert |
| `status` | TEXT NOT NULL DEFAULT `'active'` | One of `active`, `fired`, `inactive` |
| `created_at` | TEXT NOT NULL | ISO 8601 UTC, set at creation |
| `last_fired_at` | TEXT NULL | ISO 8601 UTC, set when the alert transitions to `fired` |

**State transitions**: `active → fired` (condition met, email sent) → `active`
(user re-arms) or `inactive` (user disables); `active → inactive` (user disables
without firing) → `active` (user re-enables).

**Validation rules** (enforced in `alert_service`, matching spec FR-002):
- `threshold` must be numeric and > 0.
- `email` must match a basic well-formed-email pattern.
- `condition_type` must be one of the three supported values.
- Reject an exact duplicate (same `symbol` + `condition_type` + `threshold` +
  `email`, currently `active`) per the spec's Edge Cases.

## AlertEvent

Represents one time an alert's condition was evaluated as met and a
notification was attempted — the audit trail that also powers the Dashboard's
"recent alerts" feed.

| Field | Type | Notes |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | |
| `alert_id` | INTEGER NOT NULL | References `alerts.id` (no `FOREIGN KEY` constraint enforced, consistent with the rest of this SQLite schema having none; enforced at the application layer) |
| `symbol` | TEXT NOT NULL | Denormalized copy so history remains readable even if the alert is later deleted |
| `condition_type` | TEXT NOT NULL | Denormalized copy, same reason |
| `threshold` | REAL NOT NULL | Denormalized copy, same reason |
| `triggered_price` | REAL NOT NULL | The price/percent-change value observed at trigger time |
| `triggered_at` | TEXT NOT NULL | ISO 8601 UTC |
| `email_sent` | INTEGER NOT NULL | 0/1 — whether the email actually sent successfully (FR-009: a failed send must not be recorded as a successful fire) |
| `error` | TEXT NULL | Populated when `email_sent = 0`, for troubleshooting |

## Relationships

`AlertEvent.alert_id` conceptually references `Alert.id` (one alert has many
events over time), but the fields needed to render history are denormalized
onto `AlertEvent` itself so the Dashboard's recent-alerts feed and any future
alert-deletion flow don't need a join, and history survives alert deletion.
