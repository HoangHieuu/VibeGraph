const nodes = [
  { label: "auth_routes.py", x: 50, y: 41, focus: true },
  { label: "session_service.py", x: 68, y: 27 },
  { label: "errors.py", x: 73, y: 53 },
  { label: "test_auth_flow.py", x: 47, y: 68 },
  { label: "main.py", x: 28, y: 31 },
  { label: "activity_tool.py", x: 27, y: 58 },
];

export function ProductMockup() {
  return (
    <div className="product-frame" aria-label="VibeGraph dependency map preview">
      <div className="product-toolbar">
        <span className="product-brand">VibeGraph</span>
        <span className="search-faux">Search files</span>
        <span className="status-dot">0 warnings</span>
      </div>
      <aside className="product-sidebar">
        <strong>Graph controls</strong>
        <button className="selected" type="button">Files</button>
        <button type="button">Modules</button>
        <span>67 files</span>
        <span>242 links</span>
      </aside>
      <div className="graph-stage">
        <svg viewBox="0 0 100 82" aria-hidden="true">
          <path d="M50 41 68 27M50 41l23 12M50 41l-3 27M50 41 28 31M50 41 27 58M68 27l5 26M27 58l20 10" />
        </svg>
        {nodes.map((node) => (
          <span
            className={`graph-node${node.focus ? " graph-node-focus" : ""}`}
            key={node.label}
            style={{ left: `${node.x}%`, top: `${node.y}%` }}
          >
            <i />
            {node.label}
          </span>
        ))}
      </div>
      <aside className="product-inspector">
        <span>Selected file</span>
        <strong>auth_routes.py</strong>
        <small>Python · 24 LOC</small>
        <div>
          <b>Imports</b>
          <code>validate_session</code>
          <code>InvalidCredentialsError</code>
        </div>
      </aside>
    </div>
  );
}
