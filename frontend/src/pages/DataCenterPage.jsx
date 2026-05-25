import { Database, FileUp, RefreshCcw } from 'lucide-react';

export function DataCenterPage({ status, files, setFiles, busy, runAction, onRefresh, initDatabase, importCsv }) {
  return (
    <div className="page-stack">
      <section className="panel controls">
        <div>
          <h2>数据中心</h2>
          <p>管理 DuckDB 初始化、CSV 上传导入和数据规模检查。MVP-1 当前只接 CSV，后续会接 AkShare/Tushare。</p>
        </div>
        <div className="actions">
          <button disabled={busy} onClick={() => runAction(initDatabase, (r) => `数据库已初始化：${r.db_path}`)}>
            <Database size={16} /> 初始化数据库
          </button>
          <button disabled={busy} onClick={() => runAction(onRefresh, () => '状态已刷新')}>
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
        <div className="panel">
          <h2>数据表状态</h2>
          {Object.entries(status?.tables ?? {}).map(([table, rows]) => (
            <div className="key-value" key={table}><span>{table}</span><strong>{rows ?? '-'}</strong></div>
          ))}
        </div>
      </section>
    </div>
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
