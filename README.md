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
