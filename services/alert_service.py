import re
from datetime import datetime, timedelta, timezone

from providers.factory import get_provider
from services.email_service import send_email
from storage.db import get_connection

CONDITION_TYPES = ("above", "below", "pct_change")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate(condition_type: str, threshold: float, email: str):
    if condition_type not in CONDITION_TYPES:
        raise ValueError(f"Unknown condition_type '{condition_type}'. Options: {', '.join(CONDITION_TYPES)}")
    try:
        threshold = float(threshold)
    except (TypeError, ValueError):
        raise ValueError("Threshold must be a number")
    if threshold <= 0:
        raise ValueError("Threshold must be greater than 0")
    if not email or not EMAIL_RE.match(email):
        raise ValueError("Enter a valid email address")
    return threshold


def create_alert(symbol: str, condition_type: str, threshold: float, email: str) -> dict:
    symbol = symbol.upper().strip()
    threshold = _validate(condition_type, threshold, email)

    with get_connection() as conn:
        existing = conn.execute(
            """SELECT 1 FROM alerts
               WHERE symbol = ? AND condition_type = ? AND threshold = ? AND email = ? AND status = 'active'""",
            (symbol, condition_type, threshold, email),
        ).fetchone()
        if existing:
            raise ValueError("An identical active alert already exists for this symbol")

        cursor = conn.execute(
            """INSERT INTO alerts (symbol, condition_type, threshold, email, status, created_at)
               VALUES (?, ?, ?, ?, 'active', ?)""",
            (symbol, condition_type, threshold, email, datetime.now(timezone.utc).isoformat()),
        )
        row = conn.execute("SELECT * FROM alerts WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


def list_alerts(symbol: str = None) -> list:
    with get_connection() as conn:
        if symbol:
            rows = conn.execute(
                "SELECT * FROM alerts WHERE symbol = ? ORDER BY created_at DESC", (symbol.upper(),)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM alerts ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]


def set_alert_status(alert_id: int, status: str) -> None:
    if status not in ("active", "inactive", "fired"):
        raise ValueError(f"Unknown status '{status}'")
    with get_connection() as conn:
        conn.execute("UPDATE alerts SET status = ? WHERE id = ?", (status, alert_id))


def delete_alert(alert_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))


def condition_met(condition_type: str, threshold: float, quote) -> bool:
    if condition_type == "above":
        return quote.current > threshold
    if condition_type == "below":
        return quote.current < threshold
    if condition_type == "pct_change":
        return abs(quote.percent_change) >= threshold
    return False


def _trigger_value(condition_type: str, quote) -> float:
    return quote.percent_change if condition_type == "pct_change" else quote.current


def _record_event(conn, alert: dict, triggered_price: float, email_sent: bool, error: str = None):
    conn.execute(
        """INSERT INTO alert_events
           (alert_id, symbol, condition_type, threshold, triggered_price, triggered_at, email_sent, error)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            alert["id"],
            alert["symbol"],
            alert["condition_type"],
            alert["threshold"],
            triggered_price,
            datetime.now(timezone.utc).isoformat(),
            1 if email_sent else 0,
            error,
        ),
    )


def check_alerts(provider=None) -> list:
    """Evaluate every active alert; email + record an AlertEvent for each met
    condition. Never raises for a single symbol/provider/email failure."""
    events = []
    active_provider = provider or get_provider()

    with get_connection() as conn:
        alerts = [dict(row) for row in conn.execute("SELECT * FROM alerts WHERE status = 'active'").fetchall()]

    for alert in alerts:
        try:
            quote = active_provider.get_quote(alert["symbol"])
        except Exception:
            continue  # provider unavailable for this symbol; retry next cycle

        if not condition_met(alert["condition_type"], alert["threshold"], quote):
            continue

        triggered_price = _trigger_value(alert["condition_type"], quote)
        subject = f"SmartStockTracker alert: {alert['symbol']}"
        body = (
            f"{alert['symbol']} met your alert condition ({alert['condition_type']} {alert['threshold']}).\n"
            f"Current value: {triggered_price}"
        )

        try:
            send_email(alert["email"], subject, body)
        except Exception as exc:
            with get_connection() as conn:
                _record_event(conn, alert, triggered_price, email_sent=False, error=str(exc))
            events.append({**alert, "email_sent": False, "error": str(exc)})
            continue

        with get_connection() as conn:
            _record_event(conn, alert, triggered_price, email_sent=True)
            conn.execute(
                "UPDATE alerts SET status = 'fired', last_fired_at = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), alert["id"]),
            )
        events.append({**alert, "status": "fired", "email_sent": True, "error": None})

    return events


def recent_events(days: int = 7) -> list:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM alert_events WHERE triggered_at >= ? ORDER BY triggered_at DESC", (cutoff,)
        ).fetchall()
        return [dict(row) for row in rows]
