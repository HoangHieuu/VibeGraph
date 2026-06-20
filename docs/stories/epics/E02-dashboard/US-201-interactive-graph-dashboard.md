# US-201 Interactive Graph Dashboard

## Status

implemented

## Lane

normal

## Product Contract

The local dashboard renders the scanned repository as an interactive
force-directed graph with file inspection, search, noise filters, and grouped
module mode.

## Relevant Product Docs

- `docs/product/dashboard-and-workflows.md`
- `docs/product/analysis-and-graph.md`
- `docs/ARCHITECTURE.md`

## Acceptance Criteria

- Dashboard loads live project and graph data from the backend.
- `react-force-graph-2d` renders file nodes and import links.
- Overview mode renders compact degree-scaled dots so labels do not obscure
  nodes or links.
- Labels appear for hover, selection, search matches, and close zoom levels.
- Hovering a node immediately highlights its direct neighbors and connecting
  edges, shows their labels, and dims unrelated graph elements.
- Charge, link-distance, and collision forces keep connected nodes distinct
  while preserving visible module clusters.
- Zoom, pan, drag, hover, click, and neighborhood focus work.
- Selecting a node opens an inspector with metadata, dependencies, exports,
  warnings, and context-pack action.
- Search matches file names and partial paths, highlights matches, focuses a
  selected result, and opens its inspector.
- Test, config, and orphan filters update nodes and links safely.
- Reset restores the complete file graph.
- Grouped module mode aggregates files by folder without restarting.
- The dashboard remains usable with a generated 100-node fixture.

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | Graph transformations, search, filters, inspector derivation |
| Integration | API parsing and frontend state |
| E2E | Browser interactions across all required controls |
| Platform | Desktop and mobile browser layout |
| Release | Not required |

## Evidence

- `pnpm check` passes graph transformation, 100-node fixture, API boundary
  parsing, frontend component, typecheck, and production-build checks.
- Graph visual-rule tests prove that radius follows structural degree rather
  than filename length and that ordinary labels stay hidden at overview zoom.
- In-app browser QA verified project loading, file/path search, result focus,
  file inspection, module mode, test filtering, reset, rescan, and the
  Phase-4 README action notice.
- In-app browser QA verified the corrected overview renders degree-scaled dots
  with visible edges and no default label boxes. Search selection still focuses
  `GraphCanvas.tsx` and opens its inspector without console warnings or errors.
- In-app browser QA verified hovering `GraphCanvas.tsx` immediately dims
  unrelated nodes and links while brightening the hovered node, direct
  neighbors, connecting edges, and relevant labels.
- Double-clicking a rendered canvas node selected the file, opened its
  inspector, and focused the graph neighborhood.
- Desktop dashboard layout and the default narrow responsive layout rendered
  without browser console warnings or errors.
