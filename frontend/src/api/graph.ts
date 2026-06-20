import type {
  GraphDocument,
  GraphLink,
  GraphNode,
  GraphWarning,
  ProjectSummary,
  WorkspaceEvent,
} from "../types/graph";

async function requestJson<T>(
  path: string,
  parse: (value: unknown) => T,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      Accept: "application/json",
      ...init?.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`${path} failed with status ${response.status}.`);
  }
  return parse(await response.json());
}

export async function loadWorkspace(): Promise<{
  project: ProjectSummary;
  graph: GraphDocument;
  warnings: GraphWarning[];
}> {
  const [project, graph, warnings] = await Promise.all([
    requestJson("/api/project", parseProjectSummary),
    requestJson("/api/graph", parseGraphDocument),
    requestJson("/api/warnings", parseWarnings),
  ]);
  return { project, graph, warnings };
}

export function rescanGraph(): Promise<GraphDocument> {
  return requestJson("/api/rescan", parseGraphDocument, { method: "POST" });
}

export function subscribeWorkspaceEvents(
  onEvent: (event: WorkspaceEvent) => void,
): () => void {
  let active = true;
  let socket: WebSocket | null = null;
  let reconnectTimer: number | null = null;

  const connect = () => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    socket = new WebSocket(`${protocol}//${window.location.host}/ws/events`);
    socket.addEventListener("message", (message) => {
      try {
        onEvent(parseWorkspaceEvent(JSON.parse(String(message.data))));
      } catch {
        // Invalid boundary data is ignored; the last valid graph remains usable.
      }
    });
    socket.addEventListener("close", () => {
      if (active) {
        reconnectTimer = window.setTimeout(connect, 1000);
      }
    });
  };
  connect();

  return () => {
    active = false;
    if (reconnectTimer !== null) window.clearTimeout(reconnectTimer);
    socket?.close();
  };
}

export function parseWorkspaceEvent(value: unknown): WorkspaceEvent {
  const record = requireRecord(value, "event");
  const type = requireString(record.type, "event.type");
  if (type === "graph_updated") {
    return {
      type,
      changedPaths: requireStringArray(
        record.changedPaths,
        "event.changedPaths",
      ),
      graph: parseGraphDocument(record.graph),
      warnings: parseWarnings(record.warnings),
    };
  }
  if (type === "warning_created") {
    return {
      type,
      warning: parseWarning(record.warning, "event.warning"),
    };
  }
  throw new Error("event.type has an unsupported value.");
}

export function parseGraphDocument(value: unknown): GraphDocument {
  const record = requireRecord(value, "graph");
  return {
    projectRoot: requireString(record.projectRoot, "graph.projectRoot"),
    generatedAt: requireString(record.generatedAt, "graph.generatedAt"),
    nodes: requireArray(record.nodes, "graph.nodes").map(parseGraphNode),
    links: requireArray(record.links, "graph.links").map(parseGraphLink),
    stats: parseStats(record.stats),
  };
}

export function parseProjectSummary(value: unknown): ProjectSummary {
  const record = requireRecord(value, "project");
  return {
    projectRoot: requireString(record.projectRoot, "project.projectRoot"),
    projectName: requireString(record.projectName, "project.projectName"),
    stats: parseStats(record.stats),
  };
}

export function parseWarnings(value: unknown): GraphWarning[] {
  return requireArray(value, "warnings").map((warning, index) =>
    parseWarning(warning, `warnings[${index}]`),
  );
}

