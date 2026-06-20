import type { GraphNode } from "../types/graph";
import { FileIcon, RefreshIcon, SearchIcon } from "./icons";

interface TopBarProps {
  projectName: string;
  query: string;
  results: GraphNode[];
  rescanning: boolean;
  onQueryChange: (query: string) => void;
  onGenerateReadme: () => void;
  onSelectResult: (node: GraphNode) => void;
  onRescan: () => void;
}

export function TopBar({
  projectName,
  query,
  results,
  rescanning,
  onQueryChange,
  onGenerateReadme,
  onSelectResult,
  onRescan,
}: TopBarProps) {
  return (
    <header className="top-bar">
      <div className="brand-block">
        <strong>VibeGraph</strong>
        <span>{projectName}</span>
      </div>
      <div className="search-wrap">
        <SearchIcon />
        <input
          aria-label="Search files"
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Search files…"
          value={query}
        />
        {results.length > 0 ? (
          <div className="search-results" role="listbox">
            {results.map((node) => (
              <button
                key={node.id}
                onClick={() => onSelectResult(node)}
                role="option"
                type="button"
              >
                <FileIcon />
                <span>{node.path}</span>
              </button>
            ))}
          </div>
        ) : null}
      </div>
      <div className="top-actions">
        <button
          className="secondary-button"
          disabled={rescanning}
          onClick={onRescan}
          type="button"
        >
          <RefreshIcon />
          {rescanning ? "Scanning…" : "Rescan"}
        </button>
        <button
          className="primary-button"
          onClick={onGenerateReadme}
          type="button"
        >
          Generate README
        </button>
      </div>
    </header>
  );
}
