import streamlit as st

from services import news_service, stock_service, watchlist_service
from ui_common import render_provider_selector

st.set_page_config(page_title="Stock Detail - SmartStockTracker", page_icon="📊", layout="wide")
st.title("📊 Stock Detail")

provider = render_provider_selector()

items = watchlist_service.list_symbols()
symbols = [item["symbol"] for item in items]

if not symbols:
    st.info("Add a stock to your watchlist first.")
else:
    selected = st.selectbox("Select a stock", symbols)

    if selected:
        try:
            quote = stock_service.get_quote(selected, provider_name=provider)
            color = "green" if quote.change >= 0 else "red"
            arrow = "▲" if quote.change >= 0 else "▼"
            st.markdown(
                f"## {selected}  \n"
                f"### ${quote.current:.2f} "
                f"<span style='color:{color}'>{arrow} {quote.change:+.2f} "
                f"({quote.percent_change:+.2f}%)</span>",
                unsafe_allow_html=True,
            )
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Open", f"${quote.open:.2f}")
            c2.metric("High", f"${quote.high:.2f}")
            c3.metric("Low", f"${quote.low:.2f}")
            c4.metric("Prev Close", f"${quote.previous_close:.2f}")
        except Exception as e:
            st.error(str(e))

        st.subheader("📰 Latest News")
        try:
            news = news_service.get_latest_news(selected, provider_name=provider)
            if not news:
                st.info("No recent news found.")
            for n in news:
                with st.container(border=True):
                    st.markdown(f"**[{n.headline}]({n.url})**")
                    st.caption(n.source)
                    if n.summary:
                        st.write(n.summary)
        except Exception as e:
            st.error(str(e))
