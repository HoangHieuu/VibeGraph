import type {
  GeneratedReadme,
  ReadmeMode,
  ReadmeModule,
} from "../types/readme";

export async function generateReadme(
  description: string,
): Promise<GeneratedReadme> {
  const response = await fetch("/api/readme", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ description }),
  });
  if (!response.ok) {
    throw new Error(`README generation failed with status ${response.status}.`);
  }
  return parseGeneratedReadme(await response.json());
}

export function parseGeneratedReadme(value: unknown): GeneratedReadme {
  const record = requireRecord(value, "readme");
  const mode = requireString(record.mode, "readme.mode");
  if (!["offline", "enhanced", "fallback"].includes(mode)) {
    throw new Error("readme.mode has an unsupported value.");
  }
  return {
    mode: mode as ReadmeMode,
    model:
      record.model === null ? null : requireString(record.model, "readme.model"),
    projectName: requireString(record.projectName, "readme.projectName"),
    overview: requireString(record.overview, "readme.overview"),
    architecture: requireString(record.architecture, "readme.architecture"),
    modules: requireArray(record.modules, "readme.modules").map(parseModule),
    entrypoints: parseStringArray(record.entrypoints, "readme.entrypoints"),
    keyFiles: parseStringArray(record.keyFiles, "readme.keyFiles"),
    commands: parseStringArray(record.commands, "readme.commands"),
    warnings: parseStringArray(record.warnings, "readme.warnings"),
    mermaid: requireString(record.mermaid, "readme.mermaid"),
    markdown: requireString(record.markdown, "readme.markdown"),
    providerMessage: requireString(
      record.providerMessage,
      "readme.providerMessage",
    ),
    artifactPath: requireString(record.artifactPath, "readme.artifactPath"),
  };
}

function parseModule(value: unknown, index: number): ReadmeModule {
  const record = requireRecord(value, `readme.modules[${index}]`);
  return {
    name: requireString(record.name, `readme.modules[${index}].name`),
    summary: requireString(record.summary, `readme.modules[${index}].summary`),
    files: parseStringArray(
      record.files,
      `readme.modules[${index}].files`,
    ),
    entrypoints: parseStringArray(
      record.entrypoints,
      `readme.modules[${index}].entrypoints`,
    ),
  };
}

function parseStringArray(value: unknown, name: string): string[] {
  return requireArray(value, name).map((item, index) =>
    requireString(item, `${name}[${index}]`),
  );
}

function requireRecord(
  value: unknown,
  name: string,
): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`${name} must be an object.`);
  }
  return value as Record<string, unknown>;
}

function requireArray(value: unknown, name: string): unknown[] {
  if (!Array.isArray(value)) {
    throw new Error(`${name} must be an array.`);
  }
  return value;
}

function requireString(value: unknown, name: string): string {
  if (typeof value !== "string") {
    throw new Error(`${name} must be a string.`);
  }
  return value;
}
