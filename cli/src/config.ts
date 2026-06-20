import { resolve } from "node:path";
import { existsSync, statSync } from "node:fs";

export interface LaunchConfig {
  projectPath: string;
  port: number;
  openBrowser: boolean;
  model: string | undefined;
}

export function parseLaunchConfig(
  args: readonly string[],
  cwd: string,
): LaunchConfig {
  let projectArgument = ".";
  let port = 8732;
  let openBrowser = true;
  let model: string | undefined;

  for (let index = 0; index < args.length; index += 1) {
    const argument = args[index];

    if (argument === "--no-open") {
      openBrowser = false;
      continue;
    }

    if (argument === "--port") {
      const value = args[index + 1];
      const parsedPort = Number(value);

      if (!value || !Number.isInteger(parsedPort) || parsedPort < 1 || parsedPort > 65535) {
        throw new Error("--port must be followed by an integer between 1 and 65535.");
      }

      port = parsedPort;
      index += 1;
      continue;
    }

    if (argument === "--model") {
      const value = args[index + 1]?.trim();
      if (!value) {
        throw new Error("--model must be followed by an OpenRouter model ID.");
      }
      model = value;
      index += 1;
      continue;
    }

    if (argument?.startsWith("--")) {
      throw new Error(`Unsupported option: ${argument}`);
    }

    projectArgument = argument ?? ".";
  }

  return {
    projectPath: resolve(cwd, projectArgument),
    port,
    openBrowser,
    model,
  };
}

export function validateProjectPath(projectPath: string): void {
  if (!existsSync(projectPath)) {
    throw new Error(`Project path does not exist: ${projectPath}`);
  }
  if (!statSync(projectPath).isDirectory()) {
    throw new Error(`Project path is not a directory: ${projectPath}`);
  }
}
