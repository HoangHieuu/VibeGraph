import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  findPackageRoot,
  pythonExecutableInEnvironment,
  resolveCacheRoot,
  resolveRuntimeAssets,
} from "./runtime.js";

describe("packaged runtime paths", () => {
  it("finds a package root from compiled or source files", () => {
    const root = mkdtempSync(join(tmpdir(), "vibegraph-package-"));
    const source = join(root, "dist", "runtime.js");
    mkdirSync(join(root, "dist"));
    writeFileSync(join(root, "package.json"), "{}");
    writeFileSync(source, "");

    expect(findPackageRoot(source)).toBe(root);
  });

  it("only resolves complete bundled runtime assets", () => {
    const root = mkdtempSync(join(tmpdir(), "vibegraph-assets-"));
    expect(resolveRuntimeAssets(root)).toBeUndefined();

    mkdirSync(join(root, "dist", "runtime", "backend", "app"), { recursive: true });
    mkdirSync(join(root, "dist", "runtime", "frontend"), { recursive: true });
    writeFileSync(join(root, "dist", "runtime", "backend", "app", "main.py"), "");
    writeFileSync(join(root, "dist", "runtime", "backend", "pyproject.toml"), "");
    writeFileSync(join(root, "dist", "runtime", "frontend", "index.html"), "");

    expect(resolveRuntimeAssets(root)).toEqual({
      packageRoot: root,
      backendRoot: join(root, "dist", "runtime", "backend"),
      frontendRoot: join(root, "dist", "runtime", "frontend"),
    });
  });

  it("uses explicit and platform-default cache locations", () => {
    expect(
      resolveCacheRoot({ VIBEGRAPH_CACHE_DIR: "/tmp/custom-cache" }, "linux", "/home/user"),
    ).toBe(resolve("/tmp/custom-cache"));
    expect(resolveCacheRoot({}, "darwin", "/Users/dev")).toBe(
      join("/Users/dev", "Library", "Caches", "VibeGraph"),
    );
    expect(resolveCacheRoot({}, "linux", "/home/dev")).toBe(
      join("/home/dev", ".cache", "vibegraph"),
    );
  });

  it("uses platform-specific virtual environment executables", () => {
    expect(pythonExecutableInEnvironment("/cache/runtime", "linux")).toBe(
      join("/cache/runtime", "bin", "python"),
    );
    expect(pythonExecutableInEnvironment("C:\\cache\\runtime", "win32")).toBe(
      join("C:\\cache\\runtime", "Scripts", "python.exe"),
    );
  });
});
