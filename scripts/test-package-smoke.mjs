import { spawn, spawnSync } from "node:child_process";
import {
  mkdtemp,
  mkdir,
  readdir,
  readFile,
  rm,
  stat,
  writeFile,
} from "node:fs/promises";
import { createServer } from "node:net";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const repositoryRoot = resolve(new URL("..", import.meta.url).pathname);
const distRoot = join(repositoryRoot, "dist");
const tarballs = await Promise.all(
  (await readdir(distRoot))
    .filter((name) => name.endsWith(".tgz"))
    .map(async (name) => ({
      name,
      modifiedAt: (await stat(join(distRoot, name))).mtimeMs,
    })),
);
const tarball = tarballs.sort(
  (left, right) => right.modifiedAt - left.modifiedAt,
)[0]?.name;
if (!tarball) {
  throw new Error("No npm tarball found. Run `pnpm package` first.");
}

const workRoot = await mkdtemp(join(tmpdir(), "vibegraph-package-smoke-"));
const installRoot = join(workRoot, "install");
const projectRoot = join(workRoot, "demo-project");
const cacheRoot = join(workRoot, "cache");
await mkdir(installRoot, { recursive: true });
await mkdir(join(projectRoot, "src"), { recursive: true });
await writeFile(
  join(installRoot, "package.json"),
  JSON.stringify({ name: "vibegraph-smoke", private: true }),
);
await writeFile(
  join(projectRoot, "src", "main.py"),
  "from helper import greet\n\nprint(greet('VibeGraph'))\n",
);
await writeFile(
  join(projectRoot, "src", "helper.py"),
  "def greet(name):\n    return f'Hello {name}'\n",
);

const installResult = spawnSync(
  "npm",
  [
    "install",
    "--no-audit",
    "--no-fund",
    join(distRoot, tarball),
  ],
  { cwd: installRoot, encoding: "utf8" },
);
if (installResult.status !== 0) {
  throw new Error(`Tarball installation failed:\n${installResult.stderr}`);
}

const port = await reservePort();
const executable =
  process.platform === "win32"
    ? join(installRoot, "node_modules", ".bin", "vibegraph.cmd")
    : join(installRoot, "node_modules", ".bin", "vibegraph");
let output = "";
const launchStartedAt = Date.now();
const child = spawn(
  executable,
  [projectRoot, "--port", String(port), "--no-open"],
  {
    cwd: installRoot,
    env: {
      ...process.env,
      VIBEGRAPH_CACHE_DIR: cacheRoot,
    },
    stdio: ["ignore", "pipe", "pipe"],
  },
);
child.stdout.on("data", (chunk) => {
  output += chunk.toString();
  process.stdout.write(chunk);
});
child.stderr.on("data", (chunk) => {
  output += chunk.toString();
  process.stderr.write(chunk);
});

try {
  const health = await waitForJson(`http://127.0.0.1:${port}/api/health`, 180_000);
  const graph = await waitForJson(`http://127.0.0.1:${port}/api/graph`, 30_000);
  const firstGraphMilliseconds = Date.now() - launchStartedAt;
  const frontend = await fetch(`http://127.0.0.1:${port}/`).then((response) =>
    response.text(),
  );
  await waitForOutput(
    () => output,
    `Dashboard: http://127.0.0.1:${port}`,
    5_000,
  );

  if (health.status !== "ok") {
    throw new Error(`Unexpected health response: ${JSON.stringify(health)}`);
  }
  if (graph.stats?.filesScanned !== 2) {
    throw new Error(`Unexpected graph response: ${JSON.stringify(graph.stats)}`);
  }
  if (!frontend.includes('<div id="root"></div>')) {
    throw new Error("The packaged frontend index was not served.");
  }
  if (!output.includes(`Dashboard: http://127.0.0.1:${port}`)) {
    throw new Error("The CLI did not print the dashboard URL.");
  }
  if (firstGraphMilliseconds > 30_000) {
    throw new Error(
      `First packaged graph took ${firstGraphMilliseconds} ms; expected at most 30000 ms.`,
    );
  }

  const artifact = JSON.parse(
    await readFile(join(projectRoot, ".vibegraph", "graph.json"), "utf8"),
  );
  if (artifact.stats?.filesScanned !== 2) {
    throw new Error("The packaged runtime did not write the graph artifact.");
  }
  console.log(
    `Package smoke passed on port ${port} with ${tarball} in ${firstGraphMilliseconds} ms.`,
  );
} finally {
  child.kill("SIGTERM");
  await Promise.race([
    new Promise((resolvePromise) => child.once("exit", resolvePromise)),
    new Promise((resolvePromise) => setTimeout(resolvePromise, 5_000)),
  ]);
  await rm(workRoot, { force: true, recursive: true });
}

function reservePort() {
  return new Promise((resolvePromise, reject) => {
    const server = createServer();
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      if (!address || typeof address === "string") {
        reject(new Error("Unable to reserve a package smoke-test port."));
        return;
      }
      server.close(() => resolvePromise(address.port));
    });
  });
}

async function waitForJson(url, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        return response.json();
      }
      lastError = new Error(`${url} returned ${response.status}`);
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolvePromise) => setTimeout(resolvePromise, 250));
  }
  throw new Error(`Timed out waiting for ${url}: ${lastError}`);
}

async function waitForOutput(readOutput, expected, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (readOutput().includes(expected)) {
      return;
    }
    await new Promise((resolvePromise) => setTimeout(resolvePromise, 25));
  }
  throw new Error(`Timed out waiting for CLI output: ${expected}`);
}
