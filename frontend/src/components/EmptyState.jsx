export function EmptyState({ title, stage, description, items = [] }) {
  return (
    <section className="panel placeholder-panel">
      <div className="stage-chip">{stage}</div>
      <h2>{title}</h2>
      <p>{description}</p>
      {items.length > 0 && (
        <div className="roadmap-list">
          {items.map((item) => <span key={item}>{item}</span>)}
        </div>
      )}
    </section>
  );
}
