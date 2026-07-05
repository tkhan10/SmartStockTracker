import streamlit as st

from services import alert_service, watchlist_service
from ui_common import render_provider_selector

st.set_page_config(page_title="Alerts - SmartStockTracker", page_icon="🔔", layout="wide")
st.title("🔔 Price Alerts")

render_provider_selector()

watched = watchlist_service.list_symbols()
watched_symbols = [item["symbol"] for item in watched]

st.subheader("Create Alert")

if not watched_symbols:
    st.info("Your watchlist is empty. Add a symbol from the Search page before creating an alert.")
else:
    condition_labels = {
        "above": "Price goes above",
        "below": "Price goes below",
        "pct_change": "Percent change reaches",
    }

    with st.form("create_alert_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        symbol = col1.selectbox("Symbol", watched_symbols)
        condition_type = col2.selectbox(
            "Condition", list(condition_labels), format_func=lambda k: condition_labels[k]
        )
        col3, col4 = st.columns(2)
        threshold = col3.number_input("Threshold", min_value=0.0, step=0.5)
        email = col4.text_input("Notify email")
        submitted = st.form_submit_button("Create Alert")

    if submitted:
        try:
            alert_service.create_alert(symbol, condition_type, threshold, email)
            st.success(f"Alert created for {symbol}.")
            st.rerun()
        except ValueError as e:
            st.error(str(e))

st.subheader("Your Alerts")

alerts = alert_service.list_alerts()

if not alerts:
    st.info("No alerts yet.")
else:
    condition_labels = {
        "above": "price above",
        "below": "price below",
        "pct_change": "percent change ≥",
    }
    for alert in alerts:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
            col1.subheader(alert["symbol"])
            if alert["symbol"] not in watched_symbols:
                col1.caption("⚠️ no longer in watchlist")
            col2.write(f"{condition_labels[alert['condition_type']]} {alert['threshold']}")
            col2.caption(f"Notify: {alert['email']}")
            status = alert["status"]
            status_icon = {"active": "🟢", "fired": "✅", "inactive": "⏸️"}.get(status, "")
            col3.write(f"{status_icon} {status}")

            if status == "active":
                if col4.button("Disable", key=f"disable_{alert['id']}"):
                    alert_service.set_alert_status(alert["id"], "inactive")
                    st.rerun()
            elif status in ("fired", "inactive"):
                if col4.button("Re-arm", key=f"rearm_{alert['id']}"):
                    alert_service.set_alert_status(alert["id"], "active")
                    st.rerun()

            if col4.button("🗑️ Delete", key=f"delete_{alert['id']}"):
                alert_service.delete_alert(alert["id"])
                st.rerun()
