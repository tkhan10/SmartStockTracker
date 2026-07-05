---

description: "Task list for Notifications & Dashboard (Phase 2)"
---

# Tasks: Notifications & Dashboard (Phase 2)

**Input**: Design documents from `/specs/001-notifications-dashboard/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not requested in the spec — no dedicated test-first tasks. The existing
`scripts/smoke_test.py` convention is extended instead (Polish phase), consistent
with how Phase 1 verifies itself.

**Organization**: Tasks are grouped by user story (spec.md) so each story is
independently implementable and testable. US1 and US2 are both P1 (together they
form the MVP: create an alert, get notified); US3 (Dashboard) is P2.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no unmet dependencies)
- **[Story]**: US1 / US2 / US3 per spec.md
- All paths are relative to the repository root

---

## Phase 1: Setup

**Purpose**: Additive configuration so later phases have SMTP settings to read

- [X] T001 Add `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `ALERT_FROM_EMAIL` getters to `config.py` using the existing `_get_config()` helper, alongside (not replacing) `FINNHUB_API_KEY`/`STOCK_DATA_PROVIDER`
- [X] T002 [P] Add `SMTP_*`/`ALERT_FROM_EMAIL` placeholder entries to `.env.example` and `.streamlit/secrets.toml.example`

**Checkpoint**: New config values are readable via `config.py`; nothing else depends on this yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared schema and building blocks every user story needs

**⚠️ CRITICAL**: No user story task can start until this phase is complete

