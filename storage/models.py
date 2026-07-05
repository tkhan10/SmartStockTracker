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


@dataclass
class Alert:
    id: int
    symbol: str
    condition_type: str  # "above", "below", or "pct_change"
    threshold: float
    email: str
    status: str  # "active", "fired", or "inactive"
    created_at: str
    last_fired_at: str = None


@dataclass
class AlertEvent:
    id: int
    alert_id: int
    symbol: str
    condition_type: str
    threshold: float
    triggered_price: float
    triggered_at: str
    email_sent: bool
    error: str = None
