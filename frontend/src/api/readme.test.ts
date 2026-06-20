import { describe, expect, it } from "vitest";

import { parseGeneratedReadme } from "./readme";

describe("README API parser", () => {
  it("parses an enhanced generated README", () => {
    const readme = parseGeneratedReadme({
      mode: "enhanced",
      model: "deepseek/deepseek-v4-flash",
      projectName: "VibeGraph",
      overview: "Overview",
      architecture: "Architecture",
      modules: [
        {
          name: "frontend",
          summary: "UI module",
          files: ["frontend/src/App.tsx"],
          entrypoints: ["frontend/src/main.tsx"],
        },
      ],
      entrypoints: ["frontend/src/main.tsx"],
      keyFiles: ["frontend/src/App.tsx"],
      commands: ["pnpm dev"],
      warnings: [],
      mermaid: "flowchart TD",
      markdown: "# VibeGraph",
      providerMessage: "Enhanced from graph metadata.",
      artifactPath: ".vibegraph/README.generated.md",
    });

    expect(readme.model).toBe("deepseek/deepseek-v4-flash");
    expect(readme.modules[0]?.name).toBe("frontend");
    expect(readme.commands).toEqual(["pnpm dev"]);
  });

  it("rejects malformed module files", () => {
    expect(() =>
      parseGeneratedReadme({
        mode: "offline",
        model: null,
        projectName: "VibeGraph",
        overview: "Overview",
        architecture: "Architecture",
        modules: [{ name: "frontend", summary: "UI", files: "bad" }],
      }),
    ).toThrow("readme.modules[0].files must be an array");
  });
});
