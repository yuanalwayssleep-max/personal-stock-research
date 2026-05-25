from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stock_research.data_sources import load_daily_bars_csv, load_stocks_csv, load_valuation_csv
from stock_research.storage import ResearchRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Import A-share MVP-1 CSV data into DuckDB.")
    parser.add_argument("--db", default="data/processed/research.duckdb")
    parser.add_argument("--stocks")
    parser.add_argument("--daily-bars")
    parser.add_argument("--valuation")
    args = parser.parse_args()

    repo = ResearchRepository(args.db)
    if args.stocks:
        count = repo.write_stocks(load_stocks_csv(args.stocks))
        print(f"Imported stocks: {count}")
    if args.daily_bars:
        count = repo.write_daily_bars(load_daily_bars_csv(args.daily_bars))
        print(f"Imported daily bars: {count}")
    if args.valuation:
        count = repo.write_valuation_daily(load_valuation_csv(args.valuation))
        print(f"Imported valuation rows: {count}")


if __name__ == "__main__":
    main()
