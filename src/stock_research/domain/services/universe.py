from __future__ import annotations

import pandas as pd


def build_universe(
    stocks: pd.DataFrame,
    daily_bars: pd.DataFrame,
    trade_date: str | pd.Timestamp,
    universe_name: str = "all_a_share",
    min_listed_days: int = 120,
    min_avg_amount_20d: float = 50_000_000,
    exclude_st: bool = True,
    exclude_suspended: bool = True,
    exclude_limit_locked: bool = True,
) -> pd.DataFrame:
    """Build a point-in-time A-share tradable universe for one trade date."""
    date = pd.Timestamp(trade_date).date()
    stocks_df = stocks.copy()
    bars = daily_bars.copy()
    stocks_df["list_date"] = pd.to_datetime(stocks_df["list_date"], errors="coerce")
    bars["trade_date"] = pd.to_datetime(bars["trade_date"], errors="coerce")

    history = bars[bars["trade_date"].dt.date <= date].sort_values(["stock_code", "trade_date"])
    if history.empty:
        return pd.DataFrame(columns=["trade_date", "universe_name", "stock_code", "is_member", "exclude_reason", "avg_amount_20d", "listed_days", "created_at"])

    latest = history.groupby("stock_code", as_index=False).tail(1)
    avg_amount = history.groupby("stock_code")["amount"].rolling(20, min_periods=1).mean().reset_index(level=0, drop=True)
    history = history.assign(avg_amount_20d=avg_amount)
    latest_amount = history.groupby("stock_code", as_index=False).tail(1)[["stock_code", "avg_amount_20d"]]

    merged = stocks_df.merge(latest, on="stock_code", how="left", suffixes=("", "_bar"))
    merged = merged.merge(latest_amount, on="stock_code", how="left")
    merged["listed_days"] = (pd.Timestamp(date) - merged["list_date"]).dt.days

    reasons: list[str] = []
    for row in merged.itertuples(index=False):
        reason = ""
        if not _as_bool(getattr(row, "is_active", True), default=True):
            reason = "inactive"
        elif exclude_st and _as_bool(getattr(row, "is_st", False)):
            reason = "st"
        elif pd.isna(getattr(row, "close", None)):
            reason = "no_price"
        elif pd.isna(getattr(row, "list_date", None)) or getattr(row, "listed_days", 0) < min_listed_days:
            reason = "new_stock"
        elif exclude_suspended and _as_bool(getattr(row, "is_suspended", False)):
            reason = "suspended"
        elif pd.isna(getattr(row, "avg_amount_20d", None)) or getattr(row, "avg_amount_20d", 0) < min_avg_amount_20d:
            reason = "low_liquidity"
        elif exclude_limit_locked and _is_limit_locked(row):
            reason = "limit_locked"
        reasons.append(reason)

    out = pd.DataFrame(
        {
            "trade_date": date,
            "universe_name": universe_name,
            "stock_code": merged["stock_code"],
            "is_member": [not reason for reason in reasons],
            "exclude_reason": [reason or None for reason in reasons],
            "avg_amount_20d": merged["avg_amount_20d"],
            "listed_days": merged["listed_days"],
            "created_at": pd.Timestamp.now(),
        }
    )
    return out


def _as_bool(value: object, default: bool = False) -> bool:
    if pd.isna(value):
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "t", "yes", "y", "是", "st", "停牌"}
    return bool(value)


def _is_limit_locked(row: object) -> bool:
    close = getattr(row, "close", None)
    high = getattr(row, "high", None)
    low = getattr(row, "low", None)
    limit_up = getattr(row, "limit_up_price", None)
    limit_down = getattr(row, "limit_down_price", None)
    if pd.notna(limit_up) and pd.notna(close) and pd.notna(high) and close >= limit_up and high <= limit_up:
        return True
    if pd.notna(limit_down) and pd.notna(close) and pd.notna(low) and close <= limit_down and low >= limit_down:
        return True
    return False
