import { describe, expect, it } from "vitest";

import type { GraphNode } from "../types/graph";
import { nodeRadius, shouldShowNodeLabel } from "./visuals";

function node(overrides: Partial<GraphNode> = {}): GraphNode {
  return {
    id: "src/example.ts",
    path: "src/example.ts",
    label: "example.ts",
    type: "file",
    language: "typescript",
    group: "frontend",
    loc: 10,
    sizeBytes: 100,
    lastModified: "",
    exports: [],
    inDegree: 0,
    outDegree: 0,
    riskScore: 0,
    isEntrypoint: false,
    isOrphan: false,
    hasWarning: false,
    ...overrides,
  };
}

describe("graph visual rules", () => {
  it("scales node radius by graph degree instead of filename length", () => {
    const shortHub = node({
      label: "a.ts",
      inDegree: 12,
      outDegree: 8,
    });
    const longLeaf = node({
      label: "an-extremely-long-generated-filename.ts",
      inDegree: 1,
    });

    expect(nodeRadius(shortHub)).toBeGreaterThan(nodeRadius(longLeaf));
  });

  it("clamps isolated and highly connected node sizes", () => {
    expect(nodeRadius(node())).toBeCloseTo(2.8);
    expect(nodeRadius(node({ inDegree: 10_000 }))).toBe(8.5);
  });

  it("hides ordinary labels at overview zoom while retaining emphasized labels", () => {
    expect(shouldShowNodeLabel(1, false)).toBe(false);
    expect(shouldShowNodeLabel(1, true)).toBe(true);
    expect(shouldShowNodeLabel(2.2, false)).toBe(true);
  });
});
