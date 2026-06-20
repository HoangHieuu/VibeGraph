import { endpointId } from "../graph/transforms";
import type { GraphLink, GraphNode, GraphWarning } from "../types/graph";
import { FileIcon } from "./icons";

interface FileInspectorProps {
  node: GraphNode | null;
  links: GraphLink[];
  warnings: GraphWarning[];
  onContextAction: () => void;
}

function PathList({ paths }: { paths: string[] }) {
  if (paths.length === 0) return <p className="empty-copy">None</p>;
  return (
    <ul className="path-list">
      {paths.slice(0, 7).map((path, index) => (
        <li key={`${path}-${index}`}>
          <FileIcon />
          <span>{path}</span>
        </li>
      ))}
      {paths.length > 7 ? <li>+ {paths.length - 7} more</li> : null}
    </ul>
  );
}

export function FileInspector({
  node,
  links,
  warnings,
  onContextAction,
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
        <PathList paths={imports} />
      </section>
      <section>
        <h4>Imported by ({importedBy.length})</h4>
        <PathList paths={importedBy} />
      </section>
      <section>
        <h4>Exports ({node.exports.length})</h4>
        <PathList paths={node.exports} />
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
