import { useState } from "react";

import { generateReadme } from "../api/readme";
import type { GeneratedReadme } from "../types/readme";

interface ReadmePanelProps {
  open: boolean;
  onClose: () => void;
  onNotice: (message: string) => void;
}

export function ReadmePanel({
  open,
  onClose,
  onNotice,
}: ReadmePanelProps) {
  const [description, setDescription] = useState("");
  const [readme, setReadme] = useState<GeneratedReadme | null>(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  async function generate() {
    setGenerating(true);
    setError(null);
    try {
      setReadme(await generateReadme(description.trim()));
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Unable to generate README.",
      );
    } finally {
      setGenerating(false);
    }
  }

  async function copyMarkdown() {
    if (!readme) return;
    try {
      await navigator.clipboard.writeText(readme.markdown);
      onNotice("Generated README copied.");
    } catch {
      onNotice("Unable to copy generated README.");
    }
  }

  return (
    <aside
      aria-label="README generator"
      aria-modal="true"
      className="readme-panel"
      role="dialog"
    >
      <header>
        <div>
          <span className="context-eyebrow">Graph-derived documentation</span>
          <h2>Generate README</h2>
        </div>
        <button aria-label="Close README generator" onClick={onClose} type="button">
          ×
        </button>
      </header>

      <label className="context-task">
        Project description <span>(optional)</span>
        <textarea
          maxLength={2000}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="What should judges understand about this project?"
          rows={3}
          value={description}
        />
      </label>
      <button
        className="context-generate"
        disabled={generating}
        onClick={() => void generate()}
        type="button"
      >
        {generating ? "Analyzing graph…" : "Generate README draft"}
      </button>
      {error ? <p className="context-error">{error}</p> : null}

      {readme ? (
        <div className="readme-result">
          <div className="context-status">
            <span data-mode={readme.mode}>{readme.mode}</span>
            <small>{readme.model ?? "Deterministic graph analysis"}</small>
          </div>
          <p className="provider-message">{readme.providerMessage}</p>
          <div className="readme-estimates">
            <div>
              <strong>{readme.modules.length}</strong>
              <span>modules</span>
            </div>
            <div>
              <strong>{readme.keyFiles.length}</strong>
              <span>key files</span>
            </div>
            <div>
              <strong>{readme.warnings.length}</strong>
              <span>warnings</span>
            </div>
          </div>
          <p className="artifact-path">
            Saved to <code>{readme.artifactPath}</code>
          </p>
          <div className="readme-preview">
            <h3>Preview</h3>
            <pre>{readme.markdown}</pre>
          </div>
          <button
            className="readme-copy"
            onClick={() => void copyMarkdown()}
            type="button"
          >
            Copy generated README
          </button>
        </div>
      ) : null}
    </aside>
  );
}
