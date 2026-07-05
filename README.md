# SmartStockTracker

Phase 1: search stocks, maintain a watchlist, view live price and news.

Phase 2: price alerts with email notifications, and a Dashboard for an
at-a-glance view of the whole watchlist.

## Setup

1. (Optional) Get a free API key from https://finnhub.io/register — only needed if you
   want to use the Finnhub provider. `yfinance` needs no key at all.
2. Copy `.env.example` to `.env`:
   ```
   cp .env.example .env
   ```
   Paste your Finnhub key and set `STOCK_DATA_PROVIDER` to `finnhub` or `yfinance`.
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```

## Pages

- **Search** (`app.py`) — search for a stock by symbol/name and add it to your watchlist.
- **Watchlist** — see all tracked stocks with live price/change.
- **Stock Detail** — pick a watchlist stock to see full quote stats and latest news.
- **Alerts** — create price alerts (above/below a threshold, or percent-change) on
  watchlist symbols, and manage (disable/re-arm/delete) existing ones.
- **Dashboard** — gainers/losers, summary stats, and a recent-alerts feed for the
  whole watchlist.

## Switching data providers

Two providers are supported, both behind the same `StockDataProvider` interface
(`providers/base.py`):

- **Finnhub** (`providers/finnhub_provider.py`) — needs `FINNHUB_API_KEY`.
- **Yahoo Finance** (`providers/yfinance_provider.py`, via `yfinance`) — no key needed.

Switch which one is used in two ways:
- **Default**: set `STOCK_DATA_PROVIDER=finnhub` or `yfinance` in `.env`.
- **Live, per session**: use the "Data Provider" dropdown in the sidebar of any page —
  it overrides the default instantly without restarting the app.

To add another provider later, implement `StockDataProvider` in a new
`providers/<name>_provider.py` and register it in `providers/factory.py`.

## Notifications & Email Alerts

Create an alert on the **Alerts** page for any symbol in your watchlist:
price above/below a threshold, or a percent-change threshold. When the
condition is met, an email is sent to the address on the alert and it's
marked `fired` (re-arm it from the same page to be notified again).

Alerts are evaluated by a standalone script rather than inside the running
Streamlit app, since Streamlit has no background worker process:

1. Add SMTP settings to `.env` (see `.env.example`) — host, port, username,
   password (an app-password works well for Gmail/Outlook), and
   `ALERT_FROM_EMAIL`. No third-party email API account is required.
2. Run a check manually any time with:
   ```
   python scripts/check_alerts.py           # evaluates and sends real emails
   python scripts/check_alerts.py --dry-run # evaluates only, no email sent
   ```
3. In CI/production, `.github/workflows/alert-check.yml` runs this script on
   a 15-minute cron schedule (also triggerable manually via
   `workflow_dispatch`), using the same `SMTP_*`/`ALERT_FROM_EMAIL`/
   `STOCK_DATA_PROVIDER`/`FINNHUB_API_KEY` values configured as **repository
   secrets**.

> **Note**: the scheduled GitHub Actions workflow and the deployed Streamlit
> app must read the *same* database (`DB_PATH`) for alerts to actually be
> found and checked. A plain local SQLite file checked out fresh by each
> Actions run won't see alerts created in a separately-hosted Streamlit Cloud
> instance's own disk. For a real deployment, point `DB_PATH` (or swap in a
> hosted database) at storage reachable from both the app and the Action, or
> self-host both the app and the cron job on the same machine/volume.

## Deployment

Deployed on Streamlit Community Cloud, which auto-redeploys on every push to
`main` — no separate deploy pipeline is needed for that part.

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and
PR to `main` as a safety gate *before* that auto-deploy happens: it installs
dependencies, runs `scripts/smoke_test.py` (imports every module and executes
each page's top-level code to catch import/syntax/logic errors without a
browser), then boots the real Streamlit server and confirms it responds.
