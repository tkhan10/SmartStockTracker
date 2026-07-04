import os

from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st

    _secrets = st.secrets
except Exception:
    _secrets = {}


def _get_config(key: str, default: str = "") -> str:
    """Reads env vars for local dev, falling back to Streamlit Cloud's st.secrets."""
    if key in os.environ:
        return os.environ[key]
    try:
        return _secrets[key]
    except Exception:
        return default


FINNHUB_API_KEY = _get_config("FINNHUB_API_KEY", "")
DB_PATH = os.getenv("DB_PATH", os.path.join("storage", "smartstock.db"))

# Which data provider to use by default: "finnhub" or "yfinance"
STOCK_DATA_PROVIDER = _get_config("STOCK_DATA_PROVIDER", "finnhub").lower()
