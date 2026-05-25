from __future__ import annotations

from pathlib import Path

from stock_research.infrastructure.persistence import init_db


def init_database(db_path: str | Path) -> Path:
    return init_db(db_path)
