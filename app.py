from __future__ import annotations

import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from stock_research.backtest import sma_cross_backtest
from stock_research.data import fetch_prices, normalize_symbol
from stock_research.indicators import add_indicators
from stock_research.journal import add_note, get_notes, get_watchlist, upsert_watch

st.set_page_config(page_title="个人股票投研系统", layout="wide")

st.title("个人股票投研系统")
st.caption("数据、指标、回测、观察列表和研究笔记的一体化本地工作台。仅供研究，不构成投资建议。")

with st.sidebar:
    st.header("标的设置")
    symbol = normalize_symbol(st.text_input("股票代码", value="AAPL", help="美股如 AAPL/MSFT；港股可用 0700.HK；A 股 Yahoo 格式如 600519.SS"))
    period = st.selectbox("历史区间", ["6mo", "1y", "2y", "5y", "10y"], index=2)
    refresh = st.button("刷新行情缓存")

try:
    prices = fetch_prices(symbol, period=period, refresh=refresh)
    data = add_indicators(prices)
except Exception as exc:
    st.error(f"数据获取失败：{exc}")
    st.stop()

tab_overview, tab_backtest, tab_watch, tab_notes = st.tabs(["行情指标", "策略回测", "观察列表", "研究笔记"])

with tab_overview:
    latest = data.dropna().iloc[-1]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("最新收盘", f"{latest['Close']:.2f}")
    c2.metric("20日波动率", f"{latest['Volatility20']:.2%}")
    c3.metric("RSI14", f"{latest['RSI14']:.1f}")
    c4.metric("MACD柱", f"{latest['MACDHist']:.2f}")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data["Open"], high=data["High"], low=data["Low"], close=data["Close"], name="K线"))
    fig.add_trace(go.Scatter(x=data.index, y=data["SMA20"], name="SMA20", line=dict(width=1.5)))
    fig.add_trace(go.Scatter(x=data.index, y=data["SMA60"], name="SMA60", line=dict(width=1.5)))
    fig.update_layout(height=620, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("最近数据")
    st.dataframe(data.tail(30), use_container_width=True)

with tab_backtest:
    fast, slow = st.columns(2)
    fast_window = fast.slider("快均线", 5, 80, 20)
    slow_window = slow.slider("慢均线", 20, 240, 60)
    bt, metrics = sma_cross_backtest(prices, fast=fast_window, slow=slow_window)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("策略收益", f"{metrics['strategy_return']:.2%}")
    m2.metric("买入持有", f"{metrics['buy_hold_return']:.2%}")
    m3.metric("夏普比率", f"{metrics['sharpe']:.2f}")
    m4.metric("最大回撤", f"{metrics['max_drawdown']:.2%}")

    equity = go.Figure()
    equity.add_trace(go.Scatter(x=bt.index, y=bt["Equity"], name="策略净值"))
    equity.add_trace(go.Scatter(x=bt.index, y=bt["BuyHold"], name="买入持有"))
    equity.update_layout(height=480, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(equity, use_container_width=True)

with tab_watch:
    st.subheader("添加 / 更新观察标的")
    with st.form("watch_form"):
        thesis = st.text_area("投资逻辑", placeholder="例如：收入增长、利润率改善、估值修复...")
        target_price = st.number_input("目标价", min_value=0.0, value=0.0, step=1.0)
        risk = st.text_area("主要风险", placeholder="例如：监管、竞争、需求下滑...")
        submitted = st.form_submit_button("保存到观察列表")
        if submitted:
            upsert_watch(symbol, thesis, target_price or None, risk)
            st.success(f"已保存 {symbol}")

    st.subheader("观察列表")
    st.dataframe(get_watchlist(), use_container_width=True)

with tab_notes:
    st.subheader("新增研究笔记")
    with st.form("note_form"):
        note = st.text_area("笔记内容", placeholder="记录财报要点、会议纪要、估值假设、交易计划...")
        note_submitted = st.form_submit_button("保存笔记")
        if note_submitted and note.strip():
            add_note(symbol, note.strip())
            st.success("笔记已保存")

    st.subheader(f"{symbol} 的历史笔记")
    st.dataframe(get_notes(symbol), use_container_width=True)
