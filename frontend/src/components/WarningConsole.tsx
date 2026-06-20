import type { GraphWarning } from "../types/graph";

export function WarningConsole({ warnings }: { warnings: GraphWarning[] }) {
  const latest = warnings[0];
  return (
    <footer className="warning-console">
      <strong>Warnings</strong>
      {latest ? (
        <div className="warning-summary">
          <span className="warning-count">
            {warnings.length} warning{warnings.length === 1 ? "" : "s"}
          </span>
          <span className="warning-message" title={latest.message}>
            {latest.message}
          </span>
        </div>
      ) : (
        <span className="healthy-copy">No active dependency warnings</span>
      )}
    </footer>
  );
}
