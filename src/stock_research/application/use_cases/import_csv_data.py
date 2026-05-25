from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from stock_research.infrastructure.data_sources import load_daily_bars_csv, load_stocks_csv, load_valuation_csv
from stock_research.infrastructure.persistence import ResearchRepository


@dataclass(frozen=True)
class CsvImportResult:
    stocks: int = 0
    daily_bars: int = 0
    valuation: int = 0


def import_csv_data(
    db_path: str | Path,
    stocks_path: str | Path | None = None,
    daily_bars_path: str | Path | None = None,
    valuation_path: str | Path | None = None,
) -> CsvImportResult:
    repo = ResearchRepository(db_path)
    stocks_count = repo.write_stocks(load_stocks_csv(stocks_path)) if stocks_path else 0
    daily_count = repo.write_daily_bars(load_daily_bars_csv(daily_bars_path)) if daily_bars_path else 0
    valuation_count = repo.write_valuation_daily(load_valuation_csv(valuation_path)) if valuation_path else 0
    return CsvImportResult(stocks=stocks_count, daily_bars=daily_count, valuation=valuation_count)
