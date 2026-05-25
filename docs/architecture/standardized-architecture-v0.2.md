# A 股个人量化投研系统标准化架构 v0.2

## 1. 架构原则

MVP 只限制功能范围，不降低架构标准。系统从第一天开始采用标准分层架构，确保后续从 MVP-1 扩展到模型训练、组合管理、交易计划、复盘和自动化任务时不需要推倒重来。

核心原则：

- 分层清晰：领域规则、应用编排、基础设施、外部接口分离。
- 依赖单向：外层依赖内层，领域层不依赖数据库、页面、脚本或第三方数据源。
- 中间结果可追溯：股票池、因子、模型、选股、组合、交易和复盘结果均落库。
- 配置与代码分离：策略参数、股票池过滤参数、模型参数后续进入配置文件。
- MVP 功能可小，架构不临时：新增功能必须落在正确层级，不允许脚本堆逻辑。

## 2. 标准分层

```text
interfaces       外部入口层：CLI、Streamlit、未来 API
application      应用用例层：编排一次业务动作，不写底层 SQL 和算法细节
domain           领域层：股票池、因子、标签、模型、组合、交易纪律等核心规则
infrastructure   基础设施层：数据库、数据源、文件、外部服务适配
shared           共享基础：路径、配置、通用类型、工具函数
```

依赖方向：

```text
interfaces -> application -> domain
interfaces -> application -> infrastructure
application -> domain
application -> infrastructure
infrastructure -> shared
domain -> shared，可选且应尽量少
```

禁止方向：

```text
domain -> infrastructure
domain -> interfaces
application -> interfaces
```

## 3. 当前标准目录结构

```text
src/stock_research/
├── application/
│   └── use_cases/
│       ├── build_mvp1.py
│       ├── import_csv_data.py
│       └── init_database.py
├── domain/
│   └── services/
│       ├── factors.py
│       └── universe.py
├── infrastructure/
│   ├── data_sources/
│   │   └── csv_source.py
│   └── persistence/
│       ├── db.py
│       ├── repositories.py
│       └── schema.py
├── interfaces/
│   └── cli/
├── shared/
│   └── paths.py
├── data.py
├── indicators.py
├── backtest.py
└── journal.py
```

说明：

- `application/use_cases/`：每个文件对应一个可执行业务用例，例如初始化数据库、导入数据、构建 MVP-1 结果。
- `domain/services/`：放纯业务规则和计算逻辑，例如股票池过滤、因子计算。
- `infrastructure/data_sources/`：放数据源适配，例如 CSV、AkShare、Tushare、BaoStock。
- `infrastructure/persistence/`：放 DuckDB 连接、schema、repository。
- `interfaces/`：放 CLI、Web/API 入口适配。当前 `scripts/` 是临时 CLI 入口，内部只调用 application 用例。
- `shared/`：放路径、配置、通用常量。

当前保留了少量旧路径兼容入口，例如 `stock_research.storage`、`stock_research.factors`，用于平滑迁移；新增代码应使用标准路径。

## 4. MVP 与架构边界

MVP-1 的功能边界：

```text
CSV 数据导入 -> DuckDB 存储 -> 股票池过滤 -> 基础因子计算
```

但架构边界已经按照完整系统设计：

```text
数据源适配 -> Repository -> Application Use Case -> Domain Service -> 输出落库
```

这意味着后续 MVP-2 增加模型训练时，只新增：

```text
domain/services/labels.py
domain/services/modeling.py
infrastructure/model_store/
application/use_cases/train_model.py
application/use_cases/predict_signals.py
```

不需要重写 MVP-1 的数据层和入口层。

## 5. 各层职责标准

### 5.1 Interfaces 层

职责：接收用户输入，调用应用用例，展示结果。

允许：

- CLI 参数解析。
- Streamlit 表单和图表。
- API request/response 转换。

禁止：

- 直接写 SQL。
- 直接实现因子、模型、组合规则。
- 直接操作 DuckDB 表结构。

### 5.2 Application 层

职责：编排业务流程。

示例：`build_mvp1.py` 负责：

```text
读取股票和行情 -> 调用股票池服务 -> 写入 universe_members -> 调用因子服务 -> 写入 factor_values
```

允许：

- 调用 repository。
- 调用 domain service。
- 汇总结果对象。

禁止：

- 写复杂 SQL 细节。
- 写具体数据源适配逻辑。
- 写页面展示逻辑。

### 5.3 Domain 层

职责：表达投研系统的核心业务规则。

当前包括：

- 股票池过滤：ST、停牌、上市天数、流动性、涨跌停锁死。
- 基础因子：动量、波动率、成交额、换手率、均线偏离、估值字段。

后续会包括：

- 标签构建。
- 模型训练与评分规则。
- 选股规则。
- 组合约束。
- 交易纪律。
- 复盘归因。

禁止：

- 连接数据库。
- 读取文件。
- 调用 Streamlit。
- 依赖某个数据供应商 SDK。

### 5.4 Infrastructure 层

职责：处理所有外部世界的技术细节。

当前包括：

- CSV 数据源解析。
- DuckDB schema 初始化。
- DuckDB repository 读写。

后续包括：

- AkShare/Tushare/BaoStock 数据源。
- 模型文件存储。
- 报告文件输出。
- 定时任务适配。

### 5.5 Shared 层

职责：提供通用基础能力。

当前包括：

- 项目根目录。
- 数据目录。
- 默认 DuckDB 路径。

后续可加入：

- 配置加载。
- 日期工具。
- 通用异常类型。
- 日志配置。

## 6. 标准开发规则

新增功能时按以下顺序落位：

1. 先判断是否是领域规则；如果是，放入 `domain/`。
2. 如果是一个业务流程，放入 `application/use_cases/`。
3. 如果是数据源、数据库、文件、模型存储，放入 `infrastructure/`。
4. 如果是用户入口、页面、CLI、API，放入 `interfaces/` 或 `scripts/`。
5. `scripts/` 只做参数解析，不承载业务逻辑。
6. 每个用例至少有一个测试覆盖核心路径。
7. 所有关键中间产物必须可落库或可导出。

## 7. 后续模块落位规划

### MVP-2：模型训练与选股

```text
src/stock_research/domain/services/labels.py
src/stock_research/domain/services/model_evaluation.py
src/stock_research/domain/services/selection.py
src/stock_research/infrastructure/model_store/
src/stock_research/application/use_cases/build_labels.py
src/stock_research/application/use_cases/train_model.py
src/stock_research/application/use_cases/predict_signals.py
```

### MVP-3：组合与交易计划

```text
src/stock_research/domain/services/portfolio.py
src/stock_research/domain/services/trading_rules.py
src/stock_research/application/use_cases/build_portfolio.py
src/stock_research/application/use_cases/generate_trade_plans.py
```

### MVP-4：交易记录与复盘

```text
src/stock_research/domain/services/performance.py
src/stock_research/domain/services/review.py
src/stock_research/application/use_cases/record_trade_execution.py
src/stock_research/application/use_cases/generate_weekly_review.py
src/stock_research/application/use_cases/generate_model_review.py
```

## 8. 当前兼容策略

为避免一次性破坏已有入口，当前保留兼容 wrapper：

```text
stock_research.storage -> stock_research.infrastructure.persistence
stock_research.data_sources -> stock_research.infrastructure.data_sources
stock_research.factors -> stock_research.domain.services.factors
stock_research.universe -> stock_research.domain.services.universe
stock_research.paths -> stock_research.shared.paths
```

新代码必须使用标准路径。旧 wrapper 后续可以在系统稳定后删除。
