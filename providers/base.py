from abc import ABC, abstractmethod

from storage.models import NewsItem, Quote


class StockDataProvider(ABC):
    """Common interface so the app can switch price/news data sources freely."""

    name = "base"

    @abstractmethod
    def search_symbol(self, query: str) -> list:
        """Return a list of {'symbol': str, 'description': str} dicts."""

    @abstractmethod
    def get_quote(self, symbol: str) -> Quote:
        """Return the current Quote for a symbol, or raise if unavailable."""

    @abstractmethod
    def get_company_news(self, symbol: str, days_back: int = 7, limit: int = 5) -> list:
        """Return the latest NewsItem list for a symbol, newest first."""
