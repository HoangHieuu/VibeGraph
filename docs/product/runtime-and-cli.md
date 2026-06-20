# Runtime and CLI Contract

## Launch Contract

Primary command:

```bash
npx @vibedev/vibegraph@latest .
```

Supported options:

```bash
npx @vibedev/vibegraph@latest ./path-to-project
npx @vibedev/vibegraph@latest . --port 8732
npx @vibedev/vibegraph@latest . --no-open
npx @vibedev/vibegraph@latest . --rescan
npx @vibedev/vibegraph@latest . --model deepseek/deepseek-v4-flash
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

The npm-to-Python distribution mechanism is defined by
`docs/decisions/0014-bundled-python-bootstrap-runtime.md`.

## Packaged Runtime

The npm artifact contains:

```text
compiled Node CLI
built React dashboard
installable Python backend source
```

The packaged CLI requires Node.js 22+ and Python 3.11+. On first launch it
creates an isolated versioned Python environment in the user's VibeGraph cache,
installs the bundled backend and dependencies, and reuses that environment on
later launches. It does not install into global Python or write runtime
dependencies into the analyzed repository.

In packaged mode, FastAPI serves the dashboard, REST API, and WebSocket from
the requested dashboard port. A development checkout without bundled runtime
assets continues to use the monorepo `pnpm dev` flow.

The public npm package is `@vibedev/vibegraph`, and it exposes the fixed
`vibegraph` executable. The visible project author is `vibedev`, and the
repository is released under the MIT license.

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
VIBEGRAPH_MODEL=deepseek/deepseek-v4-flash
```

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
