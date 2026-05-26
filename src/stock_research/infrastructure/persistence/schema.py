from __future__ import annotations

SCHEMA_VERSION = "2026_05_26_001_database_foundation"

CORE_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS schema_versions (
    version VARCHAR PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR
);

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

CREATE TABLE IF NOT EXISTS financial_reports (
    stock_code VARCHAR,
    report_period DATE,
    announce_date DATE,
    revenue DOUBLE,
    net_profit DOUBLE,
    roe DOUBLE,
    gross_margin DOUBLE,
    net_margin DOUBLE,
    debt_to_asset DOUBLE,
    operating_cash_flow DOUBLE,
    revenue_growth DOUBLE,
    profit_growth DOUBLE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (stock_code, report_period, announce_date)
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
    roe DOUBLE,
    revenue_growth DOUBLE,
    profit_growth DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (trade_date, stock_code, factor_version)
);

CREATE TABLE IF NOT EXISTS labels (
    trade_date DATE,
    stock_code VARCHAR,
    label_version VARCHAR,
    holding_days INTEGER,
    future_return DOUBLE,
    benchmark_return DOUBLE,
    future_excess_return DOUBLE,
    cross_section_rank INTEGER,
    cross_section_percentile DOUBLE,
    top_quantile BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (trade_date, stock_code, label_version)
);

