from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "research.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS watchlist (
    symbol TEXT PRIMARY KEY,
    thesis TEXT,
    target_price DOUBLE,
    risk TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def connect() -> duckdb.DuckDBPyConnection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    con.execute(SCHEMA)
    return con


def upsert_watch(symbol: str, thesis: str = "", target_price: float | None = None, risk: str = "") -> None:
    with connect() as con:
        con.execute(
            """
            INSERT INTO watchlist VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(symbol) DO UPDATE SET
                thesis = excluded.thesis,
                target_price = excluded.target_price,
                risk = excluded.risk,
                updated_at = CURRENT_TIMESTAMP
            """,
            [symbol.upper(), thesis, target_price, risk],
        )


def add_note(symbol: str, note: str) -> None:
    with connect() as con:
        next_id = con.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM notes").fetchone()[0]
        con.execute("INSERT INTO notes VALUES (?, ?, ?, CURRENT_TIMESTAMP)", [next_id, symbol.upper(), note])


def get_watchlist() -> pd.DataFrame:
    with connect() as con:
        return con.execute("SELECT * FROM watchlist ORDER BY updated_at DESC").fetchdf()


def get_notes(symbol: str | None = None) -> pd.DataFrame:
    with connect() as con:
        if symbol:
            return con.execute("SELECT * FROM notes WHERE symbol = ? ORDER BY created_at DESC", [symbol.upper()]).fetchdf()
        return con.execute("SELECT * FROM notes ORDER BY created_at DESC").fetchdf()
