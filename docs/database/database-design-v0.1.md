# A 股个人量化投研系统数据库设计 v0.1

## 1. 设计目标

数据库设计服务于第一阶段 MVP，目标是支持：

- A 股股票池管理。
- 日线行情、指数、财务、估值数据存储。
- 因子、标签、模型预测和选股结果追溯。
- 组合目标、交易计划、交易执行和持仓跟踪。
- 单笔交易、组合和模型复盘。

推荐数据库：

```text
data/processed/research.duckdb
```

设计原则：

- 所有日期字段使用 `DATE`。
- 股票代码使用统一格式，建议 `000001.SZ`、`600519.SH`。
- 关键结果表保留版本字段，例如 `factor_version`、`model_version`、`strategy_version`。
- 训练特征、模型预测、交易计划和复盘结果应可追溯。
- 第一阶段以宽表和简单主键为主，优先便于分析和开发。

## 2. 表分层

```text
基础数据层：stocks, trading_calendar, daily_bars, index_bars, valuation_daily, financial_reports
特征模型层：universe_members, factor_values, labels, model_runs, model_predictions, selection_results
组合交易层：portfolios, portfolio_positions, portfolio_targets, trade_plans, trade_executions, holdings_snapshot
复盘报告层：trade_reviews, portfolio_reviews, model_reviews
配置元数据层：strategy_configs, data_quality_checks
```

## 3. 基础数据层

### 3.1 stocks：股票基础表

用途：存储 A 股股票基础信息。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| stock_code | VARCHAR | 股票代码，主键 |
| stock_name | VARCHAR | 股票名称 |
| exchange | VARCHAR | 交易所，SH/SZ/BJ |
| list_date | DATE | 上市日期 |
| delist_date | DATE | 退市日期，可空 |
| industry | VARCHAR | 行业名称 |
| industry_level | VARCHAR | 行业层级，可空 |
| is_st | BOOLEAN | 是否 ST |
| is_active | BOOLEAN | 是否仍在交易 |
| updated_at | TIMESTAMP | 更新时间 |

建议主键：`stock_code`。

### 3.2 trading_calendar：交易日历表

用途：管理 A 股交易日。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| trade_date | DATE | 交易日，主键 |
| is_open | BOOLEAN | 是否开市 |
| previous_trade_date | DATE | 上一个交易日 |
| next_trade_date | DATE | 下一个交易日 |

建议主键：`trade_date`。

### 3.3 daily_bars：股票日行情表

用途：存储股票日线行情。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| trade_date | DATE | 交易日 |
| stock_code | VARCHAR | 股票代码 |
| open | DOUBLE | 开盘价 |
| high | DOUBLE | 最高价 |
| low | DOUBLE | 最低价 |
| close | DOUBLE | 收盘价 |
| pre_close | DOUBLE | 前收盘价 |
| volume | DOUBLE | 成交量 |
| amount | DOUBLE | 成交额 |
| turnover_rate | DOUBLE | 换手率 |
| adj_factor | DOUBLE | 复权因子 |
| vwap | DOUBLE | 成交均价，可空 |
| is_suspended | BOOLEAN | 是否停牌 |
| limit_up_price | DOUBLE | 涨停价 |
| limit_down_price | DOUBLE | 跌停价 |
| updated_at | TIMESTAMP | 更新时间 |

建议主键：`trade_date, stock_code`。

### 3.4 index_bars：指数日行情表

用途：存储基准指数行情。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| trade_date | DATE | 交易日 |
| index_code | VARCHAR | 指数代码 |
| index_name | VARCHAR | 指数名称 |
| open | DOUBLE | 开盘点位 |
| high | DOUBLE | 最高点位 |
| low | DOUBLE | 最低点位 |
| close | DOUBLE | 收盘点位 |
| pre_close | DOUBLE | 前收盘点位 |
| volume | DOUBLE | 成交量 |
| amount | DOUBLE | 成交额 |
| updated_at | TIMESTAMP | 更新时间 |