function parseWarning(value: unknown, name: string): GraphWarning {
  const record = requireRecord(value, name);
  const type = requireString(record.type, `${name}.type`);
  const level = requireString(record.level, `${name}.level`);
  if (
    ![
      "BROKEN_IMPORT",
      "DELETED_IMPORTED_FILE",
      "MISSING_EXPORTED_SYMBOL",
      "NEW_ORPHAN_FILE",
      "NEW_CIRCULAR_DEPENDENCY",
    ].includes(type)
  ) {
    throw new Error(`${name}.type has an unsupported value.`);
  }
  if (level !== "warn") {
    throw new Error(`${name}.level has an unsupported value.`);
  }
  return {
    type: type as GraphWarning["type"],
    level,
    source: requireString(record.source, `${name}.source`),
    target: requireString(record.target, `${name}.target`),
    symbol:
      record.symbol === null
        ? null
        : requireString(record.symbol, `${name}.symbol`),
    timestamp: requireString(record.timestamp, `${name}.timestamp`),
    message: requireString(record.message, `${name}.message`),
  };
}

function parseGraphNode(value: unknown, index: number): GraphNode {
  const name = `graph.nodes[${index}]`;
  const record = requireRecord(value, name);
  const type = requireString(record.type, `${name}.type`);
  if (
    !["file", "folder", "entrypoint", "test", "config", "unknown"].includes(
      type,
    )
  ) {
    throw new Error(`${name}.type has an unsupported value.`);
  }
  return {
    id: requireString(record.id, `${name}.id`),
    path: requireString(record.path, `${name}.path`),
    label: requireString(record.label, `${name}.label`),
    type: type as GraphNode["type"],
    language: requireString(record.language, `${name}.language`),
    group: requireString(record.group, `${name}.group`),
    loc: requireNumber(record.loc, `${name}.loc`),
    sizeBytes: requireNumber(record.sizeBytes, `${name}.sizeBytes`),
    lastModified: requireString(record.lastModified, `${name}.lastModified`),
    exports: requireStringArray(record.exports, `${name}.exports`),
    inDegree: requireNumber(record.inDegree, `${name}.inDegree`),
    outDegree: requireNumber(record.outDegree, `${name}.outDegree`),
    riskScore: requireNumber(record.riskScore, `${name}.riskScore`),
    isEntrypoint: requireBoolean(
      record.isEntrypoint,
      `${name}.isEntrypoint`,
    ),
    isOrphan: requireBoolean(record.isOrphan, `${name}.isOrphan`),
    hasWarning: requireBoolean(record.hasWarning, `${name}.hasWarning`),
  };
}

function parseGraphLink(value: unknown, index: number): GraphLink {
  const name = `graph.links[${index}]`;
  const record = requireRecord(value, name);
  return {
    source: requireString(record.source, `${name}.source`),
    target: requireString(record.target, `${name}.target`),
    type: requireString(record.type, `${name}.type`),
    symbols: requireStringArray(record.symbols, `${name}.symbols`),
    status: requireString(record.status, `${name}.status`),
  };
}

function parseStats(value: unknown): GraphDocument["stats"] {
  const record = requireRecord(value, "stats");
  return {
    filesScanned: requireNumber(record.filesScanned, "stats.filesScanned"),
    edgesFound: requireNumber(record.edgesFound, "stats.edgesFound"),
    warnings: requireNumber(record.warnings, "stats.warnings"),
    languages: requireStringArray(record.languages, "stats.languages"),
  };
}

function requireRecord(
  value: unknown,
  name: string,
): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`${name} must be an object.`);
  }
  return value as Record<string, unknown>;
}

function requireArray(value: unknown, name: string): unknown[] {
  if (!Array.isArray(value)) {
    throw new Error(`${name} must be an array.`);
  }
  return value;
}

function requireString(value: unknown, name: string): string {
  if (typeof value !== "string") {
    throw new Error(`${name} must be a string.`);
  }
  return value;
}

function requireNumber(value: unknown, name: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`${name} must be a finite number.`);
  }
  return value;
}

function requireBoolean(value: unknown, name: string): boolean {
  if (typeof value !== "boolean") {
    throw new Error(`${name} must be a boolean.`);
  }
  return value;
}

function requireStringArray(value: unknown, name: string): string[] {
  return requireArray(value, name).map((item, index) =>
    requireString(item, `${name}[${index}]`),
  );
}
