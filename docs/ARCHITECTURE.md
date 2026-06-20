# VibeGraph Architecture

## Product Surfaces

VibeGraph has two user-facing entry points:

- A Node/npm CLI launched from a project directory.
- A local React dashboard served by the VibeGraph runtime.

The CLI is the public launcher. The dashboard is the primary interactive
surface. The Python backend is an internal local service.

## Workspace Shape

```text
cli/
  src/
    arguments/
    runtime/
    commands/

backend/
  app/
    domain/
    application/
    infrastructure/
    interface/

frontend/
  src/
    api/
    components/
    features/
    graph/
    state/
```

This is the target boundary, not permission to create every folder before a
story needs it.

## Runtime Flow

```text
npx command
  -> resolve project path and CLI options
  -> start local Python backend
  -> backend scans and writes graph artifacts
  -> start or serve React dashboard
  -> optionally open local browser
  -> watcher refreshes graph and warnings
  -> dashboard receives REST/WebSocket updates
```

## Backend Layers

```text
domain
  <- application
      <- infrastructure
          <- interface
```

- Domain: file records, import references, graph records, warnings, ranking
  rules, and generated-document models.
- Application: scan, graph, rescan, context-pack, README, and warning use cases.
- Infrastructure: filesystem, parsers, NetworkX, Watchdog, and LLM clients.
- Interface: FastAPI routes, WebSocket events, DTO parsing, and presenters.

Inner layers must not depend on FastAPI, Watchdog, NetworkX concrete objects,
provider clients, environment variables, or frontend state.

## Frontend Boundaries

- API clients own backend transport and response parsing.
- Feature modules own search, inspection, filtering, context, README, and
  warning behavior.
- Graph rendering adapts product graph models to `react-force-graph-2d`.
- Components do not read generated files directly from the user's filesystem.

## CLI Boundaries

- Argument parsing produces a typed launch configuration.
- Runtime orchestration owns child-process lifecycle and signal forwarding.
- The CLI communicates with the backend through documented startup and health
  contracts, not backend internal imports.
- Packaging must preserve the public
  `npx @hoanghieudev/vibegraph@latest .` contract and `vibegraph` executable.

## Parse-First Rule

Unknown data is parsed before entering inner code:

```text
CLI args / HTTP payload / environment / parser output / provider response
  -> boundary parser
  -> typed DTO or configuration
  -> application use case
  -> domain model
```

## Data and Artifact Ownership

VibeGraph has no application database in the MVP. Generated artifacts live
under the analyzed project's `.vibegraph/` directory.

The backend is the sole writer of graph, warning, context, and generated README
artifacts. The frontend reads through the API.

## Observability

The backend emits one canonical JSON log line per request with timestamp,
level, request ID, action, duration, status code, and message. Project source
paths should be repository-relative in routine logs.

Provider errors, parser uncertainty, and unresolved imports are explicit
operational or product states. They are not silently discarded.

## Security and Privacy Boundary

Repository scanning is local. Provider calls receive structured, task-relevant
graph context rather than the entire repository by default. API keys remain in
environment configuration and must never be written under `.vibegraph/`.
