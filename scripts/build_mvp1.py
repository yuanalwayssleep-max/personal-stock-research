from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stock_research.factors import build_basic_factors
from stock_research.storage import ResearchRepository
from stock_research.universe import build_universe


def main() -> None:
    parser = argparse.ArgumentParser(description="Build MVP-1 universe and basic factors.")
    parser.add_argument("--db", default="data/processed/research.duckdb")
    parser.add_argument("--trade-date", required=True)
    parser.add_argument("--factor-version", default="factor_v0_1")
    parser.add_argument("--min-listed-days", type=int, default=120)
    parser.add_argument("--min-avg-amount-20d", type=float, default=50_000_000)
    args = parser.parse_args()

    repo = ResearchRepository(args.db)
    stocks = repo.read_table("stocks")
    bars = repo.read_table("daily_bars")
    valuation = repo.read_table("valuation_daily")

    universe = build_universe(
        stocks,
        bars,
        args.trade_date,
        min_listed_days=args.min_listed_days,
        min_avg_amount_20d=args.min_avg_amount_20d,
    )
    universe_count = repo.write_universe_members(universe)

    factors = build_basic_factors(bars, valuation=valuation, factor_version=args.factor_version)
    factor_count = repo.write_factor_values(factors)

    members = int(universe["is_member"].sum()) if not universe.empty else 0
    print(f"Wrote universe rows: {universe_count}, members: {members}")
    print(f"Wrote factor rows: {factor_count}")


if __name__ == "__main__":
    main()
