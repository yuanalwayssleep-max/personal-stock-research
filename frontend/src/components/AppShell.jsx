import {
  BarChart3,
  BrainCircuit,
  ClipboardCheck,
  Database,
  Gauge,
  Layers3,
  LineChart,
  ListChecks,
  NotebookPen,
  PieChart,
  Settings,
} from 'lucide-react';

export const NAV_ITEMS = [
  { id: 'overview', label: '总览', stage: 'MVP-1', icon: Gauge },
  { id: 'data-center', label: '数据中心', stage: 'MVP-1', icon: Database },
  { id: 'universe', label: '股票池', stage: 'MVP-1', icon: ListChecks },
  { id: 'factors', label: '因子研究', stage: 'MVP-1', icon: Layers3 },
  { id: 'models', label: '模型预测', stage: 'MVP-2', icon: BrainCircuit },
  { id: 'selection', label: '选股策略', stage: 'MVP-2', icon: BarChart3 },
  { id: 'portfolio', label: '组合管理', stage: 'MVP-3', icon: PieChart },
  { id: 'trade-plans', label: '交易计划', stage: 'MVP-3', icon: ClipboardCheck },
  { id: 'trade-records', label: '交易记录', stage: 'MVP-4', icon: NotebookPen },
  { id: 'reviews', label: '复盘分析', stage: 'MVP-4', icon: LineChart },
  { id: 'settings', label: '系统设置', stage: 'Core', icon: Settings },
];

export function AppShell({ activePage, onNavigate, health, notice, children }) {
  return (
    <div className="app-frame">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">A</div>
          <div>
            <p className="eyebrow">A-Share Quant</p>
            <h1>个人量化投研</h1>
          </div>
        </div>
        <nav className="nav-list" aria-label="一级目录">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = item.id === activePage;
            return (
              <button key={item.id} className={`nav-item ${active ? 'active' : ''}`} onClick={() => onNavigate(item.id)}>
                <Icon size={18} />
                <span>{item.label}</span>
                <em>{item.stage}</em>
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="content-shell">
        <header className="topbar">
          <div>
            <p className="eyebrow">Research Operating System</p>
            <h2>{NAV_ITEMS.find((item) => item.id === activePage)?.label ?? '总览'}</h2>
          </div>
          <div className={`status-pill ${health === 'ok' ? 'ok' : 'bad'}`}>API {health}</div>
        </header>
        {notice && <div className="notice">{notice}</div>}
        {children}
      </main>
    </div>
  );
}
