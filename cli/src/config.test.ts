import { describe, expect, it } from "vitest";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

import { parseLaunchConfig, validateProjectPath } from "./config.js";


describe("parseLaunchConfig", () => {
  it("uses the current directory and default options", () => {
    expect(parseLaunchConfig([], "/workspace")).toEqual({
      projectPath: resolve("/workspace"),
      port: 8732,
      openBrowser: true,
      model: undefined,
    });
  });

  it("parses a project path and launch options", () => {
    expect(
      parseLaunchConfig(["demo", "--port", "9000", "--no-open"], "/workspace"),
    ).toEqual({
      projectPath: resolve("/workspace", "demo"),
      port: 9000,
      openBrowser: false,
      model: undefined,
    });
  });

  it("parses an OpenRouter model override", () => {
    expect(
      parseLaunchConfig(
        [".", "--model", "deepseek/deepseek-v4-flash"],
        "/workspace",
      ).model,
    ).toBe("deepseek/deepseek-v4-flash");
  });

  it("rejects an invalid port", () => {
    expect(() => parseLaunchConfig(["--port", "invalid"], "/workspace")).toThrow(
      "--port must be followed by an integer between 1 and 65535.",
    );
  });

  it("rejects a missing model ID", () => {
    expect(() => parseLaunchConfig(["--model"], "/workspace")).toThrow(
      "--model must be followed by an OpenRouter model ID.",
    );
  });

  it("validates an existing project directory", () => {
    const directory = mkdtempSync(join(tmpdir(), "vibegraph-cli-"));
    expect(() => validateProjectPath(directory)).not.toThrow();
  });

  it("rejects a missing project path", () => {
    expect(() => validateProjectPath("/definitely/missing/vibegraph")).toThrow(
      "Project path does not exist",
    );
  });

  it("rejects a file project path", () => {
    const directory = mkdtempSync(join(tmpdir(), "vibegraph-cli-"));
    const file = join(directory, "file.txt");
    writeFileSync(file, "not a project");
    expect(() => validateProjectPath(file)).toThrow(
      "Project path is not a directory",
    );
  });
});
