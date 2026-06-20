import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ReadmePanel } from "./ReadmePanel";


afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("ReadmePanel", () => {
  it("generates, confirms the artifact, and copies Markdown", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText },
    });
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          mode: "offline",
          model: null,
          projectName: "VibeGraph",
          overview: "Overview",
          architecture: "Architecture",
          modules: [
            {
              name: "frontend",
              summary: "UI",
              files: ["frontend/src/App.tsx"],
              entrypoints: ["frontend/src/main.tsx"],
            },
          ],
          entrypoints: ["frontend/src/main.tsx"],
          keyFiles: ["frontend/src/App.tsx"],
          commands: ["pnpm dev"],
          warnings: [],
          mermaid: "flowchart TD",
          markdown: "# VibeGraph\n",
          providerMessage: "Deterministic graph analysis.",
          artifactPath: ".vibegraph/README.generated.md",
        }),
        { status: 200 },
      ),
    );
    const onNotice = vi.fn();

    render(
      <ReadmePanel
        onClose={() => undefined}
        onNotice={onNotice}
        open
      />,
    );
    fireEvent.change(screen.getByLabelText(/Project description/), {
      target: { value: "A live code graph." },
    });
    fireEvent.click(
      screen.getByRole("button", { name: "Generate README draft" }),
    );

    expect(
      await screen.findByText(".vibegraph/README.generated.md"),
    ).toBeInTheDocument();
    expect(screen.getByText("offline")).toBeInTheDocument();
    expect(screen.getByText("# VibeGraph")).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("button", { name: "Copy generated README" }),
    );
    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith("# VibeGraph\n");
    });
    expect(onNotice).toHaveBeenCalledWith("Generated README copied.");
  });
});
