import { cp, mkdir, rm } from "node:fs/promises";

const cliRoot = new URL("../", import.meta.url);
const repositoryRoot = new URL("../", cliRoot);
const runtimeRoot = new URL("dist/runtime/", cliRoot);
const backendTarget = new URL("backend/", runtimeRoot);
const frontendTarget = new URL("frontend/", runtimeRoot);

await rm(runtimeRoot, { force: true, recursive: true });
await mkdir(backendTarget, { recursive: true });

await cp(
  new URL("backend/app/", repositoryRoot),
  new URL("app/", backendTarget),
  {
    recursive: true,
    filter(source) {
      return !source.includes("__pycache__") && !source.endsWith(".pyc");
    },
  },
);
await cp(
  new URL("backend/pyproject.toml", repositoryRoot),
  new URL("pyproject.toml", backendTarget),
);
await cp(new URL("frontend/dist/", repositoryRoot), frontendTarget, {
  recursive: true,
});
