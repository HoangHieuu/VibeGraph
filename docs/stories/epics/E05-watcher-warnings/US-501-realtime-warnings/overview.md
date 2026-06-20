# Overview

## Current Behavior

The graph changes only after a manual rescan. `/api/warnings` derives unresolved
imports directly from graph links, `.vibegraph/warnings.json` is never written,
and the dashboard has no WebSocket connection.

## Target Behavior

Supported source-file saves are detected and debounced. The backend rebuilds
the graph, computes typed dependency and structural warnings, writes graph and
warning artifacts, and broadcasts the updated state to connected dashboards.
The graph, warning console, and file inspector update without a restart.

## Affected Users

- Builders changing code during a demo or hackathon.
- Teammates monitoring dependency breakage.
- AI-assisted developers who need current graph context.

## Affected Product Docs

- `docs/product/analysis-and-graph.md`
- `docs/product/dashboard-and-workflows.md`
- `docs/product/delivery-and-validation.md`

## Non-Goals

- Incremental graph recomputation.
- Runtime execution or type-checker diagnostics.
- Watching ignored directories or unsupported file types.
- Persisting historical warnings after they are resolved.
