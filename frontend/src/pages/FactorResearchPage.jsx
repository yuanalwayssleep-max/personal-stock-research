import { RefreshCcw } from 'lucide-react';
import { DataTable } from '../components/DataTable';

export function FactorResearchPage({ factors, busy, onRefresh, runAction }) {
  return (
    <div className="page-stack">
      <section className="panel controls">
        <div>
          <h2>因子研究</h2>
          <p>查看 MVP-1 已计算的基础因子。后续会加入 IC、Rank IC、分层收益、相关性和缺失率分析。</p>
        </div>
        <button disabled={busy} onClick={() => runAction(onRefresh, () => '因子已刷新')}><RefreshCcw size={16} /> 刷新</button>
      </section>
      <DataTable title="基础因子" rows={factors} columns={['trade_date', 'stock_code', 'momentum_20d', 'volatility_20d', 'avg_amount_20d', 'ma_20_ratio', 'pe_ttm', 'pb']} />
    </div>
  );
}
