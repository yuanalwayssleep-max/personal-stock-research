from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from stock_research.domain.services import build_basic_factors, build_universe
from stock_research.infrastructure.persistence import ResearchRepository


@dataclass(frozen=True)
class Mvp1BuildResult:
    universe_rows: int
    universe_members: int
    factor_rows: int


def build_mvp1(
    db_path: str | Path,
    trade_date: str,
    factor_version: str = "factor_v0_1",
    min_listed_days: int = 120,
    min_avg_amount_20d: float = 50_000_000,
) -> Mvp1BuildResult:
    repo = ResearchRepository(db_path)
    stocks = repo.read_table("stocks")
    bars = repo.read_table("daily_bars")
    valuation = repo.read_table("valuation_daily")

    universe = build_universe(
        stocks,
        bars,
        trade_date,
        min_listed_days=min_listed_days,
        min_avg_amount_20d=min_avg_amount_20d,
    )
    universe_rows = repo.write_universe_members(universe)

    factors = build_basic_factors(bars, valuation=valuation, factor_version=factor_version)
    factor_rows = repo.write_factor_values(factors)
    members = int(universe["is_member"].sum()) if not universe.empty else 0
    return Mvp1BuildResult(universe_rows=universe_rows, universe_members=members, factor_rows=factor_rows)
