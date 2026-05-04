"""SQLite-backed ledger store. Pure stdlib."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Iterator

from phoenix_core.paths import LEDGER_DB, ensure_dirs

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT    NOT NULL,            -- ISO date YYYY-MM-DD
    kind      TEXT    NOT NULL CHECK (kind IN ('income','expense')),
    amount    REAL    NOT NULL CHECK (amount >= 0),
    category  TEXT    NOT NULL,
    source    TEXT,                        -- e.g. 'gumroad sale', 'rent'
    pillar    TEXT,                        -- A..G or NULL
    note      TEXT
);
CREATE INDEX IF NOT EXISTS ix_tx_ts        ON transactions(ts);
CREATE INDEX IF NOT EXISTS ix_tx_category  ON transactions(category);

CREATE TABLE IF NOT EXISTS targets (
    key   TEXT PRIMARY KEY,
    value REAL NOT NULL
);
"""


@contextmanager
def connect(path: Path | None = None) -> Iterator[sqlite3.Connection]:
    ensure_dirs()
    conn = sqlite3.connect(path or LEDGER_DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(path: Path | None = None) -> None:
    with connect(path) as c:
        c.executescript(SCHEMA)


def add_tx(
    *,
    kind: str,
    amount: float,
    category: str,
    source: str | None = None,
    pillar: str | None = None,
    note: str | None = None,
    ts: str | None = None,
) -> int:
    if kind not in ("income", "expense"):
        raise ValueError("kind must be 'income' or 'expense'")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    ts = ts or date.today().isoformat()
    with connect() as c:
        cur = c.execute(
            "INSERT INTO transactions (ts, kind, amount, category, source, "
            "pillar, note) VALUES (?,?,?,?,?,?,?)",
            (ts, kind, amount, category, source, pillar, note),
        )
        return int(cur.lastrowid)


def set_target(key: str, value: float) -> None:
    with connect() as c:
        c.execute(
            "INSERT INTO targets(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


def get_target(key: str) -> float | None:
    with connect() as c:
        row = c.execute("SELECT value FROM targets WHERE key=?", (key,)).fetchone()
        return float(row["value"]) if row else None


def month_bounds(year: int, month: int) -> tuple[str, str]:
    start = date(year, month, 1)
    end = date(year + (month == 12), (month % 12) + 1, 1)
    return start.isoformat(), end.isoformat()


def report(year: int, month: int) -> dict:
    start, end = month_bounds(year, month)
    with connect() as c:
        rows = c.execute(
            "SELECT kind, category, SUM(amount) AS total "
            "FROM transactions WHERE ts >= ? AND ts < ? "
            "GROUP BY kind, category ORDER BY kind, total DESC",
            (start, end),
        ).fetchall()
        totals = c.execute(
            "SELECT kind, SUM(amount) AS total FROM transactions "
            "WHERE ts >= ? AND ts < ? GROUP BY kind",
            (start, end),
        ).fetchall()
    by_kind: dict[str, float] = {"income": 0.0, "expense": 0.0}
    for r in totals:
        by_kind[r["kind"]] = float(r["total"] or 0)
    return {
        "period": f"{year:04d}-{month:02d}",
        "income": by_kind["income"],
        "expense": by_kind["expense"],
        "net": by_kind["income"] - by_kind["expense"],
        "by_category": [dict(r) for r in rows],
    }


def runway_months() -> float | None:
    """Cash on hand / 3-month avg burn. Requires a 'cash_on_hand' target and
    at least one full prior month of expenses."""
    cash = get_target("cash_on_hand")
    if cash is None:
        return None
    today = date.today()
    months = []
    for i in range(1, 4):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        rep = report(y, m)
        if rep["expense"] > 0:
            months.append(rep["expense"])
    if not months:
        return None
    avg_burn = sum(months) / len(months)
    return cash / avg_burn if avg_burn > 0 else None
