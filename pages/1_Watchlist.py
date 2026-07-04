import streamlit as st

from services import stock_service, watchlist_service
from ui_common import render_provider_selector

st.set_page_config(page_title="Watchlist - SmartStockTracker", page_icon="⭐", layout="wide")
st.title("⭐ My Watchlist")

provider = render_provider_selector()

items = watchlist_service.list_symbols()

if not items:
    st.info("Your watchlist is empty. Go to the Search page to add stocks.")
else:
    for item in items:
        symbol = item["symbol"]
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 3, 3, 1])
            col1.subheader(symbol)
            col2.write(item["name"])
            try:
                quote = stock_service.get_quote(symbol, provider_name=provider)
                color = "green" if quote.change >= 0 else "red"
                arrow = "▲" if quote.change >= 0 else "▼"
                col3.markdown(
                    f"**${quote.current:.2f}** "
                    f"<span style='color:{color}'>{arrow} {quote.change:+.2f} "
                    f"({quote.percent_change:+.2f}%)</span>",
                    unsafe_allow_html=True,
                )
            except Exception:
                col3.error("Price unavailable")

            if col4.button("🗑️", key=f"remove_{symbol}"):
                watchlist_service.remove_symbol(symbol)
                st.rerun()
