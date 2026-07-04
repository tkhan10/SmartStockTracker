from datetime import datetime, timezone

from storage.db import get_connection


def add_symbol(symbol: str, name: str = ""):
    symbol = symbol.upper().strip()
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO watchlist (symbol, name, added_at) VALUES (?, ?, ?)",
            (symbol, name, datetime.now(timezone.utc).isoformat()),
        )


def remove_symbol(symbol: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol.upper(),))


def list_symbols():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM watchlist ORDER BY added_at DESC").fetchall()
        return [dict(row) for row in rows]


def is_watched(symbol: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM watchlist WHERE symbol = ?", (symbol.upper(),)
        ).fetchone()
        return row is not None
