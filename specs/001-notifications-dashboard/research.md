# Phase 0 Research: Notifications & Dashboard (Phase 2)

All `NEEDS CLARIFICATION` items from the Technical Context were resolved directly
from the existing codebase and the spec's documented assumptions — no items
required external research beyond inspecting Phase 1's own conventions.

## Decision: Periodic check via scheduled GitHub Actions workflow, not an in-app scheduler

- **Decision**: Implement the periodic alert check as a standalone script
  (`scripts/check_alerts.py`) triggered by a GitHub Actions `schedule` (cron)
  workflow, mirroring the existing `.github/workflows/ci.yml` pattern.
- **Rationale**: Streamlit Community Cloud runs the app as a request-driven
  process with no supported long-running background worker/thread that survives
  independent of a browser session. A scheduled external trigger is the only
  option that reliably fires even when nobody has the app open, which the spec
  (FR-013) requires.
- **Alternatives considered**:
  - *In-app background thread (e.g., `st.session_state` + a loop)*: rejected —
    only runs while at least one session is open, not reliable for "user isn't
    looking at the app right now."
  - *Third-party scheduler service (e.g., a hosted cron SaaS)*: rejected —
    adds an external account/dependency for no benefit over GitHub Actions,
    which the repo already uses for CI and needs no new account.
  - *APScheduler / Celery worker*: rejected — requires a persistent process or
    broker infra this single-user Streamlit-Cloud app doesn't have.

## Decision: Email via stdlib `smtplib`, config through existing `.env`/`st.secrets` pattern

- **Decision**: Send email with Python's built-in `smtplib` + `email.message.EmailMessage`
  against a user-supplied SMTP account (host/port/username/password/from-address),
  read through the same `_get_config()` helper in `config.py` already used for
  `FINNHUB_API_KEY`.
- **Rationale**: No new dependency, no new paid third-party transactional-email
  account required to try the feature; consistent with the project's existing
  "env var locally, `st.secrets` on Streamlit Cloud" configuration convention.
- **Alternatives considered**:
  - *Transactional email API (SendGrid/Mailgun/SES)*: rejected as the default —
    better deliverability at scale, but adds a new account/dependency for a
    single-user app; `email_service.py` is written behind a small interface so a
    provider could be swapped in later without touching callers.

## Decision: Additive-only schema changes in the existing SQLite DB

- **Decision**: Add `alerts` and `alert_events` tables via `CREATE TABLE IF NOT
  EXISTS` in `storage/db.py`'s existing `SCHEMA`/`init_db()`, next to the
  untouched `watchlist` table.
- **Rationale**: Matches Phase 1's existing single-file-SQLite approach; avoids
  introducing a migration framework for two new tables; `init_db()` is already
  idempotent and called on every app start, so no separate migration step is
  needed.
- **Alternatives considered**: A dedicated migrations tool (Alembic, etc.) —
  rejected as disproportionate for a two-table additive change in a project
  with no existing migration tooling.

## Decision: New pages instead of editing existing pages

- **Decision**: Alert creation/management and the Dashboard each get their own
  new page (`pages/3_Alerts.py`, `pages/4_Dashboard.py`) rather than being
  embedded into `pages/2_Stock_Detail.py` or `pages/1_Watchlist.py`.
- **Rationale**: Spec FR-012 requires zero change to existing page behavior;
  giving Phase 2 its own pages makes that guarantee mechanical (existing page
  files are literally untouched) rather than something to verify by careful
  diffing of shared files.
- **Alternatives considered**: Adding an "alerts" expander inside Stock Detail —
  rejected as a nice-to-have for later, not needed to satisfy the spec, and it
  would put Phase 1 and Phase 2 code in the same file.
