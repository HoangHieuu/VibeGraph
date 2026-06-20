import { spawn, spawnSync, type ChildProcess } from "node:child_process";
import { createHash } from "node:crypto";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { homedir, platform } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import type { LaunchConfig } from "./config.js";

interface RuntimeAssets {
  packageRoot: string;
  backendRoot: string;
  frontendRoot: string;
}

interface PythonRuntime {
  executable: string;
  cacheRoot: string;
  reused: boolean;
}

interface PythonCommand {
  executable: string;
  args: string[];
}

const PACKAGE_ROOT = findPackageRoot(fileURLToPath(import.meta.url));
const REPOSITORY_ROOT = resolve(PACKAGE_ROOT, "..");

export async function startLocalRuntime(
  config: LaunchConfig,
): Promise<ChildProcess> {
  const assets = resolveRuntimeAssets(PACKAGE_ROOT);
  if (assets) {
    return startPackagedRuntime(config, assets);
  }
  return startDevelopmentRuntime(config);
}

export function findPackageRoot(modulePath: string): string {
  let candidate = dirname(modulePath);
  for (;;) {
    if (existsSync(join(candidate, "package.json"))) {
      return candidate;
    }
    const parent = dirname(candidate);
    if (parent === candidate) {
      throw new Error("Unable to locate the VibeGraph package root.");
    }
    candidate = parent;
  }
}

export function resolveRuntimeAssets(
  packageRoot: string,
): RuntimeAssets | undefined {
  const backendRoot = join(packageRoot, "dist", "runtime", "backend");
  const frontendRoot = join(packageRoot, "dist", "runtime", "frontend");
  if (
    !existsSync(join(backendRoot, "app", "main.py")) ||
    !existsSync(join(backendRoot, "pyproject.toml")) ||
    !existsSync(join(frontendRoot, "index.html"))
  ) {
    return undefined;
  }
  return { packageRoot, backendRoot, frontendRoot };
}

export function resolveCacheRoot(
  environment: NodeJS.ProcessEnv = process.env,
  currentPlatform = platform(),
  homeDirectory = homedir(),
): string {
  if (environment.VIBEGRAPH_CACHE_DIR) {
    return resolve(environment.VIBEGRAPH_CACHE_DIR);
  }
  if (currentPlatform === "win32") {
    return join(
      environment.LOCALAPPDATA ?? join(homeDirectory, "AppData", "Local"),
      "VibeGraph",
    );
  }
  if (currentPlatform === "darwin") {
    return join(homeDirectory, "Library", "Caches", "VibeGraph");
  }
  return join(environment.XDG_CACHE_HOME ?? join(homeDirectory, ".cache"), "vibegraph");
}

export function pythonExecutableInEnvironment(
  environmentRoot: string,
  currentPlatform = platform(),
): string {
  return currentPlatform === "win32"
    ? join(environmentRoot, "Scripts", "python.exe")
    : join(environmentRoot, "bin", "python");
}

async function startPackagedRuntime(
  config: LaunchConfig,
  assets: RuntimeAssets,
): Promise<ChildProcess> {
  const dashboardUrl = `http://127.0.0.1:${config.port}`;
  const runtime = ensurePythonRuntime(assets);

  console.log("VibeGraph starting...");
  console.log(`Project: ${config.projectPath}`);
  console.log(
    runtime.reused
      ? `[INFO] Reusing Python runtime: ${runtime.cacheRoot}`
      : `[INFO] Python runtime ready: ${runtime.cacheRoot}`,
  );
  logProviderMode(config);

  const child = spawn(
    runtime.executable,
    [
      "-m",
      "uvicorn",
      "--app-dir",
      assets.backendRoot,
      "app.main:app",
      "--host",
      "127.0.0.1",
      "--port",
      String(config.port),
    ],
    {
      env: {
        ...process.env,
        VIBEGRAPH_PROJECT_ROOT: config.projectPath,
        VIBEGRAPH_FRONTEND_ROOT: assets.frontendRoot,
        ...(config.model ? { VIBEGRAPH_MODEL: config.model } : {}),
      },
      stdio: "inherit",
    },
  );

  attachProcessLifecycle(child);
  await waitForDashboard(`${dashboardUrl}/api/health`);
  console.log(`Dashboard: ${dashboardUrl}`);

  if (config.openBrowser) {
    openBrowser(dashboardUrl);
  }
  return child;
}

function startDevelopmentRuntime(config: LaunchConfig): ChildProcess {
  const dashboardUrl = `http://127.0.0.1:${config.port}`;
  const child = spawn("pnpm", ["dev"], {
    cwd: REPOSITORY_ROOT,
    env: {
      ...process.env,
      VIBEGRAPH_PROJECT_ROOT: config.projectPath,
      VITE_PORT: String(config.port),
      ...(config.model ? { VIBEGRAPH_MODEL: config.model } : {}),
    },
    stdio: "inherit",
  });

  attachProcessLifecycle(child);
  console.log("VibeGraph starting...");
  console.log(`Project: ${config.projectPath}`);
  logProviderMode(config);
  console.log(`Dashboard: ${dashboardUrl}`);

  if (config.openBrowser) {
    void waitForDashboard(dashboardUrl)
      .then(() => openBrowser(dashboardUrl))
      .catch((error: unknown) => {
        const message =
          error instanceof Error ? error.message : "Dashboard did not start.";
        console.error(`[ERROR] ${message}`);
      });
  }
  return child;
}

