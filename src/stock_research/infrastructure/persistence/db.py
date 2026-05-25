from __future__ import annotations

from pathlib import Path

import duckdb

from stock_research.shared.paths import DEFAULT_DB_PATH
from stock_research.infrastructure.persistence.schema import CORE_SCHEMA


def connect(db_path: str | Path = DEFAULT_DB_PATH) -> duckdb.DuckDBPyConnection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))
    con.execute(CORE_SCHEMA)
    return con


def init_db(db_path: str | Path = DEFAULT_DB_PATH) -> Path:
    with connect(db_path):
        pass
    return Path(db_path)
