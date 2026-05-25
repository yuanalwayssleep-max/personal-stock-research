# 个人股票投研系统

一个本地运行的股票投研 MVP，覆盖：行情获取、技术指标、简单策略回测、观察列表、研究笔记。

> 仅供学习和研究，不构成投资建议。

## 功能

- 行情数据：通过 Yahoo Finance 获取并缓存在 `data/raw/`
- 技术指标：SMA20、SMA60、20 日年化波动率、RSI14、MACD
- 回测：均线交叉 long-only 策略，对比买入持有
- 投研管理：DuckDB 本地保存观察列表和研究笔记
- Web 工作台：Streamlit + Plotly 交互式界面

## 目录结构

```text
personal-stock-research/
├── app.py
├── pyproject.toml
├── README.md
├── data/
│   ├── raw/
│   └── processed/
└── src/stock_research/
    ├── data.py
    ├── indicators.py
    ├── backtest.py
    └── journal.py
```

## 快速开始

```bash
cd /Users/cocoon/Documents/code/personal-stock-research
/Users/cocoon/.local/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
```

启动后在浏览器打开 Streamlit 提示的本地地址，一般是：

```text
http://localhost:8501
```

也可以直接运行：

```bash
cd /Users/cocoon/Documents/code/personal-stock-research
./run.sh
```

## 股票代码格式

- 美股：`AAPL`、`MSFT`、`NVDA`
- 港股：`0700.HK`、`9988.HK`
- A 股：`600519.SS`、`000001.SZ`

## 后续可扩展方向

1. 接入 A 股数据源，例如 AkShare / Tushare。
2. 加入财务报表、估值分位、盈利预测和行业对比。
3. 加入组合层面的仓位、风险暴露和归因分析。
4. 增加 AI 研报摘要、财报电话会纪要和投研模板。
5. 增加定时任务，每日收盘后自动刷新观察列表。


## 标准化架构

项目采用标准分层架构：

```text
interfaces -> application -> domain
interfaces -> application -> infrastructure
application -> domain
application -> infrastructure
```

MVP 只限制功能范围，不降低架构标准。当前标准目录包括：

- `src/stock_research/domain/`：核心投研规则，例如股票池过滤、因子计算
- `src/stock_research/application/`：业务用例编排，例如导入数据、构建 MVP-1
- `src/stock_research/infrastructure/`：DuckDB、CSV、未来 AkShare/Tushare 等外部适配
- `src/stock_research/interfaces/`：CLI、Web、未来 API 入口
- `src/stock_research/shared/`：路径、配置和通用基础能力

详细说明见：`docs/architecture/standardized-architecture-v0.2.md`。

## MVP-1：A 股数据与因子基础

当前已加入 MVP-1 的基础模块：

- DuckDB 本地数据库 schema 初始化
- A 股股票、日行情、估值 CSV 导入
- 可交易股票池过滤
- 基础动量、波动率、流动性、趋势和估值因子计算

初始化数据库：

```bash
./.venv/bin/python scripts/init_db.py --db data/processed/research.duckdb
```

导入 CSV 数据：

```bash
./.venv/bin/python scripts/import_csv_data.py \
  --db data/processed/research.duckdb \
  --stocks data/raw/stocks.csv \
  --daily-bars data/raw/daily_bars.csv \
  --valuation data/raw/valuation.csv
```

生成指定交易日的股票池和基础因子：

```bash
./.venv/bin/python scripts/build_mvp1.py \
  --db data/processed/research.duckdb \
  --trade-date 2024-06-07
```

CSV 字段可使用英文列名或部分中文列名。股票代码会规范化为 `000001.SZ`、`600519.SH` 这类格式。
