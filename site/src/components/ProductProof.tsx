const features = [
  ["Live dependency map", "Explore imports, importers, modules, and file neighborhoods."],
  ["Breakage warnings", "See missing symbols, broken imports, orphans, and dependency cycles after save."],
  ["Graph-aware context", "Rank the smallest useful file set for any coding task."],
  ["README generation", "Create a graph-derived draft with bounded Mermaid architecture."],
];

export function ProductProof() {
  return (
    <section className="proof shell" id="features">
      <div className="section-heading proof-heading">
        <h2>Built for the five minutes before the demo.</h2>
        <p>
          Understand the repo, catch the break, package the right context, and
          generate submission-ready architecture without uploading source code.
        </p>
      </div>
      <div className="proof-layout">
        <div className="feature-list">
          {features.map(([title, body], index) => (
            <article key={title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <h3>{title}</h3>
                <p>{body}</p>
              </div>
            </article>
          ))}
        </div>
        <div className="proof-media">
          <div className="warning-panel">
            <span>Warning console</span>
            <strong>Missing symbol</strong>
            <p>
              auth_routes.py imports <code>validate_session</code>, but the
              symbol is not exported by session_service.py.
            </p>
          </div>
          <div className="mermaid-panel">
            <span>README.generated.md</span>
            <pre>{`graph TD
  routes --> services
  routes --> errors
  tests --> routes`}</pre>
          </div>
        </div>
      </div>
      <p className="privacy-line">
        <span aria-hidden="true">●</span> Local-first. Source contents stay on
        your machine.
      </p>
    </section>
  );
}
