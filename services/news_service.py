from providers.factory import get_provider


def get_latest_news(symbol: str, days_back: int = 7, limit: int = 5, provider_name: str = None):
    return get_provider(provider_name).get_company_news(symbol, days_back=days_back, limit=limit)
