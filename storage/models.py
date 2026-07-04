from dataclasses import dataclass


@dataclass
class Quote:
    symbol: str
    current: float
    change: float
    percent_change: float
    high: float
    low: float
    open: float
    previous_close: float


@dataclass
class NewsItem:
    headline: str
    source: str
    url: str
    datetime: int
    summary: str = ""
