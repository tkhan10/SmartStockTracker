# Contract: `services/alert_service.py`

Internal service contract (this app has no external/public API — its
"contracts" are the function signatures other modules, pages, and the
scheduled script call).

```python
def create_alert(symbol: str, condition_type: str, threshold: float, email: str) -> dict:
    """Validate and insert a new alert (status='active').
    Raises ValueError on invalid threshold/email/condition_type or exact duplicate.
    Returns the created alert row as a dict."""

def list_alerts(symbol: str | None = None) -> list[dict]:
    """Return all alerts, optionally filtered to one symbol, newest first."""

def set_alert_status(alert_id: int, status: str) -> None:
    """Transition an alert to 'active' (re-arm/enable) or 'inactive' (disable).
    Raises ValueError for an unrecognized status."""

def delete_alert(alert_id: int) -> None:
    """Remove an alert. Does not delete its historical AlertEvent rows."""

def check_alerts(provider=None) -> list[dict]:
    """Evaluate every 'active' alert against the latest quote for its symbol
    (via providers.factory.get_provider() unless one is passed in for testing),
    send an email for each newly-met condition via services.email_service,
    record an AlertEvent for every attempt (sent or failed), and flip fired
    alerts' status to 'fired'. Never raises for a single symbol/provider/email
    failure — logs and continues (FR-009). Returns the list of AlertEvent dicts
    created during this run, for the caller (script or dashboard) to report on."""

def recent_events(days: int = 7) -> list[dict]:
    """Return AlertEvent rows from the last `days` days, newest first, for the
    Dashboard's recent-alerts feed."""
```
