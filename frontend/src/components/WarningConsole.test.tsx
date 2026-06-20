import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { WarningConsole } from "./WarningConsole";


afterEach(cleanup);

describe("WarningConsole", () => {
  it("shows the latest actionable warning", () => {
    render(
      <WarningConsole
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
    expect(
      screen.getByText(
        "src/api.ts imports validateSession, but it is not exported.",
      ),
    ).toBeInTheDocument();
  });
});
