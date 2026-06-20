import type {
  GraphDocument,
  GraphFilters,
  GraphMode,
} from "../types/graph";
import { RefreshIcon } from "./icons";

interface GraphControlsProps {
  mode: GraphMode;
  filters: GraphFilters;
  stats: GraphDocument["stats"];
  onModeChange: (mode: GraphMode) => void;
  onFiltersChange: (filters: GraphFilters) => void;
  onReset: () => void;
}

export function GraphControls({
  mode,
  filters,
  stats,
  onModeChange,
  onFiltersChange,
  onReset,
}: GraphControlsProps) {
  return (
    <aside className="control-rail">
      <h2>Graph controls</h2>
      <div className="mode-control" aria-label="Graph mode">
        <button
          aria-pressed={mode === "files"}
          onClick={() => onModeChange("files")}
          type="button"
        >
          Files
        </button>
        <button
          aria-pressed={mode === "modules"}
          onClick={() => onModeChange("modules")}
          type="button"
        >
          Modules
        </button>
      </div>
      <div className="filter-list">
        {(
          [
            ["tests", "Tests"],
            ["config", "Config"],
            ["orphans", "Orphans"],
          ] as const
        ).map(([key, label]) => (
          <label key={key}>
            <input
              checked={filters[key]}
              onChange={(event) =>
                onFiltersChange({ ...filters, [key]: event.target.checked })
              }
              type="checkbox"
            />
            <span>{label}</span>
          </label>
        ))}
      </div>
      <button className="reset-button" onClick={onReset} type="button">
        <RefreshIcon />
        Reset filters
      </button>
      <dl className="stats-list">
        <div>
          <dt>Files</dt>
          <dd>{stats.filesScanned}</dd>
        </div>
        <div>
          <dt>Links</dt>
          <dd>{stats.edgesFound}</dd>
        </div>
        <div>
          <dt>Warnings</dt>
          <dd className={stats.warnings > 0 ? "warning-text" : ""}>
            {stats.warnings}
          </dd>
        </div>
      </dl>
    </aside>
  );
}
