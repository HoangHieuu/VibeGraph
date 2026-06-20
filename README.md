# VibeGraph

**Live codebase maps for AI-powered builders.**

VibeGraph is a local-first developer tool that scans a repository, builds a
live file-level import graph, warns about dependency breakage, and recommends
the smallest useful set of files for an AI coding task.

The target launch experience is:

```bash
npx @vibedev/vibegraph@latest .
```

## Project Status

VibeGraph Phases 0 through 5 and the first Phase 6 packaging slice are
implemented locally:

- React/Vite/TypeScript frontend.
- Python/FastAPI backend.
- TypeScript CLI that launches both local services for a selected project.
- Root development, test, typecheck, and build commands.
- Safe, idempotent `.vibegraph/` output-directory initialization.
- Python, JavaScript, JSX, TypeScript, and TSX scanning.
- Directed dependency graph generation at `.vibegraph/graph.json`.
- Interactive file/module graph, search, filters, and file inspection.
- Deterministic graph-aware context ranking and `.vibegraph/context.md`.
- Optional OpenRouter wording enhancement with provider failure fallback.
- Dashboard context-pack workflow with prompt and file-mention copy actions.
- Deterministic graph-derived README generation with bounded Mermaid output.
- Optional OpenRouter README prose enhancement with offline fallback.
- Cross-platform, debounced repository watching with realtime graph refresh.
- Typed dependency, missing-symbol, orphan, and circular-dependency warnings.
- `.vibegraph/warnings.json` persistence and WebSocket dashboard updates.
- Packable npm CLI artifact containing the production dashboard and Python
  backend.
- First-run isolated Python environment bootstrap with cached reuse.
- Single-port production dashboard, API, and WebSocket runtime.
- Cross-platform GitHub Actions proof on Ubuntu and Windows.
- FastAPI/React authentication demo repository under `demo/`.
- Deployable React/Vite landing page under `site/`.

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

Optional OpenRouter enhancement:

```bash
cp .env.example .env
```

Then set:

```text
OPENROUTER_API_KEY=...
VIBEGRAPH_MODEL=deepseek/deepseek-v4-flash
```

Only structured graph metadata for deterministically ranked files is sent to
OpenRouter. Source file contents remain local, and provider failure falls back
to the offline result.

Run all current verification:

```bash
pnpm check
```

This performs TypeScript checks, Python/CLI/frontend tests, and production
builds.

The local CLI can be run after a build:

```bash
node cli/dist/index.js . --port 8732 --no-open
```

Build and smoke-test the installable npm tarball:

```bash
pnpm package
pnpm test:package
```

The tarball is written under `dist/`. The selected public package is
`@vibedev/vibegraph`, which preserves the `vibegraph` executable without
conflicting with the unrelated unscoped registry package. VibeGraph is
MIT-licensed and authored by
[vibedev](https://github.com/HoangHieuu).

Run the release demo validation:

```bash
pnpm demo:check
```

Start the landing page:

```bash
pnpm site:dev
```

## Current Work

Phases 0 through 5 are complete. Phase 6 now includes local npm packaging,
fresh-environment launch proof, Ubuntu/Windows CI, the demo repository, and the
landing page. Remaining work is public registry publication, public deployment,
and submission URLs/polish.

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
