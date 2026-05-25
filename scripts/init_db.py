from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stock_research.application.use_cases import init_database


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize the local DuckDB schema.")
    parser.add_argument("--db", default="data/processed/research.duckdb")
    args = parser.parse_args()
    path = init_database(args.db)
    print(f"Initialized database: {path}")


if __name__ == "__main__":
    main()
