import requests

from cache_utils import TTLCache
from config import FINNHUB_API_KEY

BASE_URL = "https://finnhub.io/api/v1"


class FinnhubError(Exception):
    pass


_cache = TTLCache()


def _get(path, params, ttl=0):
    cache_key = (path, tuple(sorted(params.items())))
    if ttl:
        cached = _cache.get(cache_key, ttl)
        if cached is not None:
            return cached

    if not FINNHUB_API_KEY:
        raise FinnhubError("FINNHUB_API_KEY is not set. Add it to your .env file.")

    resp = requests.get(
        f"{BASE_URL}{path}", params={**params, "token": FINNHUB_API_KEY}, timeout=10
    )
    if resp.status_code == 429:
        raise FinnhubError("Finnhub rate limit hit. Please wait a moment and try again.")
    if not resp.ok:
        raise FinnhubError(f"Finnhub API error {resp.status_code}: {resp.text}")

    data = resp.json()
    if ttl:
        _cache.set(cache_key, data)
    return data


def search_symbol(query: str):
    if not query.strip():
        return []
    data = _get("/search", {"q": query}, ttl=60)
    return data.get("result", [])


def get_quote(symbol: str):
    return _get("/quote", {"symbol": symbol}, ttl=30)


def get_company_news(symbol: str, from_date: str, to_date: str):
    return _get(
        "/company-news",
        {"symbol": symbol, "from": from_date, "to": to_date},
        ttl=300,
    )
