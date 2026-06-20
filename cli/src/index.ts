#!/usr/bin/env node

import { parseLaunchConfig, validateProjectPath } from "./config.js";
import { startLocalRuntime } from "./runtime.js";

try {
  const config = parseLaunchConfig(process.argv.slice(2), process.cwd());
  validateProjectPath(config.projectPath);
  await startLocalRuntime(config);
} catch (error) {
  const message = error instanceof Error ? error.message : "Unknown CLI error.";
  console.error(`[ERROR] ${message}`);
  process.exitCode = 1;
}
