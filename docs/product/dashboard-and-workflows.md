# Dashboard and Workflow Contract

## Dashboard

The local React/Vite dashboard contains:

- Project top bar with search, rescan, and README generation.
- Filters and context-task input.
- `react-force-graph-2d` graph canvas.
- File inspector.
- Warning console.

The graph supports zoom, pan, node dragging, hover, selection, neighborhood
focus, search, visibility filters, and file/grouped-module modes.

## File Inspection

Selecting a file shows:

- Path, language, and LOC.
- Imports and importers.
- Detected exports.
- Related warnings.
- Context-pack and copy actions.

## Context Pack

Input is a natural-language coding task. The workflow must query structured
graph data before producing recommendations.

Default constraints:

```text
max_files: 8
max_depth: 2
include_tests: true
include_config: false
include_docs: false
```

Ranking considers target match, graph distance, symbol overlap, test relevance,
and recent modification. Explicitly named files, direct dependencies,
importers, and relevant tests receive priority.

The result includes:

- Recommended file paths.
- A reason for each file.
- A copyable prompt.
- Estimated context size and reduction.
- `.vibegraph/context.md`.

Without an API key, deterministic graph heuristics and a basic prompt template
must produce a valid result. The configured OpenRouter model may improve
explanations but cannot replace graph retrieval, receive source contents by
default, or claim to edit files.

## README Generation

The generator uses project metadata and graph structure to create:

```text
.vibegraph/README.generated.md
```

It includes overview, architecture, main modules, a Mermaid diagram, run
instructions, key files, known warnings, and generation attribution.

The dashboard accepts an optional project description, confirms the generated
artifact, previews the Markdown, and supports copying the complete draft.

Without an API key, deterministic prose and structure remain available. The
configured OpenRouter model may improve overview, architecture, and
module-description prose, but it cannot add files, commands, warnings, or
Mermaid relationships and does not receive source contents.

## Local API

REST endpoints:

```text
GET  /api/health
GET  /api/project
GET  /api/graph
GET  /api/files/{file_path}
GET  /api/warnings
POST /api/rescan
POST /api/context-pack
POST /api/readme
```

WebSocket endpoint:

```text
WS /ws/events
```

Initial event types include `graph_updated` and `warning_created`.

`graph_updated` carries the complete parsed graph and active warning list so
the dashboard can replace both states without a follow-up REST request.
Transient WebSocket closure triggers a bounded client reconnect.

Unknown request payloads and provider responses must be parsed at interface
boundaries before entering application or graph logic.