function ensurePythonRuntime(assets: RuntimeAssets): PythonRuntime {
  const pythonCommand = findPythonCommand();
  const manifest = readFileSync(join(assets.backendRoot, "pyproject.toml"));
  const manifestHash = createHash("sha256").update(manifest).digest("hex");
  const cacheRoot = join(resolveCacheRoot(), `python-${manifestHash.slice(0, 12)}`);
  const executable = pythonExecutableInEnvironment(cacheRoot);
  const markerPath = join(cacheRoot, ".vibegraph-runtime");

  if (
    existsSync(executable) &&
    existsSync(markerPath) &&
    readFileSync(markerPath, "utf8").trim() === manifestHash
  ) {
    return { executable, cacheRoot, reused: true };
  }

  console.log(`[INFO] Preparing isolated Python runtime in ${cacheRoot}...`);
  rmSync(cacheRoot, { force: true, recursive: true });
  mkdirSync(dirname(cacheRoot), { recursive: true });
  runSetupCommand(
    pythonCommand.executable,
    [...pythonCommand.args, "-m", "venv", cacheRoot],
    "create Python environment",
  );
  runSetupCommand(
    executable,
    [
      "-m",
      "pip",
      "install",
      "--disable-pip-version-check",
      "--no-input",
      assets.backendRoot,
    ],
    "install VibeGraph backend dependencies",
  );
  writeFileSync(markerPath, `${manifestHash}\n`, "utf8");
  return { executable, cacheRoot, reused: false };
}

function findPythonCommand(): PythonCommand {
  const candidates = process.env.VIBEGRAPH_PYTHON
    ? [{ executable: process.env.VIBEGRAPH_PYTHON, args: [] }]
    : platform() === "win32"
      ? [
          { executable: "py", args: ["-3.11"] },
          { executable: "python", args: [] },
        ]
      : [
          { executable: "python3", args: [] },
          { executable: "python", args: [] },
        ];

  for (const candidate of candidates) {
    const result = spawnSync(
      candidate.executable,
      [
        ...candidate.args,
        "-c",
        "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')",
      ],
      { encoding: "utf8" },
    );
    if (result.status !== 0) {
      continue;
    }
    const [major, minor] = result.stdout.trim().split(".").map(Number);
    if (major === 3 && (minor ?? 0) >= 11) {
      return candidate;
    }
  }

  throw new Error(
    "Python 3.11 or newer is required. Install Python or set VIBEGRAPH_PYTHON to its executable.",
  );
}

function runSetupCommand(
  command: string,
  args: readonly string[],
  action: string,
): void {
  const result = spawnSync(command, args, { stdio: "inherit" });
  if (result.error) {
    throw new Error(`Unable to ${action}: ${result.error.message}`);
  }
  if (result.status !== 0) {
    throw new Error(`Unable to ${action}; command exited with status ${result.status}.`);
  }
}

function attachProcessLifecycle(child: ChildProcess): void {
  child.once("error", (error) => {
    console.error(`[ERROR] Unable to start VibeGraph runtime: ${error.message}`);
  });
  child.once("exit", (code, signal) => {
    if (code && code !== 0) {
      process.exitCode = code;
    } else if (signal) {
      process.exitCode = 1;
    }
  });

  for (const signal of ["SIGINT", "SIGTERM"] as const) {
    process.once(signal, () => {
      if (!child.killed) {
        child.kill(signal);
      }
    });
  }
}

function logProviderMode(config: LaunchConfig): void {
  console.log(
    process.env.OPENROUTER_API_KEY
      ? `[INFO] OpenRouter enhancement enabled with ${config.model ?? process.env.VIBEGRAPH_MODEL ?? "the configured model"}.`
      : "[INFO] No LLM API key configured. Context packs use graph heuristics.",
  );
}

async function waitForDashboard(url: string): Promise<void> {
  for (let attempt = 0; attempt < 120; attempt += 1) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        return;
      }
    } catch {
      // The local runtime is still starting.
    }
    await new Promise((resolvePromise) => setTimeout(resolvePromise, 250));
  }
  throw new Error(`Dashboard was not reachable at ${url}.`);
}

function openBrowser(url: string): void {
  const command =
    platform() === "darwin"
      ? "open"
      : platform() === "win32"
        ? "cmd"
        : "xdg-open";
  const args = platform() === "win32" ? ["/c", "start", "", url] : [url];
  spawn(command, args, { detached: true, stdio: "ignore" }).unref();
}
