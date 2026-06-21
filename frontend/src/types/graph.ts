export type GraphMode = "files" | "modules";

export interface GraphNode {
  id: string;
  path: string;
  label: string;
  type: "file" | "folder" | "entrypoint" | "test" | "config" | "unknown";
  language: string;
  group: string;
  loc: number;
  sizeBytes: number;
  lastModified: string;
  exports: string[];
  inDegree: number;
  outDegree: number;
  riskScore: number;
  isEntrypoint: boolean;
  isOrphan: boolean;
  hasWarning: boolean;
  inCycle: boolean;
  cycleId: number | null;
}

export interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  type: string;
  symbols: string[];
  status: string;
}

export interface GraphDocument {
  projectRoot: string;
  generatedAt: string;
  nodes: GraphNode[];
  links: GraphLink[];
  stats: {
    filesScanned: number;
    edgesFound: number;
    warnings: number;
    languages: string[];
  };
}

export interface ProjectSummary {
  projectRoot: string;
  projectName: string;
  stats: GraphDocument["stats"];
}

export interface GraphWarning {
  type:
    | "BROKEN_IMPORT"
    | "DELETED_IMPORTED_FILE"
    | "MISSING_EXPORTED_SYMBOL"
    | "NEW_ORPHAN_FILE"
    | "NEW_CIRCULAR_DEPENDENCY";
  level: "warn";
  source: string;
  target: string;
  symbol: string | null;
  timestamp: string;
  message: string;
}

export interface GraphUpdatedEvent {
  type: "graph_updated";
  changedPaths: string[];
  graph: GraphDocument;
  warnings: GraphWarning[];
}

export interface WarningCreatedEvent {
  type: "warning_created";
  warning: GraphWarning;
}

export type WorkspaceEvent = GraphUpdatedEvent | WarningCreatedEvent;

export interface GraphFilters {
  tests: boolean;
  config: boolean;
  orphans: boolean;
}
