from __future__ import annotations

from pathlib import Path
from typing import Iterable

import duckdb
import pandas as pd

from stock_research.infrastructure.persistence.db import connect
from stock_research.infrastructure.persistence.schema import CORE_TABLES
from stock_research.shared.paths import DEFAULT_DB_PATH


def _replace_table_rows(
    con: duckdb.DuckDBPyConnection,
    table: str,
    df: pd.DataFrame,
    key_columns: Iterable[str],
) -> int:
    if df.empty:
        return 0
    _assert_known_table(con, table)
    columns = [row[1] for row in con.execute(f"PRAGMA table_info('{table}')").fetchall()]
    df = df.reindex(columns=columns)
    keys = list(key_columns)
    tmp_name = f"tmp_{table}"
    con.register(tmp_name, df)
    where = " AND ".join([f"{table}.{col} = {tmp_name}.{col}" for col in keys])
    con.execute(f"DELETE FROM {table} USING {tmp_name} WHERE {where}")
    con.execute(f"INSERT INTO {table} SELECT * FROM {tmp_name}")
    con.unregister(tmp_name)
    return len(df)


def _assert_known_table(con: duckdb.DuckDBPyConnection, table: str) -> None:
    exists = con.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'main' AND table_name = ?
        """,
        [table],
    ).fetchone()[0]
    if not exists:
        raise ValueError(f"Unknown table: {table}")


class ResearchRepository:
    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)

    def write_table(self, table: str, df: pd.DataFrame, key_columns: Iterable[str]) -> int:
        with connect(self.db_path) as con:
            return _replace_table_rows(con, table, df, key_columns)

    def write_stocks(self, df: pd.DataFrame) -> int:
        return self.write_table("stocks", df, ["stock_code"])

    def write_daily_bars(self, df: pd.DataFrame) -> int:
        return self.write_table("daily_bars", df, ["trade_date", "stock_code"])

    def write_index_bars(self, df: pd.DataFrame) -> int:
        return self.write_table("index_bars", df, ["trade_date", "index_code"])

    def write_valuation_daily(self, df: pd.DataFrame) -> int:
        return self.write_table("valuation_daily", df, ["trade_date", "stock_code"])

    def write_universe_members(self, df: pd.DataFrame) -> int:
        return self.write_table("universe_members", df, ["trade_date", "universe_name", "stock_code"])

    def write_factor_values(self, df: pd.DataFrame) -> int:
        return self.write_table("factor_values", df, ["trade_date", "stock_code", "factor_version"])

    def read_table(self, table: str, limit: int | None = None) -> pd.DataFrame:
        with connect(self.db_path) as con:
            _assert_known_table(con, table)
            sql = f"SELECT * FROM {table}"
            if limit is not None:
                sql += " LIMIT ?"
                return con.execute(sql, [limit]).fetchdf()
            return con.execute(sql).fetchdf()

    def query(self, sql: str, params: list | None = None) -> pd.DataFrame:
        with connect(self.db_path) as con:
            return con.execute(sql, params or []).fetchdf()

    def list_tables(self) -> list[str]:
        with connect(self.db_path) as con:
            rows = con.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'main'
                ORDER BY table_name
                """
            ).fetchall()
        return [row[0] for row in rows]

    def table_counts(self, tables: Iterable[str] | None = None) -> dict[str, int]:
        selected = list(tables or CORE_TABLES)
        counts: dict[str, int] = {}
        with connect(self.db_path) as con:
            for table in selected:
                _assert_known_table(con, table)
                counts[table] = int(con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        return counts

    def latest_schema_version(self) -> str | None:
        with connect(self.db_path) as con:
            row = con.execute("SELECT version FROM schema_versions ORDER BY applied_at DESC LIMIT 1").fetchone()
        return row[0] if row else None