- [X] T003 Add `alerts` and `alert_events` tables (per `data-model.md`) to the `SCHEMA` string in `storage/db.py` via `CREATE TABLE IF NOT EXISTS`, leaving the existing `watchlist` table untouched
- [X] T004 [P] Add `Alert` and `AlertEvent` dataclasses to `storage/models.py`, matching the fields in `data-model.md`
- [X] T005 [P] Create `services/email_service.py` with `send_email(to_address, subject, body)` per `contracts/email_service.md`, using stdlib `smtplib`/`email.message.EmailMessage` and the new `config.py` SMTP getters; raises on failure (caller's job to catch)

**Checkpoint**: DB schema, models, and email transport exist — user story phases can now begin.

---

## Phase 3: User Story 1 - Create a price alert on a watched stock (Priority: P1) 🎯 MVP part 1

**Goal**: A user can create, view, disable/re-enable, and delete a price alert on a watchlist symbol.

**Independent Test**: Add a symbol to the watchlist, create an alert with a threshold, confirm it appears in the alert list with the right condition — verifiable without any email ever being sent.

- [X] T006 [US1] Implement `create_alert()`, `list_alerts()`, `set_alert_status()`, `delete_alert()` in `services/alert_service.py` per `contracts/alert_service.md`, including validation (positive numeric threshold, well-formed email, valid condition_type) and exact-duplicate rejection (depends on T003, T004)
- [X] T007 [US1] Build `pages/3_Alerts.py`: a form to create an alert (symbol selectbox sourced from `watchlist_service.list_symbols()`, condition type radio/select, threshold number input, email text input) calling `alert_service.create_alert()` (depends on T006)
- [X] T008 [US1] In `pages/3_Alerts.py`, render the alert list (symbol, condition, threshold, email, status) with buttons to deactivate, re-arm/re-enable, and delete, calling `alert_service.set_alert_status()` / `delete_alert()` (depends on T006, T007)
- [X] T009 [US1] In `pages/3_Alerts.py`, surface inline validation errors from `create_alert()` (invalid threshold/email/duplicate) without saving, and visually flag any alert whose `symbol` is no longer in the watchlist (depends on T008)

**Checkpoint**: User Story 1 is fully functional and testable independently of US2/US3.

---

## Phase 4: User Story 2 - Receive an email when an alert condition is met (Priority: P1) 🎯 MVP part 2

**Goal**: Active alerts get evaluated on a schedule; met conditions send exactly one email and get marked fired.

**Independent Test**: Create an alert whose condition is already true, run the check script directly, confirm one email sends and the alert flips to `fired`; running it again sends no duplicate.

- [X] T010 [US2] Implement `check_alerts(provider=None)` in `services/alert_service.py`: for each `active` alert, fetch a quote via `providers.factory.get_provider()` (or the injected `provider`), evaluate `above`/`below`/`pct_change`, call `email_service.send_email()` on a met condition, write an `AlertEvent` row (success or failure per FR-009), and flip status to `fired` only on a confirmed send — never raises for a single symbol/provider/email failure (depends on T005, T006)
- [X] T011 [US2] Implement `recent_events(days=7)` in `services/alert_service.py`, returning `alert_events` rows from the last N days, newest first (depends on T010)
- [X] T012 [US2] Create `scripts/check_alerts.py`: calls `storage.db.init_db()` then `alert_service.check_alerts()`, prints a one-line summary, exits non-zero only on an unexpected top-level crash; supports a `--dry-run` flag that evaluates and prints without sending email or mutating status (depends on T010)
- [X] T013 [US2] Create `.github/workflows/alert-check.yml`: a `schedule` (cron, every 15 minutes) + `workflow_dispatch` workflow mirroring `.github/workflows/ci.yml`'s setup steps, running `python scripts/check_alerts.py` with `SMTP_*`/`ALERT_FROM_EMAIL` from repository secrets (depends on T012)

**Checkpoint**: User Stories 1 AND 2 together deliver the full notifications MVP, independent of the Dashboard.

---

## Phase 5: User Story 3 - View portfolio-wide health on a Dashboard (Priority: P2)

**Goal**: A new Dashboard page shows gainers/losers, summary stats, and a recent-alerts feed for the whole watchlist.

**Independent Test**: Populate the watchlist with a few symbols, open the Dashboard, confirm the gainers/losers and stats match what the existing Watchlist page shows for the same symbols.

- [X] T014 [US3] Build `pages/4_Dashboard.py`: load `watchlist_service.list_symbols()`, fetch a quote per symbol via `providers.factory.get_provider()`, render a gainers/losers grouping and summary stats (symbol count, aggregate/average change) (depends on Foundational phase only)
- [X] T015 [US3] In `pages/4_Dashboard.py`, add a "Recent Alerts" section calling `alert_service.recent_events()` (depends on T011, T014)
- [X] T016 [US3] In `pages/4_Dashboard.py`, handle an empty watchlist (friendly empty state) and per-symbol provider failures (mark that symbol unavailable, still render the rest) (depends on T014)

**Checkpoint**: All three user stories are independently functional; Phase 2 feature set is complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the "no Phase 1 regressions" requirement and close out documentation

- [X] T017 [P] Extend `scripts/smoke_test.py` to import `services/alert_service.py` and `services/email_service.py`, and to execute the top-level code of `pages/3_Alerts.py` and `pages/4_Dashboard.py`, alongside the existing Phase 1 modules/pages (depends on T009, T016)
- [X] T018 [P] Update `README.md` with a "Notifications & Dashboard" section (SMTP env vars, the new pages, how the scheduled check works) without altering the existing Phase 1 sections (depends on T013)
- [X] T019 Run through `quickstart.md` end-to-end manually (create alert → trigger check → confirm email + fired status → view Dashboard → confirm Phase 1 pages unchanged) (depends on T009, T013, T016, T017)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational only
- **US2 (Phase 4)**: Depends on Foundational; reuses `alert_service.py` from US1 (T006) but its own tasks (T010-T013) are additive functions in the same file, not a rewrite
- **US3 (Phase 5)**: Depends on Foundational; T015 additionally depends on US2's `recent_events()` (T011) — everything else in US3 is independent of US1/US2
- **Polish (Phase 6)**: Depends on all three stories being complete

### Parallel Opportunities

- T002 can run alongside T001
- T004 and T005 can run in parallel (different files) once T003 lands
- Once Foundational is done: US1 (T006-T009) and US3's page-building (T014, T016) can proceed in parallel, since US3 doesn't need alert CRUD — only T015 (recent alerts feed) needs US2's `recent_events()`
- T017 and T018 in Polish can run in parallel

---

## Parallel Example: Foundational phase

```bash
Task: "Add Alert and AlertEvent dataclasses to storage/models.py"
Task: "Create services/email_service.py with send_email()"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational)
2. Complete Phase 3 (US1) — alerts can be created and managed
3. Complete Phase 4 (US2) — alerts actually notify by email
4. **STOP and VALIDATE**: run `quickstart.md`'s alert-creation and trigger steps
5. This is a demonstrable MVP even without the Dashboard

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US1 → alert management works end-to-end (no emails yet) → demo
3. US2 → emails actually fire → demo (full notifications MVP)
4. US3 → Dashboard adds the at-a-glance view → demo
5. Polish → confirm zero Phase 1 regressions, docs updated

---

## Notes

- No task modifies `app.py`, `pages/1_Watchlist.py`, `pages/2_Stock_Detail.py`, `providers/*`, `services/stock_service.py`, `services/watchlist_service.py`, `services/news_service.py`, or `services/finnhub_client.py` — this is what makes FR-012 (no Phase 1 regressions) structurally true rather than something to verify by diffing shared files.
- Commit after each task or logical group.
- Stop at either MVP checkpoint (after Phase 4) or the full checkpoint (after Phase 5) to validate before continuing.
