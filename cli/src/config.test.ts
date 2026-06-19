import { describe, expect, it } from "vitest";

import { parseLaunchConfig } from "./config.js";


describe("parseLaunchConfig", () => {
  it("uses the current directory and default options", () => {
    expect(parseLaunchConfig([], "/workspace")).toEqual({
      projectPath: "/workspace",
      port: 8732,
      openBrowser: true,
    });
  });

  it("parses a project path and launch options", () => {
    expect(
      parseLaunchConfig(["demo", "--port", "9000", "--no-open"], "/workspace"),
    ).toEqual({
      projectPath: "/workspace/demo",
      port: 9000,
      openBrowser: false,
    });
  });

  it("rejects an invalid port", () => {
    expect(() => parseLaunchConfig(["--port", "invalid"], "/workspace")).toThrow(
      "--port must be followed by an integer between 1 and 65535.",
    );
  });
});
