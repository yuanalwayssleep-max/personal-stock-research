from __future__ import annotations

import pandas as pd


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    close = out["Close"]

    out["Return"] = close.pct_change()
    out["SMA20"] = close.rolling(20).mean()
    out["SMA60"] = close.rolling(60).mean()
    out["Volatility20"] = out["Return"].rolling(20).std() * (252 ** 0.5)

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, pd.NA)
    out["RSI14"] = 100 - (100 / (1 + rs))

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    out["MACD"] = ema12 - ema26
    out["MACDSignal"] = out["MACD"].ewm(span=9, adjust=False).mean()
    out["MACDHist"] = out["MACD"] - out["MACDSignal"]
    return out
