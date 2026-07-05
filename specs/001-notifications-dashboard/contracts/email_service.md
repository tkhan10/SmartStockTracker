# Contract: `services/email_service.py`

```python
def send_email(to_address: str, subject: str, body: str) -> None:
    """Send a plain-text email via SMTP using SMTP_HOST/SMTP_PORT/SMTP_USERNAME/
    SMTP_PASSWORD/ALERT_FROM_EMAIL from config.py (same env-var/st.secrets
    pattern as FINNHUB_API_KEY). Raises on failure — callers (alert_service)
    are responsible for catching, logging, and recording the failure in an
    AlertEvent rather than crashing the check run."""
```

## Contract: `scripts/check_alerts.py` (CLI, run by the scheduler)

- **Invocation**: `python scripts/check_alerts.py` (no arguments).
- **Preconditions**: `DB_PATH` points at the same SQLite file the Streamlit app
  uses; SMTP env vars are set (in CI: repository secrets; locally: `.env`).
- **Behavior**: calls `storage.db.init_db()` then `services.alert_service.check_alerts()`,
  prints a one-line summary (`N alerts evaluated, M fired, K send failures`),
  and exits non-zero only on an unexpected top-level crash (never for an
  individual alert/provider/email failure, which are handled inside
  `check_alerts()` per FR-009).
- **Dry-run mode**: `python scripts/check_alerts.py --dry-run` evaluates
  conditions and prints what *would* fire without calling `send_email` or
  mutating alert status — used by the extended smoke test and for local
  verification without sending real mail.
