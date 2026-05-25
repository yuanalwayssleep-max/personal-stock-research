from __future__ import annotations

import pandas as pd


def build_basic_factors(
    daily_bars: pd.DataFrame,
    valuation: pd.DataFrame | None = None,
    index_bars: pd.DataFrame | None = None,
    benchmark_code: str | None = None,
    factor_version: str = "factor_v0_1",
) -> pd.DataFrame:
    """Compute MVP-1 daily cross-sectional factors from OHLCV data."""
    bars = daily_bars.copy()
    bars["trade_date"] = pd.to_datetime(bars["trade_date"], errors="coerce")
    bars = bars.sort_values(["stock_code", "trade_date"]).reset_index(drop=True)
    group = bars.groupby("stock_code", group_keys=False)

    close = group["close"]
    factors = bars[["trade_date", "stock_code"]].copy()
    factors["factor_version"] = factor_version
    factors["momentum_5d"] = close.pct_change(5)
    factors["momentum_10d"] = close.pct_change(10)
    factors["momentum_20d"] = close.pct_change(20)
    factors["momentum_60d"] = close.pct_change(60)

    returns = group["close"].pct_change()
    factors["volatility_20d"] = returns.groupby(bars["stock_code"]).rolling(20, min_periods=10).std().reset_index(level=0, drop=True)
    factors["volatility_60d"] = returns.groupby(bars["stock_code"]).rolling(60, min_periods=20).std().reset_index(level=0, drop=True)
    factors["avg_amount_20d"] = group["amount"].rolling(20, min_periods=5).mean().reset_index(level=0, drop=True)
    factors["turnover_20d"] = group["turnover_rate"].rolling(20, min_periods=5).mean().reset_index(level=0, drop=True)

    ma20 = group["close"].rolling(20, min_periods=10).mean().reset_index(level=0, drop=True)
    ma60 = group["close"].rolling(60, min_periods=20).mean().reset_index(level=0, drop=True)
    factors["ma_20_ratio"] = bars["close"] / ma20 - 1
    factors["ma_60_ratio"] = bars["close"] / ma60 - 1
    factors["relative_strength_20d"] = _relative_strength_20d(bars, index_bars, benchmark_code)

    if valuation is not None and not valuation.empty:
        val = valuation.copy()
        val["trade_date"] = pd.to_datetime(val["trade_date"], errors="coerce")
        keep = [col for col in ["trade_date", "stock_code", "pe_ttm", "pb", "market_cap"] if col in val]
        factors = factors.merge(val[keep], on=["trade_date", "stock_code"], how="left")
    else:
        factors["pe_ttm"] = pd.NA
        factors["pb"] = pd.NA
        factors["market_cap"] = pd.NA

    factors["created_at"] = pd.Timestamp.now()
    factors["trade_date"] = factors["trade_date"].dt.date
    return factors


def _relative_strength_20d(
    bars: pd.DataFrame,
    index_bars: pd.DataFrame | None,
    benchmark_code: str | None,
) -> pd.Series:
    stock_momentum = bars.groupby("stock_code")["close"].pct_change(20)
    if index_bars is None or index_bars.empty:
        return pd.Series(pd.NA, index=bars.index)

    idx = index_bars.copy()
    idx["trade_date"] = pd.to_datetime(idx["trade_date"], errors="coerce")
    if benchmark_code and "index_code" in idx:
        idx = idx[idx["index_code"] == benchmark_code]
    idx = idx.sort_values("trade_date")
    idx["benchmark_momentum_20d"] = idx["close"].pct_change(20)
    merged = bars[["trade_date"]].merge(idx[["trade_date", "benchmark_momentum_20d"]], on="trade_date", how="left")
    return stock_momentum.reset_index(drop=True) - merged["benchmark_momentum_20d"]
