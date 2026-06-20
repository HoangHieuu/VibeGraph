import { useEffect, useState } from "react";

import { generateContextPack } from "../api/context";
import type { ContextPack } from "../types/context";

interface ContextPanelProps {
  initialTask: string;
  open: boolean;
  onClose: () => void;
  onNotice: (message: string) => void;
}

export function ContextPanel({
  initialTask,
  open,
  onClose,
  onNotice,
}: ContextPanelProps) {
  const [task, setTask] = useState("");
  const [pack, setPack] = useState<ContextPack | null>(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && initialTask) {
      setTask((current) => current || initialTask);
    }
  }, [initialTask, open]);

  if (!open) return null;

  async function generate() {
    if (task.trim().length < 3) {
      setError("Describe a coding task using at least three characters.");
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      setPack(await generateContextPack(task.trim()));
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Unable to generate context pack.",
      );
    } finally {
      setGenerating(false);
    }
  }

  async function copy(value: string, label: string) {
    try {
      await navigator.clipboard.writeText(value);
      onNotice(`${label} copied.`);
    } catch {
      onNotice(`Unable to copy ${label.toLowerCase()}.`);
    }
  }

  return (
    <aside
      aria-label="Context pack"
      aria-modal="true"
      className="context-panel"
      role="dialog"
    >
      <header>
        <div>
          <span className="context-eyebrow">Graph-aware context</span>
          <h2>Context pack</h2>
        </div>
        <button aria-label="Close context pack" onClick={onClose} type="button">
          ×
        </button>
      </header>

      <label className="context-task">
        Coding task
        <textarea
          onChange={(event) => setTask(event.target.value)}
          placeholder="Fix login error handling in auth.ts"
          rows={4}
          value={task}
        />
      </label>
      <button
        className="context-generate"
        disabled={generating}
        onClick={() => void generate()}
        type="button"
      >
        {generating ? "Querying graph…" : "Generate context pack"}
      </button>
      {error ? <p className="context-error">{error}</p> : null}

      {pack ? (
        <div className="context-result">
          <div className="context-status">
            <span data-mode={pack.mode}>{pack.mode}</span>
            <small>
              {pack.model ?? "Deterministic graph heuristics"}
            </small>
          </div>
          <p className="provider-message">{pack.providerMessage}</p>
          <div className="context-estimates">
            <div>
              <strong>{pack.recommendations.length}</strong>
              <span>files</span>
            </div>
            <div>
              <strong>{pack.estimatedTokens.toLocaleString()}</strong>
              <span>estimated tokens</span>
            </div>
            <div>
              <strong>{pack.reductionPercent}%</strong>
              <span>smaller</span>
            </div>
          </div>
          <ol className="context-files">
            {pack.recommendations.map((item) => (
              <li key={item.path}>
                <code>{item.path}</code>
                <p>{item.reason}</p>
              </li>
            ))}
          </ol>
          <p className="artifact-path">
            Saved to <code>{pack.artifactPath}</code>
          </p>
          <div className="context-copy-actions">
            <button
              onClick={() => void copy(pack.mentions, "File mentions")}
              type="button"
            >
              Copy file mentions
            </button>
            <button
              onClick={() => void copy(pack.prompt, "Prompt")}
              type="button"
            >
              Copy prompt
            </button>
          </div>
        </div>
      ) : null}
    </aside>
  );
}
