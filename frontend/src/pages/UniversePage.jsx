import { Play, RefreshCcw } from 'lucide-react';
import { DataTable } from '../components/DataTable';

export function UniversePage({ universe, tradeDate, setTradeDate, busy, runAction, buildMvp1, onRefresh }) {
  return (
    <div className="page-stack">
      <section className="panel controls">
        <div>
          <h2>股票池构建</h2>
          <p>按 ST、停牌、上市天数、流动性和涨跌停锁死规则，生成指定交易日的可交易股票池。</p>
        </div>
        <div className="actions build-actions">
          <label className="compact-field">
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
            <Play size={16} /> 构建
          </button>
          <button disabled={busy} onClick={() => runAction(onRefresh, () => '股票池已刷新')}><RefreshCcw size={16} /> 刷新</button>
        </div>
      </section>
      <DataTable title="股票池结果" rows={universe} columns={['trade_date', 'stock_code', 'is_member', 'exclude_reason', 'avg_amount_20d', 'listed_days']} />
    </div>
  );
}
