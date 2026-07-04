from datetime import date, timedelta

from providers.base import StockDataProvider
from services import finnhub_client
from storage.models import NewsItem, Quote


class FinnhubProvider(StockDataProvider):
    name = "finnhub"

    def search_symbol(self, query: str):
        results = finnhub_client.search_symbol(query)
        return [
            {"symbol": r.get("symbol"), "description": r.get("description")}
            for r in results
            if r.get("type") == "Common Stock"
        ]

    def get_quote(self, symbol: str) -> Quote:
        data = finnhub_client.get_quote(symbol)
        if not data or data.get("c") in (None, 0):
            raise ValueError(f"No quote data available for {symbol}")
        return Quote(
            symbol=symbol,
            current=data.get("c", 0.0),
            change=data.get("d", 0.0),
            percent_change=data.get("dp", 0.0),
            high=data.get("h", 0.0),
            low=data.get("l", 0.0),
            open=data.get("o", 0.0),
            previous_close=data.get("pc", 0.0),
        )

    def get_company_news(self, symbol: str, days_back: int = 7, limit: int = 5):
        to_date = date.today()
        from_date = to_date - timedelta(days=days_back)
        raw = finnhub_client.get_company_news(symbol, from_date.isoformat(), to_date.isoformat())

        items = [
            NewsItem(
                headline=item.get("headline", ""),
                source=item.get("source", ""),
                url=item.get("url", ""),
                datetime=item.get("datetime", 0),
                summary=item.get("summary", ""),
            )
            for item in raw
            if item.get("headline")
        ]
        items.sort(key=lambda i: i.datetime, reverse=True)
        return items[:limit]