建议主键：`trade_date, index_code`。

### 3.5 valuation_daily：每日估值表

用途：存储每日估值和市值数据。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| trade_date | DATE | 交易日 |
| stock_code | VARCHAR | 股票代码 |
| pe_ttm | DOUBLE | 滚动市盈率 |
| pb | DOUBLE | 市净率 |
| ps_ttm | DOUBLE | 滚动市销率 |
| dividend_yield | DOUBLE | 股息率 |
| market_cap | DOUBLE | 总市值 |
| float_market_cap | DOUBLE | 流通市值 |
| updated_at | TIMESTAMP | 更新时间 |

建议主键：`trade_date, stock_code`。

### 3.6 financial_reports：财务报告表

用途：存储财务指标，必须保留披露日期以避免未来函数。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| stock_code | VARCHAR | 股票代码 |
| report_period | DATE | 报告期 |
| announce_date | DATE | 披露日期 |
| revenue | DOUBLE | 营业收入 |
| net_profit | DOUBLE | 净利润 |
| roe | DOUBLE | ROE |
| gross_margin | DOUBLE | 毛利率 |
| net_margin | DOUBLE | 净利率 |
| debt_to_asset | DOUBLE | 资产负债率 |
| operating_cash_flow | DOUBLE | 经营现金流 |
| revenue_growth | DOUBLE | 营收增速 |
| profit_growth | DOUBLE | 利润增速 |
| updated_at | TIMESTAMP | 更新时间 |

建议主键：`stock_code, report_period, announce_date`。

## 4. 特征模型层

### 4.1 universe_members：股票池成员表

用途：记录指定交易日进入可交易股票池的股票及过滤原因。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| trade_date | DATE | 交易日 |
| universe_name | VARCHAR | 股票池名称 |
| stock_code | VARCHAR | 股票代码 |
| is_member | BOOLEAN | 是否入池 |
| exclude_reason | VARCHAR | 剔除原因，可空 |
| avg_amount_20d | DOUBLE | 20日平均成交额 |
| listed_days | INTEGER | 已上市交易日数 |
| created_at | TIMESTAMP | 创建时间 |

建议主键：`trade_date, universe_name, stock_code`。

### 4.2 factor_values：因子值表

用途：存储模型特征。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| trade_date | DATE | 交易日 |
| stock_code | VARCHAR | 股票代码 |
| factor_version | VARCHAR | 因子版本 |
| momentum_5d | DOUBLE | 5日动量 |
| momentum_10d | DOUBLE | 10日动量 |
| momentum_20d | DOUBLE | 20日动量 |
| momentum_60d | DOUBLE | 60日动量 |
| volatility_20d | DOUBLE | 20日波动率 |
| volatility_60d | DOUBLE | 60日波动率 |
| avg_amount_20d | DOUBLE | 20日平均成交额 |
| turnover_20d | DOUBLE | 20日平均换手率 |
| ma_20_ratio | DOUBLE | 收盘价 / 20日均线 - 1 |
| ma_60_ratio | DOUBLE | 收盘价 / 60日均线 - 1 |
| relative_strength_20d | DOUBLE | 相对基准20日强弱 |
| pe_ttm | DOUBLE | PE TTM |
| pb | DOUBLE | PB |
| market_cap | DOUBLE | 总市值 |
| roe | DOUBLE | ROE |
| revenue_growth | DOUBLE | 营收增速 |
| profit_growth | DOUBLE | 利润增速 |
| created_at | TIMESTAMP | 创建时间 |

建议主键：`trade_date, stock_code, factor_version`。

### 4.3 labels：训练标签表

