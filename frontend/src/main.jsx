import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, Database, FileUp, Layers3, Play, RefreshCcw, ShieldCheck } from 'lucide-react';
import './styles.css';
import { buildMvp1, getFactors, getHealth, getStatus, getUniverse, importCsv, initDatabase } from './api';

function App() {
  const [health, setHealth] = useState('checking');
  const [status, setStatus] = useState(null);
  const [universe, setUniverse] = useState([]);
  const [factors, setFactors] = useState([]);
  const [tradeDate, setTradeDate] = useState('2024-06-07');
  const [files, setFiles] = useState({ stocks: null, dailyBars: null, valuation: null });
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');

  async function refresh() {
    const [healthResult, statusResult] = await Promise.all([getHealth(), getStatus()]);
    setHealth(healthResult.status);
    setStatus(statusResult);
    const date = tradeDate || statusResult.latest_dates?.universe_members || statusResult.latest_dates?.factor_values;
    const [universeRows, factorRows] = await Promise.all([
      getUniverse({ tradeDate: date, membersOnly: false, limit: 80 }).catch(() => []),
      getFactors({ tradeDate: date, limit: 80 }).catch(() => []),
    ]);
    setUniverse(universeRows);
    setFactors(factorRows);
  }

  useEffect(() => {
    refresh().catch((error) => {
      setHealth('offline');
      setNotice(error.message);
    });
  }, []);

  async function runAction(action, successMessage) {
    setBusy(true);
    setNotice('');
    try {
      const result = await action();
      setNotice(successMessage(result));
      await refresh();
    } catch (error) {
      setNotice(error.message);
    } finally {
      setBusy(false);
    }
  }

  const tableCards = useMemo(() => status?.tables ?? {}, [status]);

  return (
    <main className="shell">
      <section className="hero">
        <div>
          <p className="eyebrow">A-Share Quant Research</p>
          <h1>个人 A 股量化投研系统</h1>
          <p className="lead">前后端分离架构：React 负责操作台，FastAPI 负责编排数据、股票池和因子流水线。</p>
        </div>
        <div className={`status-pill ${health === 'ok' ? 'ok' : 'bad'}`}>
          <Activity size={18} /> API {health}
        </div>
      </section>

      {notice && <div className="notice">{notice}</div>}

      <section className="grid metrics">
        <Metric icon={<Database />} label="股票基础" value={tableCards.stocks ?? '-'} />
        <Metric icon={<Activity />} label="日行情" value={tableCards.daily_bars ?? '-'} />
        <Metric icon={<ShieldCheck />} label="股票池" value={tableCards.universe_members ?? '-'} />
        <Metric icon={<Layers3 />} label="因子行数" value={tableCards.factor_values ?? '-'} />
      </section>

      <section className="panel controls">
        <div>
          <h2>数据流水线</h2>
          <p>先初始化数据库，再上传 CSV，最后指定交易日构建可交易股票池和基础因子。</p>
        </div>
        <div className="actions">
          <button disabled={busy} onClick={() => runAction(initDatabase, (r) => `数据库已初始化：${r.db_path}`)}>
            <Database size={16} /> 初始化数据库
          </button>
          <button disabled={busy} onClick={() => runAction(refresh, () => '状态已刷新')}>
            <RefreshCcw size={16} /> 刷新状态
          </button>
        </div>
      </section>

      <section className="grid two">
        <div className="panel upload-panel">
          <h2>CSV 导入</h2>
          <FileInput label="股票基础 CSV" onChange={(file) => setFiles((prev) => ({ ...prev, stocks: file }))} />
          <FileInput label="日行情 CSV" onChange={(file) => setFiles((prev) => ({ ...prev, dailyBars: file }))} />
          <FileInput label="估值 CSV" onChange={(file) => setFiles((prev) => ({ ...prev, valuation: file }))} />
          <button
            disabled={busy}
            onClick={() => runAction(() => importCsv(files), (r) => `导入完成：股票 ${r.stocks}，行情 ${r.daily_bars}，估值 ${r.valuation}`)}
          >
            <FileUp size={16} /> 导入 CSV
          </button>
        </div>

        <div className="panel build-panel">
          <h2>MVP-1 构建</h2>
          <label className="field">
            <span>交易日</span>
            <input value={tradeDate} onChange={(event) => setTradeDate(event.target.value)} placeholder="YYYY-MM-DD" />
          </label>
          <button
            disabled={busy || !tradeDate}
            onClick={() => runAction(
              () => buildMvp1({ trade_date: tradeDate }),
              (r) => `构建完成：股票池 ${r.universe_rows} 行，入池 ${r.universe_members} 只，因子 ${r.factor_rows} 行`,
            )}
          >
            <Play size={16} /> 构建股票池和因子
          </button>
        </div>
      </section>

      <section className="grid two data-grid">
        <DataTable title="股票池结果" rows={universe} columns={['trade_date', 'stock_code', 'is_member', 'exclude_reason', 'avg_amount_20d']} />
        <DataTable title="基础因子" rows={factors} columns={['trade_date', 'stock_code', 'momentum_20d', 'volatility_20d', 'avg_amount_20d', 'pe_ttm', 'pb']} />
      </section>
    </main>
  );
}

function Metric({ icon, label, value }) {
  return (
    <article className="metric-card">
      <div className="metric-icon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function FileInput({ label, onChange }) {
  return (
    <label className="file-row">
      <span>{label}</span>
      <input type="file" accept=".csv" onChange={(event) => onChange(event.target.files?.[0] ?? null)} />
    </label>
  );
}

function DataTable({ title, rows, columns }) {
  return (
    <div className="panel table-panel">
      <div className="table-head">
        <h2>{title}</h2>
        <span>{rows.length} 行</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr><td colSpan={columns.length}>暂无数据</td></tr>
            ) : rows.map((row, index) => (
              <tr key={`${title}-${index}`}>
                {columns.map((column) => <td key={column}>{formatValue(row[column])}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function formatValue(value) {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'number') return Math.abs(value) > 1000 ? value.toLocaleString('zh-CN', { maximumFractionDigits: 2 }) : value.toFixed(4);
  if (typeof value === 'boolean') return value ? '是' : '否';
  return String(value);
}

createRoot(document.getElementById('root')).render(<App />);
