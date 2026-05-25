# 个人 A 股量化投研系统

一个前后端分离的个人 A 股量化投研系统。当前阶段聚焦 MVP-1：A 股数据导入、DuckDB 本地存储、可交易股票池过滤和基础因子计算。

> 仅供学习和研究，不构成投资建议。

## 架构

```text
frontend/                 React + Vite 操作台
backend/                  FastAPI API 服务
src/stock_research/       核心 Python 包
├── application/          应用用例编排
├── domain/               投研领域规则
├── infrastructure/       数据源、数据库、外部适配
├── interfaces/           未来接口适配层
└── shared/               路径、配置、通用基础能力
```

依赖方向：

```text
frontend -> backend API
backend -> application -> domain
backend -> application -> infrastructure
```

MVP 只限制功能范围，不降低架构标准。详细说明见：`docs/architecture/standardized-architecture-v0.2.md`。

## 后端启动

```bash
cd /Users/cocoon/Documents/code/personal-stock-research
/Users/cocoon/.local/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：

```text
http://localhost:8000/docs
```

## 前端启动

```bash
cd /Users/cocoon/Documents/code/personal-stock-research/frontend
npm install
npm run dev
```

前端地址：

```text
http://localhost:5174
```

如果后端不是 `http://localhost:8000`，可设置：

```bash
VITE_API_BASE=http://localhost:8000 npm run dev
```

## MVP-1 功能

当前已实现：

- DuckDB 本地数据库 schema 初始化
- A 股股票、日行情、估值 CSV 上传导入
- 股票代码规范化，例如 `000001.SZ`、`600519.SH`
- 可交易股票池过滤：ST、停牌、上市时间不足、低流动性、涨跌停锁死
- 基础因子计算：动量、波动率、流动性、趋势、估值字段
- React 页面查看数据状态、股票池结果和因子结果

## API 概览

```text
GET  /health
POST /api/database/init
POST /api/data/import-csv
POST /api/mvp1/build
GET  /api/data/status
GET  /api/universe
GET  /api/factors
```

## CSV 字段

股票基础 CSV 至少需要：

```text
stock_code,stock_name,list_date
```

日行情 CSV 至少需要：

```text
trade_date,stock_code,open,high,low,close
```

估值 CSV 至少需要：

```text
trade_date,stock_code
```

可选字段包括：`amount`、`turnover_rate`、`adj_factor`、`is_suspended`、`limit_up_price`、`limit_down_price`、`pe_ttm`、`pb`、`market_cap`。

## 测试

```bash
.venv/bin/python -m pytest -q
```

## 下一步

1. 接入 AkShare/Tushare 作为真实 A 股数据源。
2. 实现 MVP-2：标签构建、模型训练、预测选股。
3. 将 React 页面扩展为数据状态、模型表现、选股、组合、交易计划和复盘模块。
