export function DataTable({ title, rows, columns, caption = '暂无数据' }) {
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
              <tr><td colSpan={columns.length}>{caption}</td></tr>
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
  if (typeof value === 'number') {
    return Math.abs(value) > 1000
      ? value.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
      : value.toLocaleString('zh-CN', { maximumFractionDigits: 4 });
  }
  if (typeof value === 'boolean') return value ? '是' : '否';
  return String(value);
}
