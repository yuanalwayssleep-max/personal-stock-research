from __future__ import annotations

import os
from pathlib import Path

from stock_research.shared import DEFAULT_DB_PATH


def get_db_path() -> Path:
    return Path(os.getenv("STOCK_RESEARCH_DB", str(DEFAULT_DB_PATH)))
