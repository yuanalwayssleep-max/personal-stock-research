import { Activity, Database, Layers3, RefreshCcw, ShieldCheck } from 'lucide-react';
import { MetricCard } from '../components/MetricCard';

export function OverviewPage({ status, health, onRefresh, busy }) {
  const tables = status?.tables ?? {};
  const latest = status?.latest_dates ?? {};
  return (
    <div className="page-stack">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">Daily Command Center</p>
          <h2>从数据质量开始，逐步进入模型、组合和交易闭环。</h2>
          <p>这里是每天打开系统的第一屏：先看服务状态、数据规模、股票池和因子是否已经更新。</p>
        </div>
        <button disabled={busy} onClick={onRefresh}><RefreshCcw size={16} /> 刷新状态</button>
      </section>
      <section className="grid metrics">
        <MetricCard icon={<Activity />} label="API 状态" value={health} tone={health === 'ok' ? 'green' : 'red'} />
        <MetricCard icon={<Database />} label="股票基础" value={tables.stocks ?? '-'} />
        <MetricCard icon={<ShieldCheck />} label="股票池" value={tables.universe_members ?? '-'} />
        <MetricCard icon={<Layers3 />} label="因子行数" value={tables.factor_values ?? '-'} />
      </section>
      <section className="grid two">
        <div className="panel">
          <h2>最新日期</h2>
          <div className="key-value"><span>日行情</span><strong>{latest.daily_bars ?? '-'}</strong></div>
          <div className="key-value"><span>股票池</span><strong>{latest.universe_members ?? '-'}</strong></div>
          <div className="key-value"><span>因子</span><strong>{latest.factor_values ?? '-'}</strong></div>
          <div className="key-value"><span>Schema</span><strong>{status?.schema_version ?? '-'}</strong></div>
        </div>
        <div className="panel agenda-panel">
          <h2>当前阶段待办</h2>
          <p>MVP-1 聚焦数据和因子地基，完成后进入 MVP-2 模型训练与选股。</p>
          <div className="roadmap-list">
            <span>初始化数据库</span>
            <span>导入 A 股 CSV</span>
            <span>构建股票池</span>
            <span>检查基础因子</span>
          </div>
        </div>
      </section>
    </div>
  );
}
