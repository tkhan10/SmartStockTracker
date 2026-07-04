import streamlit as st

from services import stock_service, watchlist_service
from storage.db import init_db
from ui_common import render_provider_selector

st.set_page_config(page_title="SmartStockTracker", page_icon="📈", layout="wide")
init_db()

st.title("📈 SmartStockTracker")
st.caption("Search for a stock and add it to your watchlist.")

provider = render_provider_selector()

query = st.text_input("Search stock (symbol or company name)", placeholder="e.g. AAPL, Tesla")

if query:
    try:
        results = stock_service.search_stocks(query, provider_name=provider)
    except Exception as e:
        st.error(str(e))
        results = []

    if not results:
        st.info("No matching stocks found.")
    else:
        for r in results[:10]:
            col1, col2, col3 = st.columns([2, 5, 2])
            col1.write(f"**{r['symbol']}**")
            col2.write(r["description"])
            if watchlist_service.is_watched(r["symbol"]):
                col3.button("✅ Added", key=f"added_{r['symbol']}", disabled=True)
            elif col3.button("+ Add", key=f"add_{r['symbol']}"):
                watchlist_service.add_symbol(r["symbol"], r["description"])
                st.rerun()
else:
    st.info("Start typing above to search for a stock.")