用途：存储监督学习标签。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| trade_date | DATE | 特征日期 |
| stock_code | VARCHAR | 股票代码 |
| label_version | VARCHAR | 标签版本 |
| holding_days | INTEGER | 持有周期 |
| future_return | DOUBLE | 未来收益 |
| benchmark_return | DOUBLE | 同期基准收益 |
| future_excess_return | DOUBLE | 未来超额收益 |
| cross_section_rank | INTEGER | 横截面收益排名 |
| cross_section_percentile | DOUBLE | 横截面分位 |
| top_quantile | BOOLEAN | 是否进入收益前分位 |
| created_at | TIMESTAMP | 创建时间 |

建议主键：`trade_date, stock_code, label_version`。

### 4.4 model_runs：模型运行表

用途：记录模型训练元数据。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| model_version | VARCHAR | 模型版本，主键 |
| model_name | VARCHAR | 模型名称 |
| algorithm | VARCHAR | 算法类型 |
| factor_version | VARCHAR | 因子版本 |
| label_version | VARCHAR | 标签版本 |
| train_start_date | DATE | 训练开始日期 |
| train_end_date | DATE | 训练结束日期 |
| valid_start_date | DATE | 验证开始日期 |
| valid_end_date | DATE | 验证结束日期 |
| test_start_date | DATE | 测试开始日期 |
| test_end_date | DATE | 测试结束日期 |
| params_json | VARCHAR | 模型参数 JSON |
| metrics_json | VARCHAR | 评估指标 JSON |
| model_path | VARCHAR | 模型文件路径 |
| created_at | TIMESTAMP | 创建时间 |

建议主键：`model_version`。

### 4.5 model_predictions：模型预测表

用途：存储模型对指定交易日股票的预测结果。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| predict_date | DATE | 预测日期 |
| stock_code | VARCHAR | 股票代码 |
| model_version | VARCHAR | 模型版本 |
| score | DOUBLE | 模型分数 |
| expected_return | DOUBLE | 预期收益，可空 |
| rank | INTEGER | 横截面排名 |
| percentile | DOUBLE | 横截面分位 |
| signal | VARCHAR | 入选/观察/剔除 |
| top_factors_json | VARCHAR | 主要贡献因子 JSON |
| risk_flags_json | VARCHAR | 风险标签 JSON |
| created_at | TIMESTAMP | 创建时间 |

建议主键：`predict_date, stock_code, model_version`。

### 4.6 selection_results：选股结果表

用途：记录经过过滤和策略规则后的候选股票。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| selection_date | DATE | 选股日期 |
| strategy_version | VARCHAR | 策略版本 |
| model_version | VARCHAR | 模型版本 |
| stock_code | VARCHAR | 股票代码 |
| stock_name | VARCHAR | 股票名称 |
| industry | VARCHAR | 行业 |
| score | DOUBLE | 模型分数 |
| rank | INTEGER | 排名 |
| selection_tier | VARCHAR | 强推荐/观察/剔除/持有复评 |
| suggested_action | VARCHAR | 买入/观察/持有/卖出 |
| suggested_weight | DOUBLE | 建议仓位 |
| buy_condition | VARCHAR | 买入条件 |
| stop_loss_rule | VARCHAR | 止损规则 |
| take_profit_rule | VARCHAR | 止盈规则 |
| risk_flags_json | VARCHAR | 风险标签 JSON |
| created_at | TIMESTAMP | 创建时间 |

建议主键：`selection_date, strategy_version, stock_code`。

## 5. 组合交易层

### 5.1 portfolios：组合定义表

用途：定义不同组合。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| portfolio_id | VARCHAR | 组合 ID，主键 |
| portfolio_name | VARCHAR | 组合名称 |
| benchmark_code | VARCHAR | 基准指数 |
| base_currency | VARCHAR | 币种，默认 CNY |
| risk_mode | VARCHAR | 保守/平衡/进攻 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 5.2 portfolio_positions：当前持仓表

