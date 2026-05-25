const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const contentType = response.headers.get('content-type') ?? '';
  const body = contentType.includes('application/json') ? await response.json() : await response.text();
  if (!response.ok) {
    const message = typeof body === 'object' && body.detail ? body.detail : '请求失败';
    throw new Error(message);
  }
  return body;
}

export function getHealth() {
  return request('/health');
}

export function initDatabase() {
  return request('/api/database/init', { method: 'POST' });
}

export function getStatus() {
  return request('/api/data/status');
}

export function importCsv({ stocks, dailyBars, valuation }) {
  const formData = new FormData();
  if (stocks) formData.append('stocks', stocks);
  if (dailyBars) formData.append('daily_bars', dailyBars);
  if (valuation) formData.append('valuation', valuation);
  return request('/api/data/import-csv', { method: 'POST', body: formData });
}

export function buildMvp1(payload) {
  return request('/api/mvp1/build', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function getUniverse({ tradeDate, membersOnly = false, limit = 100 } = {}) {
  const params = new URLSearchParams({ limit: String(limit), members_only: String(membersOnly) });
  if (tradeDate) params.set('trade_date', tradeDate);
  return request(`/api/universe?${params.toString()}`);
}

export function getFactors({ tradeDate, limit = 100 } = {}) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (tradeDate) params.set('trade_date', tradeDate);
  return request(`/api/factors?${params.toString()}`);
}
