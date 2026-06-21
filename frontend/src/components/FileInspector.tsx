import { useState } from "react";

import { endpointId } from "../graph/transforms";
import type { GraphLink, GraphNode, GraphWarning } from "../types/graph";
import { FileIcon } from "./icons";

interface FileInspectorProps {
  node: GraphNode | null;
  links: GraphLink[];
  warnings: GraphWarning[];
  onContextAction: () => void;
  onSelectPath?: (path: string) => void;
  navigableIds?: Set<string>;
}

const COLLAPSED_LIMIT = 7;

function PathList({
  paths,
  onSelectPath,
  navigableIds,
}: {
  paths: string[];
  onSelectPath?: (path: string) => void;
  navigableIds?: Set<string>;
}) {
  const [expanded, setExpanded] = useState(false);
  if (paths.length === 0) return <p className="empty-copy">None</p>;
  const visible = expanded ? paths : paths.slice(0, COLLAPSED_LIMIT);
  return (
    <ul className="path-list">
      {visible.map((path, index) => {
        const navigable =
          onSelectPath !== undefined &&
          (navigableIds === undefined || navigableIds.has(path));
        return (
          <li key={`${path}-${index}`}>
            {navigable ? (
              <button
                className="path-link"
                onClick={() => onSelectPath?.(path)}
                title={`Inspect ${path}`}
                type="button"
              >
                <FileIcon />
                <span>{path}</span>
              </button>
            ) : (
              <>
                <FileIcon />
                <span>{path}</span>
              </>
            )}
          </li>
        );
      })}
      {paths.length > COLLAPSED_LIMIT ? (
        <li>
          <button
            className="path-toggle"
            onClick={() => setExpanded((current) => !current)}
            type="button"
          >
            {expanded
              ? "Show fewer"
              : `+ ${paths.length - COLLAPSED_LIMIT} more`}
          </button>
        </li>
      ) : null}
    </ul>
  );
}

export function FileInspector({
  node,
  links,
  warnings,
  onContextAction,
  onSelectPath,
  navigableIds,
}: FileInspectorProps) {
  if (!node) {
    return (
      <aside className="inspector-rail inspector-empty">
        <h2>File inspector</h2>
        <p>Select a file node to inspect its architecture relationships.</p>
      </aside>
    );
  }

  const imports = links
    .filter((link) => endpointId(link.source) === node.id)
    .map((link) => endpointId(link.target));
  const importedBy = links
    .filter((link) => endpointId(link.target) === node.id)
    .map((link) => endpointId(link.source));
  const nodeWarnings = warnings.filter(
    (warning) => warning.source === node.id || warning.target === node.id,
  );

  return (
    <aside className="inspector-rail">
      <h2>File inspector</h2>
      <p className="inspector-path">{node.path}</p>
      <h3>{node.label}</h3>
      <dl className="metadata">
        <div>
          <dt>Language</dt>
          <dd>{node.language}</dd>
        </div>
        <div>
          <dt>LOC</dt>
          <dd>{node.loc}</dd>
        </div>
        <div>
          <dt>Type</dt>
          <dd>{node.type}</dd>
        </div>
      </dl>
      <section>
        <h4>Imports ({imports.length})</h4>
        <PathList
          key={`imports-${node.id}`}
          navigableIds={navigableIds}
          onSelectPath={onSelectPath}
          paths={imports}
        />
      </section>
      <section>
        <h4>Imported by ({importedBy.length})</h4>
        <PathList
          key={`importedBy-${node.id}`}
          navigableIds={navigableIds}
          onSelectPath={onSelectPath}
          paths={importedBy}
        />
      </section>
      <section>
        <h4>Exports ({node.exports.length})</h4>
        <PathList key={`exports-${node.id}`} paths={node.exports} />
      </section>
      <section>
        <h4>Warnings ({nodeWarnings.length})</h4>
        {nodeWarnings.length > 0 ? (
          <ul className="warning-list">
            {nodeWarnings.map((warning) => (
              <li key={`${warning.source}-${warning.target}`}>
                {warning.message}
              </li>
            ))}
          </ul>
        ) : (
          <p className="healthy-copy">No warnings for this file.</p>
        )}
      </section>
      <button
        className="context-button"
        onClick={onContextAction}
        type="button"
      >
        Create Context Pack
      </button>
    </aside>
  );
}
