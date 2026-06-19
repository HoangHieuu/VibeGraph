# 0008 VibeGraph Workspace Stack

Date: 2026-06-19

## Status

Accepted

## Context

The accepted product specification locks a one-command npm experience, a
Python analysis backend, and a React browser dashboard. The repository needs
stable ownership boundaries before scaffolding.

## Decision

Use three explicit workspaces:

- `cli/`: Node and TypeScript.
- `backend/`: Python, FastAPI, Uvicorn, NetworkX, and Watchdog.
- `frontend/`: React, Vite, TypeScript, TailwindCSS, and
  `react-force-graph-2d`.

The CLI orchestrates the local runtime, the backend owns analysis and generated
artifacts, and the frontend consumes backend contracts.

## Alternatives Considered

1. Implement everything in TypeScript.
2. Implement a Python CLI and require users to install it directly.
3. Embed analysis logic in the frontend.

## Consequences

Positive:

- Each technology matches its strongest product responsibility.
- The public npm command remains possible.
- Backend analysis remains independently testable.

Tradeoffs:

- Cross-language process orchestration and packaging require explicit proof.
- Shared API models need disciplined synchronization.

## Follow-Up

- Phase 0 selects package-manager and Python-environment commands.
- Release work decides how the npm package acquires or ships the Python
  runtime.
