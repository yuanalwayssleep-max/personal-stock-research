import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
import { buildMvp1, getFactors, getHealth, getStatus, getUniverse, importCsv, initDatabase } from './api';
import { AppShell } from './components/AppShell';
import { OverviewPage } from './pages/OverviewPage';
import { DataCenterPage } from './pages/DataCenterPage';
import { UniversePage } from './pages/UniversePage';
import { FactorResearchPage } from './pages/FactorResearchPage';
import { PlaceholderPage } from './pages/PlaceholderPage';
import { SettingsPage } from './pages/SettingsPage';

function App() {
  const [activePage, setActivePage] = useState('overview');
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
      getUniverse({ tradeDate: date, membersOnly: false, limit: 120 }).catch(() => []),
      getFactors({ tradeDate: date, limit: 120 }).catch(() => []),
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

  const common = useMemo(() => ({
    status,
    health,
    universe,
    factors,
    tradeDate,
    setTradeDate,
    files,
    setFiles,
    busy,
    runAction,
    onRefresh: refresh,
    initDatabase,
    importCsv,
    buildMvp1,
  }), [status, health, universe, factors, tradeDate, files, busy]);

  return (
    <AppShell activePage={activePage} onNavigate={setActivePage} health={health} notice={notice}>
      {renderPage(activePage, common)}
    </AppShell>
  );
}

function renderPage(activePage, props) {
  switch (activePage) {
    case 'overview':
      return <OverviewPage {...props} />;
    case 'data-center':
      return <DataCenterPage {...props} />;
    case 'universe':
      return <UniversePage {...props} />;
    case 'factors':
      return <FactorResearchPage {...props} />;
    case 'settings':
      return <SettingsPage />;
    default:
      return <PlaceholderPage pageId={activePage} />;
  }
}

createRoot(document.getElementById('root')).render(<App />);
