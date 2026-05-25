# A 股个人量化投研系统架构设计 v0.1

## 1. 架构目标

本架构服务于第一阶段 MVP，目标是用可维护、可验证、可逐步扩展的方式打通：

```text
A 股数据 -> 数据清洗 -> 因子计算 -> 模型训练 -> 预测选股 -> 组合构建 -> 交易计划 -> 交易记录 -> 复盘
```

设计原则：

- 本地优先：持仓、交易和复盘数据默认保存在本地 DuckDB。
- 日频优先：第一阶段只处理日线级别数据，不做实时行情和高频交易。
- 模块化：数据、因子、模型、策略、组合、交易、复盘相互解耦。
- 可追溯：模型版本、因子版本、策略版本和交易计划均可回溯。
- 可验证：每个模块都能单独输出中间结果，便于排查未来函数和数据质量问题。
- 先离线后在线：优先用离线脚本和 Streamlit 页面验证闭环，再考虑自动化任务。

## 2. 当前项目基础

当前项目已有基础：

- `app.py`：Streamlit 工作台。
- `src/stock_research/data.py`：行情数据获取基础能力。
- `src/stock_research/indicators.py`：技术指标计算基础能力。
- `src/stock_research/backtest.py`：简单策略回测基础能力。
- `src/stock_research/journal.py`：DuckDB 本地记录观察列表和研究笔记。
- `data/raw/`：原始数据缓存目录。
- `data/processed/`：处理后数据目录。

当前系统偏“个人投研 MVP”，后续需要演进为“A 股量化选股 + 组合交易闭环”。

## 3. 总体架构

```text
┌────────────────────────────────────────────────────────────┐
│                    Streamlit 工作台                         │
│  选股结果 | 组合看板 | 交易计划 | 交易记录 | 复盘报告        │
└───────────────────────────┬────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                      应用服务层                              │
│  股票池服务 | 数据服务 | 因子服务 | 模型服务 | 策略服务       │
│  组合服务   | 交易服务 | 复盘服务 | 配置服务 | 报表服务       │
└───────────────────────────┬────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                      领域逻辑层                              │
│  数据清洗 | 特征工程 | 标签构建 | 模型训练 | 模型预测         │
│  股票过滤 | 组合约束 | 仓位计算 | 纪律检查 | 绩效归因         │
└───────────────────────────┬────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                      数据存储层                              │
│  DuckDB: 股票/行情/因子/预测/组合/交易/复盘                  │
│  Files: 原始数据缓存、模型文件、报告文件、配置文件            │
└───────────────────────────┬────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                      外部数据源                              │
│  AkShare/Tushare/BaoStock/CSV | 指数数据 | 财务估值数据       │
└────────────────────────────────────────────────────────────┘
```

## 4. 推荐目录结构

后续建议将代码逐步演进为以下结构：

```text
personal-stock-research/
├── app.py
├── config/
│   ├── default.yaml
│   └── strategy_a_share_ml.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   ├── models/
│   └── reports/
├── docs/
│   ├── architecture/
│   ├── database/
│   ├── project/
│   ├── requirements/
│   └── roadmap/
├── scripts/
│   ├── update_market_data.py
│   ├── build_factors.py
│   ├── train_model.py
│   ├── predict_signals.py
│   ├── build_portfolio.py
│   └── generate_review.py
└── src/stock_research/
    ├── data_sources/
    │   ├── base.py
    │   ├── akshare_source.py
    │   ├── tushare_source.py
    │   └── csv_source.py
    ├── storage/
    │   ├── db.py
    │   ├── schema.py
    │   └── repositories.py
    ├── universe.py
    ├── factors.py
    ├── labels.py
    ├── models.py
    ├── prediction.py
    ├── selection.py
    ├── portfolio.py
    ├── trading.py
    ├── review.py
    ├── metrics.py
    └── config.py
```

说明：

- `data_sources/` 负责适配不同数据源，避免业务代码直接绑定某个数据供应商。
- `storage/` 负责 DuckDB 连接、建表、读写和迁移。
- `factors.py` 负责特征工程，后续可拆为 `factors/` 包。
- `models.py` 负责训练和评估，后续可拆为 `models/baseline.py`、`models/lightgbm_model.py`。
- `trading.py` 只生成计划和记录执行，不进行自动下单。
- `review.py` 负责单笔交易、组合和模型复盘。

## 5. 核心模块设计

### 5.1 数据源模块

职责：从外部数据源或本地文件获取 A 股数据。

输入：数据源配置、日期范围、股票池。  
输出：标准化 DataFrame 或写入 DuckDB。

第一阶段支持优先级：

