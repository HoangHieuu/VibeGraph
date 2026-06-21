import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { FileInspector } from "./FileInspector";
import type { GraphLink, GraphNode } from "../types/graph";

afterEach(cleanup);

function node(overrides: Partial<GraphNode> = {}): GraphNode {
  return {
    id: "src/app.ts",
    path: "src/app.ts",
    label: "app.ts",
    type: "file",
    language: "typescript",
    group: "frontend",
    loc: 12,
    sizeBytes: 200,
    lastModified: "",
    exports: ["render"],
    inDegree: 1,
    outDegree: 1,
    riskScore: 0.4,
    isEntrypoint: false,
    isOrphan: false,
    hasWarning: false,
    inCycle: false,
    cycleId: null,
    ...overrides,
  };
}

const links: GraphLink[] = [
  {
    source: "src/app.ts",
    target: "src/lib/api.ts",
    type: "imports",
    symbols: [],
    status: "healthy",
  },
  {
    source: "tests/app.test.ts",
    target: "src/app.ts",
    type: "test_targets",
    symbols: [],
    status: "healthy",
  },
];

describe("FileInspector", () => {
  it("navigates when a navigable import path is clicked", () => {
    const onSelectPath = vi.fn();
    render(
      <FileInspector
        links={links}
        navigableIds={new Set(["src/lib/api.ts", "tests/app.test.ts"])}
        node={node()}
        onContextAction={() => {}}
        onSelectPath={onSelectPath}
        warnings={[]}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: /src\/lib\/api.ts/ }));
    expect(onSelectPath).toHaveBeenCalledWith("src/lib/api.ts");
  });

  it("expands a truncated relationship list", () => {
    const manyLinks: GraphLink[] = Array.from({ length: 9 }, (_, index) => ({
      source: "src/app.ts",
      target: `src/dep-${index}.ts`,
      type: "imports",
      symbols: [],
      status: "healthy",
    }));

    render(
      <FileInspector
        links={manyLinks}
        node={node()}
        onContextAction={() => {}}
        warnings={[]}
      />,
    );

    const toggle = screen.getByRole("button", { name: "+ 2 more" });
    fireEvent.click(toggle);
    expect(
      screen.getByRole("button", { name: "Show fewer" }),
    ).toBeInTheDocument();
  });
});
