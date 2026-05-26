# 数据库建设 v0.2

## 建设目标

当前数据库从 MVP-1 的少量表扩展为完整投研闭环的基础 schema。MVP 功能可以分阶段实现，但数据库结构先覆盖后续模型、选股、组合、交易和复盘链路，避免后续推倒重来。

## 数据库文件

默认路径：

```text
data/processed/research.duckdb
```

可通过环境变量覆盖：

```bash
STOCK_RESEARCH_DB=/path/to/research.duckdb uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8010
```

## Schema 版本

当前版本：

```text
2026_05_26_001_database_foundation
```

版本记录表：

```text
schema_versions
```

## 表分层

### 基础数据层

```text
stocks
trading_calendar
daily_bars
index_bars
valuation_daily
financial_reports
```

### 特征模型层

```text
universe_members
factor_values
labels
model_runs
model_predictions
selection_results
```

### 组合交易层

```text
portfolios
portfolio_positions
portfolio_targets
trade_plans
trade_executions
holdings_snapshot
```

### 复盘报告层

```text
trade_reviews
portfolio_reviews
model_reviews
```

### 配置与元数据层

```text
strategy_configs
data_quality_checks
data_source_runs
schema_versions
```

## 初始化方式

调用后端 API：

```bash
curl -X POST http://localhost:8010/api/database/init
```

或在 Python 中使用：

```python
from stock_research.infrastructure.persistence import init_db

init_db("data/processed/research.duckdb")
```

## 设计规则

- 股票代码统一使用 `000001.SZ`、`600519.SH` 格式。
- 所有关键中间结果必须保留版本字段，例如 `factor_version`、`label_version`、`model_version`、`strategy_version`。
- 财务数据必须保留 `announce_date`，避免未来函数。
- 模型训练、预测、选股、交易计划和复盘结果都应可追溯。
- `ResearchRepository.write_table()` 支持后续新增业务层批量写入，但表名必须已存在。

## 当前已支持

- 完整核心表初始化。
- schema 版本记录。
- 核心分析表索引。
- 泛化表写入接口。
- 表清单、行数统计、schema 版本查询。
- API 数据状态返回 schema 版本。
