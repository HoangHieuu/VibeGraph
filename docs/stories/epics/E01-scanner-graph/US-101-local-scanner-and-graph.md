# US-101 Local Scanner and Graph

## Status

implemented

## Lane

normal

## Product Contract

A builder can launch VibeGraph for a local project, scan supported source
files, resolve common imports, and consume a generated directed graph through
`.vibegraph/graph.json` and the local API.

## Relevant Product Docs

- `docs/product/runtime-and-cli.md`
- `docs/product/analysis-and-graph.md`
- `docs/product/dashboard-and-workflows.md`
- `docs/ARCHITECTURE.md`

## Acceptance Criteria

- The local CLI validates and accepts a project path.
- The CLI starts backend and frontend services and prints the dashboard URL.
- No API key is required.
- Scanner ignore and language rules match the accepted specification.
- Python, JavaScript, JSX, TypeScript, and TSX metadata is detected.
- Common Python and JS/TS imports and top-level exports are extracted.
- Relative local imports resolve to repository-relative file paths.
- Unresolved imports remain explicit without aborting a scan.
- Directed nodes and links include required metadata and degree calculations.
- Startup and rescan write valid `.vibegraph/graph.json`.
- Project, graph, file-detail, warning, and rescan API routes are available.

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | Scanner rules, parsers, resolution, node classification |
| Integration | Mixed-language fixture scan, artifact writing, API routes |
| E2E | CLI starts local services and dashboard consumes graph API |
| Platform | Project-path validation and process lifecycle |
| Release | npm publication deferred to E06 |

## Evidence

- `pnpm check` passes scanner/parser/service/API tests, typechecks, and builds.
- Backend tests cover ignore rules, five supported source extensions, imports,
  exports, parent-directory resolution, unresolved imports, graph metadata,
  artifact writing, file detail, warnings, and rescan routes.
- A live scan of this repository produced 41 source files, 110 links, and zero
  active warnings in `.vibegraph/graph.json`.
- `node cli/dist/index.js . --port 8732 --no-open` launched both services,
  printed the correct URL, served the dashboard with HTTP 200, and proxied
  `/api/project` successfully without an API key.