1. CSV/本地文件：便于快速验证和测试。
2. AkShare：适合快速接入 A 股公开数据。
3. Tushare：适合后续稳定使用，但需要 token 和积分。
4. BaoStock：可作为免费备选。

标准接口建议：

```python
class MarketDataSource:
    def get_stock_list(self) -> pd.DataFrame: ...
    def get_daily_bars(self, start_date: str, end_date: str) -> pd.DataFrame: ...
    def get_index_bars(self, start_date: str, end_date: str) -> pd.DataFrame: ...
    def get_valuation(self, trade_date: str) -> pd.DataFrame: ...
    def get_financials(self, report_period: str) -> pd.DataFrame: ...
```

### 5.2 存储模块

职责：管理 DuckDB 数据库、表结构和读写操作。

建议数据库文件：

```text
data/processed/research.duckdb
```

核心能力：

- 初始化数据库表。
- 批量 upsert 行情、因子、预测和交易数据。
- 按日期和股票查询。
- 输出训练数据集。
- 保留模型版本、因子版本和策略版本。

### 5.3 股票池模块

职责：生成指定交易日的可交易股票池。

核心规则：

- 剔除 ST、*ST。
- 剔除退市整理和已退市股票。
- 剔除上市不足 120 个交易日股票。
- 剔除停牌股票。
- 剔除成交额过低股票。
- 剔除涨跌停不可交易股票。

输出：`universe_members` 表或 DataFrame。

### 5.4 因子模块

职责：基于行情、估值、财务和指数数据生成模型特征。

第一阶段因子：

- 动量：5日、10日、20日、60日收益。
- 波动率：20日、60日收益波动率。
- 流动性：20日平均成交额、换手率。
- 趋势：价格相对 20 日/60 日均线。
- 估值：PE、PB、市值。
- 质量/成长：ROE、营收增速、利润增速，视数据可得性接入。
- 相对强弱：相对基准指数的 20 日/60 日强弱。

输出：`factor_values` 表。

### 5.5 标签模块

职责：构建训练标签，严格避免未来函数进入特征。

第一阶段主标签：

```text
future_excess_return_20d
```

辅助标签：

```text
top_quantile_20d
```

关键要求：

- 标签可以使用未来收益，但只能用于训练目标，不能进入预测日特征。
- 训练、验证和测试必须按时间切分。
- 标签计算需要扣除或至少记录基准指数收益。

### 5.6 模型模块

职责：训练、评估、保存和加载模型。

第一阶段模型：

- 基线模型：等权因子打分或线性模型。
- 主模型：LightGBM 分类、回归或排序模型。

模型产物：

```text
data/models/{model_version}/model.pkl
data/models/{model_version}/metadata.json
data/models/{model_version}/metrics.json
```

模型元数据至少包含：

- 模型版本。
- 训练时间。
- 训练数据区间。
- 验证数据区间。
- 特征版本。
- 标签定义。
- 参数配置。
- 评估指标。

### 5.7 预测与选股模块

职责：使用模型对指定交易日股票池打分，生成候选股票池。

处理流程：

```text
读取交易日股票池 -> 读取因子 -> 加载模型 -> 预测分数 -> 排名 -> 风险过滤 -> 输出候选股票
```

输出：`model_predictions` 和 `selection_results`。

### 5.8 组合模块

职责：将候选股票池转化为目标组合。

默认规则：

- 候选股票：Top 30。
- 目标持股：10 只。
- 单票最大仓位：10%。
- 单行业最大仓位：30%。
- 总仓位：60%-80%。
- 调仓频率：每周一次。

输出：`portfolio_targets` 和调仓建议。

### 5.9 交易计划模块

职责：对比当前持仓与目标组合，生成买入、卖出、加仓、减仓计划。

计划要求：

- 每条计划必须包含触发原因、模型版本、策略版本、目标仓位、参考价格、最高买入价、止损规则、止盈规则、失效条件和纪律检查结果。
- 系统只生成计划，不自动下单。

输出：`trade_plans`。

### 5.10 交易记录模块

职责：记录人工执行后的实际成交数据。

记录内容：

- 成交日期、价格、数量、金额、手续费、滑点。
- 是否按计划执行。
- 偏离原因。
- 是否非系统交易。

输出：`trade_executions`。

### 5.11 复盘模块

职责：对交易、组合和模型进行复盘。

复盘类型：

- 单笔交易复盘。
- 周度组合复盘。
- 月度模型复盘。

输出：`reviews` 表和 `data/reports/` 下的 Markdown/CSV 报告。

## 6. 数据流设计

### 6.1 每日数据更新流

```text
update_market_data.py
-> 拉取股票基础、行情、指数、估值数据
-> 标准化字段
-> 写入 DuckDB
-> 执行数据质量检查
-> 输出更新日志
```

