from config import STOCK_DATA_PROVIDER
from providers.finnhub_provider import FinnhubProvider
from providers.yfinance_provider import YFinanceProvider

_PROVIDERS = {
    "finnhub": FinnhubProvider,
    "yfinance": YFinanceProvider,
}


def get_provider(name: str = None):
    name = (name or STOCK_DATA_PROVIDER).lower()
    provider_cls = _PROVIDERS.get(name)
    if provider_cls is None:
        raise ValueError(f"Unknown provider '{name}'. Options: {', '.join(_PROVIDERS)}")
    return provider_cls()