用途：记录当前实际持仓，可由交易执行汇总得到，也可手工维护。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| portfolio_id | VARCHAR | 组合 ID |
| as_of_date | DATE | 日期 |
| stock_code | VARCHAR | 股票代码 |
| quantity | DOUBLE | 持仓数量 |
| avg_cost | DOUBLE | 平均成本 |
| market_price | DOUBLE | 当前价格 |
| market_value | DOUBLE | 市值 |
| weight | DOUBLE | 当前仓位 |
| unrealized_pnl | DOUBLE | 浮动盈亏 |
| updated_at | TIMESTAMP | 更新时间 |

建议主键：`portfolio_id, as_of_date, stock_code`。

### 5.3 portfolio_targets：目标组合表

用途：记录系统生成的目标组合和目标仓位。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| portfolio_id | VARCHAR | 组合 ID |
| target_date | DATE | 目标日期 |
| strategy_version | VARCHAR | 策略版本 |
| model_version | VARCHAR | 模型版本 |
| stock_code | VARCHAR | 股票代码 |
| target_weight | DOUBLE | 目标仓位 |
| current_weight | DOUBLE | 当前仓位 |
| weight_diff | DOUBLE | 仓位差 |
| suggested_action | VARCHAR | 买入/加仓/持有/减仓/卖出 |
| rebalance_reason | VARCHAR | 调仓原因 |
| created_at | TIMESTAMP | 创建时间 |

建议主键：`portfolio_id, target_date, strategy_version, stock_code`。

### 5.4 trade_plans：交易计划表

用途：记录系统生成的可执行交易计划。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| plan_id | VARCHAR | 交易计划 ID，主键 |
| portfolio_id | VARCHAR | 组合 ID |
| create_date | DATE | 计划生成日期 |
| stock_code | VARCHAR | 股票代码 |
| action | VARCHAR | 买入/加仓/减仓/卖出 |
| reason | VARCHAR | 交易原因 |
| model_version | VARCHAR | 模型版本 |
| strategy_version | VARCHAR | 策略版本 |
| score | DOUBLE | 模型分数 |
| target_weight | DOUBLE | 目标仓位 |
| current_weight | DOUBLE | 当前仓位 |
| reference_price | DOUBLE | 参考价格 |
| max_buy_price | DOUBLE | 最高可接受买入价 |
| stop_loss_price | DOUBLE | 止损价 |
| take_profit_rule | VARCHAR | 止盈规则 |
| holding_period | INTEGER | 预计持有交易日 |
| invalid_condition | VARCHAR | 失效条件 |
| discipline_result | VARCHAR | 纪律检查结果 |
| status | VARCHAR | 待执行/已执行/已取消/已失效 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 5.5 trade_executions：交易执行表

用途：记录人工实际成交。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| execution_id | VARCHAR | 执行 ID，主键 |
| plan_id | VARCHAR | 交易计划 ID，可空，非系统交易为空 |
| portfolio_id | VARCHAR | 组合 ID |
| trade_date | DATE | 成交日期 |
| stock_code | VARCHAR | 股票代码 |
| action | VARCHAR | 买入/卖出 |
| price | DOUBLE | 成交价格 |
| quantity | DOUBLE | 成交数量 |
| amount | DOUBLE | 成交金额 |
| fee | DOUBLE | 手续费 |
| tax | DOUBLE | 印花税 |
| slippage | DOUBLE | 滑点 |
| actual_weight | DOUBLE | 执行后仓位 |
| is_follow_plan | BOOLEAN | 是否按计划执行 |
| deviation_reason | VARCHAR | 偏离原因 |
| created_at | TIMESTAMP | 创建时间 |

### 5.6 holdings_snapshot：持仓快照表

