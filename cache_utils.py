import time


class TTLCache:
    """In-memory cache with per-entry time-to-live.

    Used to cut down repeat calls to free/unauthenticated APIs — Streamlit
    reruns the whole script on every widget interaction, so without this,
    a page with a watchlist re-fetches every symbol's quote/news on every click.
    """

    def __init__(self):
        self._store = {}

    def get(self, key, ttl):
        entry = self._store.get(key)
        if entry and (time.time() - entry[0]) < ttl:
            return entry[1]
        return None

    def set(self, key, value):
        self._store[key] = (time.time(), value)
