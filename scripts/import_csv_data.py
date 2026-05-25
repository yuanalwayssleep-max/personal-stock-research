from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stock_research.application.use_cases import import_csv_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Import A-share MVP-1 CSV data into DuckDB.")
    parser.add_argument("--db", default="data/processed/research.duckdb")
    parser.add_argument("--stocks")
    parser.add_argument("--daily-bars")
    parser.add_argument("--valuation")
    args = parser.parse_args()

    result = import_csv_data(
        args.db,
        stocks_path=args.stocks,
        daily_bars_path=args.daily_bars,
        valuation_path=args.valuation,
    )
    if args.stocks:
        print(f"Imported stocks: {result.stocks}")
    if args.daily_bars:
        print(f"Imported daily bars: {result.daily_bars}")
    if args.valuation:
        print(f"Imported valuation rows: {result.valuation}")


if __name__ == "__main__":
    main()
