# VibeGraph

**Live codebase maps for AI-powered builders.**

VibeGraph is a local-first developer tool that scans a repository, builds a
live file-level import graph, warns about dependency breakage, and recommends
the smallest useful set of files for an AI coding task.

The target launch experience is:

```bash
npx vibegraph@latest .
```

## Project Status

VibeGraph Phase 0 development foundations are running:

- React/Vite/TypeScript frontend.
- Python/FastAPI backend.
- TypeScript CLI workspace.
- Root development, test, typecheck, and build commands.

Scanner and graph behavior have not been implemented yet.

## Product Contracts

- [Product overview](docs/product/overview.md)
- [Runtime and CLI](docs/product/runtime-and-cli.md)
- [Analysis and graph engine](docs/product/analysis-and-graph.md)
- [Dashboard and generated workflows](docs/product/dashboard-and-workflows.md)
- [Delivery and validation](docs/product/delivery-and-validation.md)

`SPEC.md` is the accepted source specification and historical input. Ongoing
product changes should update the smaller contracts above, relevant story
packets, test matrix entries, and decision records.

## Planned Architecture

```text
npm CLI
  -> local Python/FastAPI runtime
      -> scanner and import parsers
      -> directed NetworkX graph
      -> watcher and warning engine
      -> context-pack and README generators
  -> React/Vite dashboard
```

The MVP supports Python, JavaScript, JSX, TypeScript, and TSX files. Core
scanning, visualization, warnings, and heuristic context recommendations must
work without an API key.

## Local Development

Prerequisites:

- Node.js 22 or newer.
- pnpm 10.
- Python 3.11 or newer.
- [uv](https://docs.astral.sh/uv/).

Install dependencies:

```bash
pnpm install
uv sync --project backend
```

Start the backend and frontend together:

```bash
pnpm dev
```

Local endpoints:

```text
Dashboard: http://127.0.0.1:5173
Backend:   http://127.0.0.1:8000
Health:    http://127.0.0.1:8000/api/health
```

No LLM API key is required.

Run all current verification:

```bash
pnpm check
```

This performs TypeScript checks, Python/CLI/frontend tests, and production
builds.

The current CLI foundation can also be inspected after a build:

```bash
node cli/dist/index.js . --port 8732 --no-open
```

Full backend process orchestration and the public `npx vibegraph@latest .`
release flow remain Phase 6 work.

## Current Work

The selected implementation initiative remains Phase 0:

- Create and reserve the `.vibegraph/` output directory.

See [the story backlog](docs/stories/backlog.md) and
[test matrix](docs/TEST_MATRIX.md) for current status.

## Agent Workflow

This repository uses Harness. Before changing code, read `AGENTS.md` and the
linked Harness documents, then query:

```bash
scripts/bin/harness-cli query matrix
```

The source hierarchy is:

```text
docs/product/* -> current product behavior
docs/stories/* -> selected implementation work
docs/TEST_MATRIX.md -> expected proof
docs/decisions/* -> durable technical choices
SPEC.md -> accepted historical source specification
```
