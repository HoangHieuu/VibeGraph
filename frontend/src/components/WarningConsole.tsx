import type { GraphWarning } from "../types/graph";

interface WarningConsoleProps {
  warnings: GraphWarning[];
  onSelectWarning: (warning: GraphWarning) => void;
}

const WARNING_LABELS: Record<GraphWarning["type"], string> = {
  BROKEN_IMPORT: "Broken imports",
  DELETED_IMPORTED_FILE: "Deleted files",
  MISSING_EXPORTED_SYMBOL: "Missing exports",
  NEW_ORPHAN_FILE: "New orphans",
  NEW_CIRCULAR_DEPENDENCY: "New cycles",
};

export function WarningConsole({
  warnings,
  onSelectWarning,
}: WarningConsoleProps) {
  const latest = warnings[0];
  const grouped = new Map<GraphWarning["type"], GraphWarning[]>();
  for (const warning of warnings) {
    const items = grouped.get(warning.type);
    if (items) items.push(warning);
    else grouped.set(warning.type, [warning]);
  }
  const groups = [...grouped.entries()];

  return (
    <footer className="warning-console">
      <strong>Warnings</strong>
      {latest ? (
        <>
          <button
            className="warning-latest"
            onClick={() => onSelectWarning(latest)}
            title={latest.message}
            type="button"
          >
            {latest.message}
          </button>
          <details className="warning-details">
            <summary>
              {warnings.length} warning{warnings.length === 1 ? "" : "s"}
            </summary>
            <div className="warning-menu">
              {groups.map(([type, items]) => (
                <section key={type}>
                  <h3>
                    {WARNING_LABELS[type]} <span>{items.length}</span>
                  </h3>
                  {items.map((warning) => (
                    <button
                      key={`${warning.type}-${warning.source}-${warning.target}-${warning.symbol ?? ""}`}
                      onClick={(event) => {
                        onSelectWarning(warning);
                        event.currentTarget.closest("details")?.removeAttribute("open");
                      }}
                      type="button"
                    >
                      <strong>{warning.source}</strong>
                      <span>{warning.message}</span>
                    </button>
                  ))}
                </section>
              ))}
            </div>
          </details>
        </>
      ) : (
        <span className="healthy-copy">No active dependency warnings</span>
      )}
    </footer>
  );
}
