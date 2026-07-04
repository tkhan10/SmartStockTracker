from providers.factory import get_provider


def search_stocks(query: str, provider_name: str = None):
    return get_provider(provider_name).search_symbol(query)


def get_quote(symbol: str, provider_name: str = None):
    return get_provider(provider_name).get_quote(symbol)
