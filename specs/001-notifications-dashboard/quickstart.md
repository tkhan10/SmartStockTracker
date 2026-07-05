# Quickstart: Validate Notifications & Dashboard (Phase 2)

## Prerequisites

- Phase 1 setup already done (`.env` with `STOCK_DATA_PROVIDER`, deps installed).
- SMTP account for sending alert emails, added to `.env`:
  ```
  SMTP_HOST=smtp.example.com
  SMTP_PORT=587
  SMTP_USERNAME=you@example.com
  SMTP_PASSWORD=app_password_here
  ALERT_FROM_EMAIL=you@example.com
  ```
  (An app-password from Gmail/Outlook etc. works well here — see `email_service.md`.)

## Setup

```bash
pip install -r requirements.txt   # unchanged; no new third-party deps
streamlit run app.py              # existing entrypoint, unchanged
```

## Validate: create and view an alert (User Story 1)

1. On the **Search** page, add a symbol (e.g. `AAPL`) to the watchlist — unchanged Phase 1 flow.
2. Open the new **Alerts** page.
3. Create an alert: symbol `AAPL`, condition "price above", threshold set below the
   current price (so it's already satisfied), destination email your own address.
4. Confirm the alert appears in the alert list with status `active`.
5. Try an invalid threshold (e.g. `-5`) or malformed email — confirm an inline
   error and that nothing is saved (spec Acceptance Scenario 3).

## Validate: trigger a notification (User Story 2)

```bash
python scripts/check_alerts.py --dry-run   # confirm it WOULD fire, no email sent
python scripts/check_alerts.py             # actually evaluates + sends
```

- Confirm the email arrives at the destination address.
- Confirm the alert's status is now `fired` on the Alerts page.
- Re-run `python scripts/check_alerts.py` — confirm no duplicate email is sent
  (fired alerts are not re-evaluated until re-armed).
- From the Alerts page, re-arm the alert and confirm status returns to `active`.

## Validate: Dashboard (User Story 3)

1. With a few symbols in the watchlist (mixed up/down), open the new **Dashboard** page.
2. Confirm gainers/losers grouping and summary stats match what the existing
   Watchlist page shows for the same symbols.
3. Confirm the fired alert from the previous step shows up in "Recent Alerts."
4. Remove all watchlist symbols and reload the Dashboard — confirm a friendly
   empty state, not an error.

## Validate: no Phase 1 regressions (SC-004)

Run the existing smoke test (extended, still covers Phase 1 pages unchanged):

```bash
python scripts/smoke_test.py
```

Manually re-confirm Search, Watchlist, and Stock Detail pages behave exactly as
before, and that switching data providers in the sidebar still works.

## Validate: scheduled runner (FR-013)

Push the new `.github/workflows/alert-check.yml` and confirm in the GitHub
Actions tab that it runs on its cron schedule (or trigger it manually via
`workflow_dispatch` for a fast check) and completes successfully using the
repo secrets for `SMTP_*`.
