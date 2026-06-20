import { describe, expect, it } from "vitest";

import {
  filterGraph,
  graphForMode,
  highlightFor,
  linkKey,
  neighborsFor,
  searchNodes,
} from "./transforms";
import type { GraphDocument, GraphNode } from "../types/graph";

function node(
  id: string,
  type: GraphNode["type"] = "file",
  overrides: Partial<GraphNode> = {},
): GraphNode {
  return {
    id,
    path: id,
    label: id.split("/").at(-1) ?? id,
    type,
    language: "typescript",
    group: type === "test" ? "test" : "frontend",
    loc: 10,
    sizeBytes: 100,
    lastModified: "",
    exports: [],
    inDegree: 1,
    outDegree: 1,
    riskScore: 0.5,
    isEntrypoint: false,
    isOrphan: false,
    hasWarning: false,
    ...overrides,
  };
}

const graph: GraphDocument = {
  projectRoot: "/project",
  generatedAt: "",
  nodes: [
    node("src/App.tsx"),
    node("src/lib/api.ts"),
    node("tests/App.test.tsx", "test"),
    node("vite.config.ts", "config"),
    node("src/orphan.ts", "file", { isOrphan: true }),
  ],
  links: [
    {
      source: "src/App.tsx",
      target: "src/lib/api.ts",
      type: "imports",
      symbols: [],
      status: "healthy",
    },
    {
      source: "tests/App.test.tsx",
      target: "src/App.tsx",
      type: "test_targets",
      symbols: [],
      status: "healthy",
    },
  ],
  stats: {
    filesScanned: 5,
    edgesFound: 2,
    warnings: 0,
    languages: ["typescript"],
  },
};

describe("graph transformations", () => {
  it("filters tests, config, and orphan nodes without dangling links", () => {
    const filtered = filterGraph(graph, {
      tests: false,
      config: false,
      orphans: false,
    });

    expect(filtered.nodes.map((item) => item.id)).toEqual([
      "src/App.tsx",
      "src/lib/api.ts",
    ]);
    expect(filtered.links).toHaveLength(1);
  });

  it("groups files by module and aggregates links", () => {
    const grouped = graphForMode(graph, "modules");

    expect(grouped.nodes.some((item) => item.id === "module:src")).toBe(true);
    expect(grouped.nodes.some((item) => item.id === "module:tests")).toBe(true);
    expect(grouped.links).toHaveLength(2);
  });

  it("searches labels and partial paths", () => {
    expect(searchNodes(graph.nodes, "lib/api")).toEqual([
      expect.objectContaining({ id: "src/lib/api.ts" }),
    ]);
    expect(searchNodes(graph.nodes, "app")).toHaveLength(2);
  });

  it("finds a selected node neighborhood", () => {
    expect(neighborsFor("src/App.tsx", graph.links)).toEqual(
      new Set(["src/App.tsx", "src/lib/api.ts", "tests/App.test.tsx"]),
    );
  });

  it("builds node and link highlight sets for a direct neighborhood", () => {
    const highlighted = highlightFor("src/App.tsx", graph.links);

    expect(highlighted.nodes).toEqual(
      new Set(["src/App.tsx", "src/lib/api.ts", "tests/App.test.tsx"]),
    );
    expect(highlighted.links).toEqual(
      new Set(graph.links.map((link) => linkKey(link))),
    );
  });

  it("returns empty highlight sets when hover ends", () => {
    expect(highlightFor(null, graph.links)).toEqual({
      nodes: new Set(),
      links: new Set(),
    });
  });

  it("processes a 100-node graph without dropping nodes", () => {
    const nodes = Array.from({ length: 100 }, (_, index) =>
      node(`src/module-${index}/file-${index}.ts`),
    );
    const largeGraph = {
      ...graph,
      nodes,
      links: nodes.slice(1).map((item, index) => ({
        source: nodes[index]?.id ?? "",
        target: item.id,
        type: "imports",
        symbols: [],
        status: "healthy",
      })),
    };

    expect(
      filterGraph(largeGraph, {
        tests: true,
        config: true,
        orphans: true,
      }).nodes,
    ).toHaveLength(100);
  });
});
