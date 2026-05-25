from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_DIR = DATA_DIR / "raw"


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def fetch_prices(symbol: str, period: str = "2y", interval: str = "1d", refresh: bool = False) -> pd.DataFrame:
    """Fetch OHLCV data from Yahoo Finance and cache it locally as CSV."""
    symbol = normalize_symbol(symbol)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = RAW_DIR / f"{symbol}_{period}_{interval}.csv"

    if cache_file.exists() and not refresh:
        df = pd.read_csv(cache_file, parse_dates=["Date"])
        return df.set_index("Date")

    df = yf.download(symbol, period=period, interval=interval, auto_adjust=False, progress=False)
    if df.empty:
        raise ValueError(f"No price data returned for {symbol}")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    df.index.name = "Date"
    df.to_csv(cache_file)
    return df
