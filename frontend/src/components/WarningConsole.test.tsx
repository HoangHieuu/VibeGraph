import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { vi } from "vitest";

import { WarningConsole } from "./WarningConsole";


afterEach(cleanup);

describe("WarningConsole", () => {
  it("shows the latest actionable warning", () => {
    const onSelectWarning = vi.fn();
    render(
      <WarningConsole
        onSelectWarning={onSelectWarning}
        warnings={[
          {
            type: "MISSING_EXPORTED_SYMBOL",
            level: "warn",
            source: "src/api.ts",
            target: "src/session.ts",
            symbol: "validateSession",
            timestamp: "2026-06-20T00:00:00Z",
            message:
              "src/api.ts imports validateSession, but it is not exported.",
          },
        ]}
      />,
    );

    expect(screen.getByText("1 warning")).toBeInTheDocument();
    const latest = screen.getByRole("button", {
      name: "src/api.ts imports validateSession, but it is not exported.",
    });
    expect(latest).toBeInTheDocument();
    fireEvent.click(
      latest,
    );
    expect(onSelectWarning).toHaveBeenCalledTimes(1);
  });

  it("groups every warning and selects one from the full list", () => {
    const onSelectWarning = vi.fn();
    render(
      <WarningConsole
        onSelectWarning={onSelectWarning}
        warnings={[
          {
            type: "BROKEN_IMPORT",
            level: "warn",
            source: "src/a.ts",
            target: "unresolved:./missing",
            symbol: null,
            timestamp: "2026-06-20T00:00:00Z",
            message: "src/a.ts could not resolve ./missing.",
          },
          {
            type: "NEW_ORPHAN_FILE",
            level: "warn",
            source: "src/orphan.ts",
            target: "src/orphan.ts",
            symbol: null,
            timestamp: "2026-06-20T00:00:01Z",
            message: "src/orphan.ts has no dependencies.",
          },
        ]}
      />,
    );

    fireEvent.click(screen.getByText("2 warnings"));
    expect(screen.getByText("Broken imports")).toBeInTheDocument();
    expect(screen.getByText("New orphans")).toBeInTheDocument();
    fireEvent.click(screen.getByText("src/orphan.ts has no dependencies."));
    expect(onSelectWarning).toHaveBeenCalledWith(
      expect.objectContaining({ source: "src/orphan.ts" }),
    );
  });
});
