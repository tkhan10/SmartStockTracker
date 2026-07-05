# Architecture: Notifications & Dashboard (Phase 2)

Mermaid diagrams for this feature. Phase 1 components are shown unchanged;
Phase 2 additions are marked `NEW`.

## System architecture

```mermaid
flowchart TB
    subgraph Browser["User's Browser"]
        UI["Streamlit UI"]
    end

    subgraph App["SmartStockTracker (Streamlit app)"]
        Search["app.py — Search\n(Phase 1, unchanged)"]
        Watchlist["pages/1_Watchlist.py\n(Phase 1, unchanged)"]
        Detail["pages/2_Stock_Detail.py\n(Phase 1, unchanged)"]
        Alerts["pages/3_Alerts.py\nNEW"]
        Dashboard["pages/4_Dashboard.py\nNEW"]

        WatchlistSvc["services/watchlist_service.py\n(Phase 1, unchanged)"]
        StockSvc["services/stock_service.py\n(Phase 1, unchanged)"]
        NewsSvc["services/news_service.py\n(Phase 1, unchanged)"]
        AlertSvc["services/alert_service.py\nNEW"]
        EmailSvc["services/email_service.py\nNEW"]

        Factory["providers/factory.py\n(Phase 1, unchanged)"]
    end

    subgraph Data["Storage"]
        DB[("SQLite\nwatchlist (unchanged)\nalerts NEW\nalert_events NEW")]
    end

    subgraph External["External services"]
        Finnhub["Finnhub API"]
        YFinance["Yahoo Finance (yfinance)"]
        SMTP["SMTP account\n(user-supplied)"]
    end

    subgraph Scheduler["Scheduled runner — NEW"]
        GHA["GitHub Actions\nschedule (cron)"]
        Script["scripts/check_alerts.py\nNEW"]
    end

    UI --> Search & Watchlist & Detail & Alerts & Dashboard

    Search --> StockSvc
    Watchlist --> WatchlistSvc
    Detail --> StockSvc & NewsSvc
    Alerts --> AlertSvc
    Dashboard --> WatchlistSvc & AlertSvc

    WatchlistSvc --> DB
    AlertSvc --> DB
    AlertSvc --> EmailSvc
    StockSvc --> Factory
    AlertSvc --> Factory
    Factory --> Finnhub
    Factory --> YFinance
    EmailSvc --> SMTP

    GHA -->|"every 15 min (default)"| Script
    Script --> AlertSvc

    classDef new fill:#d6f5d6,stroke:#2e7d32,color:#1b1b1b;
    class Alerts,Dashboard,AlertSvc,EmailSvc,Script,GHA new;
```

## Alert lifecycle (state machine)

```mermaid
stateDiagram-v2
    [*] --> active: create_alert()
    active --> fired: condition met\n+ email sent (check_alerts)
    active --> inactive: user disables
    inactive --> active: user re-enables
    fired --> active: user re-arms
    active --> [*]: delete_alert()
    fired --> [*]: delete_alert()
    inactive --> [*]: delete_alert()
```

## Scheduled check sequence

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions (cron)
    participant Script as check_alerts.py
    participant AlertSvc as alert_service
    participant Provider as StockDataProvider
    participant DB as SQLite
    participant EmailSvc as email_service
    participant SMTP as SMTP server

    GHA->>Script: run on schedule
    Script->>AlertSvc: check_alerts()
    AlertSvc->>DB: list active alerts
    loop each active alert
        AlertSvc->>Provider: get_quote(symbol)
        alt provider fails
            AlertSvc->>DB: skip, log, keep alert active
        else condition met
            AlertSvc->>EmailSvc: send_email(...)
            alt send succeeds
                EmailSvc->>SMTP: deliver message
                AlertSvc->>DB: insert AlertEvent(email_sent=1), status=fired
            else send fails
                AlertSvc->>DB: insert AlertEvent(email_sent=0, error), status stays active
            end
        else condition not met
            AlertSvc->>AlertSvc: no-op
        end
    end
    Script-->>GHA: print summary, exit 0
```
