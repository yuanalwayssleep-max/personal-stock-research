from __future__ import annotations

from pathlib import Path
from typing import Iterable

import duckdb
import pandas as pd

from stock_research.paths import DEFAULT_DB_PATH
from stock_research.storage.db import connect


def _replace_table_rows(
    con: duckdb.DuckDBPyConnection,
    table: str,
    df: pd.DataFrame,
    key_columns: Iterable[str],
) -> int:
    if df.empty:
        return 0
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


class ResearchRepository:
    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)

    def write_stocks(self, df: pd.DataFrame) -> int:
        with connect(self.db_path) as con:
            return _replace_table_rows(con, "stocks", df, ["stock_code"])

    def write_daily_bars(self, df: pd.DataFrame) -> int:
        with connect(self.db_path) as con:
            return _replace_table_rows(con, "daily_bars", df, ["trade_date", "stock_code"])

    def write_index_bars(self, df: pd.DataFrame) -> int:
        with connect(self.db_path) as con:
            return _replace_table_rows(con, "index_bars", df, ["trade_date", "index_code"])

    def write_valuation_daily(self, df: pd.DataFrame) -> int:
        with connect(self.db_path) as con:
            return _replace_table_rows(con, "valuation_daily", df, ["trade_date", "stock_code"])

    def write_universe_members(self, df: pd.DataFrame) -> int:
        with connect(self.db_path) as con:
            return _replace_table_rows(con, "universe_members", df, ["trade_date", "universe_name", "stock_code"])

    def write_factor_values(self, df: pd.DataFrame) -> int:
        with connect(self.db_path) as con:
            return _replace_table_rows(con, "factor_values", df, ["trade_date", "stock_code", "factor_version"])

    def read_table(self, table: str) -> pd.DataFrame:
        with connect(self.db_path) as con:
            return con.execute(f"SELECT * FROM {table}").fetchdf()

    def query(self, sql: str, params: list | None = None) -> pd.DataFrame:
        with connect(self.db_path) as con:
            return con.execute(sql, params or []).fetchdf()
