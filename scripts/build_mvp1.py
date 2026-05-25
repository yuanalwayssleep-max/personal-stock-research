from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stock_research.application.use_cases import build_mvp1


def main() -> None:
    parser = argparse.ArgumentParser(description="Build MVP-1 universe and basic factors.")
    parser.add_argument("--db", default="data/processed/research.duckdb")
    parser.add_argument("--trade-date", required=True)
    parser.add_argument("--factor-version", default="factor_v0_1")
    parser.add_argument("--min-listed-days", type=int, default=120)
    parser.add_argument("--min-avg-amount-20d", type=float, default=50_000_000)
    args = parser.parse_args()

    result = build_mvp1(
        args.db,
        trade_date=args.trade_date,
        factor_version=args.factor_version,
        min_listed_days=args.min_listed_days,
        min_avg_amount_20d=args.min_avg_amount_20d,
    )
    print(f"Wrote universe rows: {result.universe_rows}, members: {result.universe_members}")
    print(f"Wrote factor rows: {result.factor_rows}")


if __name__ == "__main__":
    main()