用途：每日或每周保存组合持仓快照，便于复盘和归因。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| portfolio_id | VARCHAR | 组合 ID |
| snapshot_date | DATE | 快照日期 |
| stock_code | VARCHAR | 股票代码 |
| quantity | DOUBLE | 持仓数量 |
| avg_cost | DOUBLE | 平均成本 |
| close_price | DOUBLE | 收盘价 |
| market_value | DOUBLE | 市值 |
| weight | DOUBLE | 仓位 |
| return_since_buy | DOUBLE | 持有收益率 |
| current_score | DOUBLE | 当前模型分数 |
| current_rank | INTEGER | 当前模型排名 |
| stop_loss_triggered | BOOLEAN | 是否触发止损 |
| take_profit_triggered | BOOLEAN | 是否触发止盈 |
| created_at | TIMESTAMP | 创建时间 |

建议主键：`portfolio_id, snapshot_date, stock_code`。

## 6. 复盘报告层

### 6.1 trade_reviews：单笔交易复盘表

用途：记录每笔交易或每个完整买卖周期的复盘。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| review_id | VARCHAR | 复盘 ID，主键 |
| plan_id | VARCHAR | 交易计划 ID |
| portfolio_id | VARCHAR | 组合 ID |
| stock_code | VARCHAR | 股票代码 |
| review_date | DATE | 复盘日期 |
| entry_date | DATE | 买入日期 |
| exit_date | DATE | 卖出日期，可空 |
| holding_days | INTEGER | 持有交易日 |
| return_rate | DOUBLE | 实际收益率 |
| benchmark_return | DOUBLE | 同期基准收益 |
| excess_return | DOUBLE | 超额收益 |
| win_or_loss | VARCHAR | 盈利/亏损 |
| model_correct | BOOLEAN | 模型方向是否正确 |
| discipline_result | VARCHAR | 纪律结果 |
| reason_analysis | VARCHAR | 原因分析 |
| lesson_learned | VARCHAR | 经验教训 |
| next_action | VARCHAR | 后续动作 |
| created_at | TIMESTAMP | 创建时间 |

### 6.2 portfolio_reviews：组合复盘表

用途：记录周度或月度组合表现。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| review_id | VARCHAR | 复盘 ID，主键 |
| portfolio_id | VARCHAR | 组合 ID |
| review_start_date | DATE | 复盘开始日期 |
| review_end_date | DATE | 复盘结束日期 |
| review_type | VARCHAR | 周度/月度 |
| portfolio_return | DOUBLE | 组合收益率 |
| benchmark_return | DOUBLE | 基准收益率 |
| excess_return | DOUBLE | 超额收益 |
| max_drawdown | DOUBLE | 最大回撤 |
| win_rate | DOUBLE | 胜率 |
| profit_loss_ratio | DOUBLE | 盈亏比 |
| turnover_rate | DOUBLE | 换手率 |
| top_contributors_json | VARCHAR | 主要贡献 JSON |
| top_detractors_json | VARCHAR | 主要拖累 JSON |
| industry_exposure_json | VARCHAR | 行业暴露 JSON |
| discipline_summary_json | VARCHAR | 纪律汇总 JSON |
| conclusion | VARCHAR | 复盘结论 |
| created_at | TIMESTAMP | 创建时间 |

### 6.3 model_reviews：模型复盘表

用途：记录模型月度或季度表现。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| review_id | VARCHAR | 复盘 ID，主键 |
| model_version | VARCHAR | 模型版本 |
| strategy_version | VARCHAR | 策略版本 |
| review_start_date | DATE | 复盘开始日期 |
| review_end_date | DATE | 复盘结束日期 |
| top_10_return | DOUBLE | Top 10 平均收益 |
| top_20_return | DOUBLE | Top 20 平均收益 |
| top_50_return | DOUBLE | Top 50 平均收益 |
| top_20_win_rate | DOUBLE | Top 20 胜率 |
| rank_ic | DOUBLE | Rank IC |
| rank_ic_ir | DOUBLE | Rank IC 信息比 |
| layered_returns_json | VARCHAR | 分层收益 JSON |
| industry_performance_json | VARCHAR | 行业表现 JSON |
| conclusion | VARCHAR | 复盘结论 |
| retrain_required | BOOLEAN | 是否需要重训 |
| created_at | TIMESTAMP | 创建时间 |

