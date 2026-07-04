from datetime import datetime

import yfinance as yf

from cache_utils import TTLCache
from providers.base import StockDataProvider
from storage.models import NewsItem, Quote

_cache = TTLCache()


def _pick(info, *keys):
    """yfinance's fast_info uses different key casings across versions; try each."""
    for key in keys:
        try:
            value = info[key]
        except (KeyError, TypeError):
            value = getattr(info, key, None)
        if value not in (None, ""):
            return value
    return None


class YFinanceProvider(StockDataProvider):
    name = "yfinance"

    def search_symbol(self, query: str):
        if not query.strip():
            return []

        cache_key = ("search", query)
        cached = _cache.get(cache_key, ttl=60)
        if cached is not None:
            return cached

        quotes = getattr(yf.Search(query, max_results=10), "quotes", []) or []
        results = [
            {
                "symbol": q.get("symbol"),
                "description": q.get("longname") or q.get("shortname") or q.get("symbol"),
            }
            for q in quotes
            if q.get("quoteType") == "EQUITY"
        ]
        _cache.set(cache_key, results)
        return results

    def get_quote(self, symbol: str) -> Quote:
        cache_key = ("quote", symbol)
        cached = _cache.get(cache_key, ttl=30)
        if cached is not None:
            return cached

        info = yf.Ticker(symbol).fast_info
        current = _pick(info, "lastPrice", "last_price")
        previous_close = _pick(info, "previousClose", "previous_close")
        if current is None or previous_close is None:
            raise ValueError(f"No quote data available for {symbol}")

        change = current - previous_close
        percent_change = (change / previous_close * 100) if previous_close else 0.0
        quote = Quote(
            symbol=symbol,
            current=float(current),
            change=float(change),
            percent_change=float(percent_change),
            high=float(_pick(info, "dayHigh", "day_high") or 0.0),
            low=float(_pick(info, "dayLow", "day_low") or 0.0),
            open=float(_pick(info, "open") or 0.0),
            previous_close=float(previous_close),
        )
        _cache.set(cache_key, quote)
        return quote

    def get_company_news(self, symbol: str, days_back: int = 7, limit: int = 5):
        # yfinance's news endpoint has no date-range filter; it just returns the
        # most recent items, so days_back is ignored here.
        cache_key = ("news", symbol, limit)
        cached = _cache.get(cache_key, ttl=300)
        if cached is not None:
            return cached

        raw_items = yf.Ticker(symbol).news or []
        items = [self._to_news_item(raw) for raw in raw_items]
        items = [i for i in items if i.headline]
        items.sort(key=lambda i: i.datetime, reverse=True)
        items = items[:limit]
        _cache.set(cache_key, items)
        return items

    @staticmethod
    def _to_news_item(raw: dict) -> NewsItem:
        # yfinance has changed its news payload shape across releases (flat vs.
        # nested under "content"); handle both defensively.
        content = raw.get("content", raw)
        headline = content.get("title", "")
        summary = content.get("summary") or content.get("description") or ""

        provider = content.get("provider")
        source = provider.get("displayName", "") if isinstance(provider, dict) else raw.get("publisher", "")

        url = ""
        for url_field in ("canonicalUrl", "clickThroughUrl"):
            candidate = content.get(url_field)
            if isinstance(candidate, dict) and candidate.get("url"):
                url = candidate["url"]
                break
        if not url:
            url = raw.get("link", "")

        timestamp = raw.get("providerPublishTime", 0)
        pub_date = content.get("pubDate")
        if pub_date:
            try:
                timestamp = int(datetime.fromisoformat(pub_date.replace("Z", "+00:00")).timestamp())
            except ValueError:
                pass

        return NewsItem(headline=headline, source=source, url=url, datetime=timestamp, summary=summary)
