from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from stock_research.data_sources.csv_source import load_daily_bars_csv, load_stocks_csv
from stock_research.factors import build_basic_factors
from stock_research.storage import ResearchRepository, init_db
from stock_research.universe import build_universe


def test_csv_bool_parsing_and_code_normalization(tmp_path):
    stocks_path = tmp_path / "stocks.csv"
    stocks_path.write_text(
        "stock_code,stock_name,list_date,is_st,is_active\n"
        "1,平安银行,1991-04-03,false,true\n"
        "600519,贵州茅台,2001-08-27,0,1\n",
        encoding="utf-8",
    )
    daily_path = tmp_path / "daily.csv"
    daily_path.write_text(
        "trade_date,stock_code,open,high,low,close,is_suspended\n"
        "2024-06-07,1,10,11,9,10.5,false\n",
        encoding="utf-8",
    )

    stocks = load_stocks_csv(stocks_path)
    bars = load_daily_bars_csv(daily_path)

    assert stocks.loc[0, "stock_code"] == "000001.SZ"
    assert stocks["is_st"].tolist() == [False, False]
    assert stocks["is_active"].tolist() == [True, True]
    assert bars.loc[0, "is_suspended"] == False


def test_repository_universe_and_factors_roundtrip(tmp_path):
    db_path = tmp_path / "research.duckdb"
    init_db(db_path)
    repo = ResearchRepository(db_path)

    stocks = pd.DataFrame(
        {
            "stock_code": ["000001.SZ", "600519.SH", "000002.SZ"],
            "stock_name": ["平安银行", "贵州茅台", "ST测试"],
            "exchange": ["SZ", "SH", "SZ"],
            "list_date": [date(1991, 4, 3), date(2001, 8, 27), date(1991, 1, 29)],
            "delist_date": [pd.NaT, pd.NaT, pd.NaT],
            "industry": ["银行", "食品饮料", "房地产"],
            "industry_level": ["一级", "一级", "一级"],
            "is_st": [False, False, True],
            "is_active": [True, True, True],
            "updated_at": [pd.Timestamp.now()] * 3,
        }
    )
    rows = []
    start = date(2024, 1, 1)
    for i in range(120):
        d = start + timedelta(days=i)
        if d.weekday() >= 5:
            continue
        for j, code in enumerate(stocks["stock_code"]):
            close = 10 + j * 20 + i * 0.05
            rows.append(
                {
                    "trade_date": d,
                    "stock_code": code,
                    "open": close * 0.99,
                    "high": close * 1.01,
                    "low": close * 0.98,
                    "close": close,
                    "pre_close": close * 0.995,
                    "volume": 1_000_000,
                    "amount": 80_000_000 + j * 20_000_000,
                    "turnover_rate": 1.0,
                    "adj_factor": 1.0,
                    "vwap": close,
                    "is_suspended": False,
                    "limit_up_price": close * 1.1,
                    "limit_down_price": close * 0.9,
                    "updated_at": pd.Timestamp.now(),
                }
            )
    bars = pd.DataFrame(rows)

    assert repo.write_stocks(stocks) == 3
    assert repo.write_daily_bars(bars) == len(bars)

    universe = build_universe(stocks, bars, "2024-04-29", min_listed_days=120, min_avg_amount_20d=50_000_000)
    assert int(universe["is_member"].sum()) == 2
    assert universe.loc[universe["stock_code"] == "000002.SZ", "exclude_reason"].item() == "st"

    factors = build_basic_factors(bars)
    latest = factors[factors["trade_date"] == date(2024, 4, 29)]
    assert len(latest) == 3
    assert latest["momentum_20d"].notna().all()
