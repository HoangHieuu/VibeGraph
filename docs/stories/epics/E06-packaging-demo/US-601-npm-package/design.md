# Design

## Domain Model

- A release artifact contains the compiled Node CLI, production frontend, and
  installable Python backend.
- A runtime cache is versioned by the backend dependency manifest.
- The analyzed repository remains separate from package and cache files.

## Application Flow

```text
npm executable
  -> validate project path and launch options
  -> locate bundled backend and frontend
  -> find Python 3.11+
  -> create or reuse isolated runtime cache
  -> install bundled backend dependencies when the manifest changes
  -> start Uvicorn on the requested dashboard port
  -> wait for /api/health
  -> print and optionally open the dashboard URL
```

The monorepo development fallback continues to start `pnpm dev` when bundled
runtime assets are absent.

## Interface Contract

The package exposes a `vibegraph` executable. The existing project-path,
`--port`, `--no-open`, and `--model` options remain unchanged.

Errors are concise for missing Python, environment creation failure, package
installation failure, startup failure, and port conflicts.

## Data Model

No application database changes. The Python environment is stored outside the
analyzed repository in an OS-appropriate VibeGraph cache directory. Generated
project artifacts remain under `.vibegraph/`.

## UI / Platform Impact

- The production frontend is served by FastAPI on the same port as the API.
- macOS/Linux use `bin/python`; Windows uses `Scripts/python.exe`.
- Python discovery checks `VIBEGRAPH_PYTHON`, then platform-standard commands.
- Package installation requires network access the first time dependencies are
  not already cached.

## Observability

Startup logs identify the project, Python bootstrap state, offline/provider
mode, and dashboard URL without printing API keys or source contents.

## Alternatives Considered

1. Start `pnpm dev` from the installed package. Rejected because package
   consumers do not have the monorepo or development dependencies.
2. Require users to start Python manually. Rejected because it violates the
   one-command launch contract.
3. Compile a native backend executable per platform. Deferred because it adds
   release-matrix and native-bundle complexity before npm artifact proof.
4. Rewrite the backend in Node. Rejected because it duplicates the implemented
   scanner, graph, watcher, and generation behavior.
