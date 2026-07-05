"""Standalone entrypoint for the scheduled alert check.

Run directly (`python scripts/check_alerts.py`) or via the
`.github/workflows/alert-check.yml` scheduled workflow, since Streamlit Cloud
has no long-running background worker to host this loop in-process.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _dry_run():
    from providers.factory import get_provider
    from services import alert_service
    from storage.db import get_connection

    with get_connection() as conn:
        active = [dict(row) for row in conn.execute("SELECT * FROM alerts WHERE status = 'active'").fetchall()]

    provider = get_provider()
    would_fire = 0
    for alert in active:
        try:
            quote = provider.get_quote(alert["symbol"])
        except Exception:
            continue
        if alert_service.condition_met(alert["condition_type"], alert["threshold"], quote):
            would_fire += 1
            print(f"WOULD FIRE: {alert['symbol']} {alert['condition_type']} {alert['threshold']}")

    print(f"{len(active)} active alerts evaluated, {would_fire} would fire (dry run, no email sent)")


def main():
    from storage.db import init_db

    init_db()

    if "--dry-run" in sys.argv:
        _dry_run()
        return

    from services import alert_service

    events = alert_service.check_alerts()
    fired = sum(1 for e in events if e.get("email_sent"))
    failed = sum(1 for e in events if not e.get("email_sent"))
    print(f"{len(events)} conditions met, {fired} fired, {failed} send failures")


if __name__ == "__main__":
    main()
