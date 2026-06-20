import { describe, expect, it } from "vitest";

import { parseContextPack } from "./context";

describe("context pack API parser", () => {
  it("parses an enhanced context pack", () => {
    const pack = parseContextPack({
      task: "Fix auth",
      mode: "enhanced",
      model: "deepseek/deepseek-v4-flash",
      recommendations: [
        {
          path: "src/auth.ts",
          reason: "Explicit task match",
          score: 120,
        },
      ],
      prompt: "Use src/auth.ts",
      mentions: "@src/auth.ts",
      estimatedTokens: 100,
      reductionPercent: 90,
      providerMessage: "Enhanced with structured graph metadata.",
      artifactPath: ".vibegraph/context.md",
    });

    expect(pack.model).toBe("deepseek/deepseek-v4-flash");
    expect(pack.recommendations[0]?.path).toBe("src/auth.ts");
  });

  it("rejects an unsupported mode", () => {
    expect(() =>
      parseContextPack({
        task: "Fix auth",
        mode: "unknown",
      }),
    ).toThrow("contextPack.mode has an unsupported value");
  });
});
