# 0013 Cross-Platform Polling Watcher

Date: 2026-06-20

## Status

Accepted

## Context

Phase 5 needs consistent source-file events on macOS, Linux, and Windows.
Watchdog's native macOS FSEvents observer failed to initialize reliably for
temporary repositories during integration tests. The product target allows a
full graph rebuild and requires warnings to appear within two seconds.

## Decision

Use Watchdog's `PollingObserver` with a 100 ms poll interval and a 750 ms
debounce. Filter unsupported files and ignored directories before scheduling
the graph rebuild.

The backend performs one full rebuild per debounced event group, writes graph
and warning artifacts, then broadcasts the complete parsed state through the
WebSocket event channel.

## Alternatives Considered

1. Platform-native Watchdog observers.
2. Frontend REST polling.
3. Incremental graph mutation and parser caches.

## Consequences

Positive:

- Deterministic behavior across supported operating systems.
- Simple startup and shutdown through the FastAPI lifespan.
- Measured warning latency remains below the two-second target.

Tradeoffs:

- Polling performs periodic filesystem checks.
- Full rebuild cost scales with repository size.
- Larger repositories may need adaptive polling or incremental analysis later.

## Follow-Up

- Benchmark Phase 5 on the final demo repository.
- Revisit incremental scanning only if the 30-second initial graph or
  two-second warning targets are missed.
