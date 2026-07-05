import streamlit as st

from services import alert_service, stock_service, watchlist_service
from ui_common import render_provider_selector

st.set_page_config(page_title="Dashboard - SmartStockTracker", page_icon="📈", layout="wide")
st.title("📈 Dashboard")

provider = render_provider_selector()

items = watchlist_service.list_symbols()

if not items:
    st.info("Your watchlist is empty. Go to the Search page to add stocks.")
else:
    quotes = {}
    unavailable = []
    for item in items:
        symbol = item["symbol"]
        try:
            quotes[symbol] = stock_service.get_quote(symbol, provider_name=provider)
        except Exception:
            unavailable.append(symbol)

    st.subheader("Summary")
    changes = [q.percent_change for q in quotes.values()]
    c1, c2, c3 = st.columns(3)
    c1.metric("Symbols Watched", len(items))
    c2.metric("Avg % Change", f"{(sum(changes) / len(changes)):+.2f}%" if changes else "N/A")
    c3.metric("Unavailable", len(unavailable))

    st.subheader("Gainers & Losers")
    ranked = sorted(quotes.items(), key=lambda kv: kv[1].percent_change, reverse=True)
    col_gainers, col_losers = st.columns(2)

    col_gainers.markdown("**📈 Gainers**")
    gainers = [(s, q) for s, q in ranked if q.percent_change >= 0]
    if not gainers:
        col_gainers.caption("None")
    for symbol, quote in gainers:
        col_gainers.markdown(f"**{symbol}** — ${quote.current:.2f} :green[+{quote.percent_change:.2f}%]")

    col_losers.markdown("**📉 Losers**")
    losers = [(s, q) for s, q in ranked if q.percent_change < 0]
    if not losers:
        col_losers.caption("None")
    for symbol, quote in losers:
        col_losers.markdown(f"**{symbol}** — ${quote.current:.2f} :red[{quote.percent_change:.2f}%]")

    if unavailable:
        st.warning(f"Price unavailable for: {', '.join(unavailable)}")

st.subheader("Recent Alerts")
events = alert_service.recent_events(days=7)
if not events:
    st.info("No alerts have fired in the last 7 days.")
else:
    for event in events:
        icon = "✅" if event["email_sent"] else "⚠️"
        with st.container(border=True):
            st.write(
                f"{icon} **{event['symbol']}** — {event['condition_type']} {event['threshold']} "
                f"(value: {event['triggered_price']})"
            )
            st.caption(event["triggered_at"] if event["email_sent"] else f"{event['triggered_at']} — send failed: {event['error']}")