CREATE TABLE IF NOT EXISTS model_runs (
    model_version VARCHAR PRIMARY KEY,
    model_name VARCHAR,
    algorithm VARCHAR,
    factor_version VARCHAR,
    label_version VARCHAR,
    train_start_date DATE,
    train_end_date DATE,
    valid_start_date DATE,
    valid_end_date DATE,
    test_start_date DATE,
    test_end_date DATE,
    params_json VARCHAR,
    metrics_json VARCHAR,
    model_path VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_predictions (
    predict_date DATE,
    stock_code VARCHAR,
    model_version VARCHAR,
    score DOUBLE,
    expected_return DOUBLE,
    rank INTEGER,
    percentile DOUBLE,
    signal VARCHAR,
    top_factors_json VARCHAR,
    risk_flags_json VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (predict_date, stock_code, model_version)
);

CREATE TABLE IF NOT EXISTS selection_results (
    selection_date DATE,
    strategy_version VARCHAR,
    model_version VARCHAR,
    stock_code VARCHAR,
    stock_name VARCHAR,
    industry VARCHAR,
    score DOUBLE,
    rank INTEGER,
    selection_tier VARCHAR,
    suggested_action VARCHAR,
    suggested_weight DOUBLE,
    buy_condition VARCHAR,
    stop_loss_rule VARCHAR,
    take_profit_rule VARCHAR,
    risk_flags_json VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (selection_date, strategy_version, stock_code)
);

CREATE TABLE IF NOT EXISTS portfolios (
    portfolio_id VARCHAR PRIMARY KEY,
    portfolio_name VARCHAR,
    benchmark_code VARCHAR,
    base_currency VARCHAR DEFAULT 'CNY',
    risk_mode VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS portfolio_positions (
    portfolio_id VARCHAR,
    as_of_date DATE,
    stock_code VARCHAR,
    quantity DOUBLE,
    avg_cost DOUBLE,
    market_price DOUBLE,
    market_value DOUBLE,
    weight DOUBLE,
    unrealized_pnl DOUBLE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (portfolio_id, as_of_date, stock_code)
);

CREATE TABLE IF NOT EXISTS portfolio_targets (
    portfolio_id VARCHAR,
    target_date DATE,
    strategy_version VARCHAR,
    model_version VARCHAR,
    stock_code VARCHAR,
    target_weight DOUBLE,
    current_weight DOUBLE,
    weight_diff DOUBLE,
    suggested_action VARCHAR,
    rebalance_reason VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (portfolio_id, target_date, strategy_version, stock_code)
);

CREATE TABLE IF NOT EXISTS trade_plans (
    plan_id VARCHAR PRIMARY KEY,
    portfolio_id VARCHAR,
    create_date DATE,
    stock_code VARCHAR,
    action VARCHAR,
    reason VARCHAR,
    model_version VARCHAR,
    strategy_version VARCHAR,
    score DOUBLE,
    target_weight DOUBLE,
    current_weight DOUBLE,
    reference_price DOUBLE,
    max_buy_price DOUBLE,
    stop_loss_price DOUBLE,
    take_profit_rule VARCHAR,
    holding_period INTEGER,
    invalid_condition VARCHAR,
    discipline_result VARCHAR,
    status VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trade_executions (
    execution_id VARCHAR PRIMARY KEY,
    plan_id VARCHAR,
    portfolio_id VARCHAR,
    trade_date DATE,
    stock_code VARCHAR,
    action VARCHAR,
    price DOUBLE,
    quantity DOUBLE,
    amount DOUBLE,
    fee DOUBLE,
    tax DOUBLE,
    slippage DOUBLE,
    actual_weight DOUBLE,
    is_follow_plan BOOLEAN,
    deviation_reason VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS holdings_snapshot (
    portfolio_id VARCHAR,
    snapshot_date DATE,
    stock_code VARCHAR,
    quantity DOUBLE,
    avg_cost DOUBLE,
    close_price DOUBLE,
    market_value DOUBLE,
    weight DOUBLE,
    return_since_buy DOUBLE,
    current_score DOUBLE,
    current_rank INTEGER,
    stop_loss_triggered BOOLEAN,
    take_profit_triggered BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (portfolio_id, snapshot_date, stock_code)
);

CREATE TABLE IF NOT EXISTS trade_reviews (
    review_id VARCHAR PRIMARY KEY,
    plan_id VARCHAR,
    portfolio_id VARCHAR,
    stock_code VARCHAR,
    review_date DATE,
    entry_date DATE,
    exit_date DATE,
    holding_days INTEGER,
    return_rate DOUBLE,
    benchmark_return DOUBLE,
    excess_return DOUBLE,
    win_or_loss VARCHAR,
    model_correct BOOLEAN,
    discipline_result VARCHAR,
    reason_analysis VARCHAR,
    lesson_learned VARCHAR,
    next_action VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS portfolio_reviews (
    review_id VARCHAR PRIMARY KEY,
    portfolio_id VARCHAR,
    review_start_date DATE,
    review_end_date DATE,
    review_type VARCHAR,
    portfolio_return DOUBLE,
    benchmark_return DOUBLE,
    excess_return DOUBLE,
    max_drawdown DOUBLE,
    win_rate DOUBLE,
    profit_loss_ratio DOUBLE,
    turnover_rate DOUBLE,
    top_contributors_json VARCHAR,
    top_detractors_json VARCHAR,
    industry_exposure_json VARCHAR,
    discipline_summary_json VARCHAR,
    conclusion VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_reviews (
    review_id VARCHAR PRIMARY KEY,
    model_version VARCHAR,
    strategy_version VARCHAR,
    review_start_date DATE,
    review_end_date DATE,
    top_10_return DOUBLE,
    top_20_return DOUBLE,
    top_50_return DOUBLE,
    top_20_win_rate DOUBLE,
    rank_ic DOUBLE,
    rank_ic_ir DOUBLE,
    layered_returns_json VARCHAR,
    industry_performance_json VARCHAR,
    conclusion VARCHAR,
    retrain_required BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS strategy_configs (
    strategy_version VARCHAR PRIMARY KEY,
    strategy_name VARCHAR,
    config_json VARCHAR,
    is_active BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

CREATE TABLE IF NOT EXISTS data_source_runs (
    run_id VARCHAR PRIMARY KEY,
    source_name VARCHAR,
    dataset_name VARCHAR,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    status VARCHAR,
    rows_loaded INTEGER,
    message VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_daily_bars_stock_date ON daily_bars(stock_code, trade_date);
CREATE INDEX IF NOT EXISTS idx_factor_values_stock_date ON factor_values(stock_code, trade_date);
CREATE INDEX IF NOT EXISTS idx_universe_members_date_member ON universe_members(trade_date, is_member);
CREATE INDEX IF NOT EXISTS idx_model_predictions_date_rank ON model_predictions(predict_date, rank);
CREATE INDEX IF NOT EXISTS idx_trade_plans_status ON trade_plans(status, create_date);

INSERT OR IGNORE INTO schema_versions(version, description)
VALUES ('{SCHEMA_VERSION}', 'Initial full database foundation for A-share quant research system');
"""

CORE_TABLES = [
    "schema_versions",
    "stocks",
    "trading_calendar",
    "daily_bars",
    "index_bars",
    "valuation_daily",
    "financial_reports",
    "universe_members",
    "factor_values",
    "labels",
    "model_runs",
    "model_predictions",
    "selection_results",
    "portfolios",
    "portfolio_positions",
    "portfolio_targets",
    "trade_plans",
    "trade_executions",
    "holdings_snapshot",
    "trade_reviews",
    "portfolio_reviews",
    "model_reviews",
    "strategy_configs",
    "data_quality_checks",
    "data_source_runs",
]
