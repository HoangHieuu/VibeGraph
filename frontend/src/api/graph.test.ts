import { describe, expect, it } from "vitest";

import {
  parseGraphDocument,
  parseProjectSummary,
  parseWorkspaceEvent,
  parseWarnings,
} from "./graph";

const stats = {
  filesScanned: 1,
  edgesFound: 0,
  warnings: 0,
  languages: ["typescript"],
};

describe("graph API parsers", () => {
  it("parses the workspace boundary payloads", () => {
    const graph = parseGraphDocument({
      projectRoot: "/tmp/project",
      generatedAt: "2026-06-19T00:00:00Z",
      nodes: [
        {
          id: "src/main.ts",
          path: "src/main.ts",
          label: "main.ts",
          type: "entrypoint",
          language: "typescript",
          group: "frontend",
          loc: 10,
          sizeBytes: 120,
          lastModified: "2026-06-19T00:00:00Z",
          exports: ["main"],
          inDegree: 0,
          outDegree: 0,
          riskScore: 0,
          isEntrypoint: true,
          isOrphan: true,
          hasWarning: false,
        },
      ],
      links: [],
      stats,
    });

    expect(graph.nodes[0]?.id).toBe("src/main.ts");
    expect(
      parseProjectSummary({
        projectRoot: "/tmp/project",
        projectName: "project",
        stats,
      }).projectName,
    ).toBe("project");
    expect(parseWarnings([])).toEqual([]);
  });

  it("rejects malformed unknown data", () => {
    expect(() =>
      parseGraphDocument({
        projectRoot: "/tmp/project",
        generatedAt: "today",
        nodes: "not-an-array",
        links: [],
        stats,
      }),
    ).toThrow("graph.nodes must be an array");

    expect(() => parseWarnings([{ type: "BROKEN_IMPORT" }])).toThrow(
      "warnings[0].level must be a string",
    );
  });

  it("parses a graph_updated WebSocket event", () => {
    const event = parseWorkspaceEvent({
      type: "graph_updated",
      changedPaths: ["src/main.ts"],
      graph: {
        projectRoot: "/tmp/project",
        generatedAt: "2026-06-20T00:00:00Z",
        nodes: [],
        links: [],
        stats,
      },
      warnings: [
        {
          type: "MISSING_EXPORTED_SYMBOL",
          level: "warn",
          source: "src/api.ts",
          target: "src/session.ts",
          symbol: "validateSession",
          timestamp: "2026-06-20T00:00:00Z",
          message: "validateSession is not exported.",
        },
      ],
    });

    expect(event.type).toBe("graph_updated");
    if (event.type === "graph_updated") {
      expect(event.changedPaths).toEqual(["src/main.ts"]);
      expect(event.warnings[0]?.symbol).toBe("validateSession");
    }
  });
});
