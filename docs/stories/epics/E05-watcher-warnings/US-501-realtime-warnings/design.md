# Design

## Domain Model

- `GraphWarning`: type, level, message, source, target, optional symbol, and
  timestamp.
- Warning types: `BROKEN_IMPORT`, `DELETED_IMPORTED_FILE`,
  `MISSING_EXPORTED_SYMBOL`, `NEW_ORPHAN_FILE`, and
  `NEW_CIRCULAR_DEPENDENCY`.
- Active warnings represent the latest graph state; “new” structural warnings
  compare the previous and current graph.

## Application Flow

```text
supported file event from cross-platform polling observer
  -> debounce for 750 ms
  -> rebuild full graph
  -> compare previous/current graph
  -> write graph.json and warnings.json
  -> broadcast graph_updated
  -> broadcast warning_created for newly active warnings
  -> dashboard replaces graph and warning state
```

## Interface Contract

```text
GET /api/warnings
WS  /ws/events
```

`graph_updated` contains the complete parsed graph and active warnings.
`warning_created` contains one newly active warning.

## Data Model

No database changes. Active warnings are written to
`.vibegraph/warnings.json`.

## UI / Platform Impact

- Vite proxies `/ws` with WebSocket support.
- The workspace hook reconnects after transient socket closure.
- Warning nodes and broken edges use explicit warning colors.
- The warning console displays actionable messages.

## Observability

- Watcher startup and shutdown follow the FastAPI lifespan.
- The observer polls every 100 ms before the 750 ms debounce to avoid
  platform-specific FSEvents behavior while staying below the two-second
  warning target.
- Unsupported and ignored file events are discarded before debounce.
- WebSocket disconnects remove clients without failing the watcher.

## Alternatives Considered

1. Polling REST endpoints. Rejected because the product contract specifies
   realtime events and polling adds repeated requests.
2. Incremental graph mutation. Deferred because full rebuilds are acceptable
   for the MVP and are easier to validate.
3. Sending only an invalidation event. Rejected because a complete parsed
   event avoids a REST waterfall and stale warning races.
