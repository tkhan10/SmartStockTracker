import streamlit as st

from config import STOCK_DATA_PROVIDER

PROVIDER_LABELS = {"finnhub": "Finnhub", "yfinance": "Yahoo Finance"}
LABEL_TO_KEY = {v: k for k, v in PROVIDER_LABELS.items()}


def render_provider_selector() -> str:
    """Sidebar dropdown to switch the active data provider; persists via session_state."""
    if "provider" not in st.session_state:
        st.session_state["provider"] = STOCK_DATA_PROVIDER

    labels = list(PROVIDER_LABELS.values())
    current_label = PROVIDER_LABELS.get(st.session_state["provider"], labels[0])
    selected_label = st.sidebar.selectbox("Data Provider", labels, index=labels.index(current_label))
    st.session_state["provider"] = LABEL_TO_KEY[selected_label]
    return st.session_state["provider"]
