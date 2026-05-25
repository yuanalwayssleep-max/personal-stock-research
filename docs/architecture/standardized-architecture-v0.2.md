# A 股个人量化投研系统标准化架构 v0.2

## 1. 架构原则

系统从当前阶段开始采用中长期前后端分离结构。MVP 只限制功能范围，不降低架构标准。

核心原则：

- 前后端分离：React 只负责用户交互和展示，FastAPI 负责 API、用例编排和后端入口。
- 核心业务内聚：投研规则、因子、股票池、模型、组合、交易纪律放在 `src/stock_research`。
- 依赖单向：外层依赖内层，领域层不依赖 API、数据库实现、React 或第三方数据源。
- 中间结果可追溯：股票池、因子、模型、选股、组合、交易和复盘结果均应落库。
- 不保留临时入口：不再使用 Streamlit、脚本工作台或旧兼容路径。

## 2. 顶层结构

```text
personal-stock-research/
├── backend/                 # FastAPI 后端服务
├── frontend/                # React + Vite 前端应用
├── src/stock_research/      # 核心 Python 业务包
├── tests/                   # 后端与核心逻辑测试
├── docs/                    # 项目、需求、架构、数据库文档
├── data/                    # 本地数据，数据库和 CSV 不入库
└── pyproject.toml           # 后端与核心包依赖
```

## 3. 前后端职责

### 3.1 Frontend

路径：`frontend/`

职责：

- React 页面、组件、样式和浏览器交互。
- 调用 FastAPI 接口。
- 展示数据状态、股票池、因子、后续模型和组合结果。
- 不直接读取本地文件系统、不连接 DuckDB、不实现投研规则。

当前技术栈：

```text
React + Vite + CSS
```

### 3.2 Backend

路径：`backend/`

职责：

- FastAPI 应用启动和路由注册。
- API request/response 校验。
- 文件上传、错误处理、CORS。
- 调用 application use case。
- 不直接实现因子、股票池、模型和组合核心规则。

当前 API：

```text
GET  /health
POST /api/database/init
POST /api/data/import-csv
POST /api/mvp1/build
GET  /api/data/status
GET  /api/universe
GET  /api/factors
```

## 4. 核心业务包结构

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
└── shared/
    └── paths.py
```

## 5. 分层职责

### 5.1 Application 层

路径：`src/stock_research/application/`

职责：编排业务流程。

示例：`build_mvp1.py`

```text
读取股票和行情 -> 调用股票池领域服务 -> 写入 universe_members -> 调用因子领域服务 -> 写入 factor_values
```

允许：

- 调用 domain service。
- 调用 repository。
- 返回用例结果对象。

禁止：

- 写页面逻辑。
- 写数据源解析细节。
- 写大量 SQL 细节。

### 5.2 Domain 层

路径：`src/stock_research/domain/`

职责：表达核心投研规则。

当前包括：

- 股票池过滤：ST、停牌、上市天数、流动性、涨跌停锁死。
- 基础因子：动量、波动率、成交额、换手率、均线偏离、估值字段。

后续包括：

- 标签构建。
- 模型训练评估。
- 选股规则。
- 组合约束。
- 交易纪律。
- 复盘归因。

禁止：

- 连接数据库。
- 读取文件。
- 依赖 FastAPI。
- 依赖 React。
- 依赖某个数据供应商 SDK。

### 5.3 Infrastructure 层

路径：`src/stock_research/infrastructure/`

职责：处理外部技术细节。

当前包括：

- CSV 数据源解析。
- DuckDB schema 初始化。
- DuckDB repository 读写。

后续包括：

- AkShare/Tushare/BaoStock 数据源。
- 模型文件存储。
- 报告文件输出。
- 任务调度适配。

### 5.4 Shared 层

路径：`src/stock_research/shared/`

职责：共享基础能力。

当前包括：

- 项目根目录。
- 数据目录。
- 默认 DuckDB 路径。

后续可加入：

- 配置加载。
- 日期工具。
- 通用异常类型。
- 日志配置。

## 6. 依赖方向

```text
frontend -> backend API
backend -> application
application -> domain
application -> infrastructure
infrastructure -> shared
domain -> shared，可选且应尽量少
```

禁止方向：

```text
domain -> infrastructure
src/stock_research -> backend
src/stock_research -> frontend
frontend -> DuckDB
frontend -> local CSV path
```

## 7. MVP-1 当前链路

```text
React 页面上传 CSV
-> FastAPI /api/data/import-csv
-> application.import_csv_data
-> infrastructure.csv_source 解析
-> infrastructure.repository 写入 DuckDB

React 页面触发构建
-> FastAPI /api/mvp1/build
-> application.build_mvp1
-> domain.universe 生成股票池
-> domain.factors 计算基础因子
-> infrastructure.repository 写入 DuckDB

React 页面查询结果
-> FastAPI /api/data/status, /api/universe, /api/factors
-> infrastructure.repository 查询 DuckDB
-> JSON 返回前端展示
```

## 8. 后续模块落位规划

### MVP-2：模型训练与选股

```text
src/stock_research/domain/services/labels.py
src/stock_research/domain/services/model_evaluation.py
src/stock_research/domain/services/selection.py
src/stock_research/infrastructure/model_store/
src/stock_research/application/use_cases/build_labels.py
src/stock_research/application/use_cases/train_model.py
src/stock_research/application/use_cases/predict_signals.py
backend/app/api/routes/models.py
frontend/src/pages/ModelPage.jsx
frontend/src/pages/SelectionPage.jsx
```

### MVP-3：组合与交易计划

```text
src/stock_research/domain/services/portfolio.py
src/stock_research/domain/services/trading_rules.py
src/stock_research/application/use_cases/build_portfolio.py
src/stock_research/application/use_cases/generate_trade_plans.py
backend/app/api/routes/portfolio.py
backend/app/api/routes/trade_plans.py
frontend/src/pages/PortfolioPage.jsx
frontend/src/pages/TradePlansPage.jsx
```

### MVP-4：交易记录与复盘

```text
src/stock_research/domain/services/performance.py
src/stock_research/domain/services/review.py
src/stock_research/application/use_cases/record_trade_execution.py
src/stock_research/application/use_cases/generate_weekly_review.py
src/stock_research/application/use_cases/generate_model_review.py
backend/app/api/routes/reviews.py
frontend/src/pages/ReviewsPage.jsx
```

## 9. 开发规则

- 新页面放到 `frontend/`。
- 新 API 放到 `backend/app/api/routes/`。
- 新业务流程放到 `src/stock_research/application/use_cases/`。
- 新投研规则放到 `src/stock_research/domain/services/`。
- 新外部适配放到 `src/stock_research/infrastructure/`。
- API 不直接实现核心规则，只调用 application use case。
- React 不直接接触数据库和本地文件路径。
- 删除不再使用的临时入口，避免架构漂移。
