import type {
  ContextPack,
  ContextPackMode,
  ContextRecommendation,
} from "../types/context";

export async function generateContextPack(task: string): Promise<ContextPack> {
  const response = await fetch("/api/context-pack", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      task,
      maxFiles: 8,
      maxDepth: 2,
      includeTests: true,
      includeConfig: false,
      includeDocs: false,
    }),
  });
  if (!response.ok) {
    throw new Error(`Context pack failed with status ${response.status}.`);
  }
  return parseContextPack(await response.json());
}

export function parseContextPack(value: unknown): ContextPack {
  const record = requireRecord(value, "contextPack");
  const mode = requireString(record.mode, "contextPack.mode");
  if (!["offline", "enhanced", "fallback"].includes(mode)) {
    throw new Error("contextPack.mode has an unsupported value.");
  }
  return {
    task: requireString(record.task, "contextPack.task"),
    mode: mode as ContextPackMode,
    model:
      record.model === null
        ? null
        : requireString(record.model, "contextPack.model"),
    recommendations: requireArray(
      record.recommendations,
      "contextPack.recommendations",
    ).map(parseRecommendation),
    prompt: requireString(record.prompt, "contextPack.prompt"),
    mentions: requireString(record.mentions, "contextPack.mentions"),
    estimatedTokens: requireNumber(
      record.estimatedTokens,
      "contextPack.estimatedTokens",
    ),
    reductionPercent: requireNumber(
      record.reductionPercent,
      "contextPack.reductionPercent",
    ),
    providerMessage: requireString(
      record.providerMessage,
      "contextPack.providerMessage",
    ),
    artifactPath: requireString(
      record.artifactPath,
      "contextPack.artifactPath",
    ),
  };
}

function parseRecommendation(
  value: unknown,
  index: number,
): ContextRecommendation {
  const record = requireRecord(value, `recommendations[${index}]`);
  return {
    path: requireString(record.path, `recommendations[${index}].path`),
    reason: requireString(record.reason, `recommendations[${index}].reason`),
    score: requireNumber(record.score, `recommendations[${index}].score`),
  };
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

function requireNumber(value: unknown, name: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`${name} must be a finite number.`);
  }
  return value;
}
