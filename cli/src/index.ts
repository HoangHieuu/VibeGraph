#!/usr/bin/env node

import { parseLaunchConfig } from "./config.js";

try {
  const config = parseLaunchConfig(process.argv.slice(2), process.cwd());

  console.log("VibeGraph CLI foundation");
  console.log(`Project: ${config.projectPath}`);
  console.log(`Dashboard port: ${config.port}`);
  console.log(`Open browser: ${config.openBrowser ? "yes" : "no"}`);
  console.log("Runtime orchestration will be implemented in the packaging story.");
} catch (error) {
  const message = error instanceof Error ? error.message : "Unknown CLI error.";
  console.error(`[ERROR] ${message}`);
  process.exitCode = 1;
}
