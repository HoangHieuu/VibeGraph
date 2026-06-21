import { useDeferredValue, useMemo, useState } from "react";

import { FileInspector } from "./components/FileInspector";
import { ContextPanel } from "./components/ContextPanel";
import { GraphCanvas } from "./components/GraphCanvas";
import { GraphControls } from "./components/GraphControls";
import { ReadmePanel } from "./components/ReadmePanel";
import { TopBar } from "./components/TopBar";
import { WarningConsole } from "./components/WarningConsole";
import {
  filterGraph,
  graphForMode,
  matchedVisibleIds,
  searchNodes,
} from "./graph/transforms";
import { useWorkspace } from "./hooks/useWorkspace";
import type {
  GraphFilters,
  GraphMode,
  GraphNode,
} from "./types/graph";

const DEFAULT_FILTERS: GraphFilters = {
  tests: true,
  config: true,
  orphans: true,
};

export function App() {
  const workspace = useWorkspace();
  const [mode, setMode] = useState<GraphMode>("files");
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [focusRequest, setFocusRequest] = useState(0);
  const [notice, setNotice] = useState<string | null>(null);
  const [contextOpen, setContextOpen] = useState(false);
  const [contextTask, setContextTask] = useState("");
  const [readmeOpen, setReadmeOpen] = useState(false);

  const filteredGraph = useMemo(
    () =>
      workspace.graph
        ? filterGraph(workspace.graph, filters)
        : { nodes: [], links: [] },
    [filters, workspace.graph],
  );
  const visibleGraph = useMemo(
    () => graphForMode(filteredGraph, mode),
    [filteredGraph, mode],
  );
  const searchResults = useMemo(
    () => searchNodes(filteredGraph.nodes, deferredQuery),
    [deferredQuery, filteredGraph.nodes],
  );
  const matchedIds = useMemo(
    () => matchedVisibleIds(visibleGraph.nodes, deferredQuery),
    [deferredQuery, visibleGraph.nodes],
  );
  const nodeIds = useMemo(
    () => new Set(workspace.graph?.nodes.map((node) => node.id) ?? []),
    [workspace.graph?.nodes],
  );
  const selectedNode =
    workspace.graph?.nodes.find((node) => node.id === selectedId) ?? null;

  function selectNode(node: GraphNode) {
    const original =
      workspace.graph?.nodes.find((candidate) => candidate.id === node.id) ?? node;
    setSelectedId(original.id);
    setFocusRequest((current) => current + 1);
    setQuery("");
  }

  if (workspace.loading) {
    return <main className="loading-screen">Building local code graph…</main>;
  }

  if (!workspace.graph || !workspace.project) {
    return (
      <main className="loading-screen error-screen">
        <h1>Unable to load VibeGraph</h1>
        <p>{workspace.error}</p>
      </main>
    );
  }

  return (
    <main className="workspace-shell">
      <TopBar
        connected={workspace.connected}
        onQueryChange={setQuery}
        onGenerateReadme={() => {
          setContextOpen(false);
          setReadmeOpen(true);
        }}
        onRescan={() => void workspace.rescan()}
        onSelectResult={(node) => {
          setMode("files");
          selectNode(node);
        }}
        projectName={workspace.project.projectName}
        query={query}
        rescanning={workspace.rescanning}
        results={searchResults}
      />
      <div className="workspace-grid">
        <GraphControls
          filters={filters}
          mode={mode}
          onFiltersChange={setFilters}
          onModeChange={(nextMode) => {
            setMode(nextMode);
            setSelectedId(null);
          }}
          onReset={() => {
            setFilters(DEFAULT_FILTERS);
            setMode("files");
          }}
          stats={workspace.graph.stats}
        />
        <section className="graph-stage" aria-label="Codebase graph">
          <GraphCanvas
            focusRequest={focusRequest}
            links={visibleGraph.links}
            matchedIds={matchedIds}
            nodes={visibleGraph.nodes}
            onSelectNode={selectNode}
            selectedId={selectedId}
          />
          <WarningConsole
            onSelectWarning={(warning) => {
              const node = workspace.graph?.nodes.find(
                (candidate) =>
                  candidate.id === warning.source ||
                  candidate.id === warning.target,
              );
              if (node) {
                setMode("files");
                selectNode(node);
              }
            }}
            warnings={workspace.warnings}
          />
          <button
            className="context-launcher"
            onClick={() => setContextOpen(true)}
            type="button"
          >
            Context pack
          </button>
          <ContextPanel
            initialTask={contextTask}
            onClose={() => setContextOpen(false)}
            onNotice={setNotice}
            open={contextOpen}
          />
          <ReadmePanel
            onClose={() => setReadmeOpen(false)}
            onNotice={setNotice}
            open={readmeOpen}
          />
          {notice ? (
            <button
              className="notice"
              onClick={() => setNotice(null)}
              type="button"
            >
              {notice}
            </button>
          ) : null}
        </section>
        <FileInspector
          links={workspace.graph.links}
          navigableIds={nodeIds}
          node={selectedNode}
          onSelectPath={(path) => {
            const target = workspace.graph?.nodes.find(
              (candidate) => candidate.id === path,
            );
            if (target) {
              setMode("files");
              selectNode(target);
            }
          }}
          onContextAction={() =>
            {
              setContextTask(
                selectedNode
                  ? `Work on ${selectedNode.path}`
                  : "",
              );
              setReadmeOpen(false);
              setContextOpen(true);
            }
          }
          warnings={workspace.warnings}
        />
      </div>
    </main>
  );
}
