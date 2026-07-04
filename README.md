# SmartStockTracker

Phase 1: search stocks, maintain a watchlist, view live price and news.

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