### 6.2 因子构建流

```text
build_factors.py
-> 读取行情/指数/估值/财务数据
-> 计算因子
-> 缺失值/极值/标准化处理
-> 写入 factor_values
-> 输出因子质量报告
```

### 6.3 模型训练流

```text
train_model.py
-> 读取历史因子
-> 构建标签
-> 时间切分训练/验证/测试
-> 训练基线模型和 LightGBM
-> 评估 Top N、Rank IC、分层收益
-> 保存模型文件和元数据
```

### 6.4 预测选股流

```text
predict_signals.py
-> 读取最新因子
-> 读取可交易股票池
-> 加载最新模型
-> 生成预测分数
-> 过滤风险股票
-> 输出候选股票池
```

### 6.5 组合交易流

```text
build_portfolio.py
-> 读取候选股票池
-> 读取当前持仓
-> 应用组合约束
-> 生成目标组合
-> 生成交易计划
-> 执行纪律检查
```

### 6.6 复盘流

```text
generate_review.py
-> 读取交易计划、执行记录、持仓、行情、基准
-> 计算收益、回撤、胜率、盈亏比、超额收益
-> 评估模型 Top N 后验表现
-> 输出复盘报告
```

## 7. 配置设计

建议将策略参数放入 YAML 配置文件，避免硬编码。

示例：

```yaml
market:
  region: cn_a_share
  benchmark: 000905.SH
  data_frequency: daily

universe:
  min_listed_days: 120
  exclude_st: true
  exclude_suspended: true
  min_avg_amount_20d: 50000000

model:
  label: future_excess_return_20d
  holding_days: 20
  top_quantile: 0.2
  algorithm: lightgbm

selection:
  candidate_top_n: 30

portfolio:
  target_holding_count: 10
  max_single_weight: 0.10
  max_industry_weight: 0.30
  target_total_weight: 0.70
  rebalance_frequency: weekly

trading:
  stop_loss_pct: 0.07
  take_profit_pct: 0.15
  max_buy_premium_pct: 0.03
```

## 8. 页面设计

第一阶段 Streamlit 工作台建议包含以下页面：

1. 数据状态：展示数据更新时间、数据质量、股票池规模。
2. 模型表现：展示模型版本、Top N 表现、Rank IC、分层收益。
3. 今日/本周选股：展示候选股票池、模型分数、风险标签。
4. 组合看板：展示当前组合、目标组合、行业分布和仓位差异。
5. 交易计划：展示待执行、已执行、已失效计划。
6. 交易记录：录入和查看实际执行数据。
7. 复盘报告：展示周度组合复盘、月度模型复盘和单笔交易复盘。

## 9. 自动化设计

第一阶段先使用手工运行脚本；稳定后再加入定时任务。

推荐任务顺序：

```text
收盘后更新数据 -> 构建因子 -> 预测选股 -> 构建组合 -> 生成交易计划 -> 次日人工执行 -> 周末复盘
```

后续可用 cron 或应用内按钮触发，不在第一阶段强制实现。

## 10. 关键技术选型

| 层级 | 推荐选型 | 原因 |
| --- | --- | --- |
| 前端 | Streamlit | 当前项目已使用，适合个人工作台 |
| 数据处理 | pandas / numpy | 当前项目已依赖，适合日频数据处理 |
| 本地数据库 | DuckDB | 当前项目已依赖，适合本地分析型数据 |
| 可视化 | Plotly | 当前项目已依赖，适合交互式图表 |
| 模型 | scikit-learn / LightGBM | 基线模型与树模型选股常用 |
| 配置 | YAML | 策略参数清晰可维护 |
| 报告 | Markdown / CSV | 易读、易导出、易版本管理 |

## 11. 实施顺序建议

1. 建立 DuckDB schema 和 repository 层。
2. 接入或标准化 A 股日线数据。
3. 实现股票池过滤。
4. 实现第一批基础因子。
5. 实现标签构建和训练数据导出。
6. 实现基线模型。
7. 实现 LightGBM 模型。
8. 实现选股结果表和展示页面。
9. 实现组合目标和交易计划。
10. 实现交易记录和复盘报告。

## 12. 架构风险

| 风险 | 影响 | 应对 |
| --- | --- | --- |
| 数据源不稳定 | 影响训练和预测 | 使用数据源适配层，支持多源切换 |
| 模块耦合过高 | 后续难以扩展 | 数据、模型、策略、交易分层实现 |
| 未来函数难排查 | 回测虚高 | 保留数据日期、披露日期和版本信息 |
| 配置硬编码 | 策略难迭代 | 使用 YAML 管理参数 |
| 只做页面不留中间表 | 难复盘和审计 | 所有关键中间结果写入 DuckDB |
