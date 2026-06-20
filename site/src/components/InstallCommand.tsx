import { useState } from "react";

export const INSTALL_COMMAND = "npx @vibedev/vibegraph@latest .";

interface InstallCommandProps {
  prominent?: boolean;
}

export function InstallCommand({ prominent = false }: InstallCommandProps) {
  const [copied, setCopied] = useState(false);

  async function copyCommand() {
    await navigator.clipboard.writeText(INSTALL_COMMAND);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  return (
    <div className={`install-command${prominent ? " install-command-prominent" : ""}`}>
      <span className="terminal-dot" aria-hidden="true" />
      <code>{INSTALL_COMMAND}</code>
      <button type="button" onClick={copyCommand}>
        {copied ? "Copied" : "Copy"}
      </button>
    </div>
  );
}
