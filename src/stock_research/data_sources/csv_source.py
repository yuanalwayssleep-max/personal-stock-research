from __future__ import annotations

from pathlib import Path

import pandas as pd

COLUMN_ALIASES = {
    "stock_code": ["stock_code", "ts_code", "symbol", "code", "证券代码"],
    "stock_name": ["stock_name", "name", "证券简称", "股票名称"],
    "exchange": ["exchange", "交易所"],
    "list_date": ["list_date", "上市日期"],
    "delist_date": ["delist_date", "退市日期"],
    "industry": ["industry", "行业"],
    "trade_date": ["trade_date", "date", "日期"],
    "open": ["open", "Open", "开盘"],
    "high": ["high", "High", "最高"],
    "low": ["low", "Low", "最低"],
    "close": ["close", "Close", "收盘"],
    "pre_close": ["pre_close", "前收盘"],
    "volume": ["volume", "vol", "Volume", "成交量"],
    "amount": ["amount", "成交额"],
    "turnover_rate": ["turnover_rate", "换手率"],
    "adj_factor": ["adj_factor", "复权因子"],
    "is_suspended": ["is_suspended", "停牌"],
    "limit_up_price": ["limit_up_price", "涨停价"],
    "limit_down_price": ["limit_down_price", "跌停价"],
    "pe_ttm": ["pe_ttm", "PE_TTM", "市盈率TTM"],
    "pb": ["pb", "PB", "市净率"],
    "market_cap": ["market_cap", "总市值"],
}


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map: dict[str, str] = {}
    existing = set(df.columns)
    for standard, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in existing:
                rename_map[alias] = standard
                break
    return df.rename(columns=rename_map)


def _normalize_stock_code(value: str) -> str:
    code = str(value).strip().upper()
    if code.endswith((".SH", ".SZ", ".BJ")):
        return code
    if code.endswith((".SS", ".SHG")):
        return code.split(".")[0] + ".SH"
    if code.endswith(".SHE"):
        return code.split(".")[0] + ".SZ"
    digits = code.zfill(6) if code.isdigit() else code
    if digits.startswith(("6", "9")):
        return f"{digits}.SH"
    if digits.startswith(("0", "2", "3")):
        return f"{digits}.SZ"
    if digits.startswith(("4", "8")):
        return f"{digits}.BJ"
    return code


def _read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def _to_bool_series(value: object, index: pd.Index, default: bool = False) -> pd.Series:
    if isinstance(value, pd.Series):
        series = value
    else:
        series = pd.Series(default, index=index)
    if series.dtype == bool:
        return series.fillna(default)
    truthy = {"1", "true", "t", "yes", "y", "是", "停牌", "st"}
    falsy = {"0", "false", "f", "no", "n", "否", ""}

    def convert(item: object) -> bool:
        if pd.isna(item):
            return default
        if isinstance(item, (bool, int, float)):
            return bool(item)
        normalized = str(item).strip().lower()
        if normalized in truthy:
            return True
        if normalized in falsy:
            return False
        return default

    return series.map(convert)


def load_stocks_csv(path: str | Path) -> pd.DataFrame:
    df = _rename_columns(_read_csv(path))
    required = {"stock_code", "stock_name"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"stocks CSV missing required columns: {sorted(missing)}")

    out = pd.DataFrame()
    out["stock_code"] = df["stock_code"].map(_normalize_stock_code)
    out["stock_name"] = df["stock_name"].astype(str)
    out["exchange"] = df.get("exchange", out["stock_code"].str[-2:])
    out["list_date"] = pd.to_datetime(df.get("list_date"), errors="coerce").dt.date if "list_date" in df else pd.NaT
    out["delist_date"] = pd.to_datetime(df.get("delist_date"), errors="coerce").dt.date if "delist_date" in df else pd.NaT
    out["industry"] = df.get("industry", "")
    out["industry_level"] = df.get("industry_level", "")
    name_has_st = out["stock_name"].str.contains("ST", case=False, na=False)
    out["is_st"] = _to_bool_series(df.get("is_st", name_has_st), df.index)
    out["is_active"] = _to_bool_series(df.get("is_active", True), df.index, default=True)
    out["updated_at"] = pd.Timestamp.now()
    return out


def load_daily_bars_csv(path: str | Path) -> pd.DataFrame:
    df = _rename_columns(_read_csv(path))
    required = {"trade_date", "stock_code", "open", "high", "low", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"daily bars CSV missing required columns: {sorted(missing)}")

    out = pd.DataFrame()
    out["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce").dt.date
    out["stock_code"] = df["stock_code"].map(_normalize_stock_code)
    for col in ["open", "high", "low", "close", "pre_close", "volume", "amount", "turnover_rate", "adj_factor", "limit_up_price", "limit_down_price"]:
        out[col] = pd.to_numeric(df[col], errors="coerce") if col in df else None
    out["vwap"] = out["amount"] / out["volume"].replace(0, pd.NA) if "amount" in out and "volume" in out else None
    out["is_suspended"] = _to_bool_series(df.get("is_suspended", False), df.index)
    out["updated_at"] = pd.Timestamp.now()
    return out.dropna(subset=["trade_date", "stock_code"])


def load_valuation_csv(path: str | Path) -> pd.DataFrame:
    df = _rename_columns(_read_csv(path))
    required = {"trade_date", "stock_code"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"valuation CSV missing required columns: {sorted(missing)}")
    out = pd.DataFrame()
    out["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce").dt.date
    out["stock_code"] = df["stock_code"].map(_normalize_stock_code)
    for col in ["pe_ttm", "pb", "ps_ttm", "dividend_yield", "market_cap", "float_market_cap"]:
        out[col] = pd.to_numeric(df[col], errors="coerce") if col in df else None
    out["updated_at"] = pd.Timestamp.now()
    return out.dropna(subset=["trade_date", "stock_code"])
