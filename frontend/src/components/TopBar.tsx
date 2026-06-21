import { useEffect, useRef, useState } from "react";

import type { GraphNode } from "../types/graph";
import { ConnectionBadge } from "./ConnectionBadge";
import { FileIcon, RefreshIcon, SearchIcon } from "./icons";

interface TopBarProps {
  projectName: string;
  query: string;
  results: GraphNode[];
  rescanning: boolean;
  connected: boolean;
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
  connected,
  onQueryChange,
  onGenerateReadme,
  onSelectResult,
  onRescan,
}: TopBarProps) {
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setActiveIndex(0);
  }, [results]);

  const hasQuery = query.trim().length > 0;
  const showResults = open && hasQuery;

  function commit(node: GraphNode | undefined) {
    if (!node) return;
    onSelectResult(node);
    setOpen(false);
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape") {
      setOpen(false);
      onQueryChange("");
      return;
    }
    if (results.length === 0) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setOpen(true);
      setActiveIndex((current) => (current + 1) % results.length);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveIndex(
        (current) => (current - 1 + results.length) % results.length,
      );
    } else if (event.key === "Enter") {
      event.preventDefault();
      commit(results[activeIndex]);
    }
  }

  return (
    <header className="top-bar">
      <div className="brand-block">
        <strong>VibeGraph</strong>
        <span>{projectName}</span>
      </div>
      <div
        className="search-wrap"
        onBlur={(event) => {
          if (!wrapRef.current?.contains(event.relatedTarget as Node)) {
            setOpen(false);
          }
        }}
        ref={wrapRef}
      >
        <SearchIcon />
        <input
          aria-activedescendant={
            showResults && results[activeIndex]
              ? `search-option-${results[activeIndex].id}`
              : undefined
          }
          aria-controls="search-results"
          aria-expanded={showResults}
          aria-label="Search files"
          onChange={(event) => {
            onQueryChange(event.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder="Search files…"
          role="combobox"
          value={query}
        />
        {showResults ? (
          results.length > 0 ? (
            <div className="search-results" id="search-results" role="listbox">
              {results.map((node, index) => (
                <button
                  aria-selected={index === activeIndex}
                  className={index === activeIndex ? "is-active" : undefined}
                  id={`search-option-${node.id}`}
                  key={node.id}
                  onClick={() => commit(node)}
                  role="option"
                  type="button"
                >
                  <FileIcon />
                  <span>{node.path}</span>
                </button>
              ))}
            </div>
          ) : (
            <div className="search-results search-empty" role="status">
              No files match “{query.trim()}”.
            </div>
          )
        ) : null}
      </div>
      <div className="top-actions">
        <ConnectionBadge connected={connected} />
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
