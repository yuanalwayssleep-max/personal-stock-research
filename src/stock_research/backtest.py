from __future__ import annotations

import pandas as pd


def sma_cross_backtest(df: pd.DataFrame, fast: int = 20, slow: int = 60) -> tuple[pd.DataFrame, dict[str, float]]:
    """Simple long-only SMA cross backtest for research, not investment advice."""
    out = df.copy()
    out["FastSMA"] = out["Close"].rolling(fast).mean()
    out["SlowSMA"] = out["Close"].rolling(slow).mean()
    out["Signal"] = (out["FastSMA"] > out["SlowSMA"]).astype(int)
    out["Position"] = out["Signal"].shift(1).fillna(0)
    out["MarketReturn"] = out["Close"].pct_change().fillna(0)
    out["StrategyReturn"] = out["Position"] * out["MarketReturn"]
    out["Equity"] = (1 + out["StrategyReturn"]).cumprod()
    out["BuyHold"] = (1 + out["MarketReturn"]).cumprod()

    total_return = out["Equity"].iloc[-1] - 1
    buy_hold_return = out["BuyHold"].iloc[-1] - 1
    daily = out["StrategyReturn"]
    sharpe = 0.0 if daily.std() == 0 else (daily.mean() / daily.std()) * (252 ** 0.5)
    drawdown = out["Equity"] / out["Equity"].cummax() - 1

    metrics = {
        "strategy_return": float(total_return),
        "buy_hold_return": float(buy_hold_return),
        "sharpe": float(sharpe),
        "max_drawdown": float(drawdown.min()),
    }
    return out, metrics
