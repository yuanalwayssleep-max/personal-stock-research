export function SettingsPage() {
  return (
    <div className="page-stack">
      <section className="panel settings-panel">
        <h2>系统设置</h2>
        <p>当前先展示开发环境配置，后续支持数据源、策略参数、模型参数和组合约束配置。</p>
        <div className="key-value"><span>前端地址</span><strong>http://localhost:5174</strong></div>
        <div className="key-value"><span>后端 API</span><strong>http://localhost:8010</strong></div>
        <div className="key-value"><span>API 文档</span><strong>http://localhost:8010/docs</strong></div>
      </section>
    </div>
  );
}
