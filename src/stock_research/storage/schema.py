from __future__ import annotations

CORE_SCHEMA = """
CREATE TABLE IF NOT EXISTS stocks (
    stock_code VARCHAR PRIMARY KEY,
    stock_name VARCHAR,
    exchange VARCHAR,
    list_date DATE,
    delist_date DATE,
    industry VARCHAR,
    industry_level VARCHAR,
    is_st BOOLEAN,
    is_active BOOLEAN,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trading_calendar (
    trade_date DATE PRIMARY KEY,
    is_open BOOLEAN,
    previous_trade_date DATE,
    next_trade_date DATE
);

CREATE TABLE IF NOT EXISTS daily_bars (
    trade_date DATE,
    stock_code VARCHAR,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    pre_close DOUBLE,
    volume DOUBLE,
    amount DOUBLE,
    turnover_rate DOUBLE,
    adj_factor DOUBLE,
    vwap DOUBLE,
    is_suspended BOOLEAN,
    limit_up_price DOUBLE,
    limit_down_price DOUBLE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (trade_date, stock_code)
);

CREATE TABLE IF NOT EXISTS index_bars (
    trade_date DATE,
    index_code VARCHAR,
    index_name VARCHAR,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    pre_close DOUBLE,
    volume DOUBLE,
    amount DOUBLE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (trade_date, index_code)
);

CREATE TABLE IF NOT EXISTS valuation_daily (
    trade_date DATE,
    stock_code VARCHAR,
    pe_ttm DOUBLE,
    pb DOUBLE,
    ps_ttm DOUBLE,
    dividend_yield DOUBLE,
    market_cap DOUBLE,
    float_market_cap DOUBLE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (trade_date, stock_code)
);

CREATE TABLE IF NOT EXISTS universe_members (
    trade_date DATE,
    universe_name VARCHAR,
    stock_code VARCHAR,
    is_member BOOLEAN,
    exclude_reason VARCHAR,
    avg_amount_20d DOUBLE,
    listed_days INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (trade_date, universe_name, stock_code)
);

CREATE TABLE IF NOT EXISTS factor_values (
    trade_date DATE,
    stock_code VARCHAR,
    factor_version VARCHAR,
    momentum_5d DOUBLE,
    momentum_10d DOUBLE,
    momentum_20d DOUBLE,
    momentum_60d DOUBLE,
    volatility_20d DOUBLE,
    volatility_60d DOUBLE,
    avg_amount_20d DOUBLE,
    turnover_20d DOUBLE,
    ma_20_ratio DOUBLE,
    ma_60_ratio DOUBLE,
    relative_strength_20d DOUBLE,
    pe_ttm DOUBLE,
    pb DOUBLE,
    market_cap DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (trade_date, stock_code, factor_version)
);

CREATE TABLE IF NOT EXISTS data_quality_checks (
    check_id VARCHAR PRIMARY KEY,
    check_date DATE,
    dataset_name VARCHAR,
    check_type VARCHAR,
    status VARCHAR,
    affected_rows INTEGER,
    message VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
