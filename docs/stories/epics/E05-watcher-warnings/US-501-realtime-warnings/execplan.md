# Exec Plan

## Goal

Deliver realtime graph refresh and actionable dependency warnings without
restarting VibeGraph.

## Scope

In scope:

- Recursive supported-file watching with debounce.
- Full graph rebuild on relevant changes.
- Typed warning derivation and artifact writing.
- FastAPI WebSocket event stream.
- Dashboard updates, warning display, and graph highlighting.

Out of scope:

- Incremental parser caches.
- Compiler/type-checker integration.
- Warning history and acknowledgement.
- Packaging and public npm release.

## Risk Classification

Risk flags:

- Public contracts.
- Existing behavior.
- Cross-platform filesystem behavior.
- Concurrency.
- Weak proof until filesystem and WebSocket tests exist.

## Work Phases

1. Warning model and graph comparison.
2. Watcher and debounce lifecycle.
3. WebSocket event transport.
4. Frontend state and warning visuals.
5. Automated and browser verification.
6. Harness evidence.

## Stop Conditions

Pause for human confirmation if:

- The watcher must modify source files.
- Warning generation requires executing repository code.
- The event contract must expose absolute paths or source contents.
- Validation requirements need to be weakened.
