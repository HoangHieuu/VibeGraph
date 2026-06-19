# Runtime and CLI Contract

## Launch Contract

Primary command:

```bash
npx vibegraph@latest .
```

Supported options:

```bash
npx vibegraph@latest ./path-to-project
npx vibegraph@latest . --port 8732
npx vibegraph@latest . --no-open
npx vibegraph@latest . --rescan
npx vibegraph@latest . --model google/gemini-2.0-flash-001
```

The CLI must validate the target path, start the local runtime, print the
dashboard URL, and remain usable without an LLM API key.

## Workspace Boundaries

The implementation will expose three clear workspaces:

```text
cli/       Node/TypeScript command and process orchestration
backend/   Python/FastAPI analysis and generation services
frontend/  React/Vite/TypeScript dashboard
```

The exact monorepo package manager and Python environment commands are selected
in Phase 0, but the public workspace boundaries are fixed.

## Runtime Ownership

- The Node CLI owns argument parsing, project-path resolution, process
  startup/shutdown, port selection, and browser-open behavior.
- The Python backend owns scanning, parsing, graph construction, watching,
  context selection, README generation, REST, and WebSocket events.
- The frontend owns visualization and local user interaction.

The exact npm-to-Python distribution mechanism remains an explicit packaging
decision for the release phase.

## Required Output Directory

VibeGraph creates `.vibegraph/` inside the analyzed project and reserves:

```text
.vibegraph/graph.json
.vibegraph/context.md
.vibegraph/README.generated.md
.vibegraph/warnings.json
```

The scanner must ignore `.vibegraph/`.

## Provider Contract

Preferred configuration:

```bash
OPENROUTER_API_KEY=...
VIBEGRAPH_MODEL=google/gemini-2.0-flash-001
```

`GEMINI_API_KEY` may be accepted as a convenience alias.

Without an API key, scanning, graph generation, dashboard behavior, watching,
warnings, deterministic context selection, and structured README generation
remain available. Provider failures must fall back to deterministic behavior.

## Error Contract

The CLI must emit clear, non-stack-trace-first messages for:

- Invalid target paths.
- Repositories with no supported source files.
- Missing API keys.
- Port conflicts or backend startup failures.

No API key is informational, not an error.
