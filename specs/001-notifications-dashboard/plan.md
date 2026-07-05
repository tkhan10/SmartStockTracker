# Implementation Plan: Notifications & Dashboard (Phase 2)

**Branch**: `001-notifications-dashboard` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-notifications-dashboard/spec.md`

## Summary

Add price alerts with email notifications and a portfolio Dashboard page on top of
the existing Phase 1 SmartStockTracker app, with zero changes to Phase 1 behavior.
Alerts and their evaluation/email-sending logic live in new modules and a new
standalone script; the periodic check runs via a scheduled GitHub Actions workflow
(the app has no long-running server process to host an in-process scheduler). Two
new Streamlit pages are added (`Alerts`, `Dashboard`); no existing page, service,
provider, or config default is modified except purely additive config getters.

## Technical Context

**Language/Version**: Python 3.11 (matches existing CI `setup-python` version; repo also runs fine under 3.13 locally)

**Primary Dependencies**: Streamlit, requests, python-dotenv, yfinance (all existing/unchanged). Email uses the Python standard library (`smtplib`, `email.message`) — no new third-party dependency required.

**Storage**: SQLite via the existing `storage/db.py` connection helper, extended with two new tables (`alerts`, `alert_events`) added through `CREATE TABLE IF NOT EXISTS` alongside the existing `watchlist` table — no migration of existing data, no schema changes to `watchlist`.

**Testing**: Extend the existing `scripts/smoke_test.py` convention (import + execute top-level page code, no pytest currently in the repo) to cover the two new pages and new service modules; add a dry-run mode to the alert-check script so it can be exercised in CI/local dev without sending real email.

**Target Platform**: Same as Phase 1 — Streamlit Community Cloud for the web app. New: a scheduled GitHub Actions workflow (cron) as the periodic-check runner, since Streamlit Cloud does not provide a background worker process.

**Project Type**: Single web application (unchanged) plus one new standalone CLI-style script invoked out-of-process by the scheduler.

**Performance Goals**: An alert-check run over a realistic single-user watchlist (tens of symbols, a handful of alerts each) must comfortably finish within the 15-minute default check interval; the Dashboard page must load with no perceptibly worse latency than the existing Watchlist page for the same symbol count.

**Constraints**: No new paid/external service account required to get started (SMTP creds only, following the same `.env`/`st.secrets` pattern as `FINNHUB_API_KEY`); must not alter existing Phase 1 files' observable behavior; all "periodic" logic must be runnable as a stateless one-shot script (no in-app background thread), because the Streamlit process may not be running when a check is due.

**Scale/Scope**: Single-user app (no accounts), realistically tens of watched symbols and a similar order of alerts — no need to design for multi-tenancy or high concurrency.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unfilled template for this project (no
principles have been ratified). There are no project-specific gates to evaluate
against, so this gate passes trivially. General good-practice defaults are applied
instead: additive schema changes only, no modification of existing modules' public
behavior, standard-library email over a new dependency, reuse of existing config
patterns.

**Status**: PASS (no constitution constraints defined)

## Project Structure

### Documentation (this feature)

```text
specs/001-notifications-dashboard/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md        # Phase 1 output
├── architecture.md       # Phase 1 output — mermaid architecture diagrams
├── contracts/            # Phase 1 output — internal service & script contracts
└── tasks.md              # Phase 2 output (/speckit-tasks — not created by /speckit-plan)
```

### Source Code (repository root)

```text
SmartStockTracker/
├── app.py                        # UNCHANGED (Phase 1 Search page)
├── config.py                     # ADDITIVE ONLY: new SMTP_* getters alongside existing ones
├── ui_common.py                  # UNCHANGED
├── cache_utils.py                # UNCHANGED
├── pages/
│   ├── 1_Watchlist.py            # UNCHANGED
│   ├── 2_Stock_Detail.py         # UNCHANGED
│   ├── 3_Alerts.py               # NEW — create/list/deactivate/reactivate/delete alerts
│   └── 4_Dashboard.py            # NEW — gainers/losers, summary stats, recent alerts feed
├── providers/                    # UNCHANGED (base.py, factory.py, finnhub_provider.py, yfinance_provider.py)
├── services/
│   ├── stock_service.py          # UNCHANGED
│   ├── watchlist_service.py      # UNCHANGED
│   ├── news_service.py           # UNCHANGED
│   ├── finnhub_client.py         # UNCHANGED
│   ├── alert_service.py          # NEW — Alert CRUD + condition evaluation
│   └── email_service.py          # NEW — SMTP send_email() wrapper
├── storage/
│   ├── db.py                     # ADDITIVE: new `alerts` / `alert_events` tables
│   ├── models.py                 # ADDITIVE: Alert, AlertEvent dataclasses
│   └── __init__.py                # UNCHANGED
├── scripts/
│   ├── smoke_test.py             # EXTENDED: cover new pages/modules
│   └── check_alerts.py           # NEW — one-shot script: evaluate all active alerts, send emails
└── .github/workflows/
    ├── ci.yml                    # UNCHANGED
    └── alert-check.yml           # NEW — scheduled workflow running scripts/check_alerts.py
```

**Structure Decision**: Keep the existing single-Streamlit-app layout exactly as is
and extend it additively: two new numbered pages (following the existing
`N_Name.py` convention), two new service modules (following the existing
`services/*_service.py` convention), a new standalone script (following the
existing `scripts/smoke_test.py` convention of a directly-runnable module), and
one new scheduled GitHub Actions workflow alongside the existing CI workflow. This
avoids touching any Phase 1 file's logic — `config.py`, `storage/db.py`, and
`storage/models.py` only gain new additive members.

## Complexity Tracking

*No constitution violations — table not needed.*