## 7. 配置元数据层

### 7.1 strategy_configs：策略配置表

用途：记录策略参数版本。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| strategy_version | VARCHAR | 策略版本，主键 |
| strategy_name | VARCHAR | 策略名称 |
| config_json | VARCHAR | 策略配置 JSON |
| is_active | BOOLEAN | 是否当前启用 |
| created_at | TIMESTAMP | 创建时间 |

### 7.2 data_quality_checks：数据质量检查表

用途：记录数据更新后的质量检查结果。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| check_id | VARCHAR | 检查 ID，主键 |
| check_date | DATE | 检查日期 |
| dataset_name | VARCHAR | 数据集名称 |
| check_type | VARCHAR | 检查类型 |
| status | VARCHAR | 通过/警告/失败 |
| affected_rows | INTEGER | 影响行数 |
| message | VARCHAR | 检查说明 |
| created_at | TIMESTAMP | 创建时间 |

## 8. 建表 SQL 草案

以下 SQL 可作为后续 `src/stock_research/storage/schema.py` 的基础。

```sql
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
    updated_at TIMESTAMP
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
    updated_at TIMESTAMP,
    PRIMARY KEY (trade_date, stock_code)
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
    created_at TIMESTAMP,
    PRIMARY KEY (trade_date, stock_code, factor_version)
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
    created_at TIMESTAMP,
    PRIMARY KEY (predict_date, stock_code, model_version)
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
    created_at TIMESTAMP,
    updated_at TIMESTAMP
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
    created_at TIMESTAMP
);
```

完整 schema 可在开发阶段拆分为初始化脚本和迁移脚本。

## 9. 关键查询示例

### 9.1 查询某日可交易股票池

```sql
SELECT stock_code
FROM universe_members
WHERE trade_date = ?
  AND universe_name = 'all_a_share'
  AND is_member = true;
```

### 9.2 查询某日 Top 30 候选股票

```sql
SELECT *
FROM selection_results
WHERE selection_date = ?
  AND strategy_version = ?
  AND selection_tier IN ('强推荐', '观察')
ORDER BY rank
LIMIT 30;
```

### 9.3 查询待执行交易计划

```sql
SELECT *
FROM trade_plans
WHERE portfolio_id = ?
  AND status = '待执行'
ORDER BY create_date, stock_code;
```

### 9.4 查询周度组合复盘

```sql
SELECT *
FROM portfolio_reviews
WHERE portfolio_id = ?
  AND review_type = '周度'
ORDER BY review_end_date DESC;
```

## 10. 数据版本规则

建议版本命名：

```text
factor_version: factor_vYYYYMMDD_N
label_version: label_20d_excess_vYYYYMMDD_N
model_version: lgbm_20d_vYYYYMMDD_N
strategy_version: strategy_balanced_vYYYYMMDD_N
```

要求：

- 每次训练模型必须绑定明确的 `factor_version` 和 `label_version`。
- 每次选股必须绑定明确的 `model_version` 和 `strategy_version`。
- 每条交易计划必须绑定当时使用的 `model_version` 和 `strategy_version`。
- 复盘时不得覆盖历史预测和历史交易计划。

## 11. 后续实现建议

1. 先实现 `stocks`、`daily_bars`、`factor_values`、`model_predictions`、`trade_plans`、`trade_executions` 六张核心表。
2. 再补充 `universe_members`、`labels`、`selection_results`、`portfolio_targets`。
3. 最后补充复盘表和数据质量表。
4. 使用 repository 层封装 SQL，避免页面和模型代码直接写复杂 SQL。
5. 所有关键写入操作保留 `created_at` 或 `updated_at`，便于审计。
